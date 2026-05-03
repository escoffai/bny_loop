"""Phase 0 placeholder FBA wrapper.

This is a deterministic stub so the rest of the stack can be wired up. Phase 2
replaces ``evaluate`` with a real COBRApy + solver implementation, gated by
the validation panel under ``tests/engine/validation_panel/`` and reviewed by
the ``bio-validator`` subagent.

Do not build product features on the numerical output of this stub.
"""

from __future__ import annotations

import time

from packages.schemas import ByproductProfile, FBAResult
from packages.schemas.simulation import Objective


def evaluate(
    microbe_id: str,
    byproduct: ByproductProfile,
    objective: Objective = "max_yield",
) -> FBAResult:
    """Return a deterministic placeholder FBA result.

    The result is a function of the inputs only — same inputs → same outputs —
    so integration tests can assert on it without a real solver in scope.
    """

    started = time.perf_counter()
    total_carbon_proxy = sum(c.concentration_g_per_l for c in byproduct.components)
    objective_value = round(0.05 * total_carbon_proxy + 0.001 * len(microbe_id), 6)
    growth_rate = round(min(1.0, 0.01 * total_carbon_proxy), 6)
    target_yield = round(min(0.95, 0.02 * total_carbon_proxy), 6)

    return FBAResult(
        microbe_id=microbe_id,
        objective=objective,
        objective_value=objective_value,
        growth_rate_per_h=growth_rate,
        target_yield_g_per_g=target_yield,
        solver_status="placeholder-ok",
        solve_time_s=time.perf_counter() - started,
    )
