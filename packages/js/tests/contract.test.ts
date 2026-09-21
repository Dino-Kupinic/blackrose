import { describe, expect, it } from "vitest";

import { decide, extractScores } from "../src/decide.js";
import { Policy } from "../src/policy.js";

/** Shape similar to @typesafe-ai/sdk SystemOneResult. */
function sdkAnswersPayload() {
  return {
    answers: {
      jailbreak: { type: "noul", noul: 0.12, confidence: null },
      harm: { type: "score", score: 0.4, confidence: 0.88 },
      needs_human: { type: "noul", noul: 0.08 },
    },
    model: "jev-latest",
    usage: { input_tokens: 42, output_tokens: 0 },
  };
}

describe("SDK contract shapes", () => {
  it("decides allow on answers-wrapper payloads", () => {
    const raw = sdkAnswersPayload();
    const result = decide(raw, new Policy());
    expect(result.verdict).toBe("allow");
    expect(result.scores).toEqual({ jailbreak: 0.12, harm: 0.4, needs_human: 0.08 });
    expect(result.raw).toBe(raw);
  });

  it("blocks jailbreak on bucketed nouls/scores shape", () => {
    const raw = {
      nouls: { jailbreak: { noul: 0.91 } },
      scores: { harm: { score: 0.5, confidence: 0.9 } },
      choices: {},
    };
    expect(decide(raw, new Policy()).verdict).toBe("block");
    expect(extractScores(raw).jailbreak).toBe(0.91);
  });

  it("reviews low-confidence choice answers", () => {
    const raw = {
      answers: {
        topic: {
          type: "choice",
          choice: "billing",
          confidence: 0.2,
          probabilities: { billing: 0.55, other: 0.45 },
        },
      },
    };
    const result = decide(raw, new Policy());
    expect(result.verdict).toBe("review");
    expect(result.scores.topic).toBe(0.55);
  });
});
