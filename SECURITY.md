# Security Policy

## Reporting a vulnerability

Please report security issues privately through GitHub
[Security Advisories](https://github.com/Dino-Kupinic/blackrose/security/advisories/new)
for this repository. Do not open a public issue for a vulnerability in the
decision layer, default questions, or threshold handling.

Include:

- Affected package (`blackrose` Python and/or JavaScript) and version
- A minimal reproduction (mock TypeSafe client preferred)
- The verdict you observed versus the verdict you expected

## Fail-closed expectation

Blackrose is a guardrail. When a check cannot be completed, callers must **not**
proceed as if the result were `allow`:

- Empty or missing TypeSafe answers produce `review`, not `allow`.
- Expected checks that are absent from a response produce `review`.
- Low or missing Score/Choice confidence produces `review`.
- TypeSafe transport/API failures raise `TypeSafeRequestError`. Catching that
  error and continuing generation is fail-open.

Do not log `CheckResult.raw` (or the original prompt) to systems that end users
or third parties can read. Prefer `codes` / `triggers` for metrics and
`reasons` for operator-facing review queues.

## Supported versions

This library is in alpha (`0.1.x`). Security fixes land on `develop` and are
released from the latest `0.1.x` line.
