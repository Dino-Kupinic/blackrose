# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Versioning note:** GitHub Releases tagged `v0.5.x`–`v1.0.0` belong to the
> previous Ollama/chat gateway product. The TypeSafe decision-layer libraries
> start at **0.1.0** under `packages/python` and `packages/js`. Do not treat
> those older GitHub tags as library releases.

## [Unreleased]

### Changed

- Empty TypeSafe responses and missing expected checks now return `review`
  instead of silent `allow`.
- Score/Choice answers with missing confidence are treated like low confidence
  (`review`). Present Noul confidence below `min_confidence` also reviews.
- Score block/review cutoffs apply only to named checks in `score_thresholds`
  (`harm` still defaults to `harm_review_score` / `harm_block_score`). Custom
  Score checks no longer inherit the harm scale.
- Python and JavaScript model resolution both trim empty strings and fall back
  to `TYPESAFE_MODEL` / `TYPESAFE_DEFAULT_MODEL`.
- Numeric parsing rejects booleans and blank strings (they are not `0`).
- `Guard.close` / `AsyncGuard.aclose` are idempotent; checks after close raise
  `GuardClosedError`.
- Default harm questions allocate a new Score instance per battery so input and
  output checks do not share mutable question objects.

### Added

- Structured `CheckResult.triggers` and `codes` for programmatic branching
  (`missing_check`, `empty_response`, `noul_block`, `score_block`,
  `low_confidence`, …). `reasons` remains the human-readable messages.
- `Policy` validation (`PolicyConfigError`) for ordered, finite thresholds.
- Per-check `score_thresholds` / `scoreThresholds`.
- Typed errors: `BlackroseError`, `PolicyConfigError`, `GuardClosedError`,
  `TypeSafeRequestError` (SDK failures; fail closed — do not allow).
- Python exports `decide`, `extract_scores`, `HARM_SEVERITY`, `harm_severity`,
  and `client_config` on Guard / AsyncGuard (parity with JavaScript).
- Shared `packages/shared/decide-cases.json` consumed by both language test
  suites.
- `py.typed` for PEP 561, Python 3.10/3.12/3.13 CI matrix, test typecheck for
  the JS package, and lint/test before PyPI publish.
- `SECURITY.md` and `CONTRIBUTING.md`.

## [0.1.0] - 2026-09-21

### Added

- Python package `blackrose` (`packages/python`): sync `Guard` / async
  `AsyncGuard`, configurable `Policy`, and `decide` mapping TypeSafe System One
  answers onto `allow | review | block`.
- JavaScript/TypeScript package `blackrose` (`packages/js`): parity `Guard` /
  `Policy` / `decide` API with dual ESM/CJS builds.
- Default input/output question batteries (jailbreak, harm severity,
  needs_human) with conservative confidence handling (low confidence →
  `review`, never silent `allow`).
- Unit and SDK-shape contract tests (mocked; no live API key required).
- Optional live integration tests gated on `TYPESAFE_API_KEY`.
- VitePress docs covering getting started, policy, verdicts, Python/JS APIs,
  and integration examples.
- Dual-package CI (lint, typecheck, test, build) plus docs build and CodeQL on
  `main` / `develop`.
- Publish workflows for PyPI and npm (tag / manual).
- Root monorepo task scripts (`package.json`) for install, lint, test, and build.

### Changed

- Product scope: generation / gateway / Ollama chat UI removed; Blackrose is a
  library-only decision layer over TypeSafe.

### Removed

- OpenAI gateway and related application surface from earlier releases.
