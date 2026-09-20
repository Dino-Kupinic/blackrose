# Dual-package monorepo helpers (packages/python + packages/js)

test-python:
    cd packages/python && pip install -e ".[dev]" && pytest

test-js:
    cd packages/js && npm test

test: test-python test-js

lint-python:
    cd packages/python && ruff check src tests && ruff format --check src tests

lint-js:
    cd packages/js && npm run typecheck

lint: lint-python lint-js

format:
    cd packages/python && ruff format src tests

dev-docs:
    cd docs && bun run docs:dev
