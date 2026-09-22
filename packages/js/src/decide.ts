/**
 * Map TypeSafe System One answers onto CheckResult verdicts.
 *
 * Mirrors packages/python/src/blackrose/decide.py.
 */

import type { Policy } from "./policy.js";
import type { CheckResult, Trigger, Verdict } from "./types.js";
import { qualifiedTrigger } from "./types.js";

const PRECEDENCE: readonly Verdict[] = ["block", "review", "allow"];

function hasField(obj: unknown, name: string): boolean {
  if (obj == null || typeof obj !== "object") return false;
  return name in (obj as Record<string, unknown>);
}

function attr(obj: unknown, name: string, fallback: unknown = undefined): unknown {
  if (!hasField(obj, name)) return fallback;
  return (obj as Record<string, unknown>)[name];
}

function asFloat(value: unknown): number | null {
  if (value == null || typeof value === "boolean") return null;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed === "") return null;
    const n = Number(trimmed);
    return Number.isFinite(n) ? n : null;
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }
  return null;
}

function isAnswerLike(value: unknown): boolean {
  if (value == null || typeof value !== "object") return false;
  return hasField(value, "noul") || hasField(value, "score") || hasField(value, "choice");
}

/** Normalize SDK response / mock into a name → answer mapping. */
export function answersView(raw: unknown): Record<string, unknown> {
  if (raw == null) return {};

  if (hasField(raw, "answers")) {
    const answers = attr(raw, "answers");
    if (answers != null && typeof answers === "object" && !Array.isArray(answers)) {
      return answers as Record<string, unknown>;
    }
    return {};
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
    const filtered: Record<string, unknown> = {};
    for (const [name, value] of Object.entries(raw as Record<string, unknown>)) {
      if (isAnswerLike(value)) filtered[name] = value;
    }
    return filtered;
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

export interface DecideOptions {
  /** Names that must appear in the response; missing names contribute `review`. */
  expectedChecks?: Iterable<string>;
}

function pushTrigger(
  triggered: Set<Verdict>,
  triggers: Trigger[],
  verdict: Verdict,
  trigger: Trigger,
): void {
  triggered.add(verdict);
  triggers.push(trigger);
}

function lowConfidenceTrigger(
  name: string,
  confidence: number | null,
  missing: boolean,
  minConfidence: number,
): Trigger {
  const message = missing
    ? `${name} confidence missing (< min_confidence ${minConfidence})`
    : `${name} confidence=${(confidence as number).toFixed(2)} < min_confidence (${minConfidence})`;
  return { code: "low_confidence", check: name, message };
}

/**
 * Apply policy thresholds to TypeSafe answers.
 *
 * Precedence: any `block` wins over `review`; otherwise `allow`.
 * Missing expected checks, empty responses, and low/missing Score/Choice
 * confidence contribute `review` (never silent `allow`).
 */
export function decide(raw: unknown, policy: Policy, options: DecideOptions = {}): CheckResult {
  const answers = answersView(raw);
  const scores = extractScores(raw);
  const triggers: Trigger[] = [];
  const triggered = new Set<Verdict>();

  const expected = options.expectedChecks != null ? Array.from(options.expectedChecks) : undefined;
  if (expected != null) {
    for (const name of expected) {
      if (!(name in answers)) {
        pushTrigger(triggered, triggers, "review", {
          code: "missing_check",
          check: name,
          message: `${name} missing from TypeSafe response`,
        });
      }
    }
    if (expected.length === 0 && Object.keys(answers).length === 0) {
      pushTrigger(triggered, triggers, "review", {
        code: "empty_response",
        check: null,
        message: "TypeSafe response contained no answers",
      });
    }
  } else if (Object.keys(answers).length === 0) {
    pushTrigger(triggered, triggers, "review", {
      code: "empty_response",
      check: null,
      message: "TypeSafe response contained no answers",
    });
  }

  for (const [name, answer] of Object.entries(answers)) {
    if (hasField(answer, "noul")) {
      const noul = asFloat(attr(answer, "noul"));
      if (noul != null) {
        if (noul >= policy.blockThreshold && policy.blockChecks.has(name)) {
          pushTrigger(triggered, triggers, "block", {
            code: "noul_block",
            check: name,
            message: `${name}=${noul.toFixed(2)} >= block_threshold (${policy.blockThreshold})`,
          });
        } else if (noul >= policy.reviewThreshold) {
          pushTrigger(triggered, triggers, "review", {
            code: "noul_review",
            check: name,
            message: `${name}=${noul.toFixed(2)} >= review_threshold (${policy.reviewThreshold})`,
          });
        }
      }
      if (hasField(answer, "confidence")) {
        const confidence = asFloat(attr(answer, "confidence"));
        if (confidence != null && confidence < policy.minConfidence) {
          pushTrigger(
            triggered,
            triggers,
            "review",
            lowConfidenceTrigger(name, confidence, false, policy.minConfidence),
          );
        }
      }
      continue;
    }

    if (hasField(answer, "score")) {
      const score = asFloat(attr(answer, "score"));
      const confidence = asFloat(attr(answer, "confidence"));
      const missingConfidence = !hasField(answer, "confidence") || confidence == null;
      if (missingConfidence || (confidence != null && confidence < policy.minConfidence)) {
        pushTrigger(
          triggered,
          triggers,
          "review",
          lowConfidenceTrigger(name, confidence, missingConfidence, policy.minConfidence),
        );
      }
      const cutoffs = policy.scoreCutoffs(name);
      if (score != null && cutoffs != null) {
        if (score >= cutoffs.block) {
          pushTrigger(triggered, triggers, "block", {
            code: "score_block",
            check: name,
            message: `${name}=${score.toFixed(2)} >= score_block (${cutoffs.block})`,
          });
        } else if (score >= cutoffs.review) {
          pushTrigger(triggered, triggers, "review", {
            code: "score_review",
            check: name,
            message: `${name}=${score.toFixed(2)} >= score_review (${cutoffs.review})`,
          });
        }
      }
      continue;
    }

    if (hasField(answer, "choice") || hasField(answer, "confidence")) {
      const confidence = asFloat(attr(answer, "confidence"));
      const missingConfidence = !hasField(answer, "confidence") || confidence == null;
      if (missingConfidence || (confidence != null && confidence < policy.minConfidence)) {
        pushTrigger(
          triggered,
          triggers,
          "review",
          lowConfidenceTrigger(name, confidence, missingConfidence, policy.minConfidence),
        );
      }
    }
  }

  const verdict: Verdict = PRECEDENCE.find((v) => triggered.has(v)) ?? "allow";
  return {
    verdict,
    reasons: triggers.map((t) => t.message),
    scores,
    raw,
    triggers,
    codes: triggers.map(qualifiedTrigger),
  };
}
