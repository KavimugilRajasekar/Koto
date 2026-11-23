# Exported GGUF files

| Location | Weights | Provenance | Status |
|---|---|---|---|
| `1.3.1/` | 1.3.1 (`checkpoints/koto_1.3.1_large/best_model.pt`) | `hibari.*` metadata, hashes in `configs/release/koto_1.3.1.yaml` | **current release** `Hibari-Koto1.3.1:29M` (files `Hibari-Koto1.3.1-29M-*.gguf`) |
| `1.3.0/` | 1.3.0 (`checkpoints/koto_1.3.0_large/best_model.pt`) | `hibari.*` metadata, hashes in `configs/release/koto_1.3.0.yaml` | trained on other data, **not released** (docs/33) |
| `1.1.1/` | 1.1.0 (`checkpoints/koto_1.1.0/best_model.pt`) | `hibari.*` metadata, hashes in `configs/release/koto_1.1.1.yaml` | previous release |
| `1.2.0/` | 1.2.0 (`checkpoints/koto_1.2.0/best_model.pt`) | `hibari.*` metadata, hashes in `configs/release/koto_1.2.0.yaml` | trained and evaluated, **not released** (rewriting regression, `docs/32_KOTO_1.2.0_EVALUATION.md`) |
| `1.1.0/Hibari-Koto-F32.gguf` | 1.1.0 | none (exported before provenance existed) | superseded by `1.1.1/` (same weights) |
| `Hibari-Koto-{F32,F16,Q8_0,Q4_K_M}.gguf` (this directory) | **1.0.0** (`koto_start`, step 11000) | none; labelled "koto_v4", `general.name` Hibari-Koto-Plus, `general.version` 2.0 | **legacy** — kept, not deleted |

The legacy files were the ones the old `Modelfile` loaded, so Ollama users were running 1.0.0
while the documentation described 1.1.0. This was established by comparing tensors with both
checkpoints (identical to `koto_start`, max |diff| 0; different from `koto_1.1.0`).

Every new export goes into its own `X.Y.Z/` directory via

    python ../../../../scripts/engine/export.py --profile configs/release/koto_X.Y.Z.yaml --llama-quantize <bin> --record

and is checked with `scripts/engine/validate_release.py`. The `Modelfile` in each version directory
is generated from the profile; do not edit it by hand.

    cd releases/exported/1.3.1 && ollama create kavimugil-r/Hibari-Koto1.3.1:29M -f Modelfile && ollama run kavimugil-r/Hibari-Koto1.3.1:29M

or, without building anything: `ollama run kavimugil-r/Hibari-Koto1.3.1:29M` (published, Q8_0).
