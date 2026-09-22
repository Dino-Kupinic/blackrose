/**
 * Blackrose: TypeSafe decision layer for LLM input/output.
 *
 * Decide before you generate — `checkInput` / `checkOutput` → allow | review | block.
 */

export { answersView, type DecideOptions, decide, extractScores } from "./decide.js";
export {
  BlackroseError,
  GuardClosedError,
  PolicyConfigError,
  TypeSafeRequestError,
} from "./errors.js";
export { Guard, type GuardOptions, type SystemOneClient } from "./guard.js";
export {
  defaultInputQuestions,
  defaultOutputQuestions,
  HARM_SEVERITY,
  harmSeverity,
  Policy,
  type PolicyOptions,
  type PolicySide,
  type ScoreThresholds,
} from "./policy.js";
export type { CheckResult, GuardState, Trigger, Verdict } from "./types.js";
export { qualifiedTrigger } from "./types.js";

export const VERSION = "0.1.0";
