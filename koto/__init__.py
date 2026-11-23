"""Koto — the first conversational model built on the Hibari engine.

Importing ``koto`` makes the ``hibari`` engine importable when Koto is
checked out as the ``models/Koto`` submodule of Hibari and the engine is not
installed (it adds ``<Hibari>/src`` to ``sys.path``). If ``hibari`` is already
installed, that installation is used.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

__version__ = "1.3.1"

KOTO_ROOT = Path(__file__).resolve().parents[1]

_engine_src = KOTO_ROOT.parents[1] / "src"
_spec = importlib.util.find_spec("hibari")
if (_spec is None or _spec.origin is None) and (_engine_src / "hibari" / "__init__.py").exists():
    sys.path.insert(0, str(_engine_src))
