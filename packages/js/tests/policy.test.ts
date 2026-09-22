import { describe, expect, it } from "vitest";

import { PolicyConfigError } from "../src/errors.js";
import { defaultInputQuestions, harmSeverity, Policy, type ScoreThresholds } from "../src/index.js";

describe("Policy", () => {
  it("rejects reversed noul thresholds", () => {
    expect(() => new Policy({ reviewThreshold: 0.9, blockThreshold: 0.2 })).toThrow(
      PolicyConfigError,
    );
  });

  it("rejects confidence outside 0–1", () => {
    expect(() => new Policy({ minConfidence: 1.5 })).toThrow(PolicyConfigError);
  });

  it("rejects non-finite harm cutoffs", () => {
    expect(() => new Policy({ harmBlockScore: Number.POSITIVE_INFINITY })).toThrow(
      PolicyConfigError,
    );
  });

  it("rejects reversed per-check score thresholds", () => {
    const scoreThresholds: Record<string, ScoreThresholds> = {
      toxicity: { review: 2.0, block: 0.5 },
    };
    expect(() => new Policy({ scoreThresholds })).toThrow(PolicyConfigError);
  });

  it("rejects invalid sides", () => {
    expect(() => new Policy().questionsFor("sideways" as "input")).toThrow(/side must be/);
  });

  it("does not share harm severity instances across batteries", () => {
    const a = harmSeverity();
    const b = harmSeverity();
    expect(a).not.toBe(b);
    expect(defaultInputQuestions().harm).not.toBe(a);
  });

  it("uses harm knobs as default score cutoffs", () => {
    const policy = new Policy({ harmReviewScore: 0.5, harmBlockScore: 1.5 });
    expect(policy.scoreCutoffs("harm")).toEqual({ review: 0.5, block: 1.5 });
    expect(policy.scoreCutoffs("toxicity")).toBeUndefined();
  });
});
