"""Train or fine-tune Koto.

Training YAML keys beyond ``hibari.training.trainer.TrainingArgs``:

* ``experiment``      — experiment identifier recorded in the checkpoint metadata
* ``init_checkpoint`` — start from these weights (fine-tune / continue). If the
  file does not exist the run stops with an error; it never falls back to
  random weights. ``--checkpoint`` on the command line overrides it.
* ``data_cache_dir``  — processed data directory (``--data-cache-dir`` overrides)
* ``val_examples``    — cap on validation examples
* ``model_version``   — version of the weights this run produces (default:
  ``koto.__version__``); recorded as ``run_metadata.model_version`` and checked
  against ``weights_version`` in the release profile

Relative paths are resolved against the Koto repository root.

    python training/train.py --train-config configs/training/koto_1.1.0.yaml
"""

import argparse
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import koto  # noqa: E402  (makes the hibari engine importable)

import numpy as np
import torch
from torch.utils.data import DataLoader
import yaml

from hibari.data.collator import DataCollatorForCausalLM, LengthGroupedBatchSampler
from hibari.data.formatting import DEFAULT_SYSTEM_PROMPT
from hibari.data.dataset import ConversationDataset
from hibari.data.tokenizer import HibariTokenizer
from hibari.inference.generation import generate_text
from hibari.model.config import ModelConfig
from hibari.model.llm import HibariKotoLM
from hibari.training.checkpoint import load_checkpoint, save_checkpoint
from hibari.training.optimizer import configure_optimizers
from hibari.training.scheduler import get_cosine_schedule_with_warmup
from hibari.training.trainer import Trainer, TrainingArgs
from koto.paths import CONFIG_DIR, DATA_DIR, TOKENIZER_DIR, KOTO_ROOT, resolve


