#!/usr/bin/env bash
# Exercise every script rigor's skills call, in a throwaway directory. No model calls, no network
# except `npx -y bun` on first use when bun isn't installed. Run: scripts/smoke.sh
set -uo pipefail

root="$(cd "$(dirname "$0")/.." && pwd -P)"
s="$root/skills"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
failed=0

check() {
  local label="$1"; shift
  local out
  if out="$("$@" 2>&1)"; then
    echo "ok   $label"
  else
    echo "FAIL $label"
    echo "$out" | tail -5 | sed 's/^/     /'
    failed=$((failed + 1))
  fi
}

expect_exit() {
  local want="$1"; shift
  "$@" >/dev/null 2>&1
  [[ $? -eq $want ]]
}

check "check.py" python3 "$root/scripts/check.py"
check "mode hook state machine" python3 "$root/scripts/test_mode_hook.py"
check "auto-update end to end" "$root/scripts/test_auto_update.sh"

check "install.sh into a throwaway home" env HOME="$tmp/home" CODEX_HOME="$tmp/home/.codex" "$root/install.sh"
check "  skills linked for both hosts" test -f "$tmp/home/.claude/skills/rigor/SKILL.md" -a -f "$tmp/home/.agents/skills/how/SKILL.md"
check "  agents installed for both hosts" test -f "$tmp/home/.claude/agents/rigor-agent.md" -a -f "$tmp/home/.codex/agents/rigor-agent.toml"
check "  hooks registered for both hosts" grep -q mode-hook.py "$tmp/home/.claude/settings.json" "$tmp/home/.codex/hooks.json"
check "  uninstall removes everything" bash -c "HOME='$tmp/home' CODEX_HOME='$tmp/home/.codex' '$root/install.sh' --uninstall >/dev/null && [ -z \"\$(find '$tmp/home/.claude/skills' '$tmp/home/.agents/skills' -mindepth 1)\" ] && ! grep -q mode-hook.py '$tmp/home/.codex/hooks.json' '$tmp/home/.claude/settings.json'"

m="$tmp/moved-home"; mkdir -p "$tmp/clone2"; c2="$(cd "$tmp/clone2" && pwd -P)"
(cd "$root" && git ls-files -co --exclude-standard -z | xargs -0 tar cf - | tar xf - -C "$c2")
env HOME="$m" CODEX_HOME="$m/.codex" "$root/install.sh" >/dev/null 2>&1
check "install from a second clone takes the links over" bash -c "HOME='$m' CODEX_HOME='$m/.codex' '$c2/install.sh' 2>&1 | grep -q 'Installed from $c2: 5[0-9] ' && [ \"\$(readlink '$m/.claude/skills/rigor')\" = '$c2/skills/rigor' ] && [ \"\$(readlink '$m/.claude/agents/rigor-agent.md')\" = '$c2/agents/rigor-agent.md' ] && grep -q '$c2/skills/rigor/scripts/mode-hook.py' '$m/.claude/settings.json' && ! grep -q '$root' '$m/.codex/agents/rigor-agent.toml'"

