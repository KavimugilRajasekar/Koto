# Koto changelog

Versions follow `MAJOR.MINOR.PATCH`. Each new version is developed on its own
branch (`release/<version>`). Experiment identifiers are recorded in every
checkpoint's `run_metadata.experiment`.

## [1.3.1] — RELEASED 2026-11-23 as `Hibari-Koto1.3.1:29M` (experiment EXP-0007; engine 0.4.1)

**Released by the owner's decision although EXP-0007's acceptance rule was not met** — see
`docs/34_KOTO_1.3.1_RELEASE_REPORT.md`.

- **Training (owner, CUDA, 1.72 h):** 12,000 steps on `data/processed_1.3.0` with the data fingerprint
  checked; best step 11,500, eval loss 2.781 (ppl 16.1); `best_model.pt` sha256 `468ac0e1…`.
- **Evaluation (release pipeline, seeds 0 1 2):** behaviour suite 0.628 (1.1.1: 0.660, 1.3.0: 0.558);
  conversation suite 0.733 (1.1.1: 0.645, 1.3.0: 0.555). Better: context, robustness, safety.
  Worse: rewriting 0.667 → 0.333, writing 0.25 → 0.167, empathy 0.70 → 0.59.
- **Export:** `releases/exported/1.3.1/Hibari-Koto1.3.1-29M-{F32,F16,Q8_0,Q4_K_M}.gguf` with provenance;
  validator 32/0/0; llama.cpp parity F32/F16/Q8_0 11/11, Q4_K_M 9/11.
- **Published:** Hugging Face `kavimugil-r/Hibari-Koto` (GGUFs, PyTorch checkpoint, tokenizer, configs,
  model card `releases/hub/huggingface_README.md`); Ollama `kavimugil-r/Hibari-Koto1.3.1:29M` (Q8_0;
  readme `releases/hub/ollama_README.md`). Profile key `ollama_name` names the published model.

Fixes for the problems found in 1.3.0 (prepared before training):
- **Wrong training data (root cause of EXP-0006's provenance problem):** `training/train.py` accepted any
  data directory. It now refuses a `--data-cache-dir` that differs from the YAML's `data_cache_dir`,
  checks `data_fingerprint` (conversation counts + train sha256) before loading anything else, and
  records conversation counts next to sequence counts. `configs/training/koto_1.3.0_large.yaml` and the
  new `koto_1.3.1_large.yaml` pin the 1.3.0 mix (93,509 / 3,748, sha256 `2226d67d…`).
- **Over-fitting:** `configs/model/koto_1.3.1_large.yaml` = 1.3.0 architecture + `resid_dropout: 0.1`;
  evaluation every 500 steps, early stopping after 6 evals without improvement.
- **Stale metadata:** `koto.__version__` 1.1.1 → 1.3.1 (recorded as `run_metadata.koto_version`).
- **Behaviour suite:** `no_human_claim` now catches "I am a (real) human / person" (it missed 1.3.0's
  I2 reply). Re-scoring all stored reports: that is the only reply affected; no pass rate changes.
- **GGUF parity:** 1.3.0 F32/F16 11/11 after the engine's `compare_backends` fix (`backend_parity_1.3.0_r2.json`).
- Tests: `tests/test_runners.py` (behaviour-evaluation runner end to end with a tiny model, summary and
  markdown; `train.py` fine-tune / missing-data / unknown-fingerprint-key branches). Koto line coverage 61.4% → 64.5%;
  the rest is mostly the HuggingFace download / data-building scripts, which need the network.
- Reproducibility on engine 0.4.1: the 1.1.1 and 1.2.0 behaviour suites (seeds 0 1 2) give the same
  pass rates and 63/63 identical replies per seed as the stored r4 reports (`*_behaviour_engine041.md`).
- Draft release profile `configs/release/koto_1.3.1.yaml`; GGUF metadata of 1.1.0 and 1.3.0 exports tracked.

## [1.3.0] — TRAINED 2026-11-23, evaluated: NOT ACCEPTED, not released (experiment EXP-0006; engine 0.4.0)

**Training (owner):** `checkpoints/koto_1.3.0_large/best_model.pt` (sha256 `e7057576…`), 12,000 steps
(stop: max_steps), ~1.7 h on CUDA; best eval loss 2.875 / perplexity 17.72 at step 12,000 (on the run's
own val set). Eval loss flat after step 9k while train loss fell to 1.59: possible over-fitting.
**Open issue:** the checkpoint records `data\processed` with 99,640 / 3,233 examples, not the prepared
`data/processed_1.3.0` (93,509 / 3,748); the owner must confirm the data. **Evaluated, not accepted:** behaviour suite mean 0.558
(1.1.1: 0.660), reformulation 0.333 (bar 0.67), conversation suite 0.555 (1.1.1: 0.644);
safety 1.0 and writing 0.5 improved. Reports `outputs/evaluation/koto_1.3.0_{behaviour,conversation}.md`.


**Larger model** (owner's decision): `configs/model/koto_1.3.0_large.yaml`, d_model 512, 8 layers,
d_ff 1536, **29,368,832 parameters** (1.x: 6,163,712). Same tokenizer, context and chat format.
Training config `configs/training/koto_1.3.0_large.yaml` (LR 6e-4, 12,000 steps, ~11–13 h on CPU,
names its own model config). The 6.16M configs remain as baselines (`koto_1.3.0.yaml` → `checkpoints/koto_1.3.0_6m`).

Conversation-first mix (`configs/data/koto_1.3.0.yaml`, built in `data/processed_1.3.0`):
93,509 train / 3,748 val / 911 test; natural multi-turn conversation 42.9% (1.2.1: ~30%),
writing tasks 30.2% (~40%), single-turn generic-assistant data 7.6% (16.5%); 0 evaluation
prompts in training. Measured in `outputs/data/mix_1.3.0_train.md` (vs `mix_1.2.1_train.md`).

- `behaviour_version: 3`: disagreement, repair ("no, I meant…"), topic change, follow-ups,
  reasons ("why?"), rewrite requests without text, interest recall, lost objects.
- Builder: `general_source_caps` (smoltalk 6,000, oasst1 1,500), `general_dedup` (with
  `general_dedup_exclude` for intentionally repeated sources), `general_quality_filter`,
  `general_validate` — all off by default, so older configs rebuild unchanged.
- `koto/evaluation/conversation_suite.py` — the 1.3.0 brief's regression prompts (15 cases);
  `evaluate_behaviour.py --suite conversation`.
- `scripts/dataset_report.py` — per-source statistics, quality, emotion coverage, contamination.
- `training/train.py --resume`; a training YAML may set `model_config` (a different `--model-config`
  is refused); 6.16M baselines `koto_1.3.0.yaml` / `koto_1.3.0_ft.yaml`; draft release profile.
- Report: `docs/33_KOTO_1.3.0_DEVELOPMENT_REPORT.md`.

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
