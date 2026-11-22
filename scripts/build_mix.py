"""Build the Koto 1.1.0 training mix (no downloads).

Inputs
* general conversation: ``<general_src>/{train,val}_conversations.json``
  written by ``scripts/prepare_data.py`` (old curated records are dropped
  and regenerated from ``koto.data.curated``);
* writing tasks: CoEdIT, ParaDetox and smol-rewrite from the local Hugging Face
  cache (run with ``HF_HUB_OFFLINE=1``; the script refuses to download), plus
  the hand-written sets in ``koto.data.tasks`` and ``koto.data.rewrite``;
* conversation: ``koto.data.conversation`` (small talk, explanations,
  context chains) and templated emails.

Processing
1. Task examples: de-duplicate per (task, source); a second, different target
   for the same source is a contradiction and is dropped.
2. Leak removal: every example whose source / user turn matches a prompt of
   the evaluation suites (``koto.evaluation.upgrade_suite`` and
   ``koto.evaluation.suite``) is removed.
3. Split: tasks and hand-written conversations get train / val / test by a
   stable hash of the normalised source (so one source is never in two
   splits); general data keeps the original train / val split.
4. Render (target-only replies; canonical or natural request), add the system
   prompt, drop examples longer than ``max_seq_len + 1`` tokens.
5. Write ``{train,val,test}_conversations.json`` and ``data_stats.json``
   (counts per source / task / split, provenance and licences, dedup and leak
   counts, tokenizer coverage, input file hashes).

The output directory must not exist yet unless ``--overwrite`` is given, so an
existing mix is never replaced by accident.

    HF_HUB_OFFLINE=1 python scripts/build_mix.py --config configs/data/koto_1.1.0.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import koto  # noqa: E402,F401  (makes the hibari engine importable)

import argparse  # noqa: E402
import collections  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
from typing import Dict, List  # noqa: E402

import yaml  # noqa: E402

from hibari.data.formatting import DEFAULT_SYSTEM_PROMPT  # noqa: E402
from hibari.data.tokenizer import HibariTokenizer  # noqa: E402
from hibari.inference.tasks import parse_task_request  # noqa: E402
from koto.data.behaviour import apply_identity_v2, build_behaviour_conversations  # noqa: E402
from koto.data.conversation import build_conversation_conversations  # noqa: E402
from koto.data.curated import build_curated_conversations  # noqa: E402
from koto.data.dialogue_skills import build_dialogue_skill_conversations  # noqa: E402
from koto.data.rewrite import (  # noqa: E402
    COEDIT_CAPS,
    build_email_conversations,
    coedit_examples,
    load_coedit_rows,
    load_paradetox_examples,
    load_smol_rewrite_examples,
    polite_examples,
)
from koto.data.tasks import TaskExample, dedup_examples, handwritten_task_examples, norm, remove_leaks, render, split_of  # noqa: E402
from koto.evaluation import suite as legacy_suite  # noqa: E402
from koto.evaluation.upgrade_suite import eval_user_texts  # noqa: E402
from koto.paths import resolve  # noqa: E402

LICENCES = {
    "coedit": "Apache-2.0 (grammarly/coedit)",
    "paradetox": "openrail++ (s-nlp/paradetox)",
    "smol_rewrite": "Apache-2.0 (HuggingFaceTB/smoltalk, smol-rewrite)",
    "handwritten": "MIT (written for Koto)",
    "curated": "MIT (written for Koto)",
    "conversation": "MIT (written for Koto)",
    "email": "MIT (written for Koto)",
    "dialogue_skills": "MIT (written for Koto)",
    "behaviour": "MIT (written for Koto)",
    "general": "see docs/16_DATASET_CATALOG.md (per source)",
}


def all_eval_texts() -> List[str]:
    texts = list(eval_user_texts())
    from koto.evaluation.behaviour_suite import eval_user_texts as behaviour_texts
    texts += behaviour_texts()
    for case in legacy_suite.CASES:
        texts += [t for r, t in case.turns if r == "user"]
    out = []
    for t in texts:
        out.append(t)
        req = parse_task_request(t)
        if req and req.text:
            out.append(req.text)
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/data/koto_1.1.0.yaml")
    ap.add_argument("--overwrite", action="store_true", help="Replace an existing output directory")
    a = ap.parse_args()
    cfg = yaml.safe_load(resolve(a.config).read_text())
    if os.environ.get("HF_HUB_OFFLINE") != "1":
        os.environ["HF_HUB_OFFLINE"] = "1"  # read the local cache only; never download

    out_dir = resolve(cfg["out_dir"])
    if out_dir.exists() and any(out_dir.iterdir()) and not a.overwrite:
        raise SystemExit(f"{out_dir} already exists; choose a new out_dir or pass --overwrite")
    out_dir.mkdir(parents=True, exist_ok=True)

    seed = int(cfg.get("seed", 110))
    rng = random.Random(seed)
    tok = HibariTokenizer.load(resolve(cfg.get("tokenizer_dir", "tokenizer")))
    max_tokens = int(cfg.get("max_seq_len", 256)) + 1
    # 1.2.0+: `system_prompt` replaces the prompt in EVERY example (also the
    # general corpus, whose records carry the 1.x prompt); `identity: v2`
    # rewrites the hand-written assistant turns to the new identity.
    system_prompt = (cfg.get("system_prompt") or DEFAULT_SYSTEM_PROMPT).strip()
    identity = str(cfg.get("identity", "v1"))
    ident = apply_identity_v2 if identity == "v2" else (lambda c: c)
    sysmsg = {"role": "system", "content": system_prompt}
    stats: Dict = {"experiment": cfg.get("experiment"), "config": cfg, "system_prompt": system_prompt, "identity": identity,
                   "max_tokens_per_example": max_tokens, "licences": LICENCES}
    eval_texts = all_eval_texts()
    # Conversation turns: only prompts of 3+ words can sensibly be kept out of
    # training ("ok", "Hello!" occur everywhere in real dialogue); shorter
    # overlaps are reported by the evaluation as `seen_in_training`. Task
    # sources are always filtered, whatever their length.
    banned = {norm(t) for t in eval_texts if len(norm(t).split()) >= 3}
    stats["short_eval_prompts_not_filtered"] = sorted({norm(t) for t in eval_texts if 0 < len(norm(t).split()) < 3})
    splits: Dict[str, List[dict]] = {"train": [], "val": [], "test": []}
    dropped_long = collections.Counter()
    leak_drops = collections.Counter()

    def n_tokens(msgs) -> int:
        return len(tok.encode(tok.apply_chat_template(msgs)))

    def add(split: str, source: str, msgs: List[dict], task: str | None = None, origin: str | None = None) -> None:
        msgs = [sysmsg] + msgs[1:] if msgs and msgs[0]["role"] == "system" else [sysmsg] + msgs
        if n_tokens(msgs) > max_tokens:
            dropped_long[source] += 1
            return
        rec = {"source": source, "messages": msgs}
        if task:
            rec["task"] = task
        if origin:
            rec["origin"] = origin
        splits[split].append(rec)

    def leaks(msgs: List[dict]) -> bool:
        for m in msgs:
            if m["role"] != "user":
                continue
            if norm(m["content"]) in banned:
                return True
            req = parse_task_request(m["content"])
            if req and norm(req.text) in banned:
                return True
        return False

    # ── 1. general conversation (existing processed corpus) ──
    gsrc = resolve(cfg["general_src"])
    g_train = json.loads((gsrc / "train_conversations.json").read_text())
    g_val = json.loads((gsrc / "val_conversations.json").read_text())
    stats["inputs"] = {str(gsrc / f): sha256(gsrc / f) for f in ("train_conversations.json", "val_conversations.json")}
    g_train = [r for r in g_train if r["source"] != "curated"]
    rng.shuffle(g_train)
    cap = cfg.get("general_train", "all")
    if cap != "all":
        g_train = g_train[: int(cap)]
    for r in g_train:
        if leaks(r["messages"]):
            leak_drops["general"] += 1
            continue
        add("train", r["source"], r["messages"])
    for r in g_val:
        add("val", r["source"], r["messages"])

    # ── 2. curated identity / personality / safety (train only, as in 1.0) ──
    curated = [ident(c) for c in build_curated_conversations(system_prompt, seed=seed)]
    kept_curated = [c for c in curated if not leaks(c)]
    leak_drops["curated"] = len(curated) - len(kept_curated)
    for _ in range(int(cfg.get("curated_repeats", 3))):
        for c in kept_curated:
            add("train", "curated", c)

    # ── 3. hand-written conversation set + emails (hash split) ──
    conv = [ident(c) for c in build_conversation_conversations(seed=seed, repeats=int(cfg.get("conversation_variants", 3)))]
    conv_split = collections.Counter()
    seen_conv = set()
    for c in conv:
        key = " | ".join(norm(m["content"]) for m in c if m["role"] == "user")
        if key in seen_conv:
            continue
        seen_conv.add(key)
        if leaks(c):
            leak_drops["conversation"] += 1
            continue
        sp = split_of(key, cfg.get("val_pct", 4), cfg.get("test_pct", 4))
        conv_split[sp] += 1
        reps = int(cfg.get("conversation_repeats", 3)) if sp == "train" else 1
        for _ in range(reps):
            add(sp, "conversation", c)
    for c in build_email_conversations(seed=seed, n_emails=int(cfg.get("emails", 400))):
        add("train", "email", ident(c))

    # ── 3b. dialogue skills: recall, clarification, honest limits, chat vs.
    #        correction, multi / repeated questions (koto.data.dialogue_skills).
    #        Off unless `dialogue_skills_repeats` > 0, so older configs rebuild unchanged.
    ds_repeats = int(cfg.get("dialogue_skills_repeats", 0))
    if ds_repeats > 0:
        ds_split = collections.Counter()
        seen_ds = set()
        families = build_dialogue_skill_conversations(seed=seed + 2, recall_n=int(cfg.get("recall_conversations", 1500)))
        for family, convs in families.items():
            for c in convs:
                c = ident(c)
                key = " | ".join(norm(m["content"]) for m in c)
                if key in seen_ds:
                    continue
                seen_ds.add(key)
                if leaks(c):
                    leak_drops["dialogue_skills"] += 1
                    continue
                sp = split_of(key, cfg.get("val_pct", 4), cfg.get("test_pct", 4))
                ds_split[f"{family}/{sp}"] += 1
                for _ in range(ds_repeats if sp == "train" else 1):
                    add(sp, "dialogue_skills", c, origin=family)
        stats["dialogue_skills_unique_by_family_split"] = dict(ds_split)

    # ── 3c. behaviour (1.2.0): identity v2, empathy, grief / sympathy / good
    #        news, hostile messages, informal chat, context chains, full
    #        e-mails (koto.data.behaviour). Off unless `behaviour_repeats` > 0.
    bh_repeats = int(cfg.get("behaviour_repeats", 0))
    if bh_repeats > 0:
        bh_split = collections.Counter()
        seen_bh = set()
        for family, convs in build_behaviour_conversations(seed=seed + 3).items():
            for c in convs:
                key = " | ".join(norm(m["content"]) for m in c)
                if key in seen_bh:
                    continue
                seen_bh.add(key)
                if leaks(c):
                    leak_drops["behaviour"] += 1
                    continue
                sp = split_of(key, cfg.get("val_pct", 4), cfg.get("test_pct", 4))
                bh_split[f"{family}/{sp}"] += 1
                for _ in range(bh_repeats if sp == "train" else 1):
                    add(sp, "behaviour", c, origin=family)
        stats["behaviour_unique_by_family_split"] = dict(bh_split)

    # ── 4. writing tasks ──
    tcfg = cfg.get("tasks", {})
    examples: List[TaskExample] = []
    rows = load_coedit_rows()
    examples += coedit_examples(rows, random.Random(seed), {**COEDIT_CAPS, **tcfg.get("coedit", {})})
    pdx = load_paradetox_examples()
    random.Random(seed).shuffle(pdx)
    examples += pdx[: int(tcfg.get("paradetox", 5000))]
    smol = load_smol_rewrite_examples()
    random.Random(seed).shuffle(smol)
    examples += smol  # faithful pairs only; capped at `smol_rewrite` after the length filter
    examples += polite_examples(seed=seed, n_templated=int(tcfg.get("polite_templated", 600)))
    handwritten = handwritten_task_examples(seed=seed)
    examples += handwritten

    before = len(examples)
    examples, dedup_stats = dedup_examples(examples)
    examples, n_leak = remove_leaks(examples, eval_texts)
    leak_drops["tasks"] += n_leak
    stats["task_dedup"] = {"before": before, "after_dedup": before - sum(dedup_stats.values()), **dedup_stats}

    hw_repeats = int(tcfg.get("handwritten_repeats", 2))
    task_repeats = tcfg.get("task_repeats", {})
    smol_cap = int(tcfg.get("smol_rewrite", 2500))
    smol_kept = 0
    task_counts = collections.Counter()
    canonical = float(cfg.get("canonical_share", 0.5))
    for ex in examples:
        family = ex.origin.split(":")[0]
        sp = split_of(f"{ex.task}|{ex.source}", cfg.get("val_pct", 4), cfg.get("test_pct", 4))
        if family == "smol_rewrite":
            if smol_kept >= smol_cap:
                continue
        reps = hw_repeats if (family == "handwritten" and sp == "train") else 1
        if sp == "train":
            reps *= int(task_repeats.get(ex.task, 1))
        for _ in range(reps):
            conv_msgs = render(ex, rng, canonical)
            n_before = len(splits[sp])
            add(sp, family, conv_msgs, task=ex.task, origin=ex.origin)
            if len(splits[sp]) > n_before:
                task_counts[(sp, ex.task)] += 1
                if family == "smol_rewrite":
                    smol_kept += 1

    for sp in splits:
        rng.shuffle(splits[sp])

    # ── 5. checks and stats ──
    train_users = {norm(m["content"]) for r in splits["train"] for m in r["messages"] if m["role"] == "user"}
    held_users = {norm(m["content"]) for sp in ("val", "test") for r in splits[sp] if r["source"] not in
                  {"blended_skill_talk", "dailydialog", "prosocial_dialog", "oasst1", "empathetic_dialogues",
                   "everyday_conversations", "smoltalk"} for m in r["messages"] if m["role"] == "user"}
    unk_id = tok.unk_id
    unk = sum(tok.encode(tok.apply_chat_template(r["messages"])).count(unk_id) for sp in splits for r in splits[sp][:20000])
    stats["splits"] = {sp: {"examples": len(v), "by_source": dict(collections.Counter(r["source"] for r in v))}
                       for sp, v in splits.items()}
    stats["tasks_by_split"] = {sp: {t: n for (s, t), n in task_counts.items() if s == sp} for sp in splits}
    stats["conversation_unique_by_split"] = dict(conv_split)
    stats["dropped_too_long"] = dict(dropped_long)
    stats["leak_drops"] = dict(leak_drops)
    stats["eval_prompts_checked"] = len(banned)
    stats["eval_prompts_in_train_user_turns"] = sorted(t for t in banned if t in train_users)
    stats["heldout_user_turns_also_in_train"] = len(held_users & train_users)
    stats["unk_tokens_in_first_20k_per_split"] = unk
    task_train = sum(n for (s, _), n in task_counts.items() if s == "train")
    stats["task_share_of_train"] = round(task_train / max(1, len(splits["train"])), 3)

    for sp, recs in splits.items():
        (out_dir / f"{sp}_conversations.json").write_text(json.dumps(recs, ensure_ascii=False))
    stats["outputs"] = {f"{sp}_conversations.json": sha256(out_dir / f"{sp}_conversations.json") for sp in splits}
    (out_dir / "data_stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    print(json.dumps({k: stats[k] for k in ("splits", "tasks_by_split", "dropped_too_long", "leak_drops", "task_dedup",
                                            "eval_prompts_in_train_user_turns", "heldout_user_turns_also_in_train",
                                            "unk_tokens_in_first_20k_per_split", "task_share_of_train")}, indent=1))


if __name__ == "__main__":
    main()
