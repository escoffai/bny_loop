from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, NonNegativeFloat

from .byproduct import ByproductProfile

Objective = Literal["max_yield", "max_productivity", "min_cost"]


class SimulationRequest(BaseModel):
    """Public API contract for launching a simulation."""

    byproduct: ByproductProfile
    objective: Objective = "max_yield"
    target_product: str | None = None
    candidate_microbe_ids: list[str] | None = Field(
        default=None,
        description="If set, restrict the scan to these GEMs. Otherwise scan the full library.",
    )


class FBAResult(BaseModel):
    """Outcome of evaluating a single (microbe, byproduct) pair."""

    microbe_id: str
    objective: Objective
    objective_value: float
    growth_rate_per_h: float | None = None
    target_yield_g_per_g: float | None = None
    solver_status: str
    solve_time_s: NonNegativeFloat


class SimulationResult(BaseModel):
    """Aggregated, ranked output of a multi-microbe scan."""

    request: SimulationRequest
    ranked: list[FBAResult]
    total_solve_time_s: NonNegativeFloat
    notes: list[str] = Field(default_factory=list)
