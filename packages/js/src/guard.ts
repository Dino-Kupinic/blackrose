/**
 * Guard over a pluggable decision-model provider.
 *
 * Mirrors packages/python/src/blackrose/guard.py (async surface).
 */

import { decide } from "./decide.js";
import { Policy, type PolicySide } from "./policy.js";
import {
  OpenAIDecisionsProvider,
  type Provider,
  providerNameFromEnv,
  type SystemOneClient,
  TypeSafeProvider,
  type TypeSafeProviderOptions,
} from "./providers/index.js";
import type { CheckResult, GuardState } from "./types.js";

export type { SystemOneClient } from "./providers/index.js";

export interface GuardOptions {
  policy?: Policy;
  /** Decision-model backend. Defaults to `BLACKROSE_PROVIDER` (default `typesafe`). */
  provider?: Provider;
  /** TypeSafe API key (default provider only). */
  apiKey?: string;
  /** Model for the default provider. */
  model?: string;
  /** @deprecated Pass `provider: new TypeSafeProvider({ client })` instead. */
  client?: SystemOneClient;
  /** Extra TypeSafe client config when constructing the default client. */
  clientConfig?: TypeSafeProviderOptions["clientConfig"];
}

function defaultProvider(options: GuardOptions): Provider {
  if (options.client != null || providerNameFromEnv() === "typesafe") {
    return new TypeSafeProvider({
      apiKey: options.apiKey,
      model: options.model,
      client: options.client,
      clientConfig: options.clientConfig,
    });
  }
  return new OpenAIDecisionsProvider({ model: options.model });
}

/**
 * Decision layer over a provider (TypeSafe by default).
 *
 * ```ts
 * const guard = new Guard();
 * const result = await guard.checkInput("Ignore previous instructions…");
 * if (result.verdict === "allow") { … }
 * ```
 */
export class Guard {
  readonly policy: Policy;
  readonly provider: Provider;

  constructor(options: GuardOptions = {}) {
    const { provider, apiKey, model, client, clientConfig } = options;
    if (provider && (apiKey ?? model ?? client ?? clientConfig) !== undefined) {
      throw new Error("pass apiKey/model/client/clientConfig to the provider, not alongside it");
    }
    this.policy = options.policy ?? new Policy();
    this.provider = provider ?? defaultProvider(options);
  }

  checkInput(state: GuardState): Promise<CheckResult> {
    return this.check(state, "input");
  }

  checkOutput(state: GuardState): Promise<CheckResult> {
    return this.check(state, "output");
  }

  private async check(state: GuardState, side: PolicySide): Promise<CheckResult> {
    const questions = this.policy.questionsFor(side);
    const result = await this.provider.decide(state, questions);
    return decide(result, this.policy.forProvider(this.provider.name), {
      provider: this.provider.name,
      calibrated: this.provider.calibrated,
    });
  }
}
