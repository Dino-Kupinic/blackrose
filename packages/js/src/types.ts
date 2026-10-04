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
  /** Named probabilities / scores from the provider's answers. */
  scores: Record<string, number>;
  /** Untyped snapshot of the underlying provider response (or mock). */
  raw: unknown;
  /** Name of the provider that answered (`typesafe`, `openai`, …). */
  provider?: string;
  /**
   * Whether that provider claims outcome-verified calibration. `false` means
   * probabilities are model-reported estimates.
   */
  calibrated?: boolean;
}

/** JSON-compatible state passed to the provider. */
export type GuardState =
  | string
  | number
  | boolean
  | null
  | GuardState[]
  | { [key: string]: GuardState };
