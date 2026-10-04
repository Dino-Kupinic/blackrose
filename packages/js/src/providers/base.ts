/**
 * Provider interface: the seam between Blackrose policy and a decision model.
 *
 * Mirrors packages/python/src/blackrose/providers/base.py.
 */

import type { ProviderResult } from "../answers.js";
import type { PolicyQuestion } from "../questions.js";
import type { GuardState } from "../types.js";

/** A provider is misconfigured or cannot be used yet. */
export class ProviderError extends Error {
  override name = "ProviderError";
}

/** Decision-model backend. */
export interface Provider {
  /** Short identifier (`typesafe`, `openai`) used for policy overrides. */
  readonly name: string;
  /** `true` if the provider claims outcome-verified calibration. */
  readonly calibrated: boolean;
  decide(state: GuardState, questions: Record<string, PolicyQuestion>): Promise<ProviderResult>;
}
