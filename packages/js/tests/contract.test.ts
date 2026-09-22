import { describe, expect, it } from "vitest";

import { decide, extractScores } from "../src/decide.js";
import { Policy } from "../src/policy.js";

describe("SDK contract shapes", () => {
  it("blocks jailbreak on attribute-style bucketed objects", () => {
    const raw = {
      nouls: { jailbreak: { noul: 0.91 } },
      scores: { harm: { score: 0.5, confidence: 0.9 } },
      choices: {},
    };
    const result = decide(raw, new Policy());
    expect(result.verdict).toBe("block");
    expect(extractScores(raw).jailbreak).toBe(0.91);
    expect(result.codes).toContain("noul_block:jailbreak");
  });
});
