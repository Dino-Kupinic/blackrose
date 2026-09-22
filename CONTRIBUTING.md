# Contributing

## Setup

```bash
bun run install:all
cp .env.example .env   # only needed for live TypeSafe tests
```

Requires Python 3.10+ (dev pinned to 3.12), [uv](https://docs.astral.sh/uv/),
Bun 1.1+, and a TypeSafe API key for live tests.

## Checks

From the repo root:

```bash
bun run check          # lint + typecheck + test + build (both packages + docs)
```

Python and JavaScript `decide` tests share `packages/shared/decide-cases.json`.
If you change verdict mapping, add a case there so the two languages cannot
drift.

Optional live tests (not run in CI):

```bash
TYPESAFE_API_KEY=... uv run --directory packages/python pytest -m live
TYPESAFE_API_KEY=... bun --cwd packages/js run test:live
```

## Guardrail changes

Thresholds, missing-check behavior, and confidence handling are safety-critical.

- Empty/missing answers and missing expected checks must not become `allow`.
- Catching `TypeSafeRequestError` and continuing is fail-open; do not do that
  in examples.
- Prefer structured `CheckResult.codes` over parsing `reasons` strings.
- Keep Python (`packages/python`) and JavaScript (`packages/js`) APIs in parity.

## Releases

1. Add a `## [x.y.z]` section to `CHANGELOG.md`.
2. `bun run version:sync x.y.z` (fails if the changelog heading is missing).
3. Tag `v x.y.z` and push; publish workflows upload to PyPI and npm when
   environments/secrets are configured.
