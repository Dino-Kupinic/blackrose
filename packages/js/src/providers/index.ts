/** Decision-model providers and env-based selection. */

import { ProviderError } from "./base.js";

export { type Provider, ProviderError } from "./base.js";
export {
  OpenAIDecisionsProvider,
  type OpenAIDecisionsProviderOptions,
  type OpenAIDecisionsTransport,
} from "./openai.js";
export {
  DEFAULT_TYPESAFE_MODEL,
  type SystemOneClient,
  TypeSafeProvider,
  type TypeSafeProviderOptions,
  toTypeSafe,
} from "./typesafe.js";

export const PROVIDER_ENV = "BLACKROSE_PROVIDER";
const KNOWN = ["typesafe", "openai"] as const;
export type ProviderName = (typeof KNOWN)[number];

/** Read `BLACKROSE_PROVIDER` (default `typesafe`). */
export function providerNameFromEnv(): ProviderName {
  const name = process.env[PROVIDER_ENV]?.trim().toLowerCase() || "typesafe";
  if (!(KNOWN as readonly string[]).includes(name)) {
    throw new ProviderError(
      `${PROVIDER_ENV}=${JSON.stringify(name)} is not one of ${KNOWN.join(", ")}`,
    );
  }
  return name as ProviderName;
}
