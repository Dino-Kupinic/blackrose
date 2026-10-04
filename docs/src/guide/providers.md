# Providers

Blackrose is a policy layer on top of a **decision model**: a model that answers typed questions with probabilities instead of generating text. The provider is the decision model. Policy, verdicts and reasons stay the same whichever provider you use.

| Provider | Status | Calibrated | Select with |
| --- | --- | --- | --- |
| TypeSafe (Jev) | Default, stable | Yes (outcome-verified, per TypeSafe) | nothing — or `BLACKROSE_PROVIDER=typesafe` |
| OpenAI Decisions API | **Experimental** | No (model-reported) | `provider=OpenAIDecisionsProvider(transport=...)` |

Every `CheckResult` records `provider` and `calibrated`, so you can log and audit which model produced a verdict.

## Neutral questions

Policies describe checks with provider-neutral types. Each provider translates them into its own format.

| Blackrose | Answer | TypeSafe |
| --- | --- | --- |
| `Binary` / `binary()` | probability of yes | `Noul` |
| `Scale` / `scale()` | expected score + confidence | `Score` |
| `Choice` / `choice()` | winning option's probability + confidence | `Choice` |

```python
from blackrose import Binary, Guard, Policy

policy = Policy(input_questions={"spam": Binary("Is this message spam?", yes="spam", no="not spam")})
guard = Guard(policy=policy)
```

Native TypeSafe questions (`typesafe_sdk.Noul`, `noul()` from `@typesafe-ai/sdk`) still work, but only with the TypeSafe provider.

## TypeSafe (default)

```python
from blackrose import Guard, TypeSafeProvider

guard = Guard()  # same as Guard(provider=TypeSafeProvider())
guard = Guard(provider=TypeSafeProvider(api_key="...", model="jev-latest"))
```

```ts
import { Guard, TypeSafeProvider } from "blackrose";

const guard = new Guard({ provider: new TypeSafeProvider({ apiKey: "...", model: "jev-latest" }) });
```

## OpenAI Decisions API (experimental)

OpenAI announced the Decisions API at DevDay on 29 Sep 2026. As of early October 2026 it is in limited preview, and OpenAI has **not published** a request/response schema, endpoint path or SDK method. Blackrose does not guess the wire format. Instead, you pass a `transport`, a function that calls the API however your preview access allows and returns answers.

```python
from blackrose import Guard, OpenAIDecisionsProvider

def transport(state, questions, model):
    # questions: {name: Binary | Scale | Choice}
    # return any shape blackrose.answers.normalize_answers accepts, e.g.
    return {
        "jailbreak": {"kind": "binary", "value": 0.12},
        "harm": {"kind": "scale", "value": 0.4, "confidence": 0.8},
        "needs_human": {"kind": "binary", "value": 0.05},
    }

guard = Guard(provider=OpenAIDecisionsProvider(transport=transport))
```

```ts
import { Guard, OpenAIDecisionsProvider } from "blackrose";

const guard = new Guard({
  provider: new OpenAIDecisionsProvider({
    transport: async ({ state, questions, model }) => callYourPreviewAccess(state, questions, model),
  }),
});
```

When OpenAI publishes the schema, a default transport will ship and `BLACKROSE_PROVIDER=openai` will work on its own. Until then, setting it without a transport raises `ProviderError` with an explanation.

The async Python variant is `AsyncOpenAIDecisionsProvider`, used with `AsyncGuard`.

## Per-provider thresholds

A 0.8 from one provider is not necessarily a 0.8 from another. OpenAI's scores are reported by the model and not checked against real outcomes. Tune thresholds per provider:

```python
policy = Policy(provider_overrides={"openai": {"min_confidence": 0.7, "review_threshold": 0.25}})
```

```ts
const policy = new Policy({ providerOverrides: { openai: { minConfidence: 0.7, reviewThreshold: 0.25 } } });
```

Overrides apply only when that provider answers. Unknown keys raise an error.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `BLACKROSE_PROVIDER` | `typesafe` | `typesafe` or `openai` |
| `TYPESAFE_API_KEY` | — | TypeSafe API key |
| `TYPESAFE_MODEL` | `jev-latest` | TypeSafe model |
| `OPENAI_DECISIONS_MODEL` | — | Model name passed to your OpenAI transport |

## Writing your own provider

Anything with `name`, `calibrated` and `decide(state, questions)` that returns a `ProviderResult` is a provider (`Provider` / `AsyncProvider` in Python, `Provider` in TS). Use `normalize_answers` / `normalizeAnswers` to convert a response into `Answer`s.
