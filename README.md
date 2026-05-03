# BNY LOOP

> **Byproduct-to-Yield Loop** — An *in silico* modeling engine that compresses months of trial-and-error wet-lab R&D into a 10-minute computational simulation for synthetic biology and biomanufacturing.

[![Status](https://img.shields.io/badge/status-pre--alpha-orange)]()
[![License](https://img.shields.io/badge/license-proprietary-blue)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![Node](https://img.shields.io/badge/node-20%2B-green)]()

---

## Table of Contents

1. [Vision](#vision)
2. [What BNY LOOP Does](#what-bny-loop-does)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Repository Layout](#repository-layout)
6. [Getting Started](#getting-started)
7. [Configuration](#configuration)
8. [Running a Simulation](#running-a-simulation)
9. [API Reference](#api-reference)
10. [Data Sources](#data-sources)
11. [Performance Targets](#performance-targets)
12. [Roadmap](#roadmap)
13. [Contributing](#contributing)
14. [Team & Disciplines](#team--disciplines)
15. [License](#license)

---

## Vision

The food, pharma, and chemicals industries generate vast volumes of low-value byproducts (cheese whey, brewer's spent grain, fruit pomace, glycerol from biodiesel, etc.). Converting these streams into high-value ingredients via microbial fermentation traditionally requires **6–18 months** of wet-lab screening, strain selection, and process optimization.

**BNY LOOP closes that loop in minutes.** Given a byproduct's chemical profile, the platform searches a curated library of genome-scale metabolic models, runs constraint-based simulations across hundreds of candidate microbes in parallel, and returns a ranked list of microbe-byproduct pairings with predicted yields, fermentation conditions, and economic projections.

## What BNY LOOP Does

| Input | BNY LOOP | Output |
| :--- | :--- | :--- |
| Byproduct chemical profile (CSV / manual / lab-instrument upload) | 300+ Genome-Scale Metabolic Models, FBA + MILP optimization, dynamic fermentation simulation | Ranked microbe matches, predicted yield (g/L), recommended conditions (pH, temp, aeration, feed rate), batch consistency forecast, R&D time saved |

Typical end users:

- **Biomanufacturing R&D leads** screening feedstocks
- **Food-tech and ingredient companies** valorizing waste streams
- **Sustainability and circular-economy teams** quantifying upcycling opportunities
- **Academic labs** prototyping fermentation pathways

---

## System Architecture

BNY LOOP is organized into four cooperating phases. Each phase is a deployable subsystem with clear contracts to the next.

```
+-----------------------------------------------------------------+
|                    PHASE 4 — User Experience                    |
|     React + TypeScript dashboard | Input -> Run -> Report       |
+-------------------------------+---------------------------------+
                                |  REST / GraphQL
+-------------------------------v---------------------------------+
|                 PHASE 3 — Software & Cloud Layer                |
|   FastAPI gateway | Job queue | K8s workers | Object storage    |
+-------------------------------+---------------------------------+
                                |  gRPC / message bus
+-------------------------------v---------------------------------+
|              PHASE 2 — Computational Engine                     |
|     COBRApy + Gurobi | FBA | MILP | Dynamic FBA (dFBA)          |
+-------------------------------+---------------------------------+
                                |  SQL / Parquet
+-------------------------------v---------------------------------+
|              PHASE 1 — Biological Knowledge Base                |
|  GEM library | Microbe traits DB | Byproduct ontology + index   |
+-----------------------------------------------------------------+
```

### Phase 1 — Biological Knowledge Base

The factual substrate the engine reasons over.

- **Genome-Scale Metabolic Models (GEMs):** Curated and harmonized from BiGG Models, KEGG, MetaCyc, and in-house reconstructions. Stored as SBML and indexed in PostgreSQL with metadata (organism, reaction count, growth conditions, source citation).
- **Microbial Trait Library:** Relational catalog mapping each organism to environmental tolerances (pH range, temperature, oxygen requirement, salinity), genetic-engineering tractability, regulatory status (GRAS, food-grade, BSL level), and known production capabilities.
- **Byproduct Ontology & Profiling Index:** Normalizes inputs like "cheese whey" or "brewer's spent grain" into precise molar compositions (lactose, proteins, lipids, organic acids, micronutrients) using an extensible JSON schema, allowing the engine to treat them as structured exchange-flux constraints.

### Phase 2 — Computational Engine ("Secret Sauce")

Mechanistic, not just statistical.

- **Flux Balance Analysis (FBA):** Computes theoretical maximum product yield for a given microbe-byproduct pair under steady-state mass-balance constraints.
- **Mixed-Integer Linear Programming (MILP):** Selects the optimal microbe(s) and pathway choices across the full library, optimizing user-specified objectives (yield, productivity, cost, carbon efficiency).
- **Dynamic FBA (dFBA):** Simulates batch and fed-batch fermentation trajectories over time to produce realistic operating envelopes — temperature, pH setpoints, feed-rate profiles, expected duration.
- **Sensitivity & Robustness Analysis:** Quantifies how predicted yields shift under feedstock variability, supporting the **Batch Consistency** guarantee.

### Phase 3 — Software & Cloud Architecture

Engineered for parallelism and reproducibility.

- **Cloud Infrastructure:** AWS (EKS, S3, RDS) or GCP (GKE, GCS, Cloud SQL). High-performance compute pools spin up on demand for simulation bursts.
- **API Layer:** FastAPI gateway exposing REST and GraphQL endpoints; gRPC internally for low-latency engine calls.
- **Job Orchestration:** Celery or Temporal coordinates fan-out across hundreds of GEM evaluations; Redis as broker, PostgreSQL for run history.
- **Containerization:** Each solver, model bundle, and worker is shipped as a Docker image with pinned dependencies (Gurobi license sidecar, COBRApy version, GEM hash). Identical execution from laptop to cluster.

### Phase 4 — User Experience

Hiding biology's complexity from the operator.

- **Input Dashboard:** Upload byproduct CSVs, paste chemical analyses, or pick from a templates library.
- **Live Simulation View:** Real-time progress bar of the 300+ model scan with intermediate top-N candidates.
- **Output Report:** "Perfect Match" card showing the recommended microbe, predicted yield, required fermentation conditions, R&D time saved vs. wet-lab baseline, and exportable PDF / API payload for downstream LIMS integration.

---

## Technology Stack

| Layer | Technologies | Rationale |
| :--- | :--- | :--- |
| **Bioinformatics Engine** | Python 3.11, COBRApy, Gurobi, NumPy, SciPy | COBRApy is the de-facto Python library for constraint-based modeling; Gurobi delivers fast MILP. |
| **Backend / API** | FastAPI, Pydantic, PostgreSQL, Redis | FastAPI couples Python models to the web cleanly; Pydantic enforces typed contracts at every boundary. |
| **Job Orchestration** | Celery or Temporal, RabbitMQ / Redis | Reliable fan-out and retry semantics for long-running scientific jobs. |
| **Frontend** | React, TypeScript, Tailwind CSS, Vite, Recharts | Modern, responsive, snappy dashboards; chart-rich result views. |
| **Infrastructure** | Docker, Kubernetes (EKS/GKE), Terraform, GitHub Actions | Reproducible, declarative, CI/CD from day one. |
| **Storage** | PostgreSQL (relational), S3/GCS (object), Parquet (sims) | Polyglot storage matched to access patterns. |
| **Observability** | OpenTelemetry, Prometheus, Grafana, Sentry | Traceable simulations and user-facing errors. |

---

## Repository Layout

The intended monorepo structure as the project grows:

```
bny_loop/
├── apps/
│   ├── web/                      # React + TS dashboard
│   └── api/                      # FastAPI gateway
├── services/
│   ├── engine/                   # COBRApy / Gurobi simulation workers
│   ├── ingestion/                # Byproduct profile parsers + validators
│   └── catalog/                  # GEM + microbe trait service
├── packages/
│   ├── schemas/                  # Shared Pydantic + TS types
│   └── ui/                       # Reusable React components
├── data/
│   ├── gems/                     # Curated SBML metabolic models
│   ├── microbes/                 # Trait tables (CSV / Parquet)
│   └── byproducts/               # Reference byproduct profiles
├── infra/
│   ├── docker/                   # Dockerfiles per service
│   ├── k8s/                      # Helm charts
│   └── terraform/                # Cloud IaC
├── notebooks/                    # Research + validation notebooks
├── scripts/                      # CLI utilities and dev tooling
├── tests/                        # Cross-service integration tests
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python** 3.11+
- **Node.js** 20+ and **pnpm** 9+
- **Docker** 24+ and **Docker Compose** v2
- **Gurobi** license (academic licenses available free; commercial license required for production). GLPK and CPLEX are supported as alternative solvers.
- **PostgreSQL** 15+ (or run via Docker Compose)

### Clone and bootstrap

```bash
git clone https://github.com/escoffai/bny_loop.git
cd bny_loop

# Python environment for engine + API
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend dependencies
pnpm install

# Local services (Postgres, Redis, MinIO)
docker compose up -d
```

### Seed the biological knowledge base

```bash
python scripts/seed_gems.py --source bigg --limit 50
python scripts/seed_microbes.py --source builtin
python scripts/seed_byproducts.py --source ./data/byproducts/reference.json
```

### Run the stack in development

```bash
# Terminal 1 — API
uvicorn apps.api.main:app --reload --port 8000

# Terminal 2 — Engine workers
celery -A services.engine.worker worker --loglevel=info

# Terminal 3 — Web app
pnpm --filter web dev
```

The dashboard will be available at `http://localhost:5173` and the API at `http://localhost:8000/docs`.

---

## Configuration

Environment variables are documented in `.env.example`. Key settings:

| Variable | Purpose | Default |
| :--- | :--- | :--- |
| `BNY_DATABASE_URL` | PostgreSQL connection string | `postgresql://bny:bny@localhost:5432/bny` |
| `BNY_REDIS_URL` | Redis broker URL | `redis://localhost:6379/0` |
| `BNY_OBJECT_STORE` | S3/GCS/MinIO bucket for sim artifacts | `minio://bny-artifacts` |
| `BNY_SOLVER` | LP/MILP solver (`gurobi`, `cplex`, `glpk`) | `glpk` |
| `BNY_MAX_PARALLEL_SIMS` | Per-job worker fan-out limit | `64` |
| `BNY_GEM_LIBRARY_PATH` | Local cache directory for SBML models | `./data/gems` |

---

## Running a Simulation

### Via the dashboard

1. Open the web app and click **New Simulation**.
2. Upload a byproduct CSV or choose a reference profile (e.g. *Cheese Whey — Cheddar*).
3. Set the objective: `max_yield`, `max_productivity`, `min_cost`, or a weighted combination.
4. Click **Run**. The progress view streams candidate matches as they are evaluated.
5. After ~10 minutes, download the **Perfect Match Report** as PDF or JSON.

### Via the CLI

```bash
bny simulate \
  --input ./examples/cheese_whey.json \
  --objective max_yield \
  --product "lactic_acid" \
  --output ./reports/run_001.json
```

### Via the API

```bash
curl -X POST http://localhost:8000/v1/simulations \
  -H "Content-Type: application/json" \
  -d @examples/cheese_whey.json
```

---

## API Reference

A subset of the REST surface (full OpenAPI at `/docs`):

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/byproducts` | Register a byproduct chemical profile |
| `GET`  | `/v1/byproducts/{id}` | Retrieve a stored profile |
| `POST` | `/v1/simulations` | Launch a new simulation run |
| `GET`  | `/v1/simulations/{id}` | Poll status and stream partial results |
| `GET`  | `/v1/simulations/{id}/report` | Download the final ranked report |
| `GET`  | `/v1/microbes` | Browse the microbial trait library |
| `GET`  | `/v1/gems` | Browse available genome-scale models |

All endpoints are versioned and require an API key in the `Authorization: Bearer <token>` header.

---

## Data Sources

BNY LOOP ships with adapters for the major open biological repositories:

- **BiGG Models** — http://bigg.ucsd.edu/
- **KEGG** — https://www.genome.jp/kegg/
- **MetaCyc / BioCyc** — https://metacyc.org/
- **Virtual Metabolic Human (VMH)** — https://www.vmh.life/
- **NCBI Taxonomy** — for organism canonicalization

License terms vary; consult each provider before commercial use. The platform records the source and license of every model in its provenance log.

---

## Performance Targets

| Metric | Target |
| :--- | :--- |
| End-to-end simulation latency | ≤ 10 minutes for a full 300-model scan |
| Single-model FBA evaluation | < 2 seconds (median) |
| MILP convergence (production selection) | < 90 seconds |
| Concurrent simulations per cluster node | ≥ 8 |
| Predicted-vs-measured yield correlation (R²) | ≥ 0.85 on validation panel |

---

## Roadmap

- [x] Repository scaffolding
- [ ] Phase 1 — Seed biological knowledge base (50 → 300 GEMs)
- [ ] Phase 2 — FBA + MILP MVP with reproducible benchmarks
- [ ] Phase 2 — Dynamic FBA for fed-batch trajectories
- [ ] Phase 3 — Kubernetes-native worker fan-out with autoscaling
- [ ] Phase 4 — Dashboard with live progress and exportable reports
- [ ] Wet-lab validation panel (5 industry byproducts × 3 microbes)
- [ ] Strain-engineering recommender (gene knockouts / overexpressions)
- [ ] Techno-economic analysis (TEA) and life-cycle assessment (LCA) modules
- [ ] LIMS / ERP connectors for ingredient companies
- [ ] Public sandbox tier with rate-limited access

---

## Contributing

This is a multidisciplinary effort. We welcome contributions from:

- **Software engineers** — backend, frontend, infra, MLOps
- **Bioinformaticians** — GEM curation, FBA tooling, dFBA
- **Chemical & fermentation engineers** — process modeling, validation
- **Domain advisors** — food science, sustainability, biomanufacturing operations

Workflow:

1. Fork and create a feature branch (`feat/<short-name>`).
2. Add or update tests; keep coverage above the project threshold.
3. Run `make lint test` before pushing.
4. Open a pull request with a clear description and link to any tracking issue.

Code style: `ruff` + `black` for Python, `eslint` + `prettier` for TypeScript. Pre-commit hooks are configured in `.pre-commit-config.yaml`.

---

## Team & Disciplines

Building BNY LOOP requires deep collaboration between:

- **Bioinformatics scientists** — to ensure GEMs and FBA assumptions reflect real biology.
- **Software & cloud engineers** — to deliver scalable, reproducible compute.
- **Chemical / fermentation engineers** — to translate simulation outputs into wet-lab-ready protocols.
- **Product & UX designers** — to keep the dashboard intuitive for non-PhD users.
- **Industry advisors** — to ground the platform in real customer workflows (food, pharma, materials).

The platform is only as good as the alignment between digital simulation and physical lab reality; every release is gated on validation against measured fermentation data.

---

## License

Proprietary. All rights reserved. Contact the maintainers for licensing or partnership inquiries.

---

*BNY LOOP — closing the loop between byproducts and breakthroughs.*
