.PHONY: install dev test lint run worker docker-up fmt check

install:
	python -m pip install -e ".[dev]"

# The canonical check command (what CI and `anyagent goal` should discover).
check: lint test

test:
	python -m pytest

lint:
	ruff check src tests

fmt:
	ruff format src tests

run:
	uvicorn agentgate.main:app --reload --port 8099

worker:
	python -m agentgate.worker

docker-up:
	docker compose up --build
