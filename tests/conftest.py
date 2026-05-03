"""Make the repo root importable so tests can ``import services.engine`` etc.

The monorepo deliberately avoids `src/` layouts so each subsystem keeps a
short import path. Adding the repo root here lets pytest run from any cwd.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
