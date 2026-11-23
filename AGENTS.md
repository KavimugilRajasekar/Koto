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
- Current release: **1.3.1** `Hibari-Koto1.3.1:29M` (`configs/release/koto_1.3.1.yaml`, weights `checkpoints/koto_1.3.1_large`, 29.4M) — released 2026-11-23 by the owner's decision although it failed EXP-0007's rule (behaviour 0.628 vs 0.660, rewriting 0.333); published on HF `kavimugil-r/Hibari-Koto` and Ollama `kavimugil-r/Hibari-Koto1.3.1:29M` (docs/34).
- Previous release: **1.1.1** (`configs/release/koto_1.1.1.yaml`, weights `checkpoints/koto_1.1.0`).
- **1.2.0** trained but NOT released (rewriting regression; `docs/32`, `experiments/EXP-0004.yaml`).
- **1.2.1** — data built, never trained; superseded by 1.3.0 (`experiments/EXP-0005.yaml`).
- **1.3.0** — the large model (29.4M parameters), trained 2026-11-23 on other data than its config named; evaluated, NOT accepted (`experiments/EXP-0006.yaml`, docs/33).
- **1.3.1** — retrain of the 29.4M model on `data/processed_1.3.0` (fingerprint checked, `resid_dropout 0.1`), trained and RELEASED (`experiments/EXP-0007.yaml`). Training configs must carry `data_fingerprint`. Next: raise the rewriting share (owner's decision).
- Work branch: `release/1.3.1` (1.3.1 release; `release/1.3.0` holds the same commits up to the release); tags `v1.1.0`, `v1.1.1`, `v1.3.1`.
- Suites: `--suite behaviour` (independent, 52 cases) and `--suite conversation` (the 1.3.0 brief's prompts).
- `releases/exported/*.gguf` (top level) are **1.0.0** weights; use `releases/exported/1.3.1/` (current) or `1.1.1/`.
- Decoding defaults: only `configs/inference/koto.yaml`.
- Behaviour spec `docs/28`, data standards `docs/29`, model template `docs/30`, reports `docs/31` (1.1.1), `docs/32` (1.2.0), `docs/33` (1.3.0), `docs/34` (1.3.1 release).

## Quick commands (from this directory)
```bash
source ../../.venv/bin/activate
python -m pytest -q tests
python evaluation/evaluate_behaviour.py --profile configs/release/koto_1.1.1.yaml --name <report> --seeds 0 1 2
HF_HUB_OFFLINE=1 python scripts/build_mix.py --config configs/data/koto_X.Y.Z.yaml     # new out_dir only
```
