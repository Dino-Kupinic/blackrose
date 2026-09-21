# Integration

Pattern: check the user message **before** calling your LLM; check the model reply **before** showing it.

## Chat handler sketch

::: code-group

```python [Python]
from blackrose import Guard

guard = Guard()

def handle(user_message: str) -> str:
    inbound = guard.check_input(user_message)
    if inbound.verdict == "block":
        return "I can't help with that."
    if inbound.verdict == "review":
        return queue_for_human(user_message, inbound)

    reply = call_your_llm(user_message)

    outbound = guard.check_output(reply)
    if outbound.verdict == "block":
        return "[withheld]"
    if outbound.verdict == "review":
        return queue_for_human(reply, outbound)
    return reply
```

```ts [JavaScript]
import { Guard } from "blackrose";

const guard = new Guard();

export async function handle(userMessage: string): Promise<string> {
  const inbound = await guard.checkInput(userMessage);
  if (inbound.verdict === "block") return "I can't help with that.";
  if (inbound.verdict === "review") return queueForHuman(userMessage, inbound);

  const reply = await callYourLlm(userMessage);

  const outbound = await guard.checkOutput(reply);
  if (outbound.verdict === "block") return "[withheld]";
  if (outbound.verdict === "review") return queueForHuman(reply, outbound);
  return reply;
}
```

:::

## Structured state

Both packages accept JSON-compatible state (string, object, array) — pass conversation snippets or tool payloads the same way you would to TypeSafe System One.

```python
guard.check_input({"role": "user", "content": user_message})
```

```ts
await guard.checkInput({ role: "user", content: userMessage });
```

## Observability

Log `result.verdict`, `result.reasons`, and `result.scores` next to your request id. Keep `raw` for debugging; avoid shipping full raw payloads to end users.
