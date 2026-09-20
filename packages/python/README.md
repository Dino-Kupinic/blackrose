# Blackrose (Python)

Open-source TypeSafe decision layer: `check_input` / `check_output` → `allow | review | block`.

See the repository root [README](../../README.md) for install and quickstart.

## Develop

```bash
cd packages/python
uv sync --all-groups
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
```
