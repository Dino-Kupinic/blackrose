/**
 * Blackrose: provider-neutral decision layer for LLM input/output.
 *
 * Decide before you generate — `checkInput` / `checkOutput` → allow | review | block.
 */

export {
  type Answer,
  type AnswerKind,
  normalizeAnswer,
  normalizeAnswers,
  type ProviderResult,
  providerResult,
} from "./answers.js";
export { answersView, type DecideOptions, decide, extractScores } from "./decide.js";
export { Guard, type GuardOptions } from "./guard.js";
export {
  defaultInputQuestions,
  defaultOutputQuestions,
  HARM_SEVERITY,
  Policy,
  type PolicyOptions,
  type PolicySide,
  type PolicyThresholds,
} from "./policy.js";
export {
  OpenAIDecisionsProvider,
  type OpenAIDecisionsProviderOptions,
  type OpenAIDecisionsTransport,
  PROVIDER_ENV,
  type Provider,
  ProviderError,
  type SystemOneClient,
  TypeSafeProvider,
  type TypeSafeProviderOptions,
  toTypeSafe,
} from "./providers/index.js";
export {
  type BinaryQuestion,
  binary,
  type ChoiceQuestion,
  choice,
  type NativeQuestion,
  type PolicyQuestion,
  type Question,
  type ScaleQuestion,
  scale,
} from "./questions.js";
export type { CheckResult, GuardState, Verdict } from "./types.js";

export const VERSION = "0.1.0";
