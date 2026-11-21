"""Evaluate Hibari Koto checkpoints.

Produces, for each checkpoint:
  * validation loss / perplexity (token-weighted), overall and per source,
    on the held-out validation split written by prepare_data.py;
  * the held-out conversational suite (hibari.evaluation.suite), run on the
    RAW model (no application safety layer) and through the APP pipeline
    (HibariChatSession with the deterministic safety layer), with greedy
    decoding and with the default sampling settings (seeded);
  * automated metrics: generation success, completion, repetition,
    heuristic relevance and grammar, emoji use, safety routing;
  * CPU latency (first token, tokens/s) and peak RSS.

Usage:
    python hibari/scripts/evaluate.py \
        --checkpoint hibari/models/checkpoints/koto_start/best_model.pt \
        --out release/evaluation_report
"""

from __future__ import annotations

import argparse
import collections
import json
import platform
import resource
import time
from pathlib import Path
from typing import Dict, List

import torch
from torch.utils.data import DataLoader

from hibari.data.collator import DataCollatorForCausalLM
from hibari.data.dataset import ConversationDataset
from hibari.data.formatting import DEFAULT_SYSTEM_PROMPT
from hibari.data.tokenizer import HibariTokenizer
from hibari.evaluation.suite import CASES, REPORTED_PROMPTS, EvalCase, distinct_n, score_case
from hibari.inference.conversation import HibariChatSession
from hibari.inference.generation import generate_tokens
from hibari.inference.safety import assess_message, clean_response
from hibari.training.checkpoint import load_checkpoint
from hibari.training.trainer import evaluate_loss

GREEDY = dict(temperature=0.0, top_k=0, top_p=1.0, repetition_penalty=1.0)
SAMPLED = dict(temperature=0.5, top_k=25, top_p=0.85, repetition_penalty=1.15)
MAX_NEW = 64


def val_metrics(model, tok, val_path: Path, limit: int) -> Dict:
    recs = json.loads(val_path.read_text())[:limit]
    by_src = collections.defaultdict(list)
    for r in recs:
        by_src[r.get("source", "unknown") if isinstance(r, dict) else "unknown"].append(r)
    collate = DataCollatorForCausalLM(tok.pad_id)
    out = {}
    tot_loss = tot_tok = 0.0
    for src, items in sorted(by_src.items()):
        ds = ConversationDataset(items, tok, max_seq_len=model.config.max_seq_len)
        m = evaluate_loss(model, DataLoader(ds, batch_size=32, collate_fn=collate), torch.device("cpu"))
        out[src] = {"loss": round(m["eval_loss"], 4), "perplexity": round(m["eval_perplexity"], 2), "tokens": m["eval_tokens"], "examples": len(ds)}
        tot_loss += m["eval_loss"] * m["eval_tokens"]
        tot_tok += m["eval_tokens"]
    overall = tot_loss / max(1, tot_tok)
    return {"overall": {"loss": round(overall, 4), "perplexity": round(float(torch.tensor(overall).exp()), 2), "tokens": int(tot_tok)}, "by_source": out}


def messages_for(case) -> List[Dict[str, str]]:
    return [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}] + [{"role": r, "content": t} for r, t in case.turns]


def raw_reply(model, tok, case, decoding, seed=0):
    session = HibariChatSession(model, tok, enable_safety=False)
    session.messages = messages_for(case)
    ids = session.build_prompt_ids(MAX_NEW)
    t0 = time.perf_counter()
    out = generate_tokens(model, tok, "", prompt_ids=ids, max_new_tokens=MAX_NEW, seed=seed, **decoding)
    dt = time.perf_counter() - t0
    text = clean_response(tok.decode(out, skip_special_tokens=True))
    return text, len(out) < MAX_NEW, len(out), dt, len(ids)


def app_reply(model, tok, case, decoding, seed=0):
    session = HibariChatSession(model, tok, enable_safety=True)
    session.messages = messages_for(case)[:-1]
    reply = session.reply(case.final_user, max_new_tokens=MAX_NEW, seed=seed, **decoding)
    return reply, session.last_safety_category


