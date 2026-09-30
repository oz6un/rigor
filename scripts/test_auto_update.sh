#!/usr/bin/env bash
# End to end: the session-start hook launches the updater without waiting on it, and the updater
# fast-forwards and reinstalls a clone that's behind, at most once a day behind a lock,
# while leaving clones in use alone. Local origin, clean environment, no network.
set -uo pipefail
# The test runs git itself: an inherited GIT_DIR would point those commands at your repo.
unset $(git rev-parse --local-env-vars)
root="$(cd "$(dirname "$0")/.." && pwd -P)"
tmp="$(mktemp -d)"; [ -z "${KEEP:-}" ] || echo "kept: $tmp"
trap '[ -n "${KEEP:-}" ] || rm -rf "$tmp"' EXIT
failed=0
check() { local label="$1"; shift; if "$@"; then echo "ok   $label"; else echo "FAIL $label"; failed=$((failed + 1)); fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }

# origin holds this working tree (including uncommitted edits) as v1.
mkdir "$tmp/origin"
(cd "$root" && git ls-files -co --exclude-standard -z | xargs -0 tar cf - | tar xf - -C "$tmp/origin")
g -C "$tmp/origin" init -q -b main && g -C "$tmp/origin" add -A && g -C "$tmp/origin" commit -qm v1
g clone -q "$tmp/origin" "$tmp/clone"
home="$tmp/home"
mkdir "$home"
# Only what we pass: a leaked CODEX_HOME would reinstall into the real Codex config, and a leaked
# RIGOR_NESTED would silence the hook.
clean() { env -i HOME="$home" CODEX_HOME="$home/.codex" PATH="$PATH" "$@"; }
clean "$tmp/clone/install.sh" > /dev/null

release() {  # a new origin commit; with a name, it adds that skill
  if [[ -n "${1:-}" ]]; then mkdir "$tmp/origin/skills/$1" && printf -- '---\nname: %s\ndescription: t\n---\n' "$1" > "$tmp/origin/skills/$1/SKILL.md"; fi
  g -C "$tmp/origin" add -A && g -C "$tmp/origin" commit -q --allow-empty -m "release ${1:-}" && git -C "$tmp/origin" rev-parse HEAD
}
update() { clean "$@" bash "$tmp/clone/scripts/auto-update.sh"; }
new_day() { rm -f "$home/.rigor/last-update-check"; }
head_is() { [[ "$(git -C "$tmp/clone" rev-parse HEAD)" == "$1" ]]; }
logged() { tail -1 "$home/.rigor/update.log" 2>/dev/null | grep -q -- "$1"; }
hook() { clean python3 "$tmp/clone/skills/rigor/scripts/mode-hook.py" <<< "{\"hook_event_name\":\"SessionStart\",\"session_id\":\"s\",\"source\":\"$1\"}"; }
wait_for() { for _ in $(seq 100); do "$@" && return 0; perl -e 'select(undef,undef,undef,0.1)'; done; return 1; }
settled() { [[ -e "$home/.rigor/last-update-check" && ! -e "$home/.rigor/update.lock" ]]; }  # a background run finished
now() { perl -MTime::HiRes=time -e 'printf "%.3f", time'; }

# The hook, through a real launch.
v=$(release zz-new)
s=$(now); out="$(hook startup 2>&1)"; e=$(now)
check "startup hook returns in under 0.3s and prints nothing ($(perl -e "printf '%.3f', $e-$s")s)" perl -e "exit(!($e-$s < 0.3 && q{$out} eq q{}))"
check "  the detached updater fast-forwards the clone" wait_for head_is "$v"
check "  install.sh reran: the new skill is linked" wait_for test -f "$home/.claude/skills/zz-new/SKILL.md"
check "  the log says so" wait_for logged "updated .* -> ${v:0:7}"
wait_for settled
v2=$(release); new_day; hook compact; perl -e 'select(undef,undef,undef,1)'
check "compaction doesn't start it" bash -c "[ \"\$(git -C '$tmp/clone' rev-parse HEAD)\" != '$v2' ]"
hook startup
check "  a startup does" wait_for head_is "$v2"
wait_for settled

# The updater's rules, run directly.
v3=$(release); update
check "a second run the same day does nothing" head_is "$v2"
new_day; update
check "  the next day it updates" head_is "$v3"

v4=$(release); new_day
for _ in 1 2 3 4 5 6; do update & done; wait
check "six simultaneous runs update once" bash -c "head_is() { [ \"\$(git -C '$tmp/clone' rev-parse HEAD)\" = \"\$1\" ]; }; head_is $v4 && [ \$(grep -c 'updated .* -> ${v4:0:7}' '$home/.rigor/update.log') -eq 1 ] && [ ! -e '$home/.rigor/update.lock' ]"

