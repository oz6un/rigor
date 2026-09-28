#!/usr/bin/env bash
# Run a prompt (read from stdin) through the other coding CLI and print its final answer.
# From Claude Code this calls `codex exec`; from Codex it calls `claude -p`.
#
# Usage: second-opinion.sh [--cli codex|claude] [--write] [--cd DIR] < prompt.txt
# Exit 2: bad usage. Exit 3: the target CLI is not installed (caller should fall back).

set -euo pipefail

cli=""
write=0
dir="$PWD"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cli) cli="${2:-}"; shift 2 ;;
    --write) write=1; shift ;;
    --cd) dir="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
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
    command -v codex >/dev/null || { echo "second-opinion: codex not installed" >&2; exit 3; }
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
    command -v claude >/dev/null || { echo "second-opinion: claude not installed" >&2; exit 3; }
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
