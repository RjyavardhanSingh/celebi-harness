.PHONY: install lint format test build clean docker-up docker-lint docker-test

install:
	uv sync

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	cd api && uv run pytest app/tests/ -v

build:
	python build.py

clean:
	rm -rf dist/ build/ *.spec

docker-up:
	docker compose -f docker-compose.dev.yml up

docker-lint:
	docker compose -f docker-compose.dev.yml --profile lint run celebi-lint

docker-test:
	docker compose -f docker-compose.dev.yml --profile test run celebi-test
