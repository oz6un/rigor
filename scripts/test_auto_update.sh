#!/usr/bin/env bash
# End to end: a clone one commit behind its origin gets fast-forwarded and reinstalled when a session
# starts, without slowing the hook down; clones in use are left alone. Local origin, no network.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd -P)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
failed=0
ok() { if "$@"; then echo "ok   $label"; else echo "FAIL $label"; failed=$((failed + 1)); fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }

# origin holds this working tree (including uncommitted edits) as v1, then v2 adds a skill.
mkdir "$tmp/origin"
(cd "$root" && git ls-files -co --exclude-standard -z | xargs -0 tar cf - | tar xf - -C "$tmp/origin")
g -C "$tmp/origin" init -q -b main && g -C "$tmp/origin" add -A && g -C "$tmp/origin" commit -qm v1
g clone -q "$tmp/origin" "$tmp/clone"
mkdir "$tmp/origin/skills/zz-new" && printf -- '---\nname: zz-new\ndescription: test\n---\n' > "$tmp/origin/skills/zz-new/SKILL.md"
g -C "$tmp/origin" add -A && g -C "$tmp/origin" commit -qm v2
v2="$(git -C "$tmp/origin" rev-parse HEAD)"

home="$tmp/home"
HOME="$home" CODEX_HOME="$home/.codex" "$tmp/clone/install.sh" > /dev/null
hook() { HOME="$home" python3 "$tmp/clone/skills/rigor/scripts/mode-hook.py" <<< "{\"hook_event_name\":\"SessionStart\",\"session_id\":\"s\",\"source\":\"$1\"}"; }
wait_log() { for _ in $(seq 100); do [[ -s "$home/.rigor/last-update.log" ]] && return 0; perl -e 'select(undef,undef,undef,0.2)'; done; return 1; }
fresh() { rm -f "$home/.rigor/last-update-check" "$home/.rigor/last-update.log"; }

start=$(perl -MTime::HiRes=time -e 'print time'); out="$(hook startup)"; end=$(perl -MTime::HiRes=time -e 'print time')
label="startup hook returns in under 0.3s and prints nothing ($(perl -e "printf '%.3f', $end-$start")s)"; ok perl -e "exit(!($end-$start < 0.3))" && [[ -z "$out" ]]
label="the clone is fast-forwarded to origin/main"; ok bash -c "$(declare -f wait_log); home='$home'; wait_log && [ \"\$(git -C '$tmp/clone' rev-parse HEAD)\" = '$v2' ]"
label="install.sh reran: the new skill is linked"; ok test -f "$home/.claude/skills/zz-new/SKILL.md"
label="the log says so"; ok grep -q "updated .* -> ${v2:0:7}" "$home/.rigor/last-update.log"

rm -f "$home/.rigor/last-update.log"; hook startup
label="a second start the same day doesn't check again"; ok bash -c "perl -e 'select(undef,undef,undef,1)'; [ ! -e '$home/.rigor/last-update.log' ]"
fresh; hook compact > /dev/null
label="compaction doesn't check"; ok bash -c "perl -e 'select(undef,undef,undef,1)'; [ ! -e '$home/.rigor/last-update.log' ]"

g -C "$tmp/origin" commit -q --allow-empty -m v3
echo local > "$tmp/clone/README.md"; fresh; hook startup
label="uncommitted changes: skipped, nothing touched"; ok bash -c "$(declare -f wait_log); home='$home'; wait_log && grep -q 'uncommitted' '$home/.rigor/last-update.log' && [ \"\$(git -C '$tmp/clone' rev-parse HEAD)\" = '$v2' ]"
git -C "$tmp/clone" checkout -q README.md && git -C "$tmp/clone" checkout -q -b feature; fresh; hook startup
label="not on main: skipped"; ok bash -c "$(declare -f wait_log); home='$home'; wait_log && grep -q \"isn't on main\" '$home/.rigor/last-update.log'"
git -C "$tmp/clone" checkout -q main && g -C "$tmp/clone" commit -q --allow-empty -m mine; fresh; hook startup
label="local commits on main: skipped, commit kept"; ok bash -c "$(declare -f wait_log); home='$home'; wait_log && grep -q \"can't fast-forward\" '$home/.rigor/last-update.log' && git -C '$tmp/clone' log -1 --format=%s | grep -qx mine"
touch "$home/.rigor/no-auto-update"; fresh; hook startup
label="~/.rigor/no-auto-update turns it off"; ok bash -c "perl -e 'select(undef,undef,undef,1)'; [ ! -e '$home/.rigor/last-update-check' ]"

exit $((failed > 0))
