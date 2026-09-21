import { describe, expect, it, vi } from "vitest";

import { Guard, type SystemOneClient } from "../src/index.js";

const SAFE = {
  jailbreak: { noul: 0.01 },
  harm: { score: 0.1, confidence: 0.9 },
  needs_human: { noul: 0.01 },
};

describe("Guard.close", () => {
  it("does not close an injected client", async () => {
    const close = vi.fn(async () => undefined);
    const client: SystemOneClient = {
      async systemOne() {
        return SAFE;
      },
      close,
    };

    const guard = new Guard({ client });
    await guard.checkInput("hi");
    await guard.close();
    await guard.close();
    expect(close).not.toHaveBeenCalled();
  });

  it("supports Symbol.asyncDispose", async () => {
    const client: SystemOneClient = {
      async systemOne() {
        return SAFE;
      },
    };
    {
      await using guard = new Guard({ client });
      await guard.checkInput("hi");
    }
  });
});
