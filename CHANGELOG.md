# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Versioning note:** GitHub Releases tagged `v0.5.x`–`v1.0.0` belong to the
> previous Ollama/chat gateway product. The TypeSafe decision-layer libraries
> start at **0.1.0** under `packages/python` and `packages/js`. Do not treat
> those older GitHub tags as library releases.

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