def _git_commit(path: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def train(
    model_config_path: str = str(CONFIG_DIR / "model" / "koto.yaml"),
    training_config_path: str = str(CONFIG_DIR / "training" / "koto.yaml"),
    tokenizer_dir: str = str(TOKENIZER_DIR),
    data_cache_dir: str | None = None,
    max_steps_override: int | None = None,
    checkpoint_path: str | None = None,
) -> None:
    print("=" * 60)
    print("Training Hibari Koto (Multi-Dataset Empathy Dialogue Model)")
    print("=" * 60)

    # 1. Load Configurations
    print(f"Loading model config from {model_config_path}...")
    model_config = ModelConfig.from_yaml(resolve(model_config_path))

    print(f"Loading training config from {training_config_path}...")
    with open(resolve(training_config_path), "r", encoding="utf-8") as f:
        t_cfg = yaml.safe_load(f)

    if max_steps_override is not None:
        t_cfg["max_steps"] = max_steps_override

    val_limit = int(t_cfg.pop("val_examples", 3000))
    experiment = t_cfg.pop("experiment", None)
    # version of the weights this run produces (recorded in the checkpoint and
    # checked by hibari.release.validate_profile against weights_version)
    model_version = str(t_cfg.pop("model_version", koto.__version__))
    yaml_init = t_cfg.pop("init_checkpoint", None)
    yaml_data = t_cfg.pop("data_cache_dir", None)
    checkpoint_path = checkpoint_path or yaml_init
    data_cache_dir = str(resolve(data_cache_dir or yaml_data or DATA_DIR / "processed"))
    tokenizer_dir = str(resolve(tokenizer_dir))
    if checkpoint_path:
        checkpoint_path = str(resolve(checkpoint_path))
        if not Path(checkpoint_path).exists():
            raise FileNotFoundError(f"init checkpoint {checkpoint_path} not found; refusing to train from random weights")
    t_cfg["output_dir"] = str(resolve(t_cfg.get("output_dir", "checkpoints/koto_run")))
    training_args = TrainingArgs(**t_cfg)

    # Reproducibility
    random.seed(training_args.seed)
    np.random.seed(training_args.seed)
    torch.manual_seed(training_args.seed)

    # 2. Check if data is prepared; if not, prepare it
    train_cache_path = Path(data_cache_dir) / "train_conversations.json"
    val_cache_path = Path(data_cache_dir) / "val_conversations.json"

    if not train_cache_path.exists() or not (Path(tokenizer_dir) / "tokenizer.json").exists():
        raise FileNotFoundError(
            f"Processed dataset ({train_cache_path}) or tokenizer ({tokenizer_dir}) not found. "
            "Build the data first (scripts/build_mix.py or scripts/prepare_data.py)."
        )

    # 3. Load Tokenizer
    print(f"Loading tokenizer from {tokenizer_dir}...")
    tokenizer = HibariTokenizer.load(tokenizer_dir)
    model_config.vocab_size = tokenizer.vocab_size
    print(f"Vocabulary size: {tokenizer.vocab_size}")

    # 4. Initialize Model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Initializing HibariKotoLM on device: {device}")
    if checkpoint_path:
        print(f"Loading pretrained weights from {checkpoint_path}...")
        loaded = load_checkpoint(checkpoint_path, device=device)
        model = loaded["model"]
    else:
        model = HibariKotoLM(model_config)
    param_counts = model.count_parameters()
    print(f"Total Parameters:     {param_counts['total']:,}")
    print(f"Trainable Parameters: {param_counts['trainable']:,}")

    # 5. Load Cached Conversations
    print(f"Loading cached conversations from {data_cache_dir}...")
    with open(train_cache_path, "r", encoding="utf-8") as f:
        train_convs = json.load(f)
    with open(val_cache_path, "r", encoding="utf-8") as f:
        val_convs = json.load(f)

    print(f"Building PyTorch datasets with SFT loss masking (train: {len(train_convs)}, val: {len(val_convs)})...")
    train_dataset = ConversationDataset(
        conversations=train_convs,
        tokenizer=tokenizer,
        max_seq_len=model_config.max_seq_len,
        mask_user_tokens=True,
    )
    val_dataset = ConversationDataset(
        conversations=val_convs[:val_limit],
        tokenizer=tokenizer,
        max_seq_len=model_config.max_seq_len,
        mask_user_tokens=True,
    )
    print(f"Prepared {len(train_dataset)} train sequences and {len(val_dataset)} val sequences.")

    collator = DataCollatorForCausalLM(pad_id=tokenizer.pad_id, ignore_index=-100)

    train_loader = DataLoader(
        train_dataset,
        batch_sampler=LengthGroupedBatchSampler(
            [ex["length"] for ex in train_dataset.examples],
            batch_size=training_args.batch_size,
            seed=training_args.seed,
        ),
        collate_fn=collator,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=training_args.batch_size,
        shuffle=False,
        collate_fn=collator,
        drop_last=False,
    )

    # 6. Configure Optimizer & Scheduler
    optimizer = configure_optimizers(
        model,
        learning_rate=training_args.learning_rate,
        weight_decay=training_args.weight_decay,
    )
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=training_args.warmup_steps,
        num_training_steps=training_args.max_steps,
        min_lr_ratio=training_args.min_lr_ratio,
    )

    stats_file = Path(data_cache_dir) / "data_stats.json"
    run_metadata = {
        "experiment": experiment,
        "koto_version": koto.__version__,
        "model_version": model_version,
        "model_config": model_config.to_dict(),
        "training_config": training_config_path,
        "training_config_values": {**t_cfg, "val_examples": val_limit},
        "data_cache_dir": data_cache_dir,
        "train_examples": len(train_dataset),
        "val_examples": len(val_dataset),
        "train_supervised_tokens": int(sum((ex["targets"] != -100).sum().item() for ex in train_dataset.examples)),
        "parameters": param_counts["total"],
        "init_checkpoint": checkpoint_path,
        "git_commit": _git_commit(KOTO_ROOT),
        "engine_git_commit": _git_commit(KOTO_ROOT.parents[1]),
        "data_stats_sha256": hashlib.sha256(stats_file.read_bytes()).hexdigest() if stats_file.exists() else None,
        "train_file_sha256": hashlib.sha256(train_cache_path.read_bytes()).hexdigest(),
        "torch": str(torch.__version__),
    }
    # recorded paths are repo-relative: the metadata goes into committed files
    def _rel(p):
        try:
            return str(Path(p).resolve().relative_to(KOTO_ROOT))
        except (ValueError, TypeError):
            return p
    run_metadata["data_cache_dir"] = _rel(run_metadata["data_cache_dir"])
    run_metadata["init_checkpoint"] = _rel(run_metadata["init_checkpoint"]) if run_metadata["init_checkpoint"] else None
    run_metadata["training_config_values"]["output_dir"] = _rel(run_metadata["training_config_values"]["output_dir"])
    print(json.dumps(run_metadata, indent=2))

    # 7. Start Training
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        train_dataloader=train_loader,
        val_dataloader=val_loader,
        args=training_args,
        device=device,
        run_metadata=run_metadata,
        path_root=KOTO_ROOT,
    )

    print("Beginning training...")
    result = trainer.train()
    print("Training finished successfully!")
    print(f"Checkpoints saved to {training_args.output_dir}/")

    # 8. Post-training sanity test
    print("\n" + "=" * 60)
    print("POST-TRAINING GENERATION SANITY CHECK")
    print("=" * 60)
    # the data mix records the system prompt it was built with (1.2.0+ may differ from the engine default)
    try:
        sample_system = json.loads(stats_file.read_text()).get("system_prompt") or DEFAULT_SYSTEM_PROMPT
    except (OSError, ValueError):
        sample_system = DEFAULT_SYSTEM_PROMPT
    test_prompts = [
        "Hi! How are you doing today?",
        "I had a really tough day at work today.",
        "What is your name and what do you like to do?",
    ]
    model.eval()
    for p in test_prompts:
        chat_prompt = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": sample_system},
                {"role": "user", "content": p},
            ],
            add_generation_prompt=True,
        )
        response = generate_text(
            model=model,
            tokenizer=tokenizer,
            prompt=chat_prompt,
            temperature=0.0,
            device=device,
        )
        print(f"\nUser: {p}")
        print(f"Hibari Koto: {response}")

    from hibari.inference.conversation import HibariChatSession

    session = HibariChatSession(model, tokenizer, device=device)
    for task, text in [("rephrase", "she dont like rainy days"), ("formal", "send me the notes fast")]:
        res = session.run_task(task, text, add_to_history=False)
        print(f"\n[{task}] {text}\nHibari Koto: {res.output}")


def main():
    parser = argparse.ArgumentParser(description="Train Hibari Koto")
    parser.add_argument(
        "--model-config",
        type=str,
        default=str(CONFIG_DIR / "model" / "koto.yaml"),
        help="Path to model config YAML",
    )
    parser.add_argument(
        "--train-config",
        type=str,
        default=str(CONFIG_DIR / "training" / "koto.yaml"),
        help="Path to training config YAML",
    )
    parser.add_argument(
        "--tokenizer-dir",
        type=str,
        default=str(TOKENIZER_DIR),
        help="Path to tokenizer directory",
    )
    parser.add_argument(
        "--data-cache-dir",
        type=str,
        default=None,
        help="Processed data directory (default: data_cache_dir from the training YAML, else data/processed)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Optional override for max training steps",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Start from this checkpoint (overrides init_checkpoint in the YAML)",
    )
    args = parser.parse_args()

    train(
        model_config_path=args.model_config,
        training_config_path=args.train_config,
        tokenizer_dir=args.tokenizer_dir,
        data_cache_dir=args.data_cache_dir,
        max_steps_override=args.max_steps,
        checkpoint_path=args.checkpoint,
    )


if __name__ == "__main__":
    main()
