# Verdicts

Every `check_input` / `check_output` call returns a `CheckResult`:

| Field | Meaning |
| --- | --- |
| `verdict` | Application decision: `allow`, `review`, or `block` |
| `reasons` | Human-readable triggers that produced the verdict |
| `scores` | Named numeric signals extracted from TypeSafe answers |
| `raw` | Untyped snapshot of the underlying TypeSafe response |

## Precedence

1. Any check that triggers **`block`** wins.
2. Else any **`review`** wins.
3. Else **`allow`**.

There is no soft allow: if Score/Choice confidence is below `min_confidence`, Blackrose contributes `review` even when the numeric score itself looks safe.

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
