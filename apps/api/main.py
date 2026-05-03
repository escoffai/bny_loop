"""FastAPI gateway — Phase 0 skeleton.

Exposes the minimum endpoints needed for the dashboard and CLI to wire
against a stable contract during scaffolding. Real auth, persistence, and
job orchestration arrive in Phase 3.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, HTTPException

from packages.schemas import (
    ByproductProfile,
    GEMRecord,
    MicrobeTrait,
    SimulationRequest,
    SimulationResult,
)
from services.catalog import REFERENCE_BYPRODUCTS, REFERENCE_GEMS, REFERENCE_MICROBES
from services.engine import evaluate

app = FastAPI(title="BNY LOOP API", version="0.0.1")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/gems", response_model=list[GEMRecord])
def list_gems() -> list[GEMRecord]:
    return REFERENCE_GEMS


@app.get("/v1/microbes", response_model=list[MicrobeTrait])
def list_microbes() -> list[MicrobeTrait]:
    return REFERENCE_MICROBES


@app.get("/v1/byproducts", response_model=list[ByproductProfile])
def list_byproducts() -> list[ByproductProfile]:
    return REFERENCE_BYPRODUCTS


@app.get("/v1/byproducts/{profile_id}", response_model=ByproductProfile)
def get_byproduct(profile_id: str) -> ByproductProfile:
    for profile in REFERENCE_BYPRODUCTS:
        if profile.profile_id == profile_id:
            return profile
    raise HTTPException(status_code=404, detail=f"byproduct {profile_id} not found")


@app.post("/v1/simulations", response_model=SimulationResult)
def run_simulation(request: SimulationRequest) -> SimulationResult:
    """Phase 0: synchronous, in-process scan against the reference catalog.

    Phase 3 swaps this for Celery-backed async jobs with status polling.
    """

    started = time.perf_counter()
    candidate_ids = request.candidate_microbe_ids or [g.gem_id for g in REFERENCE_GEMS]
    if not candidate_ids:
        raise HTTPException(status_code=400, detail="no candidate microbes available")

    results = [evaluate(mid, request.byproduct, request.objective) for mid in candidate_ids]
    results.sort(key=lambda r: r.objective_value, reverse=True)

    return SimulationResult(
        request=request,
        ranked=results,
        total_solve_time_s=time.perf_counter() - started,
        notes=["Phase 0 placeholder engine — values are not biologically meaningful."],
    )
