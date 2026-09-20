/** Application decision for a guardrail check. */
export type Verdict = "allow" | "review" | "block";

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
}

/** JSON-compatible state accepted by TypeSafe System One. */
export type GuardState =
  | string
  | number
  | boolean
  | null
  | GuardState[]
  | { [key: string]: GuardState };
