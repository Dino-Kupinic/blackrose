# Python chat filter

Wrap a fake streaming chat call with Blackrose input and output checks.

## Setup

```bash
cd examples/python-chat-filter
python -m venv .venv && source .venv/bin/activate
pip install -e ../../packages/python
export TYPESAFE_API_KEY=...   # required for live TypeSafe calls
# optional: export TYPESAFE_MODEL=jev-latest
```

Or copy the repo root `.env.example` and export vars from a `.env` file yourself.

## Run

```bash
python main.py
# or with a custom prompt:
python main.py "How do I reset my password?"
```

Without `TYPESAFE_API_KEY`, the script exits immediately with a clear error.

## What it does

1. `guard.check_input(user_message)` — block / review / allow before generation
2. Streams a fake assistant reply (stand-in for your LLM)
3. `guard.check_output(full_reply)` — decide whether to show the reply
