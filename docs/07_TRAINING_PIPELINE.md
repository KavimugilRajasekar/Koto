# 07 — Training Pipeline

## Full training (from random weights)

```bash
python scripts/prepare_data.py --config configs/data/koto.yaml   # or build_finetune_mix.py
python training/train.py \
  --model-config configs/model/koto.yaml \
  --train-config configs/training/koto.yaml \
  --data-cache-dir data/processed
```

## Fine-tuning (continue from a checkpoint)

Same script, plus `--checkpoint`. Only the weights are loaded; the optimizer
and LR schedule start fresh from the new config. See `08_FINE_TUNING.md`.

```bash
python training/train.py \
  --train-config configs/training/koto_v5.yaml \
  --data-cache-dir data/processed_v5 \
  --checkpoint checkpoints/koto_v4/best_model.pt
```

For long runs use `nohup … > outputs/logs/<run>.log 2>&1 &` so that
closing the terminal does not stop training. `--max-steps N` overrides the
config.

## Training runs

| Run | Type | Init | Data (`--data-cache-dir`) | Config | Steps | Best val loss / ppl (step) |
|---|---|---|---|---|---|---|
| v1 | full | random | 4-dataset v1 corpus | — | 1,500 (+250) | ppl 92–172 |
| v2 | full | random | `processed` (71,715) | `koto.yaml` | 3,000 of 12,000 (interrupted) | 3.555 / 34.99 (3000) |
| v3 | fine-tune | v2 best | `processed_ft` (33,249) | `koto_ft.yaml` | 2,500 | 3.294 / 26.95 (2000) |
| v4 | full | random | `processed_full` (73,428) | `koto_full.yaml` | 12,000 | **3.038 / 20.86 (11000)** |
| v5 | fine-tune | v4 best | `processed_v5` (57,455, + writing help) | `koto_v5.yaml` | 4,500 | in progress (2026-11-21) |
| v6 | full | random | `processed_full_v6` (107,634, + writing help) | `koto_full_v6.yaml` | 12,000 | in progress (2026-11-21) |

Each run's folder is `checkpoints/koto_v<N>/`. Its exact
configuration, data counts, supervised token count, git commit and full loss
history are in that folder's `training_history.json` and inside every
checkpoint (`run_metadata`).

What the runs showed:

* **More steps help.** v4 (12k steps from scratch) reached validation
  perplexity 20.86, against 34.99 for v2 at 3k steps. v4's validation loss
  was still falling at step 11000 and rose slightly at 12000 (3.038 → 3.059).
* **The curated share matters more than total steps.** v3 (curated ≈ 10 % of
  its mix) handled identity and insults better than v4 (curated ≈ 4 %), even
  though v4 is more fluent. Fine-tuning a well-trained base on a mix with
  about 10 % curated data (the v3 → v5 recipe) aims to keep both.
* **Run one training at a time.** Two concurrent runs on the 12-core CPU
  oversubscribe the threads: v5 slowed from about 1.0 to 3.6 s/step and v6
  from about 1.3 to 2.1 s/step. A run with `max_hours` set will then stop
  early.

## Run time (12-core CPU, no GPU)

About 1.0–1.3 s per step at batch 32, roughly 150 billion floating-point
operations per step (about 6 × 6.16M parameters × 4,000 tokens). 12,000
steps ≈ 4.4 h; 2,500 steps ≈ 45 min. Export, by contrast, only copies the
6.16M learned numbers into a file and takes about a second.

## Output files

| File | Contents |
|---|---|
| `best_model.pt` (24.7 MB) | weights at the lowest validation loss; **use this for export** |
| `final_model.pt` (24.7 MB) | weights at the last step |
| `last_checkpoint.pt` (74 MB) | weights + optimizer + scheduler state, rewritten every `checkpoint_every` steps; for resuming |
| `training_history.json` | args, run metadata, best step, per-step losses and LR |

All of `checkpoints/` is gitignored, so back up `best_model.pt`.

## v2 configuration (`configs/training/koto.yaml`)

| Setting | v1 (original) | v2 |
|---|---|---|
| Initialisation | from scratch, then a 250-step continuation | from scratch (seed 42) |
| Optimizer | AdamW β=(0.9, 0.95), decay on 2-D weights only | same |
| Peak LR / schedule | 5e-4, warmup 150, cosine → 10 % | 1e-3, warmup 500, cosine → 10 % |
| Weight decay | 0.01 | 0.1 |
| Batch | 16, random | 32, length-grouped (less padding) |
| Steps | 1,500 (~0.6 epoch) | 12,000 max, early stopping patience 4 evals, `max_hours: 5` |
| Gradient clip | 1.0 | 1.0 |
| Validation | first 2,000 val conversations, mean of batch means | full 2,933-example split, token-weighted |
| Checkpoint selection | `best_model.pt` by val loss | same, but cannot be silently overwritten |
| Architecture / tokenizer | 6,163,712 params, 4,096 BPE | **unchanged** |

`koto_full.yaml` (v4) and `koto_full_v6.yaml` (v6) are copies of
this config with a different `output_dir`. The fine-tune configs
(`koto_ft.yaml`, `koto_v5.yaml`) use LR 3e-4, warmup 100–150,
2,500–4,500 steps, an eval every 500 steps and no early stopping.

## Defects fixed in the training loop

1. **Best checkpoint overwritten.** A 250-step continuation run wrote its own
   `best_model.pt` over the 1,500-step run's file. The shipped
   `best_model.pt` was therefore a step-250 model (val loss 4.48). The
   trainer now refuses to start if `best_model.pt` already exists in
   `output_dir` (unless `overwrite_output_dir: true`).
2. **Loss recorded as 0.0** in every periodic checkpoint (`running_loss`
   saved right after being reset). Fixed.
3. **Validation loss** was a mean of per-batch means (depends on batch
   composition). Now token-weighted.
4. **Undertraining.** 1,500 × 16 sequences is about 0.6 epoch; validation
   perplexity of every v1 checkpoint was 92–172. v2 and later train for
   several epochs with the larger batch.
5. Truncation of long conversations (see `05_DATA_PIPELINE.md`).

## Loss masking, padding, attention

* Targets are shifted inputs; non-assistant positions are `-100`.
* Sequences are right-padded; padding targets are `-100`. Because attention is
  causal and padding only follows real tokens, real tokens never attend to
  padding, so no padding mask is needed during training. The model also
  accepts the collator's 0/1 `attention_mask` (converted to an additive mask).

## Pre-start checkpoints

Checkpoints from before the current Koto start are kept locally (not
tracked in Git) in `archive/2026-11-21_before_start/checkpoints/`. Their
stored loss of 0.0 comes from defect 2 above and is not a real value.
