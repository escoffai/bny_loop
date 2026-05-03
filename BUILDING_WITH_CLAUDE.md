# Building BNY LOOP with Claude

> A practical, end-to-end plan for developing the BNY LOOP platform using Claude as the primary engineering partner — Claude Code for the day-to-day build, the Claude API for runtime intelligence, the Claude Agent SDK for orchestrated subsystems, plus a curated set of skills, subagents, hooks, and MCP servers.

This document is the companion to [README.md](./README.md). The README describes *what* BNY LOOP is. This document describes *how to actually build it* when your engineering team is one person plus Claude.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What "Claude-Only Development" Means](#what-claude-only-development-means)
3. [Toolchain Setup](#toolchain-setup)
4. [Model Selection Strategy](#model-selection-strategy)
5. [Subagents Library](#subagents-library)
6. [Skills Library](#skills-library)
7. [Hooks and Slash Commands](#hooks-and-slash-commands)
8. [MCP Servers](#mcp-servers)
9. [Phase 0 — Foundation](#phase-0--foundation-week-1)
10. [Phase 1 — Biological Knowledge Base](#phase-1--biological-knowledge-base-weeks-26)
11. [Phase 2 — Computational Engine](#phase-2--computational-engine-weeks-714)
12. [Phase 3 — Cloud & API](#phase-3--cloud--api-weeks-1520)
13. [Phase 4 — User Experience](#phase-4--user-experience-weeks-2126)
14. [Phase 5 — Validation & Hardening](#phase-5--validation--hardening-weeks-2732)
15. [Working with Claude — Patterns That Work](#working-with-claude--patterns-that-work)
16. [Risks and Mitigations](#risks-and-mitigations)
17. [Cost and Time Budget](#cost-and-time-budget)
18. [Starter Prompts](#starter-prompts)

---

## Executive Summary

| Question | Answer |
| :--- | :--- |
| Can one engineer build BNY LOOP with Claude? | The MVP — yes, 6–8 months. Production scale and wet-lab validation — no, you need scientists. |
| Calendar time to first runnable demo | 4 weeks |
| Calendar time to validated MVP | 6–8 months |
| Estimated Claude spend (development) | $1,500 – $4,000 / month |
| Languages used | Python (engine, API), TypeScript (web), Bash/Terraform (infra) |
| Where humans are still required | Wet-lab validation, Gurobi license procurement, regulatory and IP review, fundraising |

The platform is divided into 5 development phases, each broken into Claude-driven workstreams. Every workstream lists the model to use, the subagent that owns it, the verification gate, and concrete prompts to copy-paste.

---

## What "Claude-Only Development" Means

### What Claude does well in this project

- **Scaffolding** — bootstrapping repos, Dockerfiles, Helm charts, CI pipelines.
- **Code generation** — FastAPI routes, Pydantic schemas, React components, Tailwind layouts.
- **Translation between domains** — turning a biology paper's equations into COBRApy code.
- **Refactoring and review** — second-pass critique of generated code.
- **Test generation** — property tests, golden-file tests, integration tests.
- **Documentation** — keeping README, ADRs, and API docs synced with code.
- **Prompt-time RAG** — pulling in BiGG/KEGG metadata via MCP and reasoning over it.

### What Claude cannot do (and shouldn't)

- **Run wet-lab fermentation.** Predicted yields must be validated experimentally before customer claims.
- **Make scientific judgement calls without literature grounding.** Always pair with citations — never accept a metabolic claim from Claude unless it cites a paper or GEM source you can re-check.
- **Procure Gurobi/CPLEX licenses or sign data-use agreements.**
- **Decide product strategy.** It can list options; you decide.

### The mental model

Treat Claude as a **senior generalist engineer** who is excellent at reading code and biology papers, fast at writing, and willing to redo work. You are the **tech lead and scientist-in-the-loop**. Your job is to:

1. Decompose the problem into well-scoped tickets.
2. Choose the right Claude surface (Code / API / Agent SDK / subagent / skill).
3. Verify outputs against ground truth (papers, golden files, wet-lab data).
4. Keep `CLAUDE.md` files current so context is reproducible.

---

## Toolchain Setup

### Claude Code (primary IDE)

The interactive CLI is your daily driver. Install in the project root and let it own the repo.

```bash
npm install -g @anthropic-ai/claude-code
cd bny_loop
claude
```

Configure `CLAUDE.md` at the repo root with the permanent context every session needs (architecture diagram, commands, conventions, tabu rules). Add scoped `CLAUDE.md` files in `services/engine/`, `apps/web/`, etc. so subsystem-specific guidance loads automatically when Claude works in that directory.

Recommended `.claude/settings.json` defaults:

```json
{
  "model": "claude-opus-4-7",
  "permissions": {
    "allow": [
      "Bash(pnpm:*)",
      "Bash(uv:*)",
      "Bash(pytest:*)",
      "Bash(ruff:*)",
      "Bash(docker compose:*)",
      "Bash(kubectl get:*)",
      "Bash(terraform plan)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "ruff check --fix" }] }
    ]
  }
}
```

### Claude API (runtime intelligence)

Use the Anthropic Python SDK inside the BNY LOOP services for any features that need an LLM at runtime:

- **Byproduct profile parsing** — convert a customer's free-text description ("we have ~30k L/day of cheese whey from cheddar production") into the structured ontology.
- **Report narrative generation** — turn the ranked simulation output into a customer-facing explanation.
- **Literature lookup assistance** — given a candidate microbe-product pair, summarize what is known from open papers.

Always enable **prompt caching** on these calls. The system prompt that describes the ontology, output schema, and few-shot examples will be large and stable.

### Claude Agent SDK (subsystem orchestration)

Use the Agent SDK to build long-running agents that reason over the simulation outputs. Concrete uses:

- A **strain-engineering recommender** agent that reads the FBA solution, queries KEGG for adjacent reactions, and proposes gene knockouts.
- A **regulatory-scout** agent that, given a recommended microbe, checks GRAS / EFSA / FDA status and flags risks.

These are best implemented with the SDK rather than embedded in Claude Code, because they need to run on a schedule and persist state.

---

## Model Selection Strategy

| Task | Model | Why |
| :--- | :--- | :--- |
| Architecting a service from scratch | **Opus 4.7** | Multi-file reasoning, tradeoff analysis. |
| Writing FBA / MILP code with biology references | **Opus 4.7** | High stakes, easy to get subtly wrong. |
| Bulk CRUD endpoints, Pydantic schemas | **Sonnet 4.6** | Fast, capable, cheaper. |
| React component conversion from Figma | **Sonnet 4.6** | Excellent UI work. |
| Generating thousands of unit tests in parallel | **Haiku 4.5** | Cheap, parallelizable. |
| Categorizing a single byproduct into the ontology at runtime | **Haiku 4.5** | Latency- and cost-sensitive. |
| Summarizing simulation outputs into customer-facing reports | **Sonnet 4.6** | Quality matters, but not Opus-grade. |

Set per-directory model defaults via `CLAUDE.md` so the right brain is loaded automatically.

---

## Subagents Library

Define these in `.claude/agents/` so any session can dispatch them. Each is a markdown file with frontmatter (`name`, `description`, `model`, `tools`).

| Subagent | Role | Model | Key tools |
| :--- | :--- | :--- | :--- |
| `bio-validator` | Audits any new metabolic-modeling code against a checklist (mass balance, charge balance, biomass objective sanity). Refuses code without references. | Opus 4.7 | Read, Bash (run COBRApy), WebFetch |
| `cobra-engineer` | Implements FBA / FVA / MILP / dFBA features in the engine service. | Opus 4.7 | Edit, Write, Bash |
| `gem-curator` | Imports SBML files, normalizes IDs, deduplicates reactions across BiGG/KEGG/MetaCyc. | Sonnet 4.6 | Read, Edit, Bash |
| `api-builder` | Builds and refactors FastAPI endpoints, handles Pydantic schema evolution. | Sonnet 4.6 | Edit, Write |
| `frontend-implementer` | Implements React/Tailwind components, especially Figma-to-code. | Sonnet 4.6 | Edit, Write, Figma MCP |
| `infra-engineer` | Owns Dockerfiles, Helm charts, Terraform, CI workflows. | Sonnet 4.6 | Edit, Write, Bash |
| `test-author` | Generates pytest / vitest cases, including property tests. | Haiku 4.5 | Edit, Write |
| `doc-keeper` | Updates README, ADRs, OpenAPI, and `CLAUDE.md` whenever code changes. | Haiku 4.5 | Edit, Read |
| `security-reviewer` | Runs the security-review skill on PRs. | Opus 4.7 | Read, Bash |
| `perf-profiler` | Profiles simulation runs, finds hotspots, suggests optimizations. | Sonnet 4.6 | Bash, Read |

Example `.claude/agents/bio-validator.md`:

```markdown
---
name: bio-validator
description: |
  Use proactively when any change touches services/engine, data/gems/, or
  metabolic-modeling logic. Validates mass balance, references published
  results, and refuses changes without citations.
model: claude-opus-4-7
tools: Read, Bash, WebFetch, Grep
---

You are a metabolic-modeling reviewer. For every change:
1. Verify mass and charge balance on any new or modified reaction.
2. Confirm objective function and exchange-flux bounds match cited literature.
3. Refuse to approve code that introduces metabolic claims without a citation
   to a published GEM, paper, or curated database.
4. Run the change against the test panel in tests/engine/known_yields/ and
   flag any deviation > 5% from published yields.
```

---

## Skills Library

Skills are reusable prompt + tool bundles. Create these in `~/.claude/skills/` or `.claude/skills/`.

| Skill | When it triggers | What it does |
| :--- | :--- | :--- |
| `validate-fba-output` | After any FBA run | Checks that biomass flux > 0, all exchange fluxes are within bounds, and the solution is unique within tolerance. |
| `import-sbml` | When user pastes a BiGG/KEGG model URL | Downloads the SBML, validates it, normalizes IDs, registers in the catalog DB. |
| `wet-lab-cross-check` | When a simulation report is generated | Compares predicted yield against the validation panel and flags outliers. |
| `gurobi-license-check` | At session start in services/engine | Verifies a valid Gurobi license is present and warns if expired. |
| `byproduct-from-text` | When a user pastes free-text byproduct description | Calls Claude API to convert into the structured ontology. |
| `golden-yield-test` | After any engine change | Runs the full validation panel and reports drift. |
| `release-notes` | Before tagging a release | Generates customer-facing release notes from commits. |

The first three are foundational and should exist before week 4.

---

## Hooks and Slash Commands

Configure hooks in `.claude/settings.json` to enforce invariants the model would otherwise drift on.

| Hook | Trigger | Command |
| :--- | :--- | :--- |
| Lint on save | `PostToolUse` matching `Edit|Write` on `*.py` | `ruff check --fix && black .` |
| Type check | `PostToolUse` on `*.ts*` | `pnpm tsc --noEmit` |
| FBA smoke test | `PostToolUse` in `services/engine/` | `pytest tests/engine/smoke -q` |
| Refuse direct main edits | `PreToolUse` on Edit | Reject if `git rev-parse --abbrev-ref HEAD` returns `main`. |
| Start-of-session brief | `SessionStart` | Print `git status`, last 5 commits, failing tests. |

Slash commands worth authoring:

- `/sim-here <byproduct.json>` — runs a local simulation against a specified byproduct file and pretty-prints the result.
- `/seed-gems <count>` — invokes the `gem-curator` agent to import N more models.
- `/dashboard` — boots the full dev stack (Docker Compose + frontend dev server).
- `/wet-lab-check` — runs the `wet-lab-cross-check` skill.
- `/cost` — prints token spend in the current session.

---

## MCP Servers

| Server | Already available | Purpose |
| :--- | :--- | :--- |
| GitHub MCP | Yes | PRs, reviews, CI status |
| Supabase MCP | Yes | Database migrations, type generation, edge functions if used for the catalog service |
| Vercel MCP | Yes | Deploy the marketing site and dashboard preview environments |
| Figma MCP | Yes | Pull designs into React components |
| **BiGG / KEGG / MetaCyc MCP** | Custom — build it | Query metabolic databases without leaving Claude Code |
| **COBRApy MCP** | Custom — build it | Run FBA / FVA from inside the model's tool calls (sandboxed) |
| **Gurobi MCP** | Custom — build it | Solve MILP problems on a licensed server |

Building the BiGG/KEGG MCP server is itself a great Phase 0 task — Claude can scaffold it from the Anthropic MCP examples in an afternoon. Once it exists, every subsequent biology question Claude asks is grounded in the real data, not training-set memory.

---

## Phase 0 — Foundation (Week 1)

**Goal:** A repository where every Claude session starts productive.

### Workstreams

1. **Repo scaffolding.** Monorepo structure as in the README. pnpm workspaces, uv for Python, single `Makefile`.
2. **`CLAUDE.md` hierarchy.** Root, `services/engine/`, `apps/api/`, `apps/web/`. Each one names the model, the active subagent, and the tabu list.
3. **CI/CD baseline.** GitHub Actions: lint, typecheck, unit tests, Docker build. Block merges on red.
4. **Pre-commit hooks.** ruff, black, eslint, prettier, mypy (strict on engine).
5. **Docker Compose dev stack.** Postgres, Redis, MinIO, mock Gurobi license server.
6. **First subagents and skills.** `bio-validator`, `validate-fba-output`, `import-sbml`.
7. **First custom MCP.** BiGG read-only server.

### Verification gate

- A clean `make bootstrap && make test` on a fresh checkout succeeds in under 10 minutes.
- Claude Code can run end-to-end: clone, open, ask "summarize the architecture", and get a correct answer.

### Sample prompt

```
Bootstrap the monorepo per README.md "Repository Layout". Create
package.json with pnpm workspaces, pyproject.toml using uv, and a Makefile
with: bootstrap, lint, test, dev-up, dev-down, sim-smoke. Add a
docker-compose.yml with Postgres 16, Redis 7, and MinIO. Add CI in
.github/workflows/ci.yml that runs lint and unit tests on PR. Stop after
this is green; do not start Phase 1.
```

---

## Phase 1 — Biological Knowledge Base (Weeks 2–6)

**Goal:** A catalog service that holds 50 curated GEMs, a microbe traits table, and a byproduct ontology, all queryable via API.

### Workstreams

1. **GEM ingestion pipeline.** SBML parser, ID normalizer, deduplication. Driven by `gem-curator` subagent.
2. **Microbe traits database.** Schema + seed data for ~100 organisms. pH range, temperature, oxygen requirement, GRAS status, BSL level, transformation tractability.
3. **Byproduct ontology.** JSON-Schema describing molar composition. Reference profiles for cheese whey, brewer's spent grain, fruit pomace, glycerol, molasses.
4. **Catalog API.** FastAPI endpoints to browse GEMs, microbes, byproducts.
5. **Provenance log.** Every imported model records source URL, license, import date, hash. Audit-ready.

### Claude usage pattern

Run `gem-curator` in parallel batches: dispatch 10 import jobs at once, each fetching a different organism, with the `bio-validator` subagent reviewing each PR. Use Haiku for the bulk normalization, Opus only on the validator pass.

### Verification gate

- 50 GEMs imported, validated, and queryable through the API.
- A reference simulation (E. coli on glucose) reproduces the published growth rate within 2%.
- The byproduct ontology round-trips: serialize → parse → re-serialize without information loss.

### Sample prompt

```
Implement services/catalog/import_bigg.py. It should:
1. Take a BiGG model ID (e.g. "iML1515") as argument.
2. Download the SBML from http://bigg.ucsd.edu via the BiGG MCP tool.
3. Validate using cobra.io.read_sbml_model.
4. Insert into the gems table with the schema in packages/schemas/gem.py.
5. Log a provenance record.

Add tests/catalog/test_import_bigg.py with golden-file tests for iML1515 and
iJO1366. Use the bio-validator subagent to review your work before you finish.
```

---

## Phase 2 — Computational Engine (Weeks 7–14)

**Goal:** The engine that takes a byproduct, scans the GEM library, and returns a ranked list of microbe matches with predicted yields and conditions.

### Workstreams

1. **FBA wrapper.** Thin, deterministic Python module on top of COBRApy. Single entry point: `evaluate(microbe_id, byproduct_profile, objective)`.
2. **MILP optimization.** Selects the best microbe(s) across the library. Pluggable solver (Gurobi, CPLEX, GLPK).
3. **Dynamic FBA.** Time-stepped simulation for batch / fed-batch. Outputs the operating envelope.
4. **Sensitivity analysis.** Monte-Carlo over feedstock variability to produce the Batch Consistency score.
5. **Engine worker.** Celery task that fans out across the library, collects results, ranks them, persists to object storage as Parquet.
6. **Validation panel.** A frozen set of (byproduct, microbe, expected yield) triples drawn from peer-reviewed papers. The engine must reproduce these within tolerance.

### Claude usage pattern

This is the highest-stakes code in the project. Use Opus 4.7 throughout. Always pair `cobra-engineer` with `bio-validator`. Never merge an engine change without the validation panel passing. Configure a hook to refuse merging if `pytest tests/engine/validation_panel` fails.

### Verification gate

- Validation panel: at least 12 known (byproduct, microbe, yield) triples reproduced within 10% on the first cut, 5% by the end of Phase 2.
- A 300-model scan runs end-to-end (mocked GEMs OK) in under 10 minutes on a 16-core machine.
- Sensitivity analysis emits a calibrated Batch Consistency number with documented methodology.

### Sample prompt

```
Implement services/engine/dfba.py — dynamic FBA for fed-batch fermentation.

Inputs: microbe_id, byproduct_profile, total_time_hours, feed_schedule.
Outputs: trajectory of biomass, substrate, product, plus recommended pH and
temperature setpoints derived from the microbe's trait record.

Reference implementations:
- Mahadevan 2002 "Dynamic flux balance analysis of diauxic growth in E. coli"
- COBRApy dfba example notebook

Add a validation test against the diauxic-growth golden file in
tests/engine/golden/diauxic_ecoli.parquet. Tolerance: 5% on max biomass and
substrate exhaustion time.

Run bio-validator before declaring done.
```

---

## Phase 3 — Cloud & API (Weeks 15–20)

**Goal:** The platform runs in a Kubernetes cluster, scales out simulation workers under load, and is observable in production.

### Workstreams

1. **API gateway.** FastAPI service exposing the public REST/GraphQL surface from the README.
2. **Auth.** API key + JWT, role-based scopes (admin, customer, read-only).
3. **Job orchestration.** Celery (or Temporal) for long-running simulations; Redis broker; Postgres for run history.
4. **Kubernetes manifests.** Helm chart for the full stack; HPA on engine workers; Gurobi license sidecar.
5. **Object storage.** S3 / GCS for SBML files, simulation Parquet, generated PDF reports.
6. **Observability.** OpenTelemetry traces across API → queue → worker; Prometheus + Grafana dashboards; Sentry.
7. **Cost guardrails.** Per-tenant simulation quotas; circuit breaker if Gurobi solver time exceeds budget.

### Claude usage pattern

`infra-engineer` subagent. Heavy use of the Vercel MCP for preview deploys and Supabase MCP if you choose Supabase as the managed Postgres. Sonnet 4.6 is sufficient for most of this work.

### Verification gate

- Helm chart deploys cleanly to a fresh kind cluster and to a managed cluster (EKS or GKE).
- Load test: 100 concurrent simulations, p95 end-to-end latency below 12 minutes, no OOMs.
- Trace from API request to engine worker is fully linked.

---

## Phase 4 — User Experience (Weeks 21–26)

**Goal:** A dashboard that any food-tech R&D lead can use without training.

### Workstreams

1. **Design system.** Tailwind tokens; primitive components; Storybook.
2. **Input dashboard.** Byproduct upload (CSV, manual, lab-instrument export); template gallery.
3. **Simulation progress view.** Live updates streamed via SSE or WebSockets; intermediate top-N candidates as they emerge.
4. **Output report.** "Perfect Match" card; predicted yield with uncertainty bands; required fermentation conditions; R&D time saved; downloadable PDF.
5. **Account and billing.** Tenant management; invoice history; usage meters.

### Claude usage pattern

`frontend-implementer` subagent + Figma MCP. Designers drop URLs in the chat; Claude pulls the frame, generates a candidate component, and a hook runs Playwright snapshot tests against the result.

### Verification gate

- All flows pass Playwright e2e tests in headless CI.
- Lighthouse performance score ≥ 90 on the dashboard route.
- A non-engineer (someone from your industry advisory board) successfully runs a simulation end-to-end in under 15 minutes without help.

---

## Phase 5 — Validation & Hardening (Weeks 27–32)

**Goal:** The platform is trustworthy enough for paying customers.

### Workstreams

1. **Wet-lab validation panel.** Five real industrial byproducts, three candidate microbes each, run in a partner lab. Compare predictions to measurements. Tune until R² ≥ 0.85.
2. **Security review.** Run the `security-review` skill across the entire codebase. Pen-test the API. Add SAST and SCA to CI.
3. **Compliance posture.** Data-residency, SOC 2 readiness checklist, model-provenance documentation for customers in regulated industries.
4. **Customer-facing docs.** Tutorials, API reference, webinar deck.
5. **Public sandbox tier.** Rate-limited, no payment, for academic and prospect access.

### Verification gate

- Validation R² ≥ 0.85 on the wet-lab panel.
- No high-severity findings open from the security review.
- First three pilot customers onboarded.

---

## Working with Claude — Patterns That Work

### 1. The Spec → Skeleton → Fill loop

Don't ask Claude for a full feature in one shot. Run three smaller turns:

1. *Spec turn.* "Write the spec for X as a markdown doc. No code yet."
2. *Skeleton turn.* "Implement the public surface (function signatures, types, stubbed bodies). No logic yet."
3. *Fill turn.* "Implement the bodies. Tests must pass."

You can review each turn quickly; the model gets unambiguous targets at each step.

### 2. Verification gates over verification prompts

Never rely on Claude saying "I tested it." Instead, configure a hook so the test command runs automatically after every edit, and the model sees the result.

### 3. Parallelize with subagents on independent tasks

Importing 50 GEMs is 50 independent jobs. Dispatch them as a fan-out of `gem-curator` calls. Use Haiku — the unit cost is small, and the wallclock saving is real.

### 4. Pin the biology

Never let the model invent a metabolic claim. Either it cites a published model or paper, or `bio-validator` rejects the change. Configure that subagent to run automatically on engine PRs via a hook.

### 5. Keep `CLAUDE.md` ruthless

The most common failure mode is context drift across long sessions. Update `CLAUDE.md` whenever an architectural decision is made. Delete anything that's no longer true. A 200-line `CLAUDE.md` that's accurate beats a 2000-line one that's stale.

### 6. Use the Plan agent for cross-cutting changes

When you need to change something that touches engine, API, and frontend together (e.g. introducing tenants), invoke the Plan agent first. Get a step plan you can review before any edits land.

### 7. Trust but verify

A subagent's summary is what it intended to do, not what it did. After every non-trivial agent run, open the diff yourself.

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Hallucinated metabolic claims slip through | Medium | High (customer trust) | `bio-validator` mandatory on engine PRs; literature citation required; wet-lab validation panel. |
| Solver licensing cost balloons | Medium | Medium | Default to GLPK in dev; Gurobi only on dedicated solver pods with rate limits. |
| Validation R² stalls below 0.85 | Medium | High | Allocate Phase 5 explicitly to closing the gap; budget for additional GEM curation; retain a fermentation engineer on retainer. |
| Claude context drift in long sessions | High | Low–Medium | Aggressive `CLAUDE.md` hygiene; `/clear` between unrelated tasks; subagents for isolation. |
| Token spend exceeds budget | Medium | Medium | Per-day spend alerts; Haiku for parallel bulk; prompt caching everywhere. |
| Single-engineer bus factor | High | High | All decisions documented as ADRs; subagents and skills checked into the repo so context is portable. |
| Dependence on third-party biological databases (license / availability) | Low | Medium | Mirror BiGG and curated subsets in S3; document license per source. |
| Wet-lab partner availability | Medium | High | Line up two partners by Phase 3; budget in advance. |

---

## Cost and Time Budget

### Calendar time (one engineer + Claude)

| Phase | Weeks | Description |
| :--- | :--- | :--- |
| 0 | 1 | Foundation |
| 1 | 5 | Knowledge base |
| 2 | 8 | Engine |
| 3 | 6 | Cloud & API |
| 4 | 6 | UX |
| 5 | 6 | Validation & hardening |
| **Total** | **32 weeks** | |

### Claude spend (rough order of magnitude)

| Phase | Estimated monthly spend | Notes |
| :--- | :--- | :--- |
| 0 | $500 – $1,000 | Heavy Opus use early |
| 1 | $1,500 – $2,500 | Parallel imports on Haiku/Sonnet |
| 2 | $2,500 – $4,000 | Opus-heavy; bio-validator runs frequently |
| 3 | $1,500 – $2,500 | Mostly Sonnet |
| 4 | $1,000 – $2,000 | Mostly Sonnet |
| 5 | $1,500 – $2,500 | Security and validation runs |

Total development Claude spend: roughly **$30,000 – $60,000** over eight months. Single engineer salary, infra, and Gurobi license dwarf this.

### Where you still need humans

| Role | Engagement |
| :--- | :--- |
| Fermentation engineer | Retainer, 20% from Phase 2 onward |
| Bioinformatician | Retainer, 20% across Phases 1–2; on-call afterward |
| Wet-lab partner | Statement of work for Phase 5 |
| Security auditor | One engagement before launch |
| Designer | Contract for design system + key flows in Phase 4 |
| Industry advisors | Quarterly sessions throughout |

---

## Starter Prompts

Copy-paste these into Claude Code at the start of each phase. Each one is self-contained.

### Week 1, Day 1 — bootstrap

```
Read README.md. Create the monorepo structure listed under "Repository Layout".
Use pnpm workspaces and uv. Add a Makefile with bootstrap, lint, test, dev-up,
dev-down, sim-smoke targets. Add docker-compose.yml with Postgres 16, Redis 7,
MinIO. Add .github/workflows/ci.yml that runs lint and unit tests. Stop after
make bootstrap && make test passes on a fresh checkout. Don't begin Phase 1.
```

### Week 1, Day 3 — first subagents

```
Create .claude/agents/bio-validator.md, .claude/agents/cobra-engineer.md, and
.claude/agents/gem-curator.md per the specs in BUILDING_WITH_CLAUDE.md. Then
create .claude/skills/validate-fba-output/ with a SKILL.md that runs a
deterministic check on any FBA solution. Verify by invoking each agent on a
trivial test task.
```

### Week 2 — first GEM import

```
Implement services/catalog/import_bigg.py per the spec in
BUILDING_WITH_CLAUDE.md Phase 1. Add tests for iML1515 and iJO1366. Use
gem-curator and have bio-validator review before completing. Then import the
first 10 BiGG models in parallel using a fan-out of gem-curator agents.
```

### Week 7 — engine kickoff

```
Implement services/engine/fba.py — thin deterministic FBA wrapper.

Single public function:
  evaluate(microbe_id: str, byproduct: ByproductProfile, objective: str) -> FBAResult

Use COBRApy. Solver selection via BNY_SOLVER env var (default glpk).
Validate inputs with Pydantic. Log every solver call.

Add tests against three published references in
tests/engine/validation_panel/. Target 5% tolerance.

Use cobra-engineer subagent. bio-validator must approve before merge.
```

### Week 15 — cloud kickoff

```
Implement the API gateway in apps/api per OpenAPI spec at packages/schemas/openapi.yaml.
Wire to the engine via Celery (Redis broker). Add OpenTelemetry tracing
end-to-end. Add Helm chart in infra/k8s/bny-loop with HPA on engine workers
and a Gurobi license sidecar. Verify by deploying to a kind cluster and
running 10 concurrent /v1/simulations requests.
```

### Week 21 — UX kickoff

```
Implement the New Simulation flow per the Figma file the user shares. Use the
Figma MCP to fetch the design, the frontend-implementer subagent to write the
React components, and add Playwright tests for the happy path and the CSV
upload edge cases. Style with Tailwind tokens already defined in
packages/ui/tokens.ts.
```

### Week 27 — validation panel

```
Run the wet-lab validation panel against the predictions from the engine.
Inputs are tests/validation/wetlab_results.csv. Output a markdown report
showing predicted vs measured yield, R² overall and per-microbe, and
flag any pair > 15% off. Spawn the perf-profiler agent in parallel to
identify any solver performance issues during the run.
```

---

## Appendix — A Day in the Life

A representative day at week 10:

1. **Morning.** `git pull`. Open Claude Code. The `SessionStart` hook prints `git status`, the last 5 commits, and any failing tests. One test in `tests/engine/validation_panel/lactic_acid_whey.py` is red.
2. **Triage.** "What changed in services/engine since the test went red?" Claude reads the log, identifies the suspect commit, opens the diff.
3. **Fix.** "Reproduce the failure locally and propose a minimal fix." `cobra-engineer` runs the test with verbose solver output, identifies a flux bound that drifted during a refactor, fixes it.
4. **Verify.** Hook runs `pytest tests/engine/validation_panel` automatically. All green.
5. **Review.** `bio-validator` runs on the diff. Approves with a note that the fix matches the original Mahadevan 2002 formulation.
6. **Push.** Claude opens a PR with a description that links the failing test, the root cause, and the citation. CI passes; merge.
7. **Afternoon.** Switch to `apps/web`. `CLAUDE.md` in that directory swaps the active model to Sonnet and the active subagent to `frontend-implementer`. Build the next dashboard component from a Figma URL.
8. **End of day.** `/cost` shows $42 spent. Notes from the session are appended to the running architectural decision log.

That cadence — short loops, automatic verification, subagents pinned to roles — is what makes Claude-only development work for a project this ambitious.

---

*This plan is a living document. As the project evolves, update it alongside `README.md` and the per-directory `CLAUDE.md` files.*
