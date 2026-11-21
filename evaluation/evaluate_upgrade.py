"""Run the Koto 1.1.0 suite (koto.evaluation.upgrade_suite) on checkpoints.

For every checkpoint and every mode the report records, per scored turn:
input, generated output, expected behaviour, pass/fail with the failed
checks, and the generation settings.

Modes
* ``unrouted`` — the pre-1.1.0 chat path: every message is sent to the model
  as typed, with the chat decoding settings.
* ``routed``   — the 1.1.0 path: ``HibariChatSession`` recognises rewriting
  requests and sends them in the canonical task form with task decoding;
  other messages use the chat decoding settings.

Chat decoding is run twice: greedy, and the default sampling settings with a
fixed seed. Stability is measured by re-running the sampled pass with three
seeds (share of cases whose pass/fail does not change, and the mean pairwise
chrF of the outputs).

Optional: ``--data-dir`` with ``val``/``test`` conversation files adds a
held-out loss / perplexity table per source, and ``--train-file`` flags
evaluation prompts that occur in that training data (``seen_in_training``).

    python evaluation/evaluate_upgrade.py \\
        --checkpoint checkpoints/koto_start/best_model.pt --name koto_1.0.0 \\
        --data-dir data/processed_1.1.0 --train-file data/processed/train_conversations.json
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import platform
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import koto  # noqa: E402  (makes the hibari engine importable)

import torch  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from hibari.data.collator import DataCollatorForCausalLM  # noqa: E402
from hibari.data.dataset import ConversationDataset  # noqa: E402
from hibari.data.tokenizer import HibariTokenizer  # noqa: E402
from hibari.evaluation.metrics import char_ngram_f, distinct_n, mean  # noqa: E402
from hibari.inference.conversation import HibariChatSession  # noqa: E402
from hibari.inference.tasks import TASK_DECODING, parse_task_request  # noqa: E402
from hibari.training.checkpoint import load_checkpoint  # noqa: E402
from hibari.training.trainer import evaluate_loss  # noqa: E402
from koto.evaluation.upgrade_suite import CASES, CATEGORY_ORDER, Case, score_turn  # noqa: E402
from koto.paths import EVAL_OUTPUT_DIR, TOKENIZER_DIR, resolve  # noqa: E402

GREEDY = dict(temperature=0.0, top_k=0, top_p=1.0, repetition_penalty=1.0, no_repeat_ngram_size=0)
SAMPLED = dict(temperature=0.5, top_k=25, top_p=0.85, repetition_penalty=1.15, no_repeat_ngram_size=0)
CHAT_MAX_NEW = 96


def _norm(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


def training_user_texts(path: Optional[Path]) -> set:
    if not path or not path.exists():
        return set()
    out = set()
    for rec in json.loads(path.read_text()):
        msgs = rec["messages"] if isinstance(rec, dict) else rec
        for m in msgs:
            if m["role"] == "user":
                out.add(_norm(m["content"]))
                req = parse_task_request(m["content"])
                if req and req.text:
                    out.add(_norm(req.text))
    return out


def seen_in_training(case: Case, train_texts: set) -> List[str]:
    hits = []
    for t in case.turns:
        req = parse_task_request(t)
        for cand in [t] + ([req.text] if req and req.text else []):
            if _norm(cand) and _norm(cand) in train_texts:
                hits.append(cand)
    return hits


def run_case(model, tok, case: Case, routed: bool, decoding: Dict, seed: int) -> List[Dict]:
    session = HibariChatSession(model, tok, enable_safety=True, route_tasks=routed)
    rows = []
    for i, turn in enumerate(case.turns):
        t0 = time.perf_counter()
        out = session.reply(turn, max_new_tokens=CHAT_MAX_NEW, seed=seed, **decoding)
        dt = time.perf_counter() - t0
        task = session.last_task.task if session.last_task else None
        # Who produced the reply: the model, or a fixed application-layer
        # message (empty rewrite input, safety routing, empty chat input).
        lt = session.last_task
        flagged = session.last_safety_category not in (None, "none")
        if lt is not None:
            answered_by = "app" if (not lt.input or flagged or lt.chunks == 0) else "model"
        else:
            answered_by = "app" if (flagged or session.last_stopped_on_eos is None) else "model"
        settings = dict(TASK_DECODING, max_new_tokens="input-scaled") if task else dict(decoding, max_new_tokens=CHAT_MAX_NEW, seed=seed)
        row = {"turn": i, "input": turn, "output": out, "routed_task": task, "settings": settings,
               "stopped_on_eos": bool(session.last_stopped_on_eos), "answered_by": answered_by, "seconds": round(dt, 3)}
        if i in case.checks:
            row["scored"] = True
            row.update(score_turn(case.checks[i], out, turn, bool(session.last_stopped_on_eos)))
        rows.append(row)
    return rows


def run_suite(model, tok, routed: bool, decoding: Dict, seed: int, train_texts: set) -> List[Dict]:
    results = []
    for case in CASES:
        rows = run_case(model, tok, case, routed, decoding, seed)
        scored = [r for r in rows if r.get("scored")]
        results.append({"id": case.id, "category": case.category, "expected": case.expected,
                        "passed": all(r["passed"] for r in scored), "seen_in_training": seen_in_training(case, train_texts),
                        "turns": rows})
    return results


def summarise(results: List[Dict]) -> Dict:
    by_cat = collections.defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)
    scored = [t for r in results for t in r["turns"] if t.get("scored")]
    chat = [t for t in scored if "output_only" not in t["checks"]]      # conversational turns
    rewrites = [t for t in scored if "output_only" in t["checks"]]      # rewriting turns

    def rate(rows, key):
        vals = [row["checks"][key] for row in rows if key in row["checks"]]
        return round(sum(vals) / len(vals), 3) if vals else None

    def cat_rate(cats):
        rows = [r for r in results if r["category"] in cats]
        return round(sum(r["passed"] for r in rows) / len(rows), 3) if rows else None

    return {
        "cases": len(results),
        "pass_rate": round(sum(r["passed"] for r in results) / len(results), 3),
        "pass_rate_held_out_only": (lambda rows: round(sum(r["passed"] for r in rows) / len(rows), 3) if rows else None)(
            [r for r in results if not r["seen_in_training"]]),
        "by_category": {c: {"n": len(by_cat[c]), "pass_rate": round(sum(r["passed"] for r in by_cat[c]) / len(by_cat[c]), 3)}
                        for c in CATEGORY_ORDER if c in by_cat},
        "metrics": {
            "conversational_relevance": rate(chat, "require_any"),
            "context_retention": cat_rate({"context"}),
            "rephrasing_accuracy": cat_rate({"rephrase", "formal", "casual"}),
            "grammar_correction_exact": cat_rate({"grammar"}),
            "meaning_preservation": rate(rewrites, "preserves_terms"),
            "meaning_preservation_cases": cat_rate({"preservation"}),
            "output_only_rate": rate(rewrites, "output_only"),
            "coherence_grammar_heuristic": round(mean([t["grammar_heuristic_ok"] for t in scored]), 3),
            "repetition_free_rate": rate(scored, "no_repetition"),
            "eos_termination_rate": rate(scored, "complete"),
            "self_intro_free_rate": rate(scored, "no_self_intro"),
            "echo_free_rate": rate(scored, "no_echo"),
            "mean_reference_chrf": round(mean([t["reference_chrf"] for t in rewrites if t.get("reference_chrf") is not None]), 3),
            "distinct_2_chat": round(distinct_n([t["output"] for t in chat]), 3),
        },
    }


def stability(model, tok, routed: bool, seeds=(0, 1, 2)) -> Dict:
    runs = [run_suite(model, tok, routed, SAMPLED, s, set()) for s in seeds]
    agree, sims = [], []
    for per_case in zip(*runs):
        agree.append(len({r["passed"] for r in per_case}) == 1)
        finals = [[t["output"] for t in r["turns"] if t.get("scored")][-1] for r in per_case]
        sims += [char_ngram_f(a, b) for a, b in itertools.combinations(finals, 2)]
    return {"seeds": list(seeds), "pass_agreement_rate": round(mean(agree), 3), "mean_pairwise_chrf": round(mean(sims), 3),
            "pass_rate_per_seed": [summarise(r)["pass_rate"] for r in runs]}


def heldout_loss(model, tok, data_dir: Path) -> Dict:
    out = {}
    collate = DataCollatorForCausalLM(tok.pad_id)
    for split in ("val", "test"):
        f = data_dir / f"{split}_conversations.json"
        if not f.exists():
            continue
        by_src = collections.defaultdict(list)
        for rec in json.loads(f.read_text()):
            by_src[rec.get("source", "unknown")].append(rec)
        out[split] = {}
        for src, items in sorted(by_src.items()):
            ds = ConversationDataset(items, tok, max_seq_len=model.config.max_seq_len)
            if len(ds) == 0:
                continue
            m = evaluate_loss(model, DataLoader(ds, batch_size=32, collate_fn=collate), torch.device("cpu"))
            out[split][src] = {"loss": round(m["eval_loss"], 4), "perplexity": round(m["eval_perplexity"], 2), "examples": len(ds)}
    return out


def esc(s: str, n: int = 300) -> str:
    s = s.replace("|", "\\|").replace("\n", " ⏎ ")
    return s if len(s) <= n else s[: n - 1] + "…"


def to_markdown(rep: Dict) -> str:
    L = [f"# Koto evaluation — `{rep['name']}`", "",
         f"Checkpoint: `{rep['checkpoint']}` (step {rep['step']}, {rep['parameters']:,} parameters)  ",
         f"Generated: {rep['generated']} — {rep['machine']}", "",
         "All scores are **automatic rule checks** (regex expectations, exact corrections, preserved terms, length, "
         "repetition, echo, self-introduction and lead detection). chrF to a reference is shown for information only. "
         "`seen` marks cases whose prompt or source text occurs in this checkpoint's training data.", ""]
    if rep.get("heldout_loss"):
        L += ["## Held-out loss", "", "| split | source | loss | ppl | examples |", "|---|---|---|---|---|"]
        for split, srcs in rep["heldout_loss"].items():
            L += [f"| {split} | {s} | {m['loss']} | {m['perplexity']} | {m['examples']} |" for s, m in srcs.items()]
        L.append("")
    L += ["## Summary", "", "| mode | decoding | pass rate | held-out-only pass | " + " | ".join(CATEGORY_ORDER) + " |",
          "|---|---|---|---|" + "---|" * len(CATEGORY_ORDER)]
    for key, run in rep["runs"].items():
        s = run["summary"]
        cats = [str(s["by_category"].get(c, {}).get("pass_rate", "–")) for c in CATEGORY_ORDER]
        L.append(f"| {run['mode']} | {run['decoding_name']} | {s['pass_rate']} | {s['pass_rate_held_out_only']} | " + " | ".join(cats) + " |")
    L += ["", "| mode | decoding | " + " | ".join(next(iter(rep["runs"].values()))["summary"]["metrics"]) + " |",
          "|---|---|" + "---|" * len(next(iter(rep["runs"].values()))["summary"]["metrics"])]
    for run in rep["runs"].values():
        L.append(f"| {run['mode']} | {run['decoding_name']} | " + " | ".join(str(v) for v in run["summary"]["metrics"].values()) + " |")
    if rep.get("stability"):
        L += ["", "**Generation stability (sampled, seeds " + ", ".join(map(str, next(iter(rep['stability'].values()))['seeds'])) + "):** "
              + "; ".join(f"{m}: pass agreement {v['pass_agreement_rate']}, mean pairwise chrF {v['mean_pairwise_chrf']}, "
                          f"pass rate per seed {v['pass_rate_per_seed']}" for m, v in rep["stability"].items())]
    for key, run in rep["runs"].items():
        L += ["", f"## Transcripts — {run['mode']} / {run['decoding_name']}", "",
              "| id | turn | input | output | expected | result | failed checks | settings |", "|---|---|---|---|---|---|---|---|"]
        for c in run["cases"]:
            for t in c["turns"]:
                res = ("PASS" if t["passed"] else "FAIL") if t.get("scored") else "(context)"
                if t.get("answered_by") == "app":
                    res += " (app layer)"
                seen = " (seen)" if c["seen_in_training"] and t["turn"] == 0 else ""
                st = t["settings"]
                sets = (f"task {t['routed_task']}, greedy, ngram-block {st['no_repeat_ngram_size']}" if t["routed_task"]
                        else f"T={st['temperature']}, k={st['top_k']}, p={st['top_p']}, rep={st['repetition_penalty']}, max={st['max_new_tokens']}")
                L.append(f"| {c['id']}{seen} | {t['turn'] + 1} | {esc(t['input'], 160)} | {esc(t['output'])} | "
                         f"{esc(c['expected'], 120) if t.get('scored') else ''} | {res} | {esc(', '.join(t.get('failed_checks', [])), 160)} | {sets} |")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--name", required=True, help="Label for the report, e.g. koto_1.0.0")
    ap.add_argument("--tokenizer-dir", default=str(TOKENIZER_DIR))
    ap.add_argument("--data-dir", default=None, help="Directory with val/test_conversations.json for held-out loss")
    ap.add_argument("--train-file", default=None, help="Training conversations used to flag seen eval prompts")
    ap.add_argument("--modes", nargs="*", default=["unrouted", "routed"])
    ap.add_argument("--no-stability", action="store_true")
    ap.add_argument("--out-dir", default=str(EVAL_OUTPUT_DIR))
    a = ap.parse_args()

    torch.manual_seed(0)
    tok = HibariTokenizer.load(resolve(a.tokenizer_dir))
    loaded = load_checkpoint(resolve(a.checkpoint))
    model = loaded["model"].eval()
    train_texts = training_user_texts(resolve(a.train_file) if a.train_file else None)

    rep = {"name": a.name, "checkpoint": a.checkpoint, "step": loaded["step"], "parameters": model.count_parameters()["total"],
           "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "machine": f"{platform.machine()}, torch {torch.__version__}, threads {torch.get_num_threads()}",
           "suite_size": len(CASES), "train_file_for_seen_check": a.train_file, "runs": {}}
    if a.data_dir:
        rep["heldout_loss"] = heldout_loss(model, tok, resolve(a.data_dir))
    for mode in a.modes:
        for dname, dec in [("greedy", GREEDY), ("sampled_seed0", SAMPLED)]:
            print(f"[{a.name}] {mode} / {dname} ...")
            results = run_suite(model, tok, mode == "routed", dec, 0, train_texts)
            rep["runs"][f"{mode}/{dname}"] = {"mode": mode, "decoding_name": dname, "decoding": dec,
                                               "summary": summarise(results), "cases": results}
    if not a.no_stability:
        rep["stability"] = {m: stability(model, tok, m == "routed") for m in a.modes}

    out_dir = resolve(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{a.name}.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    (out_dir / f"{a.name}.md").write_text(to_markdown(rep))
    for k, run in rep["runs"].items():
        print(k, json.dumps({"pass_rate": run["summary"]["pass_rate"], **run["summary"]["by_category"]}))
    print(f"Wrote {out_dir / (a.name + '.json')} and .md")


if __name__ == "__main__":
    main()
