#!/usr/bin/env bash
# Fast-forward this clone to origin/main and reinstall. mode-hook.py starts it detached on every
# session start; it does the real work at most once a day, one run at a time, and never prompts.
# It leaves alone a clone you're working in: not on main, uncommitted changes, or local commits.
# Off: touch ~/.rigor/no-auto-update. History: ~/.rigor/update.log
set -u
dir="$HOME/.rigor"
[[ -e "$dir/no-auto-update" ]] && exit 0
stamp="$dir/last-update-check"
[[ -n "$(find "$stamp" -mmin -1440 2>/dev/null)" ]] && exit 0

mkdir -p "$dir"
lock="$dir/update.lock"
[[ -n "$(find "$lock" -maxdepth 0 -mmin +10 2>/dev/null)" ]] && rmdir "$lock"  # left by a killed run
mkdir "$lock" 2>/dev/null || exit 0
trap 'rmdir "$lock"' EXIT

log="$dir/update.log"
note() { echo "$(date '+%Y-%m-%d %H:%M:%S') $(echo "$*" | grep -v '^hint:' | tr -s '\n\t' '  ')" >> "$log"; tail -n 200 "$log" > "$log.tmp" && mv "$log.tmp" "$log"; }
# A finished check counts for the day; a failed fetch (offline) is retried at the next session start.
finish() { note "$@"; touch "$stamp"; exit 0; }

# Ignore a GIT_DIR or GIT_WORK_TREE inherited from the host, which would point git at another repo.
unset $(git rev-parse --local-env-vars)
root="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$root" || exit 0
in_use() {
  [[ "$(git symbolic-ref --short -q HEAD)" == main ]] || finish "skipped: $root isn't on main"
  [[ -z "$(git --no-optional-locks status --porcelain)" ]] || finish "skipped: $root has uncommitted changes"
}
in_use

# Never prompt: no terminal prompt, askpass program, or credential helper, and SSH in batch mode on
# top of the user's own SSH command.
unset GIT_ASKPASS SSH_ASKPASS
export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never SSH_ASKPASS_REQUIRE=never
if [[ -z "${GIT_SSH:-}" ]]; then
  ssh_cmd="${GIT_SSH_COMMAND:-$(git config core.sshCommand || echo ssh)}"
  export GIT_SSH_COMMAND="$ssh_cmd -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=2"
fi
if ! out="$(git -c credential.helper= -c core.askPass= -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=20 \
    fetch -q origin main 2>&1)"; then
  note "fetch failed, retrying next session: $out"
  exit 0
fi
target="$(git rev-parse FETCH_HEAD)"

in_use  # again: you may have switched branches or started editing during the fetch
before="$(git rev-parse HEAD)"
if ! out="$(git merge -q --ff-only --no-overwrite-ignore "$target" 2>&1)"; then
  finish "skipped: can't fast-forward main to ${target:0:7}: $out"
fi
head="$(git rev-parse HEAD)"

# Install whenever HEAD differs from the last successful install, so a failed or interrupted
# install is retried instead of being hidden behind "up to date".
installed="$dir/installed-rev"
[[ "$(cat "$installed" 2>/dev/null)" == "$head" ]] && finish "up to date at ${head:0:7}"
if ! out="$("$root/install.sh" 2>&1 >/dev/null)"; then
  note "install.sh failed at ${head:0:7}, retrying next session: $out"
  exit 0
fi
echo "$head" > "$installed"
[[ -n "$out" ]] && note "install.sh: $out"
if [[ "$before" == "$head" ]]; then finish "installed ${head:0:7}"; fi
finish "updated ${before:0:7} -> ${head:0:7}"
