import { describe, expect, it } from "vitest";

const hasKey = Boolean(process.env.TYPESAFE_API_KEY?.trim());

describe.runIf(hasKey)("live TypeSafe", () => {
  it("safe input is not block", async () => {
    const { Guard } = await import("../src/index.js");
    await using guard = new Guard();
    const result = await guard.checkInput("What is the capital of Austria?");
    expect(["allow", "review"]).toContain(result.verdict);
    expect(Object.keys(result.scores).length).toBeGreaterThan(0);
  });
});

describe.runIf(!hasKey)("live TypeSafe (skipped)", () => {
  it("skips when TYPESAFE_API_KEY is unset", () => {
    expect(hasKey).toBe(false);
  });
});
