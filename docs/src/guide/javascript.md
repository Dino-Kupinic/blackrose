# JavaScript API

Package: `packages/js` · npm name `blackrose`

Requires `@typesafe-ai/sdk` `^0.6.0` (latest JS line as of this release; Python uses `typesafe-sdk>=0.7.0` — keep each package on the newest compatible SDK).

## Install

```bash
bun add blackrose
# or: npm install blackrose
# from this repo: cd packages/js && bun install
```

## Guard

```ts
import { Guard, Policy } from "blackrose";

const guard = new Guard({
  apiKey: process.env.TYPESAFE_API_KEY,
  model: "jev-latest",
  policy: new Policy(),
});

try {
  const inbound = await guard.checkInput(userMessage);
  const outbound = await guard.checkOutput(modelReply);
} finally {
  await guard.close();
}

// or:
await using guard2 = new Guard();
```

Constructor options:

| Option | Purpose |
| --- | --- |
| `apiKey` | Passed to TypeSafe; else `TYPESAFE_API_KEY` |
| `model` | Override; else `TYPESAFE_MODEL` → `TYPESAFE_DEFAULT_MODEL` → `jev-latest` (blank strings are ignored) |
| `policy` | Thresholds / questions |
| `client` | Inject a `SystemOneClient` test double |
| `clientConfig` | Extra TypeSafe client config when constructing the default client |

`close()` / `[Symbol.asyncDispose]()` dispose the owned SDK client when Blackrose constructed it. Safe to call more than once. Checks after close raise `GuardClosedError`.

TypeSafe call failures raise `TypeSafeRequestError` — fail closed; do not treat that as `allow`.

## Exports

- `Guard`, `GuardOptions`, `SystemOneClient`
- `Policy`, `PolicyOptions`, `PolicySide`, `ScoreThresholds`, `PolicyConfigError`
- `defaultInputQuestions`, `defaultOutputQuestions`, `harmSeverity`, `HARM_SEVERITY`
- `decide`, `extractScores`, `answersView`
- `CheckResult`, `Trigger`, `GuardState`, `Verdict`
- `BlackroseError`, `GuardClosedError`, `TypeSafeRequestError`
- `VERSION`

## Tests

```bash
bun run lint
bun run typecheck
bun run test
bun run build
# optional live calls:
TYPESAFE_API_KEY=... bun run test:live
```
