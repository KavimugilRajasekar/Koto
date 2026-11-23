"""Default locations inside the Koto repository.

Relative paths in Koto configs and command-line options are resolved against
the Koto root, so scripts work from any working directory.
"""

from __future__ import annotations

from pathlib import Path

from koto import KOTO_ROOT

TOKENIZER_DIR = KOTO_ROOT / "tokenizer"
CONFIG_DIR = KOTO_ROOT / "configs"
DATA_DIR = KOTO_ROOT / "data"
CHECKPOINT_DIR = KOTO_ROOT / "checkpoints"
OUTPUT_DIR = KOTO_ROOT / "outputs"
EVAL_OUTPUT_DIR = OUTPUT_DIR / "evaluation"


def resolve(path: str | Path) -> Path:
    """Absolute paths are returned unchanged; relative ones are taken from the Koto root."""
    p = Path(path).expanduser()
    return p if p.is_absolute() else KOTO_ROOT / p
