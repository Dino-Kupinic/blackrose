/**
 * TypeSafe (Jev) provider — the default backend.
 *
 * Mirrors packages/python/src/blackrose/providers/typesafe.py.
 */

import {
  type Question as NativeQuestion,
  noul,
  type SystemOneResult,
  score,
  TypeSafeClient,
  type TypeSafeClientConfig,
  choice as tsChoice,
} from "@typesafe-ai/sdk";

import { normalizeAnswers, type ProviderResult, providerResult } from "../answers.js";
import { isNeutralQuestion, type PolicyQuestion, type Question } from "../questions.js";
import type { GuardState } from "../types.js";
import type { Provider } from "./base.js";

export const DEFAULT_TYPESAFE_MODEL = "jev-latest";

export function resolveTypeSafeModel(model?: string | null): string {
  if (model != null && model.trim() !== "") return model.trim();
  for (const env of ["TYPESAFE_MODEL", "TYPESAFE_DEFAULT_MODEL"] as const) {
    const value = process.env[env]?.trim();
    if (value) return value;
  }
  return DEFAULT_TYPESAFE_MODEL;
}

/** Translate a neutral question into a TypeSafe question; native ones pass through. */
export function toTypeSafe(question: PolicyQuestion): NativeQuestion {
  if (!isNeutralQuestion(question)) return question as NativeQuestion;
  const q: Question = question;
  switch (q.kind) {
    case "binary":
      return q.yes != null || q.no != null
        ? noul(q.instructions, { true: q.yes ?? null, false: q.no ?? null })
        : noul(q.instructions);
    case "scale":
      return score(q.instructions, q.criteria as [string, string, ...string[]]);
    case "choice":
      return tsChoice(q.instructions, { ...q.options });
  }
}

export function toTypeSafeQuestions(
  questions: Record<string, PolicyQuestion>,
): Record<string, NativeQuestion> {
  return Object.fromEntries(Object.entries(questions).map(([name, q]) => [name, toTypeSafe(q)]));
}

/** Minimal System One client surface (real SDK or test double). */
export interface SystemOneClient {
  systemOne(request: {
    state: GuardState;
    questions: Record<string, NativeQuestion>;
    model?: string;
  }): Promise<SystemOneResult<Record<string, NativeQuestion>> | unknown>;
}

export interface TypeSafeProviderOptions {
  apiKey?: string;
  model?: string;
  /** Inject a mock or custom client; defaults to `TypeSafeClient`. */
  client?: SystemOneClient;
  /** Extra TypeSafe client config when constructing the default client. */
  clientConfig?: Omit<TypeSafeClientConfig, "apiKey" | "defaultModel">;
}

/** Provider over TypeSafe `systemOne` (calibrated). */
export class TypeSafeProvider implements Provider {
  readonly name = "typesafe";
  readonly calibrated = true;
  readonly model: string;
  private readonly client: SystemOneClient;

  constructor(options: TypeSafeProviderOptions = {}) {
    this.model = resolveTypeSafeModel(options.model);
    this.client =
      options.client ??
      new TypeSafeClient({
        ...options.clientConfig,
        apiKey: options.apiKey,
        defaultModel: this.model,
      });
  }

  async decide(
    state: GuardState,
    questions: Record<string, PolicyQuestion>,
  ): Promise<ProviderResult> {
    const response = await this.client.systemOne({
      state,
      questions: toTypeSafeQuestions(questions),
      model: this.model,
    });
    return providerResult(normalizeAnswers(response), response);
  }
}
