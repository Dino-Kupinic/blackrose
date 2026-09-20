import { describe, expect, it } from "vitest";

import { decide, extractScores } from "../src/decide.js";
import { Policy } from "../src/policy.js";

describe("decide", () => {
  it("allows when all signals are low", () => {
    const raw = {
      jailbreak: { noul: 0.02 },
      harm: { score: 0.1, confidence: 0.9 },
      needs_human: { noul: 0.05 },
    };
    const result = decide(raw, new Policy());
    expect(result.verdict).toBe("allow");
    expect(result.reasons).toEqual([]);
    expect(result.scores.jailbreak).toBe(0.02);
    expect(result.scores.harm).toBe(0.1);
  });

  it("reviews on mid noul", () => {
    const raw = {
      jailbreak: { noul: 0.4 },
      harm: { score: 0.2, confidence: 0.9 },
      needs_human: { noul: 0.1 },
    };
    const result = decide(raw, new Policy());
    expect(result.verdict).toBe("review");
    expect(result.reasons.some((r) => r.includes("jailbreak"))).toBe(true);
  });

  it("blocks on high jailbreak", () => {
    const raw = {
      jailbreak: { noul: 0.95 },
      harm: { score: 0.5, confidence: 0.9 },
      needs_human: { noul: 0.2 },
    };
    expect(decide(raw, new Policy()).verdict).toBe("block");
  });

  it("treats high needs_human as review, not block", () => {
    const raw = {
      jailbreak: { noul: 0.05 },
      harm: { score: 0.2, confidence: 0.9 },
      needs_human: { noul: 0.92 },
    };
    const result = decide(raw, new Policy());
    expect(result.verdict).toBe("review");
    expect(result.reasons.some((r) => r.includes("needs_human"))).toBe(true);
  });

  it("blocks on high harm score", () => {
    const raw = {
      jailbreak: { noul: 0.05 },
      harm: { score: 2.4, confidence: 0.85 },
      needs_human: { noul: 0.1 },
    };
    expect(decide(raw, new Policy()).verdict).toBe("block");
  });

  it("forces review on low confidence instead of allow", () => {
    const raw = {
      jailbreak: { noul: 0.05 },
      harm: { score: 0.3, confidence: 0.2 },
      needs_human: { noul: 0.05 },
    };
    const result = decide(raw, new Policy());
    expect(result.verdict).toBe("review");
    expect(result.reasons.some((r) => r.includes("confidence"))).toBe(true);
  });

  it("does not downgrade block when confidence is low", () => {
    const raw = {
      jailbreak: { noul: 0.95 },
      harm: { score: 0.3, confidence: 0.1 },
      needs_human: { noul: 0.05 },
    };
    expect(decide(raw, new Policy()).verdict).toBe("block");
  });

  it("respects custom thresholds", () => {
    const policy = new Policy({ reviewThreshold: 0.2, blockThreshold: 0.5 });
    const raw = {
      jailbreak: { noul: 0.55 },
      harm: { score: 0.0, confidence: 0.99 },
      needs_human: { noul: 0.0 },
    };
    expect(decide(raw, policy).verdict).toBe("block");
  });

  it("extracts scores from nested SDK-shaped responses", () => {
    const raw = {
      nouls: { jailbreak: { noul: 0.8 } },
      scores: { harm: { score: 1.5, confidence: 0.7 } },
      choices: {},
    };
    expect(extractScores(raw)).toEqual({ jailbreak: 0.8, harm: 1.5 });
  });

  it("extracts scores from answers wrapper", () => {
    const raw = {
      answers: {
        jailbreak: { type: "noul", noul: 0.12 },
        harm: { type: "score", score: 0.4, confidence: 0.88 },
      },
      model: "jev-latest",
      usage: { input_tokens: 10, output_tokens: 0 },
    };
    expect(extractScores(raw)).toEqual({ jailbreak: 0.12, harm: 0.4 });
    expect(decide(raw, new Policy()).verdict).toBe("allow");
  });
});
