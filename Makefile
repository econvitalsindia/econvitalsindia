# See AGENTS.md → Commands. Stubs print "not implemented yet" until their phase lands.
PY ?= uv run python

.PHONY: setup check test update update-auto india-update build dev archive-raw

setup:
	uv sync
	@[ -f site/package.json ] && (cd site && npm install) || echo "site/ not scaffolded yet (Phase 1)"

check:
	$(PY) scripts/validate_registry.py
	$(PY) scripts/check_name.py
	uv run pytest -q

test:
	uv run pytest -q

update:
	@echo "not implemented yet (Phase 1): make update SOURCE=$(SOURCE)"

update-auto:
	@echo "not implemented yet (Phase 1)"

india-update:
	@echo "not implemented yet (Phase 1): runs all fetch: manual series and opens a PR"

build:
	@echo "not implemented yet (Phase 1)"

dev:
	@echo "not implemented yet (Phase 1)"

archive-raw:
	@echo "not implemented yet (Phase 1)"