vl=$(release); new_day; mkdir "$home/.rigor/update.lock"; update
check "while another run holds the lock, a run does nothing" bash -c "! git -C '$tmp/clone' merge-base --is-ancestor $vl HEAD 2>/dev/null"
touch -t 202001010000 "$home/.rigor/update.lock"; update
check "  a lock over 10 minutes old (a killed or stuck run) is taken over" head_is "$vl"

v5=$(release); new_day
git -C "$tmp/clone" remote set-url origin "$tmp/nowhere"; update
check "offline: logged, clone untouched, and not counted for the day" bash -c "tail -1 '$home/.rigor/update.log' | grep -q 'fetch failed' && [ ! -e '$home/.rigor/last-update-check' ]"
git -C "$tmp/clone" remote set-url origin "$tmp/origin"; update
check "  the next session start retries and updates" head_is "$v5"

v6=$(release zz-six); new_day
cp "$home/.claude/settings.json" "$tmp/settings.good"; echo '{ broken' > "$home/.claude/settings.json"; update
check "install.sh fails: logged and not counted for the day" bash -c "tail -1 '$home/.rigor/update.log' | grep -q 'install.sh failed' && [ ! -e '$home/.rigor/last-update-check' ] && [ ! -e '$home/.claude/skills/zz-six' ]"
cp "$tmp/settings.good" "$home/.claude/settings.json"; update
check "  the retry installs it although the clone was already updated" bash -c "test -f '$home/.claude/skills/zz-six/SKILL.md' && tail -1 '$home/.rigor/update.log' | grep -q 'installed ${v6:0:7}'"

g clone -q "$tmp/origin" "$tmp/proj" && g -C "$tmp/proj" reset -q --hard HEAD~1
proj_head="$(git -C "$tmp/proj" rev-parse HEAD)"
v7=$(release); new_day; update env GIT_DIR="$tmp/proj/.git" GIT_WORK_TREE="$tmp/proj"
check "an inherited GIT_DIR doesn't redirect it to another repo" bash -c "[ \"\$(git -C '$tmp/proj' rev-parse HEAD)\" = '$proj_head' ] && [ \"\$(git -C '$tmp/clone' rev-parse HEAD)\" = '$v7' ]"

v8=$(release); new_day; echo local > "$tmp/clone/README.md"; update
check "uncommitted changes: skipped, clone untouched" bash -c "$(declare -f head_is logged); tmp='$tmp'; home='$home'; head_is $v7 && logged 'uncommitted'"
git -C "$tmp/clone" checkout -q README.md && git -C "$tmp/clone" checkout -q -b feature; new_day; update
check "not on main: skipped" bash -c "$(declare -f logged); home='$home'; logged \"isn't on main\""
git -C "$tmp/clone" checkout -q main && g -C "$tmp/clone" commit -q --allow-empty -m mine; new_day; update
check "local commits on main: skipped, the commit kept" bash -c "$(declare -f logged); home='$home'; logged 'local commits' && [ \"\$(git -C '$tmp/clone' log -1 --format=%s)\" = mine ]"
g -C "$tmp/clone" reset -q --hard "$v7"
g -C "$tmp/origin" reset -q --hard "$v7"; g -C "$tmp/clone" commit -q --allow-empty -m ahead; new_day; update
check "local commits and nothing new upstream: skipped, not installed" bash -c "$(declare -f logged); home='$home'; logged 'local commits' && [ \"\$(cat '$home/.rigor/installed-rev')\" != \"\$(git -C '$tmp/clone' rev-parse HEAD)\" ]"
g -C "$tmp/clone" reset -q --hard "$v7"

echo mine > "$tmp/clone/notes.txt"; echo notes.txt >> "$tmp/clone/.git/info/exclude"
echo theirs > "$tmp/origin/notes.txt"; v9=$(release); new_day; update
check "an ignored local file the update would overwrite: skipped, file kept" bash -c "grep -qx mine '$tmp/clone/notes.txt' && ! git -C '$tmp/clone' merge-base --is-ancestor $v9 HEAD 2>/dev/null"
rm "$tmp/clone/notes.txt"

touch "$home/.rigor/no-auto-update"; new_day; update
check "~/.rigor/no-auto-update turns it off" bash -c "! git -C '$tmp/clone' merge-base --is-ancestor $v9 HEAD 2>/dev/null"
rm "$home/.rigor/no-auto-update"; update
check "  and removing it turns it back on" head_is "$v9"

echo mine > "$tmp/clone/draft.txt"; v10=$(release); new_day; update
check "an untracked file doesn't block the update" head_is "$v10"
echo theirs > "$tmp/origin/draft.txt"; v11=$(release); new_day; update
check "  but an update that would overwrite it is skipped, and the file kept" bash -c "$(declare -f logged); home='$home'; logged \"can't fast-forward\" && grep -qx mine '$tmp/clone/draft.txt' && ! git -C '$tmp/clone' merge-base --is-ancestor $v11 HEAD 2>/dev/null"

exit $((failed > 0))
