# RAG passage gate (cookbook)

Score retrieved passages and map each to **keep** / **flag** / **drop** before stuffing them into the prompt.

This is an application pattern on top of Blackrose — not a second library API.

## Setup

```bash
cd examples/rag-passage-gate
python -m venv .venv && source .venv/bin/activate
pip install -e ../../packages/python
export TYPESAFE_API_KEY=...   # required for live TypeSafe calls
```

## Run

```bash
python main.py
```

Without `TYPESAFE_API_KEY`, the script exits immediately with a clear error.

## Decision mapping

| Blackrose verdict | Passage action |
| --- | --- |
| `allow` | **keep** — include in context |
| `review` | **flag** — include only with human / audit note |
| `block` | **drop** — exclude from the prompt |

Checks use a small custom `Policy` tuned for retrieved text (toxicity / off-topic / PII risk), not the default chat jailbreak battery.
