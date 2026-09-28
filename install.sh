#!/usr/bin/env bash
# Install rigor's skills and agents for Claude Code and Codex from this clone.
#
#   ./install.sh              install, or repair after moving the clone (safe to rerun)
#   ./install.sh --uninstall  remove everything this script installed
#
# Skills and Claude Code agents are symlinks into this clone, so `git pull` (or a local edit)
# takes effect in new sessions without reinstalling. Codex agents are copied, so rerun this
# script after pulling if codex/agents/ changed.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd -P)"
claude_skills="$HOME/.claude/skills"
codex_skills="$HOME/.agents/skills"
claude_agents="$HOME/.claude/agents"
codex_agents="${CODEX_HOME:-$HOME/.codex}/agents"
# Codex has no skill-scoped hooks, so rigor's stay-on reminder is a global hook that only speaks in
# sessions where $rigor was used. Claude Code gets the same hook from rigor's frontmatter.
codex_hooks="${CODEX_HOME:-$HOME/.codex}/hooks.json"
mode_hook="$root/skills/rigor/scripts/mode-hook.py"
mode="${1:-install}"

ours() { [[ -L "$1" && "$(readlink "$1")" == "$root/"* ]]; }

link() {
  local target="$1" dest="$2"
  if ours "$dest" || [[ -L "$dest" && ! -e "$dest" ]]; then
    ln -sfn "$target" "$dest"
  elif [[ -e "$dest" || -L "$dest" ]]; then
    echo "skip $dest: already exists and isn't from this clone" >&2
    return
  else
    ln -s "$target" "$dest"
  fi
}

uninstall() {
  for dir in "$claude_skills" "$codex_skills" "$claude_agents"; do
    [[ -d "$dir" ]] || continue
    for entry in "$dir"/*; do ours "$entry" && rm "$entry" && echo "removed $entry"; done
  done
  for toml in "$root"/codex/agents/*.toml; do
    dest="$codex_agents/$(basename "$toml")"
    [[ -f "$dest" ]] && cmp -s "$toml" "$dest" && rm "$dest" && echo "removed $dest"
  done
  python3 "$root/scripts/codex-hook.py" remove "$codex_hooks" "$mode_hook" && echo "removed rigor's hook from $codex_hooks"
  return 0
}

case "$mode" in
  --uninstall) uninstall; exit 0 ;;
  install) ;;
  *) echo "usage: install.sh [--uninstall]" >&2; exit 2 ;;
esac

mkdir -p "$claude_skills" "$codex_skills" "$claude_agents" "$codex_agents"

# Drop links to skills that no longer exist in this clone.
for dir in "$claude_skills" "$codex_skills" "$claude_agents"; do
  for entry in "$dir"/*; do ours "$entry" && [[ ! -e "$entry" ]] && rm "$entry"; done
done

count=0
for skill in "$root"/skills/*/; do
  name="$(basename "$skill")"
  link "$root/skills/$name" "$claude_skills/$name"
  link "$root/skills/$name" "$codex_skills/$name"
  count=$((count + 1))
done

for agent in "$root"/agents/*.md; do
  link "$agent" "$claude_agents/$(basename "$agent")"
done
cp "$root"/codex/agents/*.toml "$codex_agents/"
python3 "$root/scripts/codex-hook.py" add "$codex_hooks" "$mode_hook"

echo "Installed $count skills and $(ls "$root"/agents/*.md | wc -l | tr -d ' ') agents for Claude Code and Codex."
echo "Codex only: open Codex, run /hooks, and trust the rigor hook once."
echo "Then start a new session and type /rigor (Claude Code) or \$rigor (Codex). It stays on for the rest of that session."
