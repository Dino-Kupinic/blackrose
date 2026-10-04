/**
 * Map normalized provider answers onto CheckResult verdicts.
 *
 * Vendor-neutral: reads only `Answer`s (or shapes `normalizeAnswers` accepts).
 * Mirrors packages/python/src/blackrose/decide.py.
 */

import { type Answer, isProviderResult, normalizeAnswers } from "./answers.js";
import type { Policy } from "./policy.js";
import type { CheckResult, Verdict } from "./types.js";

export { answersView } from "./answers.js";

const PRECEDENCE: readonly Verdict[] = ["block", "review", "allow"];

function scoreOf(answer: Answer): number | null {
  if (answer.kind === "choice") {
    // Only report a choice when the provider gave the winning option's probability.
    const label = answer.choice;
    if (label == null || answer.probabilities?.[label] == null) return null;
  }
  return answer.value;
}

function scoresOf(answers: Record<string, Answer>): Record<string, number> {
  const scores: Record<string, number> = {};
  for (const [name, answer] of Object.entries(answers)) {
    const value = scoreOf(answer);
    if (value != null) scores[name] = value;
  }
  return scores;
}

/** Pull named numeric signals from a provider result, response or mock dict. */
export function extractScores(raw: unknown): Record<string, number> {
  return scoresOf(normalizeAnswers(raw));
}

export interface DecideOptions {
  /** Name of the provider that answered, copied onto the result. */
  provider?: string;
  /** Whether that provider claims outcome-verified calibration. */
  calibrated?: boolean;
}

/**
 * Apply policy thresholds to provider answers.
 *
 * Precedence: any `block` wins over `review`; otherwise `allow`.
 * Low scale/choice confidence always contributes `review`.
 */
export function decide(raw: unknown, policy: Policy, options: DecideOptions = {}): CheckResult {
  const answers = normalizeAnswers(raw);
  const scores = scoresOf(answers);
  const reasons: string[] = [];
  const triggered = new Set<Verdict>();

  for (const [name, answer] of Object.entries(answers)) {
    if (answer.kind === "binary") {
      const p = answer.value;
      if (p >= policy.blockThreshold && policy.blockChecks.has(name)) {
        triggered.add("block");
        reasons.push(`${name}=${p.toFixed(2)} >= block_threshold (${policy.blockThreshold})`);
      } else if (p >= policy.reviewThreshold) {
        triggered.add("review");
        reasons.push(`${name}=${p.toFixed(2)} >= review_threshold (${policy.reviewThreshold})`);
      }
      continue;
    }

    // Scale and choice: low confidence → review; never silent allow on uncertainty
    const confidence = answer.confidence;
    if (confidence != null && confidence < policy.minConfidence) {
      triggered.add("review");
      reasons.push(
        `${name} confidence=${confidence.toFixed(2)} < min_confidence (${policy.minConfidence})`,
      );
    }

    if (answer.kind === "scale") {
      const score = answer.value;
      if (score >= policy.harmBlockScore) {
        triggered.add("block");
        reasons.push(`${name}=${score.toFixed(2)} >= harm_block_score (${policy.harmBlockScore})`);
      } else if (score >= policy.harmReviewScore) {
        triggered.add("review");
        reasons.push(
          `${name}=${score.toFixed(2)} >= harm_review_score (${policy.harmReviewScore})`,
        );
      }
    }
  }

  const verdict: Verdict = PRECEDENCE.find((v) => triggered.has(v)) ?? "allow";

  return {
    verdict,
    reasons,
    scores,
    raw: isProviderResult(raw) ? raw.raw : raw,
    provider: options.provider,
    calibrated: options.calibrated,
  };
}
