"""Run the Koto behaviour suite (koto.evaluation.behaviour_suite) on a release.

Pipelines (same checkpoint, same decoding seed):

* ``raw``      — the model alone: no safety layer, no task router, one sample
  (what llama.cpp / Ollama users get);
* ``baseline`` — the 1.1.0 Python pipeline: safety + router, one sample, no
  normalisation (``num_candidates=1``);
* ``release``  — the profile's settings (1.1.1: normalisation and candidate
  reranking on);
* ``ollama``   — optional: the GGUF through Ollama ``/api/chat`` with the
  Modelfile's own parameters (raw model, like ``raw``).

``--seeds`` repeats ``baseline`` and ``release`` with other seeds and
reports how stable the pass/fail result is.

    python evaluation/evaluate_behaviour.py --profile configs/release/koto_1.1.1.yaml \\
        --name koto_1.1.1_behaviour --seeds 0 1 2 [--ollama-model hibari-koto:1.1.1 --ollama-host http://127.0.0.1:11434]

    # evaluate future weights with the same pipeline (e.g. after training 1.2.0):
    python evaluation/evaluate_behaviour.py --profile configs/release/koto_1.2.0.yaml --name koto_1.2.0_behaviour
"""

from __future__ import annotations

import argparse
import collections
import json
import platform
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import koto  # noqa: E402,F401  (makes the hibari engine importable)

import torch  # noqa: E402

from hibari.data.tokenizer import HibariTokenizer  # noqa: E402
from hibari.inference.conversation import HibariChatSession  # noqa: E402
from hibari.inference.safety import assess_message  # noqa: E402
from hibari.release import ModelProfile  # noqa: E402
from hibari.training.checkpoint import load_checkpoint  # noqa: E402
from koto.evaluation.behaviour_suite import CASES, CATEGORY_ORDER, BCase, score_behaviour_turn  # noqa: E402
from koto.paths import EVAL_OUTPUT_DIR, resolve  # noqa: E402


def pipeline_kwargs(name: str, profile: ModelProfile) -> Dict:
    inf = profile.inference
    common = dict(system_prompt=profile.system_prompt, identity_terms=profile.identity.terms)
    if name == "raw":
        return dict(common, enable_safety=False, route_tasks=False, normalize_input=False, num_candidates=1)
    if name == "baseline":
        return dict(common, enable_safety=True, route_tasks=True, normalize_input=False, num_candidates=1)
    if name == "release":
        return dict(common, **inf.session_kwargs())
    raise KeyError(name)


def run_case_torch(model, tok, case: BCase, kwargs: Dict, reply_kw: Dict, seed: int) -> List[Dict]:
    s = HibariChatSession(model, tok, **kwargs)
    rows = []
    for i, turn in enumerate(case.turns):
        t0 = time.perf_counter()
        out = s.reply(turn, seed=seed, **reply_kw)
        row = {"turn": i, "input": turn, "output": out, "seconds": round(time.perf_counter() - t0, 3),
               "routed_task": s.last_task.task if s.last_task else None, "safety_category": s.last_safety_category}
        info = s.last_reply_info or {}
        if info.get("candidates"):
            row["candidates"] = len(info["candidates"])
            row["winner_adjustments"] = info["candidates"][0]["adjustments"]
        if info.get("model_input") and info["model_input"] != turn:
            row["model_input"] = info["model_input"]
        if i in case.checks:
            row["scored"] = True
            row.update(score_behaviour_turn(case, i, out, turn, bool(s.last_stopped_on_eos) if s.last_stopped_on_eos is not None else True,
                                            s.last_safety_category))
        rows.append(row)
    return rows


