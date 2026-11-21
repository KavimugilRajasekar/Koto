# Koto changelog

Versions follow `MAJOR.MINOR.PATCH`. Each new version is developed on its own
branch (`release/<version>`). Experiment identifiers are recorded in every
checkpoint's `run_metadata.experiment`.

## [1.1.0] — in development (branch `release/1.1.0`)

Goal: natural conversation, use of earlier turns, and sentence rewriting
(rephrase, grammar correction, formal / casual / polite, shorter, simpler)
that returns only the rewritten text and keeps the meaning.

**Status: implemented and tested; the 1.1.0 model has NOT been trained yet.**
No capability below is claimed for a trained 1.1.0 checkpoint until the full
run (`configs/training/koto_1.1.0.yaml`, experiment `koto-1.1.0`) has been
trained and evaluated.

### Added
- `koto` Python package (`koto/`): `koto.data.curated`, `koto.data.rewrite`
  (moved from `scripts/`), `koto.evaluation.suite` (moved from `evaluation/`),
  and new `koto.data.tasks`, `koto.data.conversation`,
  `koto.evaluation.upgrade_suite`, `koto.paths`. Importing `koto` makes the
  Hibari engine importable from the submodule checkout.
- **Task data** (`koto.data.tasks`) in the engine's canonical task format
  (`hibari.inference.tasks`), half canonical and half natural requests:
  templated grammar errors with verified corrections, passive → active and
  wordy → natural rephrasing, meaning-preservation templates (times, dates,
  numbers, names, technical terms), hand-written formal / casual / shorter
  pairs and templates, empty / fragment inputs.
- **Conversation data** (`koto.data.conversation`): greetings and small talk
  without self-introduction, 37 topics with a short and a detailed answer,
  fun facts, feelings, career advice, and 3-turn context chains (learning →
  what next → project; goal → tool → which language; event tomorrow → not
  prepared → what now; fact shared → later recall).
- **`scripts/build_mix.py`** + `configs/data/koto_1.1.0.yaml`: builds
  `data/processed_1.1.0/{train,val,test}_conversations.json` with no
  downloads (local HF cache only); dedup and contradiction removal, stable
  hash splits, leak removal against both evaluation suites, faithfulness
  filter for smol-rewrite, provenance / licence / coverage stats in
  `data_stats.json`. Result (before the dialogue-skill data): 105,496 train / 3,944 val / 1,009 test, 27.4 %
  rewriting tasks, 0 unknown tokens, 0 evaluation prompts (3+ words) in
  training.
- **Dialogue-skill data** (`koto.data.dialogue_skills`, 2026-11-21), added
  because the 1.0.0 evaluation scored 0 % on context retention and the model
  invented answers to vague or unanswerable questions. Five slot-filled
  families: context recall (name, pet, city, job, favourites, siblings, with
  0–2 unrelated turns in between), clarification questions for vague
  requests, honest "I don't know" for live data / private facts / obscure
  figures / unknown terms, chat-with-mistakes answered for its meaning (not
  corrected) vs. explicit "is this correct?" answered with a correction and
  a short explanation, and several / repeated questions in one turn. Enabled
  in `configs/data/koto_1.1.0.yaml` (`dialogue_skills_repeats: 2`,
  `recall_conversations: 1500`); `build_mix.py` filters evaluation prompts
  and hash-splits it like the other hand-written data. Rebuilt mix:
  **108,850 train / 4,018 val / 1,082 test** (3,354 / 74 / 73 dialogue-skill
  examples, about 3 % of training).
- **`configs/training/koto_1.1.0.yaml`** — full run from scratch (same
  architecture and recipe as 1.0.0, new data) and
  `configs/training/koto_1.1.0_ft.yaml` — optional fine-tune of 1.0.0.
- **`evaluation/evaluate_upgrade.py`** + `koto.evaluation.upgrade_suite`:
  43 cases (brief categories A–H plus the brief's behaviour examples),
  unrouted vs routed, greedy vs sampled, 3-seed stability, held-out loss on
  val / test, `seen_in_training` flags, Markdown + JSON reports in
  `outputs/evaluation/`.
- Tests: `tests/test_upgrade.py` (58 Koto tests in total).

### Changed
- Rewrite replies no longer start with a fixed lead ("Here's the corrected
  sentence:"); the reply is the rewritten text only. Emails keep their lead.
- External rewrite targets are cleaned (spacing), and smol-rewrite pairs
  that add content (most "professional" / "friendly" emails) are excluded.
- `training/train.py` reads `experiment`, `init_checkpoint` and
  `data_cache_dir` from the training YAML (previously `koto_continue.yaml`
  crashed with a TypeError), refuses to start when a requested init
  checkpoint is missing (previously fell back to random weights silently),
  resolves paths from the Koto root and records experiment, data hashes and
  both repositories' commits.
- All active configs and scripts use Koto-relative paths instead of the
  pre-split `hibari/...` paths. The 1M-era `koto_1m` configs stay archived.

### Baseline (1.0.0 on the 1.1.0 suite)
See `outputs/evaluation/koto_1.0.0_baseline.md`. Pass rate 9.3 % (unrouted,
greedy) / 18.6 % (routed, greedy); 0 % on rephrasing, formal, casual and
context cases.

## [1.0.0] — 2026-11-21

The `koto_start` checkpoint (`checkpoints/koto_start/best_model.pt`): the
full 12k-step training run recorded as experiment v4
(`koto_full.yaml`, best step 11,000, validation perplexity 20.86), released
as GGUF in `releases/exported/`. Earlier runs (v2, v3, v5, v6) are kept as
records in `archive/2026-11-21_before_start/`.
