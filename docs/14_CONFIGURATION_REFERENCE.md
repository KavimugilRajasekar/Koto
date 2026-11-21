# 14 — Configuration Reference

All configs are YAML files in `hibari/configs/`. The `base` files are older templates;
Koto uses the files listed below.

```
hibari/configs/
├── model/      koto.yaml
├── data/       koto.yaml
├── training/   koto.yaml, koto_full.yaml, koto_full_v6.yaml   (full training)
│               koto_ft.yaml, koto_v5.yaml                          (fine-tunes)
│               sft.yaml                                                      (placeholder, unused)
└── inference/  koto.yaml
```

## Model (`configs/model/koto.yaml` → `hibari.model.config.ModelConfig`)

| Field | Koto | Meaning |
|---|---|---|
| `model_name` | `Hibari-Koto` | written into GGUF metadata |
| `vocab_size` | 4096 | overwritten by the tokenizer's size at train time |
| `max_seq_len` | 256 | context length (RoPE tables, generation window) |
| `d_model` | 256 | hidden width |
| `n_layers` | 6 | transformer blocks |
| `n_heads` | 8 | attention heads (head dim = d_model / n_heads = 32) |
| `d_ff` | 768 | SwiGLU hidden width |
| `norm_eps` | 1e-5 | RMSNorm epsilon |
| `dropout` | 0.0 | attention dropout |
| `tie_embeddings` | true | output head shares the embedding matrix |
| `rope_theta` | 10000.0 | RoPE base frequency |

## Training (`configs/training/*.yaml` → `hibari.training.trainer.TrainingArgs`)

| Field | `koto.yaml` (full) | `koto_v5.yaml` (fine-tune) | Meaning |
|---|---|---|---|
| `learning_rate` | 1e-3 | 3e-4 | peak AdamW LR |
| `min_lr_ratio` | 0.1 | 0.1 | cosine floor as a fraction of the peak |
| `weight_decay` | 0.1 | 0.1 | applied to 2-D weights only |
| `warmup_steps` | 500 | 150 | linear warmup |
| `max_steps` | 12000 | 4500 | optimizer steps |
| `batch_size` | 32 | 32 | sequences per step (length-grouped) |
| `gradient_clip` | 1.0 | 1.0 | max grad norm (0 = off) |
| `checkpoint_every` | 1000 | 500 | rewrite `last_checkpoint.pt` |
| `eval_every` | 1000 | 500 | validation + maybe `best_model.pt` |
| `log_every` | 100 | 100 | history / progress-bar interval |
| `val_examples` | 4000 | 4000 | cap on validation examples (read by `train.py`) |
| `output_dir` | `…/koto_v2` | `…/koto_v5` | run folder; must not already hold `best_model.pt` |
| `save_best` | true | true | keep the lowest-val-loss weights |
| `overwrite_output_dir` | false | false | allow replacing an existing `best_model.pt` |
| `early_stopping_patience` | 4 | 0 | evals without improvement before stopping (0 = off) |
| `max_hours` | 5.0 | 2.5 | wall-clock limit (0 = off) |
| `seed` | 42 | 42 | RNG seed |

## Data (`configs/data/koto.yaml`, read by `prepare_data.py`)

| Field | Meaning |
|---|---|
| `sources` | loaders to run: `empathetic_dialogues`, `everyday_conversations`, `smoltalk`, `blended_skill_talk`, `dailydialog`, `prosocial_dialog`, `oasst1`, `coedit` |
| `source_caps` | per-source `{train, val}` example caps after cleaning / windowing |
| `source_repeats` | repetition factor per source (e.g. `curated: 3`) |
| `vocab_size`, `max_seq_len`, `min_frequency` | tokenizer settings (the tokenizer is not retrained for Koto) |
| `tokenizer_dir` | `hibari/models/tokenizer` |
| `data_cache_dir` | output folder (`hibari/data/processed`) |
| `retrain_tokenizer` | must stay `false`; retraining changes token IDs |
| `seed` | shuffle seed |

`build_finetune_mix.py` takes its settings as command-line flags instead
(`05_DATA_PIPELINE.md`).

## Inference (`configs/inference/koto.yaml`)

| Field | Value | Meaning |
|---|---|---|
| `model_checkpoint` | `…/koto_v2/best_model.pt` | default checkpoint |
| `max_new_tokens` | 80 | reply length cap |
| `temperature` | 0.5 | 0 = greedy |
| `top_k` / `top_p` | 25 / 0.85 | sampling filters |
| `repetition_penalty` | 1.15 | penalises repeated tokens |
| `device` | `cpu` | |

The same sampling values are in the Ollama Modelfile.
