/** Application decision for a guardrail check. */
export type Verdict = "allow" | "review" | "block";

/**
 * Structured reason a check contributed to the verdict.
 *
 * `code` is stable for programmatic branching (e.g. `noul_block`).
 * `message` is the human-readable string also stored on `CheckResult.reasons`.
 */
export interface Trigger {
  code: string;
  check: string | null;
  message: string;
}

/**
 * Outcome of a single input or output guardrail check.
 */
export interface CheckResult {
  /** Application decision — allow, review, or block. */
  verdict: Verdict;
  /** Human-readable triggers that produced the verdict. */
  reasons: string[];
  /** Named probabilities / scores from TypeSafe answers. */
  scores: Record<string, number>;
  /** Untyped snapshot of the underlying TypeSafe response (or mock). */
  raw: unknown;
  /** Structured codes for the same events as `reasons`. */
  triggers: Trigger[];
  /** Qualified trigger codes (`code` or `code:check`). */
  codes: string[];
}

/** JSON-compatible state accepted by TypeSafe System One. */
export type GuardState =
  | string
  | number
  | boolean
  | null
  | GuardState[]
  | { [key: string]: GuardState };

export function qualifiedTrigger(trigger: Trigger): string {
  return trigger.check ? `${trigger.code}:${trigger.check}` : trigger.code;
}
