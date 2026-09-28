#!/usr/bin/env bash
# Run a prompt (read from stdin) through the other coding CLI and print its final answer.
# From Claude Code this calls `codex exec`; from Codex it calls `claude -p`.
#
# Usage: second-opinion.sh [--cli codex|claude] [--write] [--cd DIR] < prompt.txt
#
#   (default)   read-only: the other CLI can read files but not edit them
#   --write     let it edit files under DIR; give it a separate worktree
#   --cd DIR    run it in DIR (default: the current directory)
#   --cli NAME  use codex or claude instead of detecting the host
#
# MSTACK_CODEX_MODEL and MSTACK_CLAUDE_MODEL override the model it uses.
#
# Exit codes:
#   0      the answer is on stdout
#   2      bad usage
#   3      the other CLI is not installed: run this seat as a host subagent
#          instead and say so in your report
#   other  the other CLI failed; its output is on stderr

set -euo pipefail

cli=""
write=0
dir="$PWD"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cli) cli="${2:-}"; shift 2 ;;
    --write) write=1; shift ;;
    --cd) dir="${2:-}"; shift 2 ;;
    -h|--help) awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 0 ;;
    *) echo "second-opinion: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$cli" ]]; then
  if [[ -n "${CLAUDECODE:-}" ]]; then
    cli=codex
  elif env | grep -q '^CODEX_'; then
    cli=claude
  else
    echo "second-opinion: can't detect the host CLI; pass --cli codex or --cli claude" >&2
    exit 2
  fi
fi

if [[ -t 0 ]]; then
  echo "second-opinion: pipe the prompt on stdin" >&2
  exit 2
fi
prompt="$(cat)"

case "$cli" in
  codex)
    command -v codex >/dev/null || { echo "second-opinion: codex not installed; run this seat as a host subagent instead and say so in your report" >&2; exit 3; }
    out="$(mktemp)"
    log="$(mktemp)"
    trap 'rm -f "$out" "$log"' EXIT
    sandbox=read-only
    [[ $write -eq 1 ]] && sandbox=workspace-write
    args=(exec -s "$sandbox" -C "$dir" --skip-git-repo-check --ephemeral -o "$out")
    [[ -n "${MSTACK_CODEX_MODEL:-}" ]] && args+=(-m "$MSTACK_CODEX_MODEL")
    if ! printf '%s' "$prompt" | codex "${args[@]}" - >"$log" 2>&1; then
      cat "$log" >&2
      exit 1
    fi
    cat "$out"
    echo
    ;;
  claude)
    command -v claude >/dev/null || { echo "second-opinion: claude not installed; run this seat as a host subagent instead and say so in your report" >&2; exit 3; }
    mode=plan
    [[ $write -eq 1 ]] && mode=acceptEdits
    args=(-p --permission-mode "$mode" --no-session-persistence)
    [[ -n "${MSTACK_CLAUDE_MODEL:-}" ]] && args+=(--model "$MSTACK_CLAUDE_MODEL")
    (cd "$dir" && printf '%s' "$prompt" | claude "${args[@]}")
    ;;
  *)
    echo "second-opinion: --cli must be codex or claude" >&2
    exit 2
    ;;
esac
