"""Measure a processed Koto data mix (read-only; no downloads).

For each source: conversations, multi-turn share, reply length, duplicate share
(``hibari.data.pipeline``), schema problems, quality-filter rejections, the
emotional coverage of user turns (``hibari.inference.intent``), and overlap
with every evaluation suite (contamination).

    python scripts/dataset_report.py --data-dir data/processed_1.2.1 --split train --name mix_1.2.1
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import koto  # noqa: E402,F401

import argparse  # noqa: E402
import collections  # noqa: E402
import json  # noqa: E402

from hibari.data.pipeline import QualityFilter, conversation_stats, normalize_text, validate_conversation  # noqa: E402
from hibari.inference.intent import Intent, analyze_message  # noqa: E402
from koto.paths import OUTPUT_DIR, resolve  # noqa: E402


def eval_prompts():
    from koto.evaluation import suite as legacy
    from koto.evaluation.behaviour_suite import eval_user_texts as behaviour
    from koto.evaluation.upgrade_suite import eval_user_texts as upgrade
    texts = list(upgrade()) + list(behaviour()) + [t for c in legacy.CASES for r, t in c.turns if r == "user"]
    try:
        from koto.evaluation.conversation_suite import eval_user_texts as conversation
        texts += list(conversation())
    except ImportError:
        pass
    return {normalize_text(t) for t in texts if len(normalize_text(t).split()) >= 3}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--split", default="train")
    ap.add_argument("--name", required=True)
    ap.add_argument("--analyze-limit", type=int, default=4000, help="user turns analysed per source (emotion coverage)")
    a = ap.parse_args()

    recs = json.loads((resolve(a.data_dir) / f"{a.split}_conversations.json").read_text(encoding="utf-8"))
    by = collections.defaultdict(list)
    for r in recs:
        by[r.get("source", "unknown")].append(r)
    stats = conversation_stats(recs)
    qf = QualityFilter()
    banned = eval_prompts()
    report = {"data_dir": a.data_dir, "split": a.split, "conversations": len(recs), "sources": {}}
    for src, items in sorted(by.items()):
        schema = collections.Counter(p.split(":")[-1].strip() for r in items for p in validate_conversation(r["messages"]))
        _, rejects = qf.apply(items)
        users = [m["content"] for r in items for m in r["messages"] if m["role"] == "user"]
        emo, intents = collections.Counter(), collections.Counter()
        for u in users[: a.analyze_limit]:
            an = analyze_message(u)
            emo[an.emotion.value] += 1
            intents[an.intent.value] += 1
        n_an = max(1, min(len(users), a.analyze_limit))
        contaminated = sum(normalize_text(u) in banned for u in users)
        report["sources"][src] = {
            **stats[src],
            "share_of_mix": round(len(items) / len(recs), 3),
            "schema_problems": dict(schema),
            "quality_rejections": rejects,
            "quality_rejection_share": round(sum(1 for r in items if qf.check(r["messages"])) / len(items), 3),
            "emotional_user_turn_share": round(1 - emo.get("none", 0) / n_an, 3),
            "emotions": {k: round(v / n_an, 3) for k, v in emo.most_common() if k != "none"},
            "rewrite_request_share": round(intents.get(Intent.REWRITE_REQUEST.value, 0) / n_an, 3),
            "question_share": round(intents.get(Intent.QUESTION.value, 0) / n_an, 3),
            "eval_prompt_overlap": contaminated,
        }
    out = OUTPUT_DIR / "data"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.name}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    cols = ["conversations", "share_of_mix", "multi_turn_share", "mean_turn_pairs", "mean_reply_words", "duplicate_share",
            "quality_rejection_share", "emotional_user_turn_share", "rewrite_request_share", "eval_prompt_overlap"]
    lines = [f"# Dataset report — `{a.name}` ({a.data_dir}, {a.split}, {len(recs):,} conversations)", "",
             "| source | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for src, s in report["sources"].items():
        lines.append(f"| {src} | " + " | ".join(str(s[c]) for c in cols) + " |")
    lines += ["", "Emotion detection uses the rule-based analyzer (English heuristics); shares are approximate.", ""]
    for src, s in report["sources"].items():
        lines.append(f"- **{src}**: emotions {s['emotions'] or '-'}; quality rejections {s['quality_rejections'] or '-'}; "
                     f"schema {s['schema_problems'] or 'ok'}")
    (out / f"{a.name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:len(report['sources']) + 4]))


if __name__ == "__main__":
    main()
