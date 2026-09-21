#!/usr/bin/env bash
# Maintainer helper: close pre-rewrite GitHub issues and refresh repo metadata.
# Requires write access (personal PAT or repo admin). The cloud agent gh token is
# read-only — run this locally after merging the hygiene PR.
set -euo pipefail

REPO="${REPO:-Dino-Kupinic/blackrose}"

# Issues that targeted the removed Ollama/chat gateway product.
LEGACY_ISSUES=(4 8 35 36 115 118 137)

CLOSE_COMMENT='Closing as obsolete: Blackrose is now a TypeSafe decision-layer library (packages/python + packages/js), not an Ollama/chat gateway. Please open a new issue against the library APIs if this still applies.'

echo "==> Closing legacy issues on ${REPO}"
for n in "${LEGACY_ISSUES[@]}"; do
  if gh issue view "$n" --repo "$REPO" --json state -q .state 2>/dev/null | grep -qi open; then
    gh issue close "$n" --repo "$REPO" --comment "$CLOSE_COMMENT"
    echo "  closed #$n"
  else
    echo "  skip #$n (already closed or missing)"
  fi
done

echo "==> Updating repository description, homepage, and topics"
gh repo edit "$REPO" \
  --description "TypeSafe decision layer for LLM apps: check_input / check_output → allow | review | block" \
  --homepage "https://blackrose.dev" \
  --add-topic typesafe \
  --add-topic guardrails \
  --add-topic llm \
  --add-topic safety \
  --add-topic python \
  --add-topic typescript \
  --add-topic javascript

# Drop topics from the previous product when present.
for topic in fastapi llama3 meta-ai ollama python3; do
  gh repo edit "$REPO" --remove-topic "$topic" 2>/dev/null || true
done

echo "==> Done. Verify: https://github.com/${REPO}"