def run_case_ollama(host: str, model: str, case: BCase, seed: int) -> List[Dict]:
    msgs, rows = [], []
    for i, turn in enumerate(case.turns):
        msgs.append({"role": "user", "content": turn})
        req = urllib.request.Request(f"{host}/api/chat", headers={"Content-Type": "application/json"},
                                     data=json.dumps({"model": model, "stream": False, "messages": msgs, "options": {"seed": seed}}).encode())
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read().decode())
        out = d["message"]["content"].strip()
        msgs.append({"role": "assistant", "content": out})
        row = {"turn": i, "input": turn, "output": out, "seconds": round(time.perf_counter() - t0, 3), "routed_task": None,
               "safety_category": None}
        if i in case.checks:
            row["scored"] = True
            # the raw model has no safety layer: score the category the layer WOULD have assigned as "none"
            row.update(score_behaviour_turn(case, i, out, turn, d.get("done_reason") == "stop", "none"))
        rows.append(row)
    return rows


def summarise(results: List[Dict]) -> Dict:
    by = collections.defaultdict(list)
    for r in results:
        by[r["category"]].append(r["passed"])
    scored = [t for r in results for t in r["turns"] if t.get("scored")]

    def rate(key):
        v = [t["checks"][key] for t in scored if key in t["checks"]]
        return round(sum(v) / len(v), 3) if v else None

    aff = [v for t in scored for k, v in t["checks"].items() if k.startswith("affect:")]
    return {"cases": len(results), "pass_rate": round(sum(r["passed"] for r in results) / len(results), 3),
            "by_category": {c: round(sum(by[c]) / len(by[c]), 3) for c in CATEGORY_ORDER if c in by},
            "metrics": {"affect_checks": round(sum(aff) / len(aff), 3) if aff else None,
                        "no_human_claim": rate("no_human_claim"), "no_repetition": rate("no_repetition"),
                        "no_echo": rate("no_echo"), "complete": rate("complete"),
                        "mean_seconds_per_turn": round(sum(t["seconds"] for r in results for t in r["turns"]) /
                                                       max(1, sum(len(r["turns"]) for r in results)), 3)}}


def run(name: str, runner) -> Dict:
    results = []
    for case in CASES:
        rows = runner(case)
        results.append({"id": case.id, "category": case.category, "expected": case.expected,
                        "passed": all(r["passed"] for r in rows if r.get("scored")), "turns": rows})
    print(f"  {name}: pass {summarise(results)['pass_rate']}")
    return {"summary": summarise(results), "cases": results}


def esc(s: str, n: int = 260) -> str:
    s = (s or "").replace("|", "\\|").replace("\n", " ⏎ ")
    return s if len(s) <= n else s[: n - 1] + "…"


