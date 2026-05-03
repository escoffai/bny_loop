# CLAUDE.md — BNY LOOP root context

This file is loaded automatically at the start of every Claude Code session in
this repo. Keep it short, accurate, and current. See `README.md` for the
product overview and `BUILDING_WITH_CLAUDE.md` for the full development plan.

## What this project is

BNY LOOP — an *in silico* engine that maps industrial byproducts to candidate
microbes using genome-scale metabolic models, FBA / MILP / dFBA, and
constraint-based simulation. Output: a ranked list of microbe-byproduct
pairings with predicted yields and recommended fermentation conditions.

## Architecture (4 phases)

1. **Knowledge base** (`services/catalog`, `data/`) — GEMs + microbe traits +
   byproduct ontology.
2. **Engine** (`services/engine`) — COBRApy + solver. Highest-stakes code.
3. **API & cloud** (`apps/api`, `infra/`) — FastAPI gateway, Celery workers,
   Kubernetes deployment.
4. **UX** (`apps/web`) — React + TypeScript dashboard.

Shared types live in `packages/schemas` (Pydantic + generated TS types).

## Repo layout

```
apps/{web,api}            services/{engine,ingestion,catalog}
packages/{schemas,ui}     data/{gems,microbes,byproducts}
infra/{docker,k8s,terraform}
notebooks/  scripts/  tests/
```

## Commands

| Task | Command |
| :--- | :--- |
| Install everything | `make bootstrap` |
| Lint | `make lint` |
| Tests | `make test` |
| Bring up dev stack | `make dev-up` |
| Tear down dev stack | `make dev-down` |
| Smoke a simulation | `make sim-smoke` |

## Conventions

- Python: 3.11+, `uv` for env/deps, `ruff` + `black`, `mypy --strict` in
  `services/engine`.
- TypeScript: pnpm workspaces, `eslint` + `prettier`, strict `tsconfig`.
- Tests: `pytest` (Python), `vitest` / Playwright (TS). Validation panel in
  `tests/engine/validation_panel/` is mandatory-green for engine PRs.
- All secrets via env vars. Never commit `.env`.

## Tabu list (do not do)

- Do **not** introduce metabolic claims without a citation. The
  `bio-validator` subagent will reject them.
- Do **not** edit `main` directly. Work on a feature branch.
- Do **not** disable the validation panel to make a PR pass.
- Do **not** widen public API surface without updating
  `packages/schemas/openapi.yaml` and the OpenAPI tests.

## Default model

Opus 4.7 at the root. Subdirectory `CLAUDE.md` files may override (Sonnet for
`apps/web` and `apps/api`, Haiku for bulk parallel jobs).

## Status

Phase 0 — scaffolding only. No simulation logic yet. See the roadmap in
`README.md` and the per-phase plan in `BUILDING_WITH_CLAUDE.md`.
