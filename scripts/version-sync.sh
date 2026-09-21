#!/usr/bin/env bash
# Bump package versions in lockstep. Usage: ./scripts/version-sync.sh 0.1.1
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
  echo "usage: $0 <semver>" >&2
  exit 1
fi

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-].+)?$ ]]; then
  echo "invalid semver: $VERSION" >&2
  exit 1
fi

PYPROJECT="$ROOT/packages/python/pyproject.toml"
JS_PKG="$ROOT/packages/js/package.json"
PY_INIT="$ROOT/packages/python/src/blackrose/__init__.py"
JS_INDEX="$ROOT/packages/js/src/index.ts"

perl -0pi -e "s/(?m)^version = \".*\"/version = \"$VERSION\"/" "$PYPROJECT"
perl -0pi -e "s/\"version\":\\s*\"[^\"]+\"/\"version\": \"$VERSION\"/" "$JS_PKG"
perl -0pi -e "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" "$PY_INIT"
perl -0pi -e "s/export const VERSION = \".*\"/export const VERSION = \"$VERSION\"/" "$JS_INDEX"

echo "Synced package versions to $VERSION"
echo "  - packages/python/pyproject.toml"
echo "  - packages/python/src/blackrose/__init__.py"
echo "  - packages/js/package.json"
echo "  - packages/js/src/index.ts"
echo "Update CHANGELOG.md, then: git tag v$VERSION && git push origin v$VERSION"
