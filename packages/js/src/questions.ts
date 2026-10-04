/**
 * Provider-neutral question types.
 *
 * Policies describe checks with these; each provider translates them into its own
 * native format (for example TypeSafe `noul` / `score` / `choice`).
 *
 * Mirrors packages/python/src/blackrose/questions.py.
 */

/** Yes/no question answered with the probability of yes (TypeSafe `noul`). */
export interface BinaryQuestion {
  readonly kind: "binary";
  readonly instructions: string;
  readonly yes?: string | null;
  readonly no?: string | null;
}

/** Ordered rubric answered with an expected score (TypeSafe `score`). `criteria[i]` is score i. */
export interface ScaleQuestion {
  readonly kind: "scale";
  readonly instructions: string;
  readonly criteria: readonly string[];
}

/** Closed set of options answered with per-option probabilities (TypeSafe `choice`). */
export interface ChoiceQuestion {
  readonly kind: "choice";
  readonly instructions: string;
  readonly options: Readonly<Record<string, string | null>>;
}

export type Question = BinaryQuestion | ScaleQuestion | ChoiceQuestion;

/** A provider-native question (e.g. from `@typesafe-ai/sdk`), identified by `type`. */
export interface NativeQuestion {
  readonly type: string;
}

/** What a policy may hold: neutral questions work everywhere, native ones only on their provider. */
export type PolicyQuestion = Question | NativeQuestion;

export function binary(
  instructions: string,
  outcomes: { yes?: string | null; no?: string | null } = {},
): BinaryQuestion {
  return { kind: "binary", instructions, yes: outcomes.yes ?? null, no: outcomes.no ?? null };
}

export function scale(instructions: string, criteria: readonly string[]): ScaleQuestion {
  if (criteria.length < 2) {
    throw new Error("scale needs at least two criteria (one per score from zero)");
  }
  return { kind: "scale", instructions, criteria: [...criteria] };
}

export function choice(
  instructions: string,
  options: Readonly<Record<string, string | null>>,
): ChoiceQuestion {
  if (Object.keys(options).length < 2) {
    throw new Error("choice needs at least two options");
  }
  return { kind: "choice", instructions, options: { ...options } };
}

export function isNeutralQuestion(q: unknown): q is Question {
  if (q == null || typeof q !== "object") return false;
  const kind = (q as { kind?: unknown }).kind;
  return kind === "binary" || kind === "scale" || kind === "choice";
}
