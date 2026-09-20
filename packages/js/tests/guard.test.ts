import { noul } from "@typesafe-ai/sdk";
import { describe, expect, it } from "vitest";

import {
  defaultInputQuestions,
  defaultOutputQuestions,
  Guard,
  Policy,
  type SystemOneClient,
} from "../src/index.js";

type Call = {
  state: unknown;
  questions: Record<string, unknown>;
  model?: string;
};

class FakeClient implements SystemOneClient {
  calls: Call[] = [];

  constructor(private readonly response: unknown) {}

  async systemOne(request: {
    state: unknown;
    questions: Record<string, unknown>;
    model?: string;
  }): Promise<unknown> {
    this.calls.push(request);
    return this.response;
  }
}

const SAFE = {
  jailbreak: { noul: 0.02 },
  harm: { score: 0.1, confidence: 0.9 },
  needs_human: { noul: 0.05 },
};

const JAILBREAK = {
  jailbreak: { noul: 0.98 },
  harm: { score: 1.1, confidence: 0.9 },
  needs_human: { noul: 0.4 },
};

describe("Guard", () => {
  it("checkInput allows safe content and uses input questions", async () => {
    const client = new FakeClient(SAFE);
    const guard = new Guard({ client, model: "jev-latest" });
    const result = await guard.checkInput("Tell me about Vienna");
    expect(result.verdict).toBe("allow");
    expect(client.calls).toHaveLength(1);
    expect(client.calls[0]?.state).toBe("Tell me about Vienna");
    expect(client.calls[0]?.model).toBe("jev-latest");
    expect(Object.keys(client.calls[0]?.questions ?? {}).sort()).toEqual(
      Object.keys(defaultInputQuestions()).sort(),
    );
  });

  it("checkOutput blocks jailbroken replies and uses output questions", async () => {
    const client = new FakeClient(JAILBREAK);
    const guard = new Guard({ client });
    const result = await guard.checkOutput("Sure, I'll ignore all rules now.");
    expect(result.verdict).toBe("block");
    expect(Object.keys(client.calls[0]?.questions ?? {}).sort()).toEqual(
      Object.keys(defaultOutputQuestions()).sort(),
    );
  });

  it("uses custom policy questions", async () => {
    const custom = { only: noul("Is this spam?") };
    const policy = new Policy({
      inputQuestions: custom,
      outputQuestions: custom,
    });
    const client = new FakeClient({ only: { noul: 0.01 } });
    const guard = new Guard({ client, policy });
    await guard.checkInput("hi");
    expect(Object.keys(client.calls[0]?.questions ?? {})).toEqual(["only"]);
  });

  it("checkInput accepts structured state", async () => {
    const client = new FakeClient(SAFE);
    const guard = new Guard({ client, model: "jev-latest" });
    const result = await guard.checkInput({ message: "hello" });
    expect(result.verdict).toBe("allow");
    expect(client.calls[0]?.state).toEqual({ message: "hello" });
  });

  it("checkOutput reviews low-confidence harm", async () => {
    const uncertain = {
      jailbreak: { noul: 0.05 },
      harm: { score: 0.4, confidence: 0.15 },
      needs_human: { noul: 0.05 },
    };
    const client = new FakeClient(uncertain);
    const guard = new Guard({ client });
    const result = await guard.checkOutput("maybe?");
    expect(result.verdict).toBe("review");
  });
});
