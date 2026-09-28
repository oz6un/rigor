#!/usr/bin/env bash
# Push local edits into the installed plugin. Both hosts cache the plugin by version, so this bumps
# the patch version, then refreshes each host whose `mstack` marketplace points at this checkout.
# Hosts installed from GitHub are skipped: push and update from there instead.
set -euo pipefail
cd "$(dirname "$0")/.."
here="$(pwd -P)"

python3 scripts/check.py

hosts=()
if command -v claude >/dev/null && claude plugin marketplace list 2>/dev/null | grep -A2 '❯ mstack$' | grep -qF "Directory ($here)"; then
  hosts+=(claude)
fi
if command -v codex >/dev/null && codex plugin marketplace list 2>/dev/null | grep -qE "^mstack +$here\$"; then
  hosts+=(codex)
fi
if [[ ${#hosts[@]} -eq 0 ]]; then
  echo "No host has the mstack marketplace registered from $here. Add it first:" >&2
  echo "  claude plugin marketplace add $here && claude plugin install mstack@mstack" >&2
  echo "  codex plugin marketplace add $here && codex plugin add mstack@mstack" >&2
  exit 1
fi

version="$(python3 - <<'EOF'
import re
paths = [".claude-plugin/plugin.json", "plugin.json"]
texts = [open(p).read() for p in paths]
old = re.search(r'"version": "(\d+)\.(\d+)\.(\d+)"', texts[0])
new = f"{old[1]}.{old[2]}.{int(old[3]) + 1}"
for p, t in zip(paths, texts):
    open(p, "w").write(re.sub(r'"version": "[^"]*"', f'"version": "{new}"', t, count=1))
print(new)
EOF
)"
echo "version $version"

failed=()
for host in "${hosts[@]}"; do
  case "$host" in
    claude) claude plugin marketplace update mstack && claude plugin update mstack@mstack || failed+=(claude) ;;
    codex) { codex plugin remove mstack@mstack >/dev/null 2>&1 || true; } && codex plugin add mstack@mstack && codex/install-agents.sh || failed+=(codex) ;;
  esac
done

if [[ ${#failed[@]} -gt 0 ]]; then
  echo "Refresh failed for: ${failed[*]}. Rerun after fixing; check.py will catch a half-bumped version." >&2
  exit 1
fi
echo "Refreshed ${hosts[*]} to $version. Restart open sessions to load it."
