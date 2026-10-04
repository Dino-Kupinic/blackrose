/**
 * Normalized answers: the only shape `decide` reads, whatever the provider.
 *
 * Mirrors packages/python/src/blackrose/answers.py.
 */

export type AnswerKind = "binary" | "scale" | "choice";

/**
 * One provider answer, normalized.
 *
 * `value` is the probability of yes (binary), expected score (scale) or the winning
 * option's probability (choice).
 */
export interface Answer {
  kind: AnswerKind;
  value: number;
  confidence?: number | null;
  choice?: string | null;
  probabilities?: Record<string, number> | null;
}

/** What a provider returns: normalized answers plus the untouched response. */
export interface ProviderResult {
  answers: Record<string, Answer>;
  raw: unknown;
}

const PROVIDER_RESULT = Symbol.for("blackrose.ProviderResult");

export function providerResult(answers: Record<string, Answer>, raw: unknown): ProviderResult {
  return Object.defineProperty({ answers, raw }, PROVIDER_RESULT, { value: true });
}

export function isProviderResult(value: unknown): value is ProviderResult {
  return value != null && typeof value === "object" && PROVIDER_RESULT in value;
}

function attr(obj: unknown, name: string): unknown {
  if (obj == null || typeof obj !== "object") return undefined;
  return name in obj ? (obj as Record<string, unknown>)[name] : undefined;
}

function asFloat(value: unknown): number | null {
  if (value == null) return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value != null && typeof value === "object" && !Array.isArray(value);
}

function floatMap(value: unknown): Record<string, number> | null {
  if (!isRecord(value)) return null;
  const out: Record<string, number> = {};
  for (const [key, prob] of Object.entries(value)) {
    const p = asFloat(prob);
    if (p != null) out[key] = p;
  }
  return out;
}

/** Find the name → answer mapping in a response, wrapper or flat mock. */
export function answersView(raw: unknown): Record<string, unknown> {
  if (raw == null) return {};

  const answers = attr(raw, "answers");
  if (isRecord(answers)) return answers;

  const combined: Record<string, unknown> = {};
  for (const bucket of ["nouls", "scores", "choices"] as const) {
    const group = attr(raw, bucket);
    if (isRecord(group)) Object.assign(combined, group);
  }
  if (Object.keys(combined).length > 0) return combined;

  // Flat mock: { jailbreak: { noul: 0.9 }, harm: { score: 2.1, confidence: 0.8 } }
  return isRecord(raw) ? raw : {};
}

/**
 * Coerce one answer into an `Answer`. Recognizes `noul` / `score` / `choice` fields
 * (the TypeSafe shape) and `kind` + `value` (the neutral shape). Returns null otherwise.
 */
export function normalizeAnswer(answer: unknown): Answer | null {
  const confidence = asFloat(attr(answer, "confidence"));
  const probabilities = floatMap(attr(answer, "probabilities"));

  const kind = attr(answer, "kind");
  const value = asFloat(attr(answer, "value"));
  if ((kind === "binary" || kind === "scale" || kind === "choice") && value != null) {
    const label = attr(answer, "choice");
    return {
      kind,
      value,
      confidence,
      choice: label == null ? null : String(label),
      probabilities,
    };
  }

  const noul = asFloat(attr(answer, "noul"));
  if (noul != null) return { kind: "binary", value: noul };

  const score = asFloat(attr(answer, "score"));
  if (score != null) return { kind: "scale", value: score, confidence, probabilities };

  const label = attr(answer, "choice");
  if (label != null) {
    const p = probabilities?.[String(label)];
    return {
      kind: "choice",
      value: p ?? confidence ?? 0,
      confidence,
      choice: String(label),
      probabilities,
    };
  }
  return null;
}

/** Coerce a provider result, response or mock into `{ name: Answer }`; unknown shapes are dropped. */
export function normalizeAnswers(raw: unknown): Record<string, Answer> {
  if (isProviderResult(raw)) return { ...raw.answers };
  const out: Record<string, Answer> = {};
  for (const [name, answer] of Object.entries(answersView(raw))) {
    const normalized = normalizeAnswer(answer);
    if (normalized != null) out[name] = normalized;
  }
  return out;
}
