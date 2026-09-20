/**
 * Map TypeSafe System One answers onto CheckResult verdicts.
 *
 * Mirrors packages/python/src/blackrose/decide.py.
 */

import type { Policy } from "./policy.js";
import type { CheckResult, Verdict } from "./types.js";

const PRECEDENCE: readonly Verdict[] = ["block", "review", "allow"];

function attr(obj: unknown, name: string, fallback: unknown = undefined): unknown {
  if (obj == null) return fallback;
  if (typeof obj === "object" && name in (obj as Record<string, unknown>)) {
    return (obj as Record<string, unknown>)[name];
  }
  return fallback;
}

function asFloat(value: unknown): number | null {
  if (value == null) return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

/** Normalize SDK response / mock into a name → answer mapping. */
export function answersView(raw: unknown): Record<string, unknown> {
  if (raw == null) return {};

  const answers = attr(raw, "answers");
  if (answers != null && typeof answers === "object" && !Array.isArray(answers)) {
    return answers as Record<string, unknown>;
  }

  const combined: Record<string, unknown> = {};
  for (const bucket of ["nouls", "scores", "choices"] as const) {
    const group = attr(raw, bucket);
    if (group != null && typeof group === "object" && !Array.isArray(group)) {
      Object.assign(combined, group);
    }
  }
  if (Object.keys(combined).length > 0) return combined;

  if (typeof raw === "object" && !Array.isArray(raw)) {
    // Flat mock: { jailbreak: { noul: 0.9 }, harm: { score: 2.1, confidence: 0.8 } }
    return raw as Record<string, unknown>;
  }
  return {};
}

/** Pull named numeric signals from a TypeSafe response or mock dict. */
export function extractScores(raw: unknown): Record<string, number> {
  const scores: Record<string, number> = {};
  for (const [name, answer] of Object.entries(answersView(raw))) {
    const noul = asFloat(attr(answer, "noul"));
    if (noul != null) {
      scores[name] = noul;
      continue;
    }
    const score = asFloat(attr(answer, "score"));
    if (score != null) {
      scores[name] = score;
      continue;
    }
    const choice = attr(answer, "choice");
    const probs = attr(answer, "probabilities");
    if (choice != null && probs != null && typeof probs === "object" && !Array.isArray(probs)) {
      const p = asFloat((probs as Record<string, unknown>)[String(choice)]);
      if (p != null) scores[name] = p;
    }
  }
  return scores;
}

/**
 * Apply policy thresholds to TypeSafe answers.
 *
 * Precedence: any `block` wins over `review`; otherwise `allow`.
 * Low Score/Choice confidence always contributes `review`.
 */
export function decide(raw: unknown, policy: Policy): CheckResult {
  const answers = answersView(raw);
  const scores = extractScores(raw);
  const reasons: string[] = [];
  const triggered = new Set<Verdict>();

  for (const [name, answer] of Object.entries(answers)) {
    const noul = asFloat(attr(answer, "noul"));
    if (noul != null) {
      if (noul >= policy.blockThreshold && policy.blockChecks.has(name)) {
        triggered.add("block");
        reasons.push(`${name}=${noul.toFixed(2)} >= block_threshold (${policy.blockThreshold})`);
      } else if (noul >= policy.reviewThreshold) {
        triggered.add("review");
        reasons.push(`${name}=${noul.toFixed(2)} >= review_threshold (${policy.reviewThreshold})`);
      }
      continue;
    }

    const score = asFloat(attr(answer, "score"));
    let confidence = asFloat(attr(answer, "confidence"));
    if (score != null) {
      if (confidence != null && confidence < policy.minConfidence) {
        triggered.add("review");
        reasons.push(
          `${name} confidence=${confidence.toFixed(2)} < min_confidence (${policy.minConfidence})`,
        );
      }
      if (score >= policy.harmBlockScore) {
        triggered.add("block");
        reasons.push(`${name}=${score.toFixed(2)} >= harm_block_score (${policy.harmBlockScore})`);
      } else if (score >= policy.harmReviewScore) {
        triggered.add("review");
        reasons.push(
          `${name}=${score.toFixed(2)} >= harm_review_score (${policy.harmReviewScore})`,
        );
      }
      continue;
    }

    // Choice answers: low confidence → review; never silent allow on uncertainty
    confidence = asFloat(attr(answer, "confidence"));
    if (confidence != null && confidence < policy.minConfidence) {
      triggered.add("review");
      reasons.push(
        `${name} confidence=${confidence.toFixed(2)} < min_confidence (${policy.minConfidence})`,
      );
    }
  }

  const verdict: Verdict = PRECEDENCE.find((v) => triggered.has(v)) ?? "allow";

  return { verdict, reasons, scores, raw };
}
