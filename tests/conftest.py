import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import koto  # noqa: E402,F401  (makes the hibari engine importable)
