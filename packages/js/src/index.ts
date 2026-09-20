/**
 * Blackrose: TypeSafe decision layer for LLM input/output.
 *
 * Decide before you generate — `checkInput` / `checkOutput` → allow | review | block.
 */

export type { CheckResult, GuardState, Verdict } from "./types.js";
export { decide, extractScores, answersView } from "./decide.js";
export {
  Policy,
  HARM_SEVERITY,
  defaultInputQuestions,
  defaultOutputQuestions,
  type PolicyOptions,
  type PolicySide,
} from "./policy.js";
export { Guard, type GuardOptions, type SystemOneClient } from "./guard.js";

export const VERSION = "0.1.0";
