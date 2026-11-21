"""Prepare the Hibari Koto training corpus.

Steps
1. Load every source (Hugging Face Hub, cached locally after first run) and
   convert it to chat messages.
2. Normalise: Hibari system prompt, cleaned text, strict alternation,
   ends with an assistant turn, emojis stripped from assistant turns.
3. Filter: drop examples whose assistant turns claim another identity
   (ChatGPT, OpenAssistant, "as an AI language model", ...).
4. Window: split long conversations at turn boundaries so every example fits
   ``max_seq_len`` tokens and ends with ``<|eos|>`` (no mid-reply truncation).
5. De-duplicate, remove train/validation overlap, apply per-source caps.
6. Save ``train_conversations.json`` / ``val_conversations.json`` as
   ``[{"source": str, "messages": [...]}, ...]`` plus ``data_stats.json``.

The existing tokenizer (hibari/models/tokenizer) is reused by default so the
vocabulary and token IDs of Hibari Koto do not change. Pass
``--retrain-tokenizer`` to build a new one.

Usage:
    python hibari/scripts/prepare_data.py --config hibari/configs/data/koto.yaml
"""

from __future__ import annotations

import argparse
import collections
import io
import json
import random
import re
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pyarrow.parquet as pq
import yaml
from datasets import load_dataset
from huggingface_hub import hf_hub_download

from hibari.data.curated import build_curated_conversations
from hibari.data.rewrite import build_polite_conversations, load_coedit
from hibari.data.formatting import (
    DEFAULT_SYSTEM_PROMPT,
    extract_raw_texts_for_tokenizer,
    format_blended_skill_talk_example,
    format_dailydialog_example,
    format_oasst1_example,
    format_prosocial_dialog_example,
    normalize_conversation,
    window_conversation,
)
from hibari.data.tokenizer import HibariTokenizer

Conv = List[Dict[str, str]]

FOREIGN_IDENTITY = re.compile(
    r"\b(openai|chatgpt|gpt-?[34]|llama|meta ai|hugging ?face|smollm|anthropic|claude|"
    r"open ?assistant|laion|language model|as an ai)\b",
    re.IGNORECASE,
)


def _parquet_rows(repo: str, filename: str) -> List[dict]:
    return pq.read_table(hf_hub_download(repo, filename, repo_type="dataset")).to_pylist()


# ───────────────────────── source loaders ─────────────────────────
# Each returns (train_convs, val_convs) as raw message lists.


def load_bst() -> Tuple[List[Conv], List[Conv]]:
    tr = [format_blended_skill_talk_example(ex) for ex in load_dataset("anezatra/blended-skill-talk", split="train")]
    va = [format_blended_skill_talk_example(ex) for ex in load_dataset("anezatra/blended-skill-talk", split="validation")]
    return tr, va


def load_dailydialog() -> Tuple[List[Conv], List[Conv]]:
    out = []
    for split in ["train", "validation"]:
        z = hf_hub_download("roskoN/dailydialog", f"{split}.zip", repo_type="dataset")
        with zipfile.ZipFile(z) as zf, zf.open(f"{split}/dialogues_{split}.txt") as f:
            lines = [ln.decode("utf-8").strip() for ln in f if ln.strip()]
        convs = []
        for line in lines:
            turns = [u.strip() for u in line.split("__eou__") if u.strip()]
            if len(turns) >= 2:
                convs.append(format_dailydialog_example(turns))
        out.append(convs)
    return out[0], out[1]


def load_prosocial() -> Tuple[List[Conv], List[Conv]]:
    tr = [format_prosocial_dialog_example(ex) for ex in load_dataset("allenai/prosocial-dialog", split="train")]
    va = [format_prosocial_dialog_example(ex) for ex in load_dataset("allenai/prosocial-dialog", split="validation")]
    return tr, va


