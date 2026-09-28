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

check "install.sh into a throwaway home" env HOME="$tmp/home" CODEX_HOME="$tmp/home/.codex" "$root/install.sh"
check "  skills linked for both hosts" test -f "$tmp/home/.claude/skills/rigor/SKILL.md" -a -f "$tmp/home/.agents/skills/how/SKILL.md"
check "  agents installed for both hosts" test -f "$tmp/home/.claude/agents/rigor-agent.md" -a -f "$tmp/home/.codex/agents/rigor-agent.toml"
check "  hooks registered for both hosts" grep -q mode-hook.py "$tmp/home/.claude/settings.json" "$tmp/home/.codex/hooks.json"
check "  uninstall removes everything" bash -c "HOME='$tmp/home' CODEX_HOME='$tmp/home/.codex' '$root/install.sh' --uninstall >/dev/null && [ -z \"\$(find '$tmp/home/.claude/skills' '$tmp/home/.agents/skills' -mindepth 1)\" ] && [ ! -e '$tmp/home/.codex/hooks.json' ]"

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
check "check-plan.mjs accepts the plan skeleton's structure" bash -c "node '$s/rigor/scripts/check-plan.mjs' '$tmp/plan.md' | grep -q '1 PR sections'"

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
