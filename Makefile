.PHONY: bootstrap lint typecheck test dev-up dev-down sim-smoke clean

PY ?= python3
UV ?= uv
PNPM ?= pnpm

bootstrap:
	@command -v $(UV) >/dev/null 2>&1 || { echo "Install uv: https://docs.astral.sh/uv/"; exit 1; }
	@command -v $(PNPM) >/dev/null 2>&1 || { echo "Install pnpm: https://pnpm.io/installation"; exit 1; }
	$(UV) sync --extra dev
	$(PNPM) install

lint:
	$(UV) run ruff check .
	$(UV) run black --check .
	$(PNPM) run -s lint || true

typecheck:
	$(UV) run mypy services/engine || true
	$(PNPM) run -s typecheck || true

test:
	$(UV) run pytest

dev-up:
	docker compose up -d

dev-down:
	docker compose down

sim-smoke:
	$(UV) run python scripts/sim_smoke.py

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache **/__pycache__ dist build .venv
