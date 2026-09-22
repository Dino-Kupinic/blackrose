# Python API

Package: `packages/python` · module `blackrose`

Requires `typesafe-sdk>=0.7.0` (Python SDK; the JS package tracks `@typesafe-ai/sdk` at its latest major-compatible line — currently `^0.6.0`).

## Install

```bash
uv add blackrose
# from this repo: cd packages/python && uv sync --all-groups
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
| `model` | Override; else `TYPESAFE_MODEL` → `TYPESAFE_DEFAULT_MODEL` → `jev-latest` (blank strings are ignored) |
| `policy` | Thresholds / questions |
| `client` | Inject a sync/async TypeSafe client or test double |
| `client_config` | Extra kwargs for the default TypeSafe client (timeouts, base URL, …) |

`close()` / `aclose()` dispose the owned SDK client and are safe to call more than once. Checks after close raise `GuardClosedError`. Context managers call them automatically.

TypeSafe call failures raise `TypeSafeRequestError` — fail closed; do not treat that as `allow`.

## Exports

- `Guard`, `AsyncGuard`
- `Policy`, `PolicyConfigError`, `ScoreThresholds`
- `default_input_questions`, `default_output_questions`, `harm_severity`, `HARM_SEVERITY`
- `CheckResult`, `Trigger`, `Verdict`
- `decide`, `extract_scores`, `answers_view`
- `BlackroseError`, `GuardClosedError`, `TypeSafeRequestError`

## Tests

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run pytest -m "not live"
# optional live calls:
TYPESAFE_API_KEY=... uv run pytest -m live
```
