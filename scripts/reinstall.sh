#!/usr/bin/env bash
# Push local edits into the installed plugin. Both hosts serve a cached copy keyed by version,
# so this bumps the patch version, then refreshes Claude Code and Codex.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/check.py

version="$(python3 - <<'EOF'
import json
paths = [".claude-plugin/plugin.json", "plugin.json"]
data = [json.load(open(p)) for p in paths]
major, minor, patch = map(int, data[0]["version"].split("."))
new = f"{major}.{minor}.{patch + 1}"
for p, d in zip(paths, data):
    d["version"] = new
    open(p, "w").write(json.dumps(d, indent=2) + "\n")
print(new)
EOF
)"
echo "version $version"

if command -v claude >/dev/null; then
  claude plugin marketplace update mstack
  claude plugin update mstack@mstack
fi
if command -v codex >/dev/null; then
  codex plugin remove mstack@mstack >/dev/null 2>&1 || true
  codex plugin add mstack@mstack
  codex/install-agents.sh
fi
echo "Restart open sessions to load version $version."
