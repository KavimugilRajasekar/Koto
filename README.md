# Koto

Koto is the first conversational model built on the
[Hibari](https://github.com/KavimugilRajasekar/Hibari) engine.

This repository holds Koto's model-specific resources: configurations,
dataset processing and curated data, tokenizer assets, training and
evaluation scripts, experiment records and model documentation.
The engine code (the `hibari` Python package) lives in the Hibari repository.

Author: Kavimugil Rajasekar — [GitHub](https://github.com/KavimugilRajasekar) · [Hugging Face](https://huggingface.co/kavimugil-r) · [Ollama](https://ollama.com/kavimugil-r)

Processed training data (`data/processed_1.3.0`, not in git) is in the private Hugging Face dataset
[`kavimugil-r/koto-data`](https://huggingface.co/datasets/kavimugil-r/koto-data) (owner access only):
`hf download kavimugil-r/koto-data --repo-type dataset --include "processed_1.3.0/*" --local-dir data`

| Path | Contents |
|---|---|
| `MODEL_CARD.md` | Model card |
| `configs/` | Model, training, data and inference YAML configs |
| `tokenizer/` | BPE tokenizer files |
| `data/` | Dataset folders (contents are not committed) |
| `scripts/` | Data preparation, curated data and rewrite data |
| `training/` | Training scripts |
| `evaluation/` | Evaluation script and held-out suite |
| `tests/` | Tests for the Koto data and evaluation suite |
| `notebooks/` | Exploratory notebooks |
| `checkpoints/` | Local checkpoints (weights are not committed) |
| `releases/` | Ollama Modelfile and local GGUF exports (GGUFs are not committed) |
| `outputs/` | Local logs, metrics and samples |
| `archive/` | Local records of experiments before the current start point |
| `docs/` | Model-specific documentation |