def load_oasst() -> Tuple[List[Conv], List[Conv]]:
    def pairs(split):
        rows = {r["message_id"]: r for r in load_dataset("OpenAssistant/oasst1", split=split) if r.get("lang") == "en"}
        out = []
        for m in rows.values():
            if m.get("role") == "assistant" and m.get("rank") == 0 and m.get("parent_id") in rows:
                parent = rows[m["parent_id"]]
                if parent.get("role") == "prompter":
                    out.append(format_oasst1_example(parent["text"], m["text"]))
        return out
    return pairs("train"), pairs("validation")


def load_empathetic() -> Tuple[List[Conv], List[Conv]]:
    repo = "Estwld/empathetic_dialogues_llm"
    tr = [r["conversations"] for r in _parquet_rows(repo, "data/train-00000-of-00001.parquet")]
    va = [r["conversations"] for r in _parquet_rows(repo, "data/valid-00000-of-00001.parquet")]
    return tr, va


def load_everyday() -> Tuple[List[Conv], List[Conv]]:
    repo = "HuggingFaceTB/everyday-conversations-llama3.1-2k"
    tr = [r["messages"] for r in _parquet_rows(repo, "data/train_sft-00000-of-00001.parquet")]
    va = [r["messages"] for r in _parquet_rows(repo, "data/test_sft-00000-of-00001.parquet")]
    return tr, va


SMOLTALK_SUBSETS = {"openhermes-50k", "smol-magpie-ultra-short", "explore-instruct-rewrite"}


