import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { answersView, decide, extractScores } from "../src/decide.js";
import { Policy, type PolicyOptions } from "../src/policy.js";

const fixturePath = join(dirname(fileURLToPath(import.meta.url)), "../../shared/decide-cases.json");

interface DecideCase {
  name: string;
  raw: unknown;
  policy?: Record<string, unknown>;
  expected_checks?: string[];
  verdict: string;
  codes: string[];
}

const cases = JSON.parse(readFileSync(fixturePath, "utf8")) as DecideCase[];

function policyFromSpec(spec?: Record<string, unknown>): Policy {
  if (spec == null) return new Policy();
  const options: PolicyOptions = {};
  if (spec.review_threshold != null) options.reviewThreshold = spec.review_threshold as number;
  if (spec.block_threshold != null) options.blockThreshold = spec.block_threshold as number;
  if (spec.harm_review_score != null) options.harmReviewScore = spec.harm_review_score as number;
  if (spec.harm_block_score != null) options.harmBlockScore = spec.harm_block_score as number;
  if (spec.min_confidence != null) options.minConfidence = spec.min_confidence as number;
  if (spec.block_checks != null) options.blockChecks = spec.block_checks as string[];
  if (spec.score_thresholds != null) {
    options.scoreThresholds = spec.score_thresholds as PolicyOptions["scoreThresholds"];
  }
  return new Policy(options);
}

describe("decide (shared fixtures)", () => {
  for (const testCase of cases) {
    it(testCase.name, () => {
      const result = decide(testCase.raw, policyFromSpec(testCase.policy), {
        expectedChecks: testCase.expected_checks,
      });
      expect(result.verdict, testCase.name).toBe(testCase.verdict);
      expect(result.codes, testCase.name).toEqual(testCase.codes);
      expect(result.reasons).toEqual(result.triggers.map((t) => t.message));
    });
  }
});

describe("decide extras", () => {
  it("allows when all signals are low and records scores", () => {
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

  it("answersView ignores non-answer keys", () => {
    const raw = {
      model: "jev-latest",
      usage: { input_tokens: 3 },
      jailbreak: { noul: 0.2 },
    };
    expect(Object.keys(answersView(raw))).toEqual(["jailbreak"]);
  });

  it("does not treat booleans or blank strings as scores", () => {
    expect(extractScores({ flag: { noul: true } })).toEqual({});
    expect(extractScores({ harm: { score: "" } })).toEqual({});
    expect(extractScores({ harm: { score: "  " } })).toEqual({});
  });
});
