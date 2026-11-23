# 34 — Koto 1.3.1 Release Report (`Hibari-Koto1.3.1:29M`)

Date: 2026-11-23 · Experiment: `experiments/EXP-0007.yaml` · Engine: Hibari 0.4.1 ·
Profile: `configs/release/koto_1.3.1.yaml` · Status: **released** (owner's decision, see §5)

## 1. What 1.3.1 is

A retrain of the 29.4M-parameter model of 1.3.0 (d_model 512, 8 layers, 8 heads × 64, SwiGLU 1536,
256-token context, 4,096-token BPE, tied embeddings) on the data 1.3.0 was designed for, with two
changes:

- **Data provenance enforced.** EXP-0006 (1.3.0) trained on a different dataset than its config
  named. `training/train.py` now checks `data_fingerprint` before training; the 1.3.1 run recorded
  `data_fingerprint_checked: true`, 93,509 train / 3,748 val conversations, train sha256 `2226d67d…`.
- **Residual dropout 0.1** (`ModelConfig.resid_dropout`, engine 0.4.1) against 1.3.0's over-fitting.

## 2. Training (run by the owner)

| | |
|---|---|
| Config | `configs/training/koto_1.3.1_large.yaml` (not changed after the run) |
| Code | Koto `e0f1232`, engine `d283626` (recorded in `run_metadata`) |
| Hardware | one CUDA GPU (torch 2.12.1+cu126), 1.72 h |
| Steps | 12,000 of 12,000 (`stop_reason: max_steps`) |
| Best checkpoint | step 11,500 — eval loss **2.781** (perplexity 16.1); `best_model.pt` sha256 `468ac0e1…` |
| Final train loss | 1.455 (log window at step 12,000) |

Eval loss every 1,000 steps: 4.21, 3.59, 3.28, 3.21, 3.09, 3.00, 2.94, 2.87, 2.83, 2.81, 2.79, 2.79
(steps 1k–12k; minimum 2.781 at 11.5k). Unlike 1.3.0 (flat after 9k), eval loss still fell until
11.5k, but the train/eval gap (1.46 vs 2.78) shows the model still fits its training data much
more closely than new data.

## 3. Export and verification

| Check | Result |
|---|---|
| `validate_release.py` (checkpoint, tokenizer, config, inference, 4 GGUFs, provenance, Modelfile) | 32 ok, 0 warnings, 0 errors |
| Backend parity, llama.cpp vs PyTorch, greedy, 11 prompts (`outputs/evaluation/backend_parity_1.3.1.json`) | F32 11/11, F16 11/11, Q8_0 11/11, Q4_K_M 9/11 |
| Pre-flight before training (scratch script, no weights changed) | config, fingerprint, 93,509 sequences, 29,368,832 params, finite gradients, GGUF round trip |
| llama-cli smoke test (Q8_0, the card's command) | "I'm not a person. I'm Koto, a small AI made for friendly conversation." |

Files (`releases/exported/1.3.1/`, named by the owner): `Hibari-Koto1.3.1-29M-{F32,F16,Q8_0,Q4_K_M}.gguf`
(112.2 / 56.2 / 29.9 / 17.5 MiB), generated `Modelfile`, `export_manifest.json`.

## 4. Evaluation

Release pipeline (reranking, normalisation, safety, task router), seeds 0 1 2. 1.1.1 was re-scored on
the same suite version the same day (`koto_1.1.1_behaviour_review_2026-11-23`,
`koto_1.1.1_conversation_engine041`).

| Suite | 1.1.1 | **1.3.1** | 1.3.0 |
|---|---|---|---|
| Behaviour (52 cases), mean of seeds | 0.660 (0.615 / 0.654 / 0.712) | **0.628** (0.615 / 0.654 / 0.615) | 0.558 |
| Conversation (15 cases), mean of seeds | 0.645 (0.600 / 0.667 / 0.667) | **0.733** (0.733 / 0.733 / 0.733) | 0.555 |

Behaviour suite by category (mean of seeds, 1.1.1 → 1.3.1):

| basic | empathy | context | reformulation | writing | robustness | safety | identity |
|---|---|---|---|---|---|---|---|
| 0.83 → 0.83 | 0.70 → 0.59 | 0.40 → 0.53 | **0.67 → 0.33** | 0.25 → 0.17 | 0.77 → 0.90 | 0.89 → 1.00 | 0.33 → 0.33 |

Conversation suite by category (1.1.1 → 1.3.1): natural 1.00 → 0.00, empathy 1.00 → 1.00,
sympathy 1.00 → 1.00, context 0.00 → 0.00, reformulation 0.75 → 1.00, naturalness 0.17 → 0.50.

Typical failures (seed 0): "Rephrase: the movie was very much boring and long" is returned
unchanged; "Make this formal: hey, can u send me the file today" → "I would like to request a file
today." (meaning lost); the professor e-mail asks for "a day of leave" instead of an extension.

Reports: `outputs/evaluation/koto_1.3.1_behaviour.{json,md}`, `koto_1.3.1_conversation.{json,md}`.

## 5. Decision

EXP-0007's acceptance rule — behaviour mean > 0.660 **and** reformulation ≥ 0.67 — is **not met**
(0.628; 0.333). The owner reviewed these numbers and decided to release 1.3.1 for its gains in
conversation (conversation suite 0.733 vs 0.645; context, robustness and safety up), accepting the
rewriting and writing regression, which every published card states.

Published as **`Hibari-Koto1.3.1:29M`**:
- Hugging Face `kavimugil-r/Hibari-Koto` — 4 GGUFs, Modelfile, manifest, PyTorch checkpoint,
  tokenizer, configs, model card (`releases/hub/huggingface_README.md`).
- Ollama `kavimugil-r/Hibari-Koto1.3.1:29M` — Q8_0 (readme text: `releases/hub/ollama_README.md`,
  pasted on ollama.com by the owner).

## 6. Limitations and next steps

- Rewriting halved vs 1.1.1 and the 1.2.x line. The 1.3.0 mix is conversation-first; the next data
  change (owner's decision) is to raise the rewriting share again (1.2.x had ~40%).
- Two changes at once (correct data + resid_dropout): a run with `resid_dropout 0.0` would separate
  their effects.
- The train/eval gap suggests more data, not more steps.
- The suites' failures above were read for this report; no data or decoding was tuned on them.