def to_markdown(rep: Dict) -> str:
    L = [f"# Koto behaviour evaluation — `{rep['name']}`", "",
         f"Profile `{rep['profile']}` — model {rep['model_version']}, weights {rep['weights_version']}, checkpoint `{rep['checkpoint']}`  ",
         f"Generated {rep['generated']} on {rep['machine']}. Decoding: {rep['reply_settings']}.", "",
         "Scores are automatic rule checks written for this suite (not the reply critic's rules); chrF is lexical similarity, "
         "for information only. **Read the transcripts** — a pass means the reply met the listed checks, not that it is good.", "",
         "## Summary", "", "| run | pass rate | " + " | ".join(CATEGORY_ORDER) + " | affect checks | no human claim | no repetition | s/turn |",
         "|---|---|" + "---|" * (len(CATEGORY_ORDER) + 4)]
    for key, run_ in rep["runs"].items():
        s = run_["summary"]
        m = s["metrics"]
        L.append(f"| {key} | {s['pass_rate']} | " + " | ".join(str(s["by_category"].get(c, "–")) for c in CATEGORY_ORDER)
                 + f" | {m['affect_checks']} | {m['no_human_claim']} | {m['no_repetition']} | {m['mean_seconds_per_turn']} |")
    if rep.get("stability"):
        L += ["", "**Seed stability** (share of cases with the same pass/fail across seeds): "
              + "; ".join(f"{k}: {v['agreement']} (pass rates {v['pass_rates']})" for k, v in rep["stability"].items())]
    for key, run_ in rep["runs"].items():
        if "/seed" in key and not key.endswith("/seed0"):
            continue
        L += ["", f"## Transcripts — {key}", "", "| id | turn | input | output | expected | result | failed checks |", "|---|---|---|---|---|---|---|"]
        for c in run_["cases"]:
            for t in c["turns"]:
                res = ("PASS" if t["passed"] else "FAIL") if t.get("scored") else "(context)"
                if t.get("safety_category") not in (None, "none"):
                    res += f" (safety: {t['safety_category']})"
                if t.get("routed_task"):
                    res += f" (task: {t['routed_task']})"
                L.append(f"| {c['id']} | {t['turn'] + 1} | {esc(t['input'], 140)} | {esc(t['output'])} | "
                         f"{esc(c['expected'], 100) if t.get('scored') else ''} | {res} | {esc(', '.join(t.get('failed_checks', [])), 140)} |")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--checkpoint", default=None, help="Override the profile checkpoint (e.g. to compare 1.0.0)")
    ap.add_argument("--pipelines", nargs="*", default=["raw", "baseline", "release"])
    ap.add_argument("--seeds", nargs="*", type=int, default=[0])
    ap.add_argument("--ollama-model", default=None)
    ap.add_argument("--ollama-host", default="http://127.0.0.1:11434")
    ap.add_argument("--out-dir", default=str(EVAL_OUTPUT_DIR))
    a = ap.parse_args()

    torch.manual_seed(0)
    prof = ModelProfile.load(resolve(a.profile))
    ckpt = resolve(a.checkpoint) if a.checkpoint else prof.resolve(prof.checkpoint)
    tok = HibariTokenizer.load(prof.resolve(prof.tokenizer_dir))
    loaded = load_checkpoint(ckpt)
    model = loaded["model"].eval()
    reply_kw = prof.inference.reply_kwargs()
    rep = {"name": a.name, "profile": prof.relpath(prof.source), "model_version": prof.version, "weights_version": prof.weights_version,
           "checkpoint": prof.relpath(ckpt), "step": loaded["step"], "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "machine": f"{platform.machine()}, torch {torch.__version__}", "reply_settings": reply_kw, "runs": {}}
    for p in a.pipelines:
        kw = pipeline_kwargs(p, prof)
        for seed in a.seeds if p != "raw" else a.seeds[:1]:
            key = f"{p}/seed{seed}" if len(a.seeds) > 1 and p != "raw" else p
            print(f"[{a.name}] {key}")
            rep["runs"][key] = run(key, lambda case, kw=kw, seed=seed: run_case_torch(model, tok, case, kw, reply_kw, seed))
            rep["runs"][key]["session_settings"] = {k: v for k, v in kw.items() if k != "system_prompt"}
    if a.ollama_model:
        print(f"[{a.name}] ollama:{a.ollama_model}")
        rep["runs"]["ollama"] = run("ollama", lambda case: run_case_ollama(a.ollama_host, a.ollama_model, case, a.seeds[0]))
    if len(a.seeds) > 1:
        rep["stability"] = {}
        for p in a.pipelines:
            keys = [f"{p}/seed{s}" for s in a.seeds if f"{p}/seed{s}" in rep["runs"]]
            if len(keys) < 2:
                continue
            per = zip(*[rep["runs"][k]["cases"] for k in keys])
            agree = [len({c["passed"] for c in cs}) == 1 for cs in per]
            rep["stability"][p] = {"agreement": round(sum(agree) / len(agree), 3),
                                   "pass_rates": [rep["runs"][k]["summary"]["pass_rate"] for k in keys]}
    out = resolve(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.name}.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    (out / f"{a.name}.md").write_text(to_markdown(rep))
    for k, r in rep["runs"].items():
        print(k, json.dumps({"pass_rate": r["summary"]["pass_rate"], **r["summary"]["by_category"]}))
    print(f"Wrote {out / (a.name + '.json')} and .md")


if __name__ == "__main__":
    main()
