#!/usr/bin/env bash
# Fast-forward this clone to origin/main and reinstall. mode-hook.py starts it detached at most once
# a day when a session starts, so it must never prompt, and it leaves alone a clone you're working in:
# not on main, uncommitted changes, or local commits (the fast-forward fails). Result: ~/.rigor/last-update.log
set -u
root="$(cd "$(dirname "$0")/.." && pwd -P)"
log="$HOME/.rigor/last-update.log"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" > "$log"; exit 0; }
cd "$root" || exit 0

[[ "$(git symbolic-ref --short -q HEAD)" == main ]] || say "skipped: $root isn't on main"
[[ -z "$(git status --porcelain)" ]] || say "skipped: $root has uncommitted changes"

export GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh} -o BatchMode=yes -o ConnectTimeout=10"
before="$(git rev-parse HEAD)"
git -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=20 fetch -q origin main 2>/dev/null || say "skipped: fetch failed"
git merge -q --ff-only FETCH_HEAD 2>/dev/null || say "skipped: can't fast-forward (local commits on main?)"
after="$(git rev-parse HEAD)"
[[ "$before" == "$after" ]] && say "up to date at ${after:0:7}"
"$root/install.sh" > /dev/null 2>&1 || say "updated ${before:0:7} -> ${after:0:7}, but install.sh failed; run it by hand"
say "updated ${before:0:7} -> ${after:0:7}"
