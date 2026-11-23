# 30 — Koto Model Development Template

Koto's instance of the Official Hibari Development Template
(`../../../Docs/template/21_DEVELOPMENT_TEMPLATE.md`, lifecycle 22, standards 23,
templates 24, checklist 25).

## Files for a version X.Y.Z

| Purpose | File |
|---|---|
| Architecture | `configs/model/koto.yaml` (6.2M) or `configs/model/koto_1.2.0_large.yaml` |
| Data | `configs/data/koto_X.Y.Z.yaml` → `data/processed_X.Y.Z/` |
| Training (owner-run) | `configs/training/koto_X.Y.Z.yaml` → `checkpoints/koto_X.Y.Z/` |
| Inference (only source of defaults) | `configs/inference/koto.yaml` |
| Release profile | `configs/release/koto_X.Y.Z.yaml` |
| Experiment record | `experiments/EXP-NNNN.yaml` |
| Reports | `outputs/evaluation/koto_X.Y.Z_behaviour.*`, `backend_parity_X.Y.Z.json` |
| GGUFs + Modelfile | `releases/exported/X.Y.Z/` |
| Docs | `CHANGELOG.md`, `MODEL_CARD.md`, `docs/18_KNOWN_LIMITATIONS.md`, a report in `docs/` |

## Versions so far

| Version | Weights | Training | Experiment | Profile |
|---|---|---|---|---|
| 1.0.0 | `koto_start` | COMPLETED | EXP-0001 | — (legacy GGUFs, no provenance) |
| 1.1.0 | `koto_1.1.0` | COMPLETED | EXP-0002 | — |
| 1.1.1 | `koto_1.1.0` (unchanged) | NOT_REQUIRED | EXP-0003 | `koto_1.1.1.yaml` (validated) |
| 1.2.0 | `koto_1.2.0` (to be trained) | NOT_STARTED | EXP-0004 | `koto_1.2.0.yaml` (draft) |

## Workflow for 1.2.0 (commands from the Koto root)

```bash
source ../../.venv/bin/activate
# data (done once; already built)
HF_HUB_OFFLINE=1 python scripts/build_mix.py --config configs/data/koto_1.2.0.yaml
# training gate: set experiments/EXP-0004.yaml training.status MANUALLY_AUTHORIZED + authorized_by, then
python training/train.py --model-config configs/model/koto.yaml --train-config configs/training/koto_1.2.0.yaml
# after training: record sha256 + COMPLETED in configs/release/koto_1.2.0.yaml and EXP-0004, then
python ../../scripts/engine/validate_release.py --profile configs/release/koto_1.2.0.yaml --no-gguf
python evaluation/evaluate_behaviour.py --profile configs/release/koto_1.2.0.yaml --name koto_1.2.0_behaviour --seeds 0 1 2
python evaluation/evaluate_upgrade.py --checkpoint checkpoints/koto_1.2.0/best_model.pt --name koto_1.2.0 --data-dir data/processed_1.2.0
LD_LIBRARY_PATH=~/llama.cpp python ../../scripts/engine/export.py --profile configs/release/koto_1.2.0.yaml --llama-quantize ~/llama.cpp/llama-quantize --record
python ../../scripts/engine/validate_release.py --profile configs/release/koto_1.2.0.yaml
python ../../scripts/engine/compare_backends.py --profile configs/release/koto_1.2.0.yaml --llama-bin ~/llama.cpp --report outputs/evaluation/backend_parity_1.2.0.json
```

Accept 1.2.0 only if the behaviour suite improves over `koto_1.1.1_behaviour` on the same
seeds without a regression in `reformulation` and in the upgrade suite's grammar / preservation.
