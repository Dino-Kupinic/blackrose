# Changelog

## Unreleased

### Added

- Provider abstraction (#301): `Provider` / `AsyncProvider` (Python) and `Provider` (JS) separate Blackrose policy from the decision model.
- `TypeSafeProvider` (default, calibrated) and experimental `OpenAIDecisionsProvider` (uncalibrated; requires a `transport` until OpenAI publishes the Decisions API schema).
- Provider-neutral question types `Binary` / `Scale` / `Choice` (`binary()` / `scale()` / `choice()` in JS) and normalized `Answer` / `ProviderResult`.
- `CheckResult.provider` and `CheckResult.calibrated`.
- Per-provider thresholds via `Policy(provider_overrides=...)` / `providerOverrides`.
- `BLACKROSE_PROVIDER` and `OPENAI_DECISIONS_MODEL` environment variables.

### Changed

- Default question batteries use neutral types. Native TypeSafe questions in custom policies still work with the TypeSafe provider.
- `decide` / `extract_scores` no longer depend on TypeSafe response shapes directly.
- `Guard(client=...)` still works but is deprecated in favor of `Guard(provider=TypeSafeProvider(client=...))`.
