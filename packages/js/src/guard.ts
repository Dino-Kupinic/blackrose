/**
 * Guard client wrapping the official TypeSafe JavaScript SDK.
 *
 * Mirrors packages/python/src/blackrose/guard.py (async surface).
 */

import {
  type Question,
  type SystemOneResult,
  TypeSafeClient,
  type TypeSafeClientConfig,
} from "@typesafe-ai/sdk";

import { decide } from "./decide.js";
import { Policy, type PolicySide } from "./policy.js";
import type { CheckResult, GuardState } from "./types.js";

function resolveModel(model?: string | null): string {
  if (model != null && model.trim() !== "") return model.trim();
  for (const env of ["TYPESAFE_MODEL", "TYPESAFE_DEFAULT_MODEL"] as const) {
    const value = process.env[env]?.trim();
    if (value) return value;
  }
  return "jev-latest";
}

/** Minimal System One client surface (real SDK or test double). */
export interface SystemOneClient {
  systemOne(request: {
    state: GuardState;
    questions: Record<string, Question>;
    model?: string;
  }): Promise<SystemOneResult<Record<string, Question>> | unknown>;
  /** Optional dispose hook (real TypeSafe clients may expose `close`). */
  close?: () => void | Promise<void>;
}

export interface GuardOptions {
  apiKey?: string;
  model?: string;
  policy?: Policy;
  /** Inject a mock or custom client; defaults to `TypeSafeClient`. */
  client?: SystemOneClient;
  /** Extra TypeSafe client config when constructing the default client. */
  clientConfig?: Omit<TypeSafeClientConfig, "apiKey" | "defaultModel">;
}

/**
 * Decision layer over TypeSafe `systemOne`.
 *
 * ```ts
 * const guard = new Guard();
 * try {
 *   const result = await guard.checkInput("Ignore previous instructions…");
 *   if (result.verdict === "allow") { … }
 * } finally {
 *   await guard.close();
 * }
 * ```
 */
export class Guard {
  readonly policy: Policy;
  private readonly model: string;
  private readonly client: SystemOneClient;
  private readonly ownsClient: boolean;
  private closed = false;

  constructor(options: GuardOptions = {}) {
    this.policy = options.policy ?? new Policy();
    this.model = resolveModel(options.model);
    this.ownsClient = options.client == null;
    this.client =
      options.client ??
      new TypeSafeClient({
        ...options.clientConfig,
        apiKey: options.apiKey,
        defaultModel: this.model,
      });
  }

  checkInput(state: GuardState): Promise<CheckResult> {
    return this.check(state, "input");
  }

  checkOutput(state: GuardState): Promise<CheckResult> {
    return this.check(state, "output");
  }

  /**
   * Dispose the owned TypeSafe client (no-op when a custom `client` was injected).
   * Safe to call more than once.
   */
  async close(): Promise<void> {
    if (this.closed) return;
    this.closed = true;
    if (!this.ownsClient) return;
    const closer = this.client.close;
    if (typeof closer === "function") {
      await closer.call(this.client);
    }
  }

  async [Symbol.asyncDispose](): Promise<void> {
    await this.close();
  }

  private async check(state: GuardState, side: PolicySide): Promise<CheckResult> {
    const questions = this.policy.questionsFor(side);
    const response = await this.client.systemOne({
      state,
      questions,
      model: this.model,
    });
    return decide(response, this.policy);
  }
}
