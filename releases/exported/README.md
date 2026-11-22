# Exported GGUF files

| Location | Weights | Provenance | Status |
|---|---|---|---|
| `1.1.1/` | 1.1.0 (`checkpoints/koto_1.1.0/best_model.pt`) | `hibari.*` metadata, hashes in `configs/release/koto_1.1.1.yaml` | **current release** |
| `1.1.0/Hibari-Koto-F32.gguf` | 1.1.0 | none (exported before provenance existed) | superseded by `1.1.1/` (same weights) |
| `Hibari-Koto-{F32,F16,Q8_0,Q4_K_M}.gguf` (this directory) | **1.0.0** (`koto_start`, step 11000) | none; labelled "koto_v4", `general.name` Hibari-Koto-Plus, `general.version` 2.0 | **legacy** — kept, not deleted |

The legacy files were the ones the old `Modelfile` loaded, so Ollama users were running 1.0.0
while the documentation described 1.1.0. This was established by comparing tensors with both
checkpoints (identical to `koto_start`, max |diff| 0; different from `koto_1.1.0`).

Every new export goes into its own `X.Y.Z/` directory via

    python ../../../../scripts/engine/export.py --profile configs/release/koto_X.Y.Z.yaml --llama-quantize <bin> --record

and is checked with `scripts/engine/validate_release.py`. The `Modelfile` in each version directory
is generated from the profile; do not edit it by hand.

    cd releases/exported/1.1.1 && ollama create hibari-koto:1.1.1 -f Modelfile && ollama run hibari-koto:1.1.1
