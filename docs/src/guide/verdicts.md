# Verdicts

Every `check_input` / `check_output` call returns a `CheckResult`:

| Field | Meaning |
| --- | --- |
| `verdict` | Application decision: `allow`, `review`, or `block` |
| `reasons` | Human-readable triggers that produced the verdict |
| `codes` | Stable qualified codes (`noul_block:jailbreak`, `missing_check:harm`, …) |
| `triggers` | Structured `{ code, check, message }` for the same events as `reasons` |
| `scores` | Named numeric signals extracted from TypeSafe answers |
| `raw` | Untyped snapshot of the underlying TypeSafe response |

Use `codes` / `triggers` in application logic. Keep `raw` for debugging; do not ship it (or the original prompt) to end users.

## Precedence

1. Any check that triggers **`block`** wins.
2. Else any **`review`** wins.
3. Else **`allow`**.

There is no soft allow:

- Score/Choice confidence below `min_confidence`, **or missing**, contributes `review`.
- Noul confidence, when present and below `min_confidence`, contributes `review`.
- An empty TypeSafe response contributes `review` (`empty_response`).
- An expected check name that is absent from the response contributes `review` (`missing_check`).

`Guard` always passes the question names it asked as expected checks.

## Fail closed on transport errors

If TypeSafe `system_one` raises (timeout, auth, HTTP error), Blackrose wraps it as `TypeSafeRequestError` and does **not** return `allow`. Catching that error and calling the LLM anyway is fail-open.

## What each verdict means in your app

| Verdict | Typical handling |
| --- | --- |
| `allow` | Proceed (call the LLM, or show the reply) |
| `review` | Queue for a human, escalate, or refuse with a soft message |
| `block` | Hard stop — do not generate / do not show the reply |

`needs_human` is a Noul check that defaults to **review-only** (it is not in `block_checks`). High jailbreak or high harm can still `block`.

## Default signals

One TypeSafe `system_one` call asks, in parallel:

| Check | Primitive | Role |
| --- | --- | --- |
| `jailbreak` | Noul | Probability the text tries to bypass instructions |
| `harm` | Score (0–3 rubric) | How much harm complying (or the reply) would cause |
| `needs_human` | Noul | Probability a human should review before proceeding |

Override cutoffs and question batteries via [`Policy`](/guide/policy).