def load_smoltalk(n_shards: int = 3) -> Tuple[List[Conv], List[Conv]]:
    """Single-turn (first user/assistant pair) examples from selected subsets."""
    convs: List[Conv] = []
    for i in range(n_shards):
        for r in _parquet_rows("HuggingFaceTB/smol-smoltalk", f"data/train-{i:05d}-of-00004.parquet"):
            if r["source"] not in SMOLTALK_SUBSETS:
                continue
            msgs = [m for m in r["messages"] if m["role"] != "system"]
            if len(msgs) >= 2 and msgs[0]["role"] == "user" and msgs[1]["role"] == "assistant":
                convs.append(msgs[:2])
    rng = random.Random(7)
    rng.shuffle(convs)
    n_val = min(1000, len(convs) // 50)
    return convs[n_val:], convs[:n_val]


SOURCES = {
    "blended_skill_talk": load_bst,
    "dailydialog": load_dailydialog,
    "prosocial_dialog": load_prosocial,
    "oasst1": load_oasst,
    "empathetic_dialogues": load_empathetic,
    "everyday_conversations": load_everyday,
    "smoltalk": load_smoltalk,
    "coedit": load_coedit,
}


# ───────────────────────── processing ─────────────────────────


def _key(conv: Conv) -> str:
    return "\x1f".join(re.sub(r"\W+", " ", m["content"].lower()).strip() for m in conv[1:])


def process(convs: Iterable[Conv], tokenizer: HibariTokenizer, max_tokens: int) -> List[Conv]:
    def count(msgs: Conv) -> int:
        return len(tokenizer.encode(tokenizer.apply_chat_template(msgs)))

    out: List[Conv] = []
    for raw in convs:
        conv = normalize_conversation(raw, DEFAULT_SYSTEM_PROMPT)
        if not conv:
            continue
        if any(FOREIGN_IDENTITY.search(m["content"]) for m in conv if m["role"] == "assistant"):
            continue
        out.extend(window_conversation(conv, count, max_tokens))
    return out


def prepare_data(config_path: str) -> None:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    max_seq_len = int(cfg.get("max_seq_len", 256))
    # +1 because the dataset shifts inputs/targets by one token.
    max_tokens = max_seq_len + 1
    tokenizer_dir = Path(cfg.get("tokenizer_dir", "hibari/models/tokenizer"))
    data_cache_dir = Path(cfg.get("data_cache_dir", "hibari/data/processed"))
    data_cache_dir.mkdir(parents=True, exist_ok=True)
    caps: Dict[str, Dict[str, int]] = cfg.get("source_caps", {})
    repeats: Dict[str, int] = cfg.get("source_repeats", {})
    seed = int(cfg.get("seed", 42))
    rng = random.Random(seed)

    if cfg.get("retrain_tokenizer", False) or not (tokenizer_dir / "tokenizer.json").exists():
        raise SystemExit(
            "Tokenizer retraining is disabled for Koto (keeps token IDs stable). "
            "Restore hibari/models/tokenizer or set retrain_tokenizer explicitly in code."
        )
    tokenizer = HibariTokenizer.load(tokenizer_dir)
    print(f"Using tokenizer {tokenizer_dir} (vocab {tokenizer.vocab_size})")

    train_all: List[dict] = []
    val_all: List[dict] = []
    stats: Dict[str, dict] = {}

    for name in cfg.get("sources", list(SOURCES)):
        print(f"\n[{name}] loading...")
        tr_raw, va_raw = SOURCES[name]()
        tr = process(tr_raw, tokenizer, max_tokens)
        va = process(va_raw, tokenizer, max_tokens)
        rng.shuffle(tr)
        rng.shuffle(va)
        cap = caps.get(name, {})
        tr = tr[: cap.get("train", len(tr))]
        va = va[: cap.get("val", len(va))]
        print(f"  raw {len(tr_raw)}/{len(va_raw)} -> windows kept train {len(tr)}, val {len(va)}")
        stats[name] = {"raw_train": len(tr_raw), "raw_val": len(va_raw), "train": len(tr), "val": len(va)}
        train_all += [{"source": name, "messages": c} for c in tr]
        val_all += [{"source": name, "messages": c} for c in va]

    curated = build_curated_conversations(DEFAULT_SYSTEM_PROMPT, seed=seed)
    stats["curated"] = {"train": len(curated), "val": 0}
    train_all += [{"source": "curated", "messages": c} for c in curated]
    print(f"\n[curated] {len(curated)} conversations")

    polite = process(build_polite_conversations(seed=seed), tokenizer, max_tokens)
    stats["polite"] = {"train": len(polite), "val": 0}
    train_all += [{"source": "polite", "messages": c} for c in polite]
    print(f"[polite] {len(polite)} conversations")

    # De-duplicate within each split and remove train/val overlap.
    def dedup(items: List[dict]) -> List[dict]:
        seen, out = set(), []
        for it in items:
            k = _key(it["messages"])
            if it["source"] == "curated" or k not in seen:
                seen.add(k)
                out.append(it)
        return out

    train_all, val_all = dedup(train_all), dedup(val_all)
    val_keys = {_key(it["messages"]) for it in val_all}
    before = len(train_all)
    train_all = [it for it in train_all if _key(it["messages"]) not in val_keys]
    stats["_overlap_removed"] = before - len(train_all)

    # Up-weight small high-value sources by repetition.
    extra = []
    for it in train_all:
        extra += [it] * (repeats.get(it["source"], 1) - 1)
    train_all += extra
    rng.shuffle(train_all)

    counts = collections.Counter(it["source"] for it in train_all)
    stats["_final_train_by_source"] = dict(counts)
    stats["_final_train"] = len(train_all)
    stats["_final_val"] = len(val_all)
    stats["_system_prompt"] = DEFAULT_SYSTEM_PROMPT
    stats["_max_tokens_per_example"] = max_tokens

    with open(data_cache_dir / "train_conversations.json", "w", encoding="utf-8") as f:
        json.dump(train_all, f)
    with open(data_cache_dir / "val_conversations.json", "w", encoding="utf-8") as f:
        json.dump(val_all, f)
    with open(data_cache_dir / "data_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("\n" + "=" * 60)
    print(json.dumps(stats, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Prepare the Hibari Koto corpus")
    parser.add_argument("--config", default="hibari/configs/data/koto.yaml")
    args = parser.parse_args()
    prepare_data(args.config)


if __name__ == "__main__":
    main()
