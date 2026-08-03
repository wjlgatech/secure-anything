.PHONY: install test lint fmt check build build-check northstar route \
        manifest registry ainative publish-gate public public-drift run worker docker-up

install:
	python -m pip install -e ".[dev]"

# THE canonical gate (what CI and `anyagent goal` discover).
# Offline and deterministic: no network, no API key. Order is deliberate — cheap
# structural gates fail fast before the test suite runs.
check: lint manifest registry build-check publish-gate public-drift ainative test

lint:
	ruff check src tests scripts

fmt:
	ruff format src tests scripts

test:
	python -m pytest

# --- the meta-repo's own gates ------------------------------------------------
manifest:            ## charter docs exist, with their required headings
	python3 scripts/manifest_gate.py

registry:            ## refuse any status promotion lacking on-disk evidence
	python3 scripts/verify_registry.py

build:               ## regenerate every published surface from data/
	python3 scripts/build.py

build-check:         ## fail if a generated surface drifted from data/
	python3 scripts/build.py --check

ainative:            ## the repo audits its own disciplines (gate >= 90)
	python3 scripts/ainative.py

northstar:           ## Verified Control Coverage, computed offline from data/
	python3 scripts/northstar.py

route:               ## drive the router: make route Q="scan my repo"
	@python3 -c "import sys; sys.path.insert(0,'src'); from secure_anything.router import route; \
	r = route('$(Q)'); \
	print('capabilities:', [c.id for c in r.capabilities] or '-'); \
	print('knowledge:   ', [c.id for c in r.cards] or '-'); \
	[print('WARN', w) for w in r.warnings]; \
	print(r.gap) if r.gap else None"

# --- the public mirror (IP boundary) -----------------------------------------
publish-gate:        ## would exporting leak anything? path allowlist + content denylist
	python3 scripts/publish_gate.py

public-drift:        ## has the published tree fallen behind what we would export?
	python3 scripts/public_drift.py

public:              ## export the public subset and prove it passes its own gate
	python3 scripts/publish_public.py --force --verify

# --- the AgentGate organ ------------------------------------------------------
run:
	uvicorn secure_anything.organs.agentgate.main:app --reload --port 8099

worker:
	python -m secure_anything.organs.agentgate.worker

docker-up:
	docker compose up --build
