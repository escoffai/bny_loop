"""BNY LOOP simulation engine.

Phase 0 stub. Real FBA / MILP / dFBA implementations land in Phase 2 — see
``BUILDING_WITH_CLAUDE.md``. This module currently exposes a deterministic
placeholder that satisfies the public contract so downstream services
(catalog, API, web) can integrate against a stable surface.
"""

from .fba import evaluate

__all__ = ["evaluate"]
