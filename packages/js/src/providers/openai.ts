/**
 * OpenAI Decisions API provider — EXPERIMENTAL.
 *
 * OpenAI announced the Decisions API (GPT-6 Luna) at DevDay on 2026-09-29 but has not
 * published a request/response schema, endpoint path or SDK method. Rather than guess a
 * wire format, this provider takes a `transport` you supply. Once OpenAI publishes the
 * schema, a default transport will ship here.
 *
 * A transport receives the provider-neutral questions and returns answers in any shape
 * `normalizeAnswers` accepts, e.g.
 * `{ jailbreak: { kind: "binary", value: 0.12 }, harm: { kind: "scale", value: 0.4, confidence: 0.8 } }`.
 *
 * Scores are model-reported, not outcome-calibrated: results carry `calibrated: false`.
 * Tune thresholds with `new Policy({ providerOverrides: { openai: { … } } })`.
 *
 * Mirrors packages/python/src/blackrose/providers/openai.py.
 */

import { normalizeAnswers, type ProviderResult, providerResult } from "../answers.js";
import { isNeutralQuestion, type PolicyQuestion, type Question } from "../questions.js";
import type { GuardState } from "../types.js";
import { type Provider, ProviderError } from "./base.js";

export type OpenAIDecisionsTransport = (request: {
  state: GuardState;
  questions: Record<string, Question>;
  model?: string;
}) => Promise<unknown>;

export interface OpenAIDecisionsProviderOptions {
  transport?: OpenAIDecisionsTransport;
  /** Defaults to `OPENAI_DECISIONS_MODEL` when set. */
  model?: string;
}

const NO_TRANSPORT =
  "OpenAI has not published the Decisions API schema yet, so Blackrose ships no default " +
  "transport. Pass `transport` (an async function taking { state, questions, model }) or " +
  "use the TypeSafe provider.";

/** OpenAI Decisions provider (experimental, uncalibrated). */
export class OpenAIDecisionsProvider implements Provider {
  readonly name = "openai";
  readonly calibrated = false;
  readonly model: string | undefined;
  private readonly transport: OpenAIDecisionsTransport;

  constructor(options: OpenAIDecisionsProviderOptions = {}) {
    if (!options.transport) throw new ProviderError(NO_TRANSPORT);
    this.transport = options.transport;
    this.model = options.model ?? (process.env.OPENAI_DECISIONS_MODEL?.trim() || undefined);
  }

  async decide(
    state: GuardState,
    questions: Record<string, PolicyQuestion>,
  ): Promise<ProviderResult> {
    const neutral: Record<string, Question> = {};
    for (const [name, q] of Object.entries(questions)) {
      if (!isNeutralQuestion(q)) {
        throw new TypeError(
          `question ${JSON.stringify(name)} is not provider-neutral; the OpenAI provider ` +
            "only accepts binary(), scale() or choice() questions",
        );
      }
      neutral[name] = q;
    }
    const response = await this.transport({ state, questions: neutral, model: this.model });
    return providerResult(normalizeAnswers(response), response);
  }
}
