#!/usr/bin/env bash
# Install rigor's skills and agents for Claude Code and Codex from this clone.
#
#   ./install.sh              install, or repair after moving the clone (safe to rerun)
#   ./install.sh --uninstall  remove everything this script installed
#
# Skills and Claude Code agents are symlinks into this clone, so `git pull` (or a local edit)
# takes effect in new sessions without reinstalling. Codex agents are copied, so rerun this
# script after pulling if codex/agents/ changed.
# The hook also starts scripts/auto-update.sh at session start, which updates at most once a day.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd -P)"
claude_skills="$HOME/.claude/skills"
codex_skills="$HOME/.agents/skills"
claude_agents="$HOME/.claude/agents"
codex_agents="${CODEX_HOME:-$HOME/.codex}/agents"
# rigor's stay-on hook: registered globally in both hosts, silent except in sessions where rigor was
# invoked (see skills/rigor/scripts/mode-hook.py).
claude_settings="$HOME/.claude/settings.json"
codex_hooks="${CODEX_HOME:-$HOME/.codex}/hooks.json"
mode_hook="$root/skills/rigor/scripts/mode-hook.py"
mode="${1:-install}"

# A link is ours if it points into this clone or into another rigor clone (moving to a new clone
# takes the links over). A skill or agent link points at <clone>/<dir>/<name>.
is_clone() { [[ -f "$1/install.sh" && -f "$1/skills/rigor/scripts/mode-hook.py" ]]; }
ours() { [[ -L "$1" ]] || return 1; local t; t="$(readlink "$1")"; [[ "$t" == "$root/"* ]] || is_clone "${t%/*/*}"; }
stamp="# installed by rigor's install.sh"
# A Codex agent file is ours if it carries the stamp, or is an unstamped copy from an older install.
ours_toml() { [[ -f "$2" ]] && { [[ "$(head -1 "$2")" == "$stamp"* ]] || cmp -s "$1" "$2"; }; }
skipped=()

link() {
  local target="$1" dest="$2"
  if ours "$dest" || [[ -L "$dest" && ! -e "$dest" ]]; then
    ln -sfn "$target" "$dest"
    linked=$((linked + 1))
  elif [[ -e "$dest" || -L "$dest" ]]; then
    echo "skip $dest: already exists and isn't from this clone" >&2
    skipped+=("$dest")
    return
  else
    ln -s "$target" "$dest"
    linked=$((linked + 1))
  fi
}

uninstall() {
  for dir in "$claude_skills" "$codex_skills" "$claude_agents"; do
    [[ -d "$dir" ]] || continue
    for entry in "$dir"/*; do ours "$entry" && rm "$entry" && echo "removed $entry"; done
  done
  for dest in "$codex_agents"/*.toml; do
    toml="$root/codex/agents/$(basename "$dest")"
    if ours_toml "$toml" "$dest"; then rm "$dest" && echo "removed $dest"; fi
  done
  local status=0
  for config in "$claude_settings" "$codex_hooks"; do
    if python3 "$root/scripts/hooks.py" remove "$config" "$mode_hook"; then
      echo "removed rigor's hook from $config"
    else
      [[ $? -eq 1 ]] || status=1
    fi
  done
  return $status
}

case "$mode" in
  --uninstall) uninstall; exit ;;  # removes what it can and reports a config it can't parse
  install) ;;
  *) echo "usage: install.sh [--uninstall]" >&2; exit 2 ;;
esac

# Refuse to install on a config we can't parse, before changing anything.
python3 "$root/scripts/hooks.py" check "$claude_settings" "$mode_hook"
python3 "$root/scripts/hooks.py" check "$codex_hooks" "$mode_hook"

mkdir -p "$claude_skills" "$codex_skills" "$claude_agents" "$codex_agents"

# Drop links to skills that no longer exist in this clone.
for dir in "$claude_skills" "$codex_skills" "$claude_agents"; do
  for entry in "$dir"/*; do ours "$entry" && [[ ! -e "$entry" ]] && rm "$entry"; done
done

for dest in "$codex_agents"/*.toml; do
  toml="$root/codex/agents/$(basename "$dest")"
  if [[ ! -f "$toml" ]] && ours_toml "$toml" "$dest"; then
    rm "$dest"
  fi
done

linked=0
for skill in "$root"/skills/*/; do
  [[ -f "$skill/SKILL.md" ]] || continue
  name="$(basename "$skill")"
  link "$root/skills/$name" "$claude_skills/$name"
  link "$root/skills/$name" "$codex_skills/$name"
done

for agent in "$root"/agents/*.md; do
  link "$agent" "$claude_agents/$(basename "$agent")"
done
for toml in "$root"/codex/agents/*.toml; do
  [[ -f "$toml" ]] || continue
  dest="$codex_agents/$(basename "$toml")"
  if [[ -e "$dest" ]] && ! ours_toml "$toml" "$dest"; then
    echo "skip $dest: already exists and isn't from this clone" >&2
    skipped+=("$dest")
    continue
  fi
  { echo "$stamp from $root"; cat "$toml"; } > "$dest"
done
python3 "$root/scripts/hooks.py" add "$claude_settings" "$mode_hook" || [[ $? -eq 1 ]]
python3 "$root/scripts/hooks.py" add "$codex_hooks" "$mode_hook" || [[ $? -eq 1 ]]

if [[ ${#skipped[@]} -gt 0 ]]; then
  echo "WARNING: ${#skipped[@]} item(s) were skipped because you already have your own with the same name." >&2
  echo "rigor will use yours in their place. Rename or remove them and rerun to use rigor's:" >&2
  printf '  %s\n' "${skipped[@]}" >&2
fi
echo "Installed from $root: $linked skill and agent links for Claude Code and Codex."
echo "Codex only: after a first install, or if Codex stops running rigor, open Codex, run /hooks, and trust rigor's two hooks."
echo "rigor updates itself from GitHub once a day at session start; to stop that: touch ~/.rigor/no-auto-update"
echo "Then start a new session and type /rigor (Claude Code) or \$rigor (Codex). It stays on for the rest of that session."
