# Python API

Package: `packages/python` · module `blackrose`

Requires `typesafe-sdk>=0.7.0` (Python SDK; the JS package tracks `@typesafe-ai/sdk` at its latest major-compatible line — currently `^0.6.0`).

## Install

```bash
cd packages/python && uv sync --all-groups
# once published: uv add blackrose / pip install blackrose
```

## Guard / AsyncGuard

```python
from blackrose import AsyncGuard, Guard, Policy

with Guard(api_key=None, model="jev-latest", policy=Policy()) as guard:
    inbound = guard.check_input(user_message)
    outbound = guard.check_output(model_reply)

async with AsyncGuard() as guard:
    inbound = await guard.check_input({"message": user_message})
```

Constructor options:

| Argument | Purpose |
| --- | --- |
| `api_key` | Passed to TypeSafe; else `TYPESAFE_API_KEY` |
| `model` | Override; else `TYPESAFE_MODEL` → `TYPESAFE_DEFAULT_MODEL` → `jev-latest` |
| `policy` | Thresholds / questions |
| `client` | Inject a sync/async TypeSafe client or test double |

`close()` / `aclose()` dispose the owned SDK client. Context managers call them automatically.

## Exports

- `Guard`, `AsyncGuard`
- `Policy`, `default_input_questions`, `default_output_questions`
- `CheckResult`, `Verdict`
- `decide`, `extract_scores` (via `blackrose.decide`)

## Tests

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run pytest
# optional live calls:
TYPESAFE_API_KEY=... uv run pytest -m live
```
