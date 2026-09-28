#!/usr/bin/env bash
# Install mstack's Codex custom agents into ~/.codex/agents (or a project's .codex/agents with --project DIR).
set -euo pipefail

src="$(cd "$(dirname "$0")/agents" && pwd)"
dest="${CODEX_HOME:-$HOME/.codex}/agents"
if [[ "${1:-}" == "--project" ]]; then
  dest="${2:?usage: install-agents.sh [--project DIR]}/.codex/agents"
fi

mkdir -p "$dest"
for f in "$src"/*.toml; do
  cp "$f" "$dest/"
  echo "installed $(basename "$f") -> $dest"
done
