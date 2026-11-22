# AGENTS.md — Koto

**Koto** is the first conversational model on the Hibari engine. This repository is normally
checked out as the `models/Koto` submodule of Hibari; the full agent instructions live in
the engine repository: [`../../agents/`](../../agents/README.md)
(<https://github.com/KavimugilRajasekar/Hibari/tree/main/agents> when checked out alone).

## Non-negotiable
- **Never run `training/train.py`** or any other training. Build data and write configs only;
  give the owner the command.
- **Never overwrite or delete** `checkpoints/`, `data/processed*`, `archive/`, `releases/exported/**`,
  `outputs/evaluation/*` (create new versioned files instead; `build_mix.py` without `--overwrite`).
- **Never `git push`** or publish. Commit only when asked.
- Never put evaluation-suite prompts into training data or tune on them.

## Koto-specific facts
- Current release: **1.1.1** (`configs/release/koto_1.1.1.yaml`, weights `checkpoints/koto_1.1.0`).
- **1.2.0** trained but NOT released (rewriting regression; `docs/32`, `experiments/EXP-0004.yaml`).
- Next: **1.2.1** — data built in `data/processed_1.2.1`, training NOT STARTED (`experiments/EXP-0005.yaml`).
- Work branch: `release/1.2.0`; tags `v1.1.0`, `v1.1.1`.
- `releases/exported/*.gguf` (top level) are **1.0.0** weights; use `releases/exported/1.1.1/`.
- Decoding defaults: only `configs/inference/koto.yaml`.
- Behaviour spec `docs/28`, data standards `docs/29`, model template `docs/30`, reports `docs/31` (1.1.1), `docs/32` (1.2.0).

## Quick commands (from this directory)
```bash
source ../../.venv/bin/activate
python -m pytest -q tests
python evaluation/evaluate_behaviour.py --profile configs/release/koto_1.1.1.yaml --name <report> --seeds 0 1 2
HF_HUB_OFFLINE=1 python scripts/build_mix.py --config configs/data/koto_X.Y.Z.yaml     # new out_dir only
```
