# JavaScript chat filter

Wrap a fake streaming chat call with Blackrose `checkInput` / `checkOutput`.

## Setup

```bash
cd examples/js-chat-filter
npm install
# links local packages/js via file: dependency
export TYPESAFE_API_KEY=...   # required for live TypeSafe calls
# optional: export TYPESAFE_MODEL=jev-latest
```

Build the local package once if `dist/` is missing:

```bash
cd ../../packages/js && npm install && npm run build
```

## Run

```bash
npm start
# or with a custom prompt:
npm start -- "How do I reset my password?"
```

Without `TYPESAFE_API_KEY`, the script exits immediately with a clear error.

## What it does

1. `guard.checkInput(userMessage)` — block / review / allow before generation
2. Streams a fake assistant reply (stand-in for your LLM)
3. `guard.checkOutput(fullReply)` — decide whether to show the reply
