#!/usr/bin/env bash
# Idempotent Cloud Agent setup for the Blackrose monorepo.
# Installs the pinned toolchains (uv, bun) and syncs every workspace package.
set -euo pipefail

BUN_VERSION="1.3.13"

export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"

# --- uv (Python package manager) ---
if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# --- bun (JavaScript runtime / package manager, pinned) ---
if ! command -v bun >/dev/null 2>&1 || [ "$(bun --version 2>/dev/null)" != "$BUN_VERSION" ]; then
  echo "Installing bun ${BUN_VERSION}..."
  curl -fsSL https://bun.sh/install | bash -s "bun-v${BUN_VERSION}"
fi

# Make the toolchains available in future interactive shells.
BASHRC="$HOME/.bashrc"
PATH_LINE='export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"'
if ! grep -qF "$PATH_LINE" "$BASHRC" 2>/dev/null; then
  echo "$PATH_LINE" >>"$BASHRC"
fi

echo "uv:  $(uv --version)"
echo "bun: $(bun --version)"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Python package ---
echo "Syncing packages/python..."
(cd "$REPO_ROOT/packages/python" && uv sync --all-groups)

# --- JavaScript package ---
echo "Installing packages/js..."
(cd "$REPO_ROOT/packages/js" && bun install --frozen-lockfile)

# --- Docs site ---
echo "Installing docs..."
(cd "$REPO_ROOT/docs" && bun install --frozen-lockfile)

echo "Blackrose environment ready."
