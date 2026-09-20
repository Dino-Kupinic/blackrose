/**
 * Blackrose: TypeSafe decision layer for LLM input/output.
 *
 * Decide before you generate — `checkInput` / `checkOutput` → allow | review | block.
 */

export { answersView, decide, extractScores } from "./decide.js";
export { Guard, type GuardOptions, type SystemOneClient } from "./guard.js";
export {
  defaultInputQuestions,
  defaultOutputQuestions,
  HARM_SEVERITY,
  Policy,
  type PolicyOptions,
  type PolicySide,
} from "./policy.js";
export type { CheckResult, GuardState, Verdict } from "./types.js";

export const VERSION = "0.1.0";