h="$tmp/seeded"
mkdir -p "$h/.claude" "$h/.codex/agents"
cat > "$h/.claude/settings.json" <<'EOF'
{
  "statusLine": {"type": "command", "command": "echo café ✓"},
  "hooks": {"UserPromptSubmit": [{"hooks": [
    {"type": "command", "command": "python3 ~/tools/mode-hook.py"},
    {"type": "command", "command": "echo keepme"}]}]}
}
EOF
echo '{}' > "$h/.codex/hooks.json"
echo '# my own agent' > "$h/.codex/agents/rigor-agent.toml"
cp "$h/.claude/settings.json" "$tmp/settings.orig"
same_json() { python3 -c 'import json,sys; sys.exit(json.load(open(sys.argv[1])) != json.load(open(sys.argv[2])))' "$1" "$2"; }
check "install next to existing config" env HOME="$h" CODEX_HOME="$h/.codex" "$root/install.sh"
check "  keeps the user's hooks and non-ASCII text" python3 -c '
import json, sys
d = json.load(open(sys.argv[1]))
cmds = [x["command"] for g in d["hooks"]["UserPromptSubmit"] for x in g["hooks"]]
assert "python3 ~/tools/mode-hook.py" in cmds and "echo keepme" in cmds, cmds
assert d["statusLine"]["command"] == "echo café ✓"
assert sum("skills/rigor/scripts/mode-hook.py" in c for c in cmds) == 1, cmds' "$h/.claude/settings.json"
check "  skips the user's own Codex agent" grep -qx '# my own agent' "$h/.codex/agents/rigor-agent.toml"
check "  a rerun adds no duplicate hook" bash -c "HOME='$h' CODEX_HOME='$h/.codex' '$root/install.sh' >/dev/null 2>&1 && [ \$(grep -c 'skills/rigor/scripts/mode-hook.py' '$h/.claude/settings.json') -eq 2 ]"
check "  uninstall restores the user's config" bash -c "HOME='$h' CODEX_HOME='$h/.codex' '$root/install.sh' --uninstall >/dev/null"
check "    settings.json back to the original" same_json "$h/.claude/settings.json" "$tmp/settings.orig"
check "    the user's {} hooks.json is kept" grep -qx '{}' "$h/.codex/hooks.json"
check "    the user's Codex agent is kept" grep -qx '# my own agent' "$h/.codex/agents/rigor-agent.toml"
check "  a malformed config stops install before any change" bash -c "m='$tmp/bad'; mkdir -p \$m/.claude; echo '{ // nope' > \$m/.claude/settings.json; ! HOME=\$m CODEX_HOME=\$m/.codex '$root/install.sh' >/dev/null 2>&1 && [ ! -e \$m/.claude/skills ]"

check "second-opinion.sh --help" "$s/rigor/scripts/second-opinion.sh" --help
check "second-opinion.sh exits 3 without the other CLI" expect_exit 3 env PATH=/usr/bin:/bin bash -c "echo hi | '$s/rigor/scripts/second-opinion.sh' --cli codex"

check "log.sh appends a row" bash -c "'$s/show-me-your-work/scripts/log.sh' '$tmp/log/decisions.tsv' build 'use X' 'faster' 'bench' kept && grep -q 'use X' '$tmp/log/decisions.tsv'"

git -C "$tmp" init -q repo && git -C "$tmp/repo" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
check "worktree-audit.sh on a repo" bash -c "cd '$tmp/repo' && '$s/rigor/scripts/worktree-audit.sh' '$tmp/repo'"

python3 - "$s/rigor/playbooks/multi-phase-plan.md" "$tmp/plan.md" <<'EOF'
import re, sys
text = open(sys.argv[1]).read()
blocks = re.findall(r"^(`{3,4})markdown\n(.*?)^\1$", text, re.S | re.M)
open(sys.argv[2], "w").write(max(blocks, key=lambda b: len(b[1]))[1])
EOF
sed -i.bak 's|<fast model>|haiku|g' "$tmp/plan.md"
check "check-plan.mjs accepts the filled-in plan skeleton" bash -c "node '$s/rigor/scripts/check-plan.mjs' '$tmp/plan.md' | grep -q '1 PR sections, 0 problems'"
sed 's|/goal|/loop 30m|g' "$tmp/plan.md" > "$tmp/plan-loop.md"
check "check-plan.mjs rejects a plan that arms /loop instead of /goal" bash -c "! node '$s/rigor/scripts/check-plan.mjs' '$tmp/plan-loop.md' | grep -q ' 0 problems'"

orch="$s/rigor/scripts/orch/orch"
export ORCH_STORE="$tmp/orch"
check "orch init" "$orch" init
check "orch unit add" "$orch" unit add u1 --track core
check "orch unit set" "$orch" unit set u1 --state building
check "orch status" "$orch" status
check "watch-pr --help" "$s/rigor/scripts/watch-pr/watch-pr" --help

echo
[[ $failed -eq 0 ]] && echo "all smoke checks passed" || echo "$failed smoke check(s) failed"
exit $((failed > 0))
