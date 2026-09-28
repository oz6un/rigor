#!/usr/bin/env python3
"""UserPromptSubmit hook that keeps rigor on for the rest of a session once it's invoked.

Claude Code runs it from rigor's frontmatter with --active: the hook only exists after /rigor ran.
Codex runs it globally (installed by install.sh): it turns on for a session when a prompt mentions
$rigor and stays on after that. Either way it adds one reminder line to each turn. It must never exit 2: that blocks the prompt.
"""
import json
import re
import sys
import time
from pathlib import Path

skill = Path(__file__).resolve().parent.parent / "SKILL.md"
state = Path.home() / ".rigor" / "sessions"

try:
    event = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
session = re.sub(r"[^\w-]", "", str(event.get("session_id", "")))

if "--active" not in sys.argv:
    marker = state / session
    if session and re.search(r"\$rigor\b", event.get("prompt", "")):
        state.mkdir(parents=True, exist_ok=True)
        marker.touch()
        cutoff = time.time() - 30 * 86400
        for old in state.iterdir():
            if old.stat().st_mtime < cutoff:
                old.unlink(missing_ok=True)
    if not (session and marker.exists()):
        sys.exit(0)

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": (
        "rigor is on for this session. New task that matches a rigor playbook or needs care: "
        f"follow the rigor skill (re-read {skill} if it's no longer in context). "
        "Casual turn, or the user turned rigor off: don't."
    ),
}}))
