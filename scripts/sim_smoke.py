"""Run a tiny end-to-end smoke simulation against the in-process stub.

Used by ``make sim-smoke`` and the SessionStart hook to confirm the engine
contract is intact after every change.
"""

from __future__ import annotations

import json

from packages.schemas import SimulationRequest
from services.catalog import REFERENCE_BYPRODUCTS, REFERENCE_GEMS
from services.engine import evaluate


def main() -> int:
    request = SimulationRequest(byproduct=REFERENCE_BYPRODUCTS[0], objective="max_yield")
    results = [evaluate(g.gem_id, request.byproduct, request.objective) for g in REFERENCE_GEMS]
    results.sort(key=lambda r: r.objective_value, reverse=True)

    print(json.dumps({"ranked": [r.model_dump() for r in results]}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
