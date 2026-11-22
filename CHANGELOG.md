# Koto changelog

Versions follow `MAJOR.MINOR.PATCH`. Each new version is developed on its own
branch (`release/<version>`). Experiment identifiers are recorded in every
checkpoint's `run_metadata.experiment`.

## [1.2.1] — PREPARED 2026-11-22, not trained (experiment EXP-0005)

- Data: `behaviour_version: 2` — hostile family rebuilt (25 insults × 8 × 7 reply parts,
  plus "after an answer" turns), new `social` (farewells / greetings / thanks that are not
  apologies), `user_facts` ("say my name?" never told → "You haven't told me…"), `mood`
  ("bad thats all", own bad day); `behaviour_repeats` 3 → 1; rewriting up-weighted
  (`handwritten_repeats` 3; formal 4, correct_grammar 2, rephrase 2).
- Built in `data/processed_1.2.1` (133,300 train examples; 0 evaluation prompts in training).
- Configs: `configs/data/koto_1.2.1.yaml`, `configs/training/koto_1.2.1.yaml`, draft `configs/release/koto_1.2.1.yaml`.

## [1.2.0] — trained 2026-11-22, NOT released (experiment EXP-0004)

Trained by the owner (14,000 steps, best eval loss 2.739). Evaluation: `docs/32_KOTO_1.2.0_EVALUATION.md`.

- Learned the identity "I'm Koto, a conversational AI built on the Hibari architecture".
- Better: writing 0.25 → 0.50, context 0.40 → 0.47, empathy 0.70 → 0.74 (behaviour suite, release pipeline, 3 seeds).
- Worse: reformulation 0.67 → 0.44; insult replies leak into ordinary turns ("see you later!" → an apology).
- Overall release pass rate 0.648 vs 1.1.1's 0.660 → 1.1.1 remains the current release.
- GGUFs with provenance in `releases/exported/1.2.0/` (llama.cpp greedy parity 11/11 on every variant).

## [1.1.1] — 2026-11-22 (weights unchanged: 1.1.0; engine 0.3.0; experiment EXP-0003)

PATCH: inference, export and evaluation repairs. Report: `docs/31_KOTO_1.1.1_REPAIR_REPORT.md`.

### Fixed
- **Ollama ran the 1.0.0 weights.** `releases/exported/*.gguf` are tensor-identical to
  `koto_start` (labelled koto_v4 / Hibari-Koto-Plus / 2.0). New exports in
  `releases/exported/1.1.1/` carry `hibari.*` provenance (checkpoint / tokenizer SHA-256,
  versions); the Modelfiles point there; the legacy files are kept and documented.
- Decoding defaults now exist only in `configs/inference/koto.yaml`; the Modelfile is generated.
- `training/train.py` records `model_version`; sample generation uses the data's system prompt.

### Added
- `configs/release/koto_1.1.1.yaml` (validated: 32 checks, 0 errors).
- Python path: input normalisation and candidate reranking (8 candidates, 16 for
  emotional / hostile / e-mail messages).
- Behaviour suite (52 held-out cases) and `evaluation/evaluate_behaviour.py`;
  backend parity report (F32 / F16 / Q8_0 exact on PyTorch, llama.cpp, Ollama).
- Experiment records `experiments/EXP-0001…0004.yaml`; docs 28–31.

### Measured (behaviour suite, 3 seeds)
- Pass rate 0.590 (1.1.0 pipeline) → 0.660 (1.1.1); empathy 0.41 → 0.70; seed agreement 0.81 → 0.90; ~10× latency per turn.

## [1.1.0] — trained and evaluated 2026-11-22, not yet released (branch `release/1.1.0`)

Goal: natural conversation, use of earlier turns, and sentence rewriting
(rephrase, grammar correction, formal / casual / polite, shorter, simpler)
that returns only the rewritten text and keeps the meaning.

**Status: trained (`checkpoints/koto_1.1.0/best_model.pt`, step 12,000) and
evaluated against 1.0.0 on identical data. Not exported to GGUF or released.**
Full results and limitations: `docs/19_KOTO_1.1.0_DEVELOPMENT_REPORT.md`.

### Results (same data, same code as 1.0.0)
| | 1.0.0 | 1.1.0 |
|---|---|---|
| 1.1.0 suite pass rate (routed, greedy) | 16.7 % | **53.7 %** |
| … grammar / meaning preservation | 20 % / 66.7 % | **100 % / 100 %** |
| … context / held-out dialogue | 0 % / 9.1 % | 33.3 % / 54.5 % |
| Writing-task test perplexity (CoEdIT / ParaDetox) | 7.67 / 15.48 | **3.49 / 3.19** |
| Open-conversation val perplexity (old split) | **20.86** | 22.39 (worse) |
| Legacy suite heuristic relevance / grammar | 35.3 % / **94.8 %** | **54.9 %** / 89.7 % |

Known regressions: slightly worse open-conversation perplexity on every
general source; still invents facts (e.g. "The capital of Japan is Berlin").

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

### Evaluation
- New held-out `dialogue` category in `koto.evaluation.upgrade_suite`
  (11 cases: recall, clarification, honest limits, chat vs. correction,
  several questions); test that its prompts are not in the dialogue-skill data.
- Reports: `outputs/evaluation/koto_1.1.0.*`, `koto_1.0.0_rerun.*` (1.0.0 on
  the final suite and data), `legacy_1.1.0_vs_1.0.*` (58-case suite and
  old-split perplexity).

### Baseline (1.0.0 on the 1.1.0 suite, before the dialogue category)
See `outputs/evaluation/koto_1.0.0_baseline.md`. Pass rate 9.3 % (unrouted,
greedy) / 18.6 % (routed, greedy); 0 % on rephrasing, formal, casual and
context cases.

## [1.0.0] — 2026-11-21

The `koto_start` checkpoint (`checkpoints/koto_start/best_model.pt`): the
full 12k-step training run recorded as experiment v4
(`koto_full.yaml`, best step 11,000, validation perplexity 20.86), released
as GGUF in `releases/exported/`. Earlier runs (v2, v3, v5, v6) are kept as
records in `archive/2026-11-21_before_start/`.
