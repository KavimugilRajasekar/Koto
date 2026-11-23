"""Build a fine-tuning data mix: fresh curated conversations + general replay.

Reads the already-processed cache written by ``prepare_data.py`` (no
downloads), drops the old curated examples, samples ``--replay`` general
conversations to limit forgetting, and adds the current curated set from
``koto.data.curated`` repeated ``--curated-repeats`` times. The validation
split is copied unchanged so eval loss stays comparable across runs.

    python scripts/build_finetune_mix.py --src data/processed --dst data/processed_ft

(Koto 1.0 recipe. For 1.1.0 use scripts/build_mix.py, which also writes a
test split, provenance and leak checks.)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import koto  # noqa: E402,F401  (makes the hibari engine importable)

import argparse
import collections
import json
import random
import shutil

from hibari.data.formatting import DEFAULT_SYSTEM_PROMPT
from hibari.data.tokenizer import HibariTokenizer
from koto.data.curated import build_curated_conversations
from koto.data.rewrite import build_polite_conversations, load_coedit, load_paradetox, load_smol_rewrite
from koto.paths import DATA_DIR, TOKENIZER_DIR, resolve


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(DATA_DIR / "processed"))
    ap.add_argument("--dst", default=str(DATA_DIR / "processed_ft"))
    ap.add_argument("--tokenizer-dir", default=str(TOKENIZER_DIR))
    ap.add_argument("--replay", type=int, default=30000)
    ap.add_argument("--curated-repeats", type=int, default=3)
    ap.add_argument("--max-seq-len", type=int, default=256)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--coedit", type=int, default=0,
                    help="Number of CoEdIT writing-help examples to add (downloads grammarly/coedit)")
    ap.add_argument("--paradetox", type=int, default=0,
                    help="Number of ParaDetox rude->polite examples (downloads s-nlp/paradetox)")
    ap.add_argument("--smol-rewrite", type=int, default=0,
                    help="Max smol-rewrite examples that fit the context (downloads HuggingFaceTB/smoltalk)")
    ap.add_argument("--polite-repeats", type=int, default=0,
                    help="Add the hand-written polite/formal/email set this many times")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    src, dst = resolve(args.src), resolve(args.dst)
    dst.mkdir(parents=True, exist_ok=True)
    tok = HibariTokenizer.load(resolve(args.tokenizer_dir))

    with open(src / "train_conversations.json", encoding="utf-8") as f:
        train = json.load(f)
    general = [it for it in train if it["source"] != "curated"]
    rng.shuffle(general)
    replay = general[: args.replay]

    max_tokens = args.max_seq_len + 1
    dropped = collections.Counter()

    def fit(convs, source):
        kept = []
        for conv in convs:
            if conv[0]["role"] != "system":
                conv = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}] + conv
            n = len(tok.encode(tok.apply_chat_template(conv, add_generation_prompt=False)))
            if n <= max_tokens:
                kept.append({"source": source, "messages": conv})
            else:
                dropped[source] += 1
        return kept

    curated = fit(build_curated_conversations(DEFAULT_SYSTEM_PROMPT, seed=args.seed), "curated")
    writing: list = []
    if args.coedit:
        coedit_train, _ = load_coedit(seed=args.seed)
        writing += fit(coedit_train, "coedit")[: args.coedit]
    if args.paradetox:
        writing += fit(load_paradetox(seed=args.seed)[: args.paradetox * 2], "paradetox")[: args.paradetox]
    if args.smol_rewrite:
        writing += fit(load_smol_rewrite(seed=args.seed), "smol_rewrite")[: args.smol_rewrite]
    polite = fit(build_polite_conversations(seed=args.seed), "polite") if args.polite_repeats else []

    mix = replay + curated * args.curated_repeats + writing + polite * args.polite_repeats
    rng.shuffle(mix)

    with open(dst / "train_conversations.json", "w", encoding="utf-8") as f:
        json.dump(mix, f)
    shutil.copy(src / "val_conversations.json", dst / "val_conversations.json")
    stats = {
        "src": str(src),
        "replay": len(replay),
        "curated_unique": len(curated),
        "dropped_too_long": dict(dropped),
        "curated_repeats": args.curated_repeats,
        "writing_total": len(writing),
        "polite_unique": len(polite),
        "polite_repeats": args.polite_repeats,
        "final_train": len(mix),
        "by_source": dict(collections.Counter(it["source"] for it in mix)),
        "seed": args.seed,
    }
    with open(dst / "data_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