def first_token_latency(model, tok, n=20) -> float:
    ids = tok.encode(tok.apply_chat_template(messages_for(CASES[0]), add_generation_prompt=True))
    ts = []
    for _ in range(n):
        t0 = time.perf_counter()
        generate_tokens(model, tok, "", prompt_ids=ids, max_new_tokens=1, temperature=0.0)
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return ts[len(ts) // 2]


def aggregate(rows: List[Dict]) -> Dict:
    n = len(rows)
    rel = [r for r in rows if r["relevant"] is not None]
    return {
        "n": n,
        "generation_success_rate": round(sum(r["non_empty"] for r in rows) / n, 3),
        "eos_termination_rate": round(sum(r["stopped_on_eos"] for r in rows) / n, 3),
        "response_completion_rate": round(sum(r["complete"] for r in rows) / n, 3),
        "repetition_rate": round(sum(r["repetitive"] for r in rows) / n, 3),
        "mean_3gram_repetition": round(sum(r["repetition_3gram"] for r in rows) / n, 3),
        "heuristic_relevance_rate": round(sum(r["relevant"] for r in rel) / max(1, len(rel)), 3),
        "heuristic_grammar_rate": round(sum(r["grammar_ok"] for r in rows) / n, 3),
        "forbidden_content_hits": sum(bool(r["forbidden_hits"]) for r in rows),
        "responses_with_emoji": sum(r["emoji_count"] > 0 for r in rows),
    }


def evaluate_checkpoint(ckpt: str, tok, val_path: Path, val_limit: int) -> Dict:
    loaded = load_checkpoint(ckpt)
    model = loaded["model"].eval()
    torch.set_num_threads(max(1, torch.get_num_threads()))
    res = {"checkpoint": ckpt, "step": loaded["step"], "parameters": model.count_parameters()["total"]}
    res["validation"] = val_metrics(model, tok, val_path, val_limit) if val_path.exists() else None

    for mode, dec in [("greedy", GREEDY), ("sampled", SAMPLED)]:
        rows, n_tok, secs = [], 0, 0.0
        for case in CASES:
            text, eos, ntok, dt, plen = raw_reply(model, tok, case, dec)
            n_tok += ntok
            secs += dt
            s = score_case(case, text, eos)
            app_text, app_cat = app_reply(model, tok, case, dec)
            rows.append({"id": case.id, "category": case.category, "user": case.final_user[:200],
                         "prompt_tokens": plen, "raw_reply": text, "app_reply": app_text,
                         "app_safety_category": app_cat, "expected_safety": case.safety, **s})
        by_cat = collections.defaultdict(list)
        for r in rows:
            by_cat[r["category"]].append(r)
        res[mode] = {
            "decoding": dec, "max_new_tokens": MAX_NEW,
            "summary": aggregate(rows),
            "by_category": {c: aggregate(v) for c, v in by_cat.items()},
            "distinct_2": round(distinct_n([r["raw_reply"] for r in rows]), 3),
            "tokens_per_second": round(n_tok / max(secs, 1e-9), 1),
            "cases": rows,
        }

    # Safety routing (application layer) on safety cases
    saf = [r for r in res["greedy"]["cases"] if r["category"] == "safety"]
    res["safety"] = {
        "app_layer_routing": [
            {"id": r["id"], "user": r["user"], "expected": r["expected_safety"], "got": r["app_safety_category"],
             "correct": (r["expected_safety"] or "none") == r["app_safety_category"]} for r in saf
        ],
        "raw_model_safe_and_helpful": [
            {"id": r["id"], "relevant": r["relevant"], "forbidden_hits": r["forbidden_hits"], "raw_reply": r["raw_reply"]} for r in saf
        ],
    }
    res["reported_prompts"] = []
    for p in REPORTED_PROMPTS:
        c = EvalCase("R", "reported", [("user", p)])
        raw, _, _, _, _ = raw_reply(model, tok, c, GREEDY)
        app, cat = app_reply(model, tok, c, SAMPLED)
        res["reported_prompts"].append({"user": p, "raw_model_greedy": raw, "app_sampled_seed0": app, "app_safety_category": cat})
    res["latency"] = {"first_token_seconds_median": round(first_token_latency(model, tok), 4)}
    return res


def to_markdown(report: Dict) -> str:
    L = ["# Hibari Koto — Evaluation Report", "",
         f"Generated: {report['generated']}  ", f"Machine: {report['machine']}  ",
         "All metrics are **automated**. *Relevance* and *grammar* are heuristic checks (regex expectations / surface rules), "
         "not human ratings. Prompts are held out from the curated training data.", ""]
    for r in report["results"]:
        L += [f"## `{r['checkpoint']}` (step {r['step']}, {r['parameters']:,} params)", ""]
        if r["validation"]:
            v = r["validation"]
            L += [f"**Validation (token-weighted):** loss {v['overall']['loss']}, perplexity {v['overall']['perplexity']} over {v['overall']['tokens']:,} tokens", "",
                  "| source | loss | ppl | examples |", "|---|---|---|---|"]
            L += [f"| {s} | {m['loss']} | {m['perplexity']} | {m['examples']} |" for s, m in v["by_source"].items()]
            L.append("")
        for mode in ["greedy", "sampled"]:
            s = r[mode]["summary"]
            L += [f"### {mode} decoding `{r[mode]['decoding']}`", "",
                  "| metric | value |", "|---|---|"]
            L += [f"| {k} | {v} |" for k, v in s.items()]
            L += [f"| distinct_2 | {r[mode]['distinct_2']} |", f"| tokens/s (CPU, PyTorch) | {r[mode]['tokens_per_second']} |", ""]
            L += ["| category | n | relevance | grammar | completion | repetition |", "|---|---|---|---|---|---|"]
            L += [f"| {c} | {a['n']} | {a['heuristic_relevance_rate']} | {a['heuristic_grammar_rate']} | {a['response_completion_rate']} | {a['repetition_rate']} |"
                  for c, a in r[mode]["by_category"].items()]
            L.append("")
        sr = r["safety"]["app_layer_routing"]
        L += [f"**Safety routing (application layer):** {sum(x['correct'] for x in sr)}/{len(sr)} correct", "",
              f"**First-token latency (median, PyTorch CPU):** {r['latency']['first_token_seconds_median']} s", "",
              "### Prompts from the original bug report (not held out — see suite.py)", "",
              "| user | raw model (greedy) | app pipeline (sampled, seed 0) | safety layer |", "|---|---|---|---|"]
        for c in r["reported_prompts"]:
            esc = lambda s: s.replace("|", "\\|").replace("\n", " ")[:220]
            L.append(f"| {c['user']} | {esc(c['raw_model_greedy'])} | {esc(c['app_sampled_seed0'])} | {c['app_safety_category']} |")
        L += ["", "### Greedy transcripts (raw model, no safety layer → app pipeline)", "",
              "| id | user | raw model | app reply | rel |", "|---|---|---|---|---|"]
        for c in r["greedy"]["cases"]:
            esc = lambda s: s.replace("|", "\\|").replace("\n", " ")[:220]
            L.append(f"| {c['id']} | {esc(c['user'])} | {esc(c['raw_reply'])} | {esc(c['app_reply'])} | {c['relevant']} |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--compare", nargs="*", default=[], help="Other checkpoints to evaluate side by side")
    ap.add_argument("--tokenizer-dir", default="hibari/models/tokenizer")
    ap.add_argument("--val", default="hibari/data/processed/val_conversations.json")
    ap.add_argument("--val-limit", type=int, default=4000)
    ap.add_argument("--out", default="release/evaluation_report")
    a = ap.parse_args()

    tok = HibariTokenizer.load(a.tokenizer_dir)
    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "machine": f"{platform.processor() or platform.machine()}, torch {torch.__version__}, threads {torch.get_num_threads()}",
        "results": [],
    }
    for ck in [a.checkpoint] + a.compare:
        print(f"Evaluating {ck} ...")
        report["results"].append(evaluate_checkpoint(ck, tok, Path(a.val), a.val_limit))
    report["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    out.with_suffix(".md").write_text(to_markdown(report))
    for r in report["results"]:
        print(r["checkpoint"], json.dumps(r["greedy"]["summary"]), r["validation"]["overall"] if r["validation"] else "")
    print(f"Wrote {out.with_suffix('.json')} and {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
