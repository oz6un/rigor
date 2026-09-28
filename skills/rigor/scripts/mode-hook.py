#!/usr/bin/env python3
"""Keeps rigor on for the rest of a session once it's invoked, in Claude Code and Codex.

install.sh registers this for UserPromptSubmit and SessionStart in both hosts. Per session, a
marker file under ~/.rigor/sessions means "on":

  prompt with /rigor or $rigor        -> on
  prompt with "rigor off"             -> off
  any prompt while on                 -> one-line reminder
  SessionStart compact/resume while on -> tell the model to re-read SKILL.md now, because
                                          compaction drops or truncates the skill's text

The state lives in the file, not the conversation, so compaction can't lose an "off".
Never exit 2: in UserPromptSubmit that blocks the user's prompt.
"""
import json
import re
import sys
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"
STATE = Path.home() / ".rigor" / "sessions"
ON = re.compile(r"(^|\s)[/$]rigor\b")
OFF = re.compile(r"\brigor\s+off\b|\b(stop|disable|exit|turn\s+off)\s+(using\s+)?rigor\b|\bturn\s+rigor\s+off\b", re.I)
KEEP_DAYS = 30
REREAD_COOLDOWN = 120


def reminder(event_name, source):
    if event_name == "SessionStart":
        return (f"rigor is on for this session and the context was just {'compacted' if source == 'compact' else 'resumed'}. "
                f"Before continuing, re-read {SKILL} in full; its text may be missing or cut short. "
                'Stay in the playbook you were running. The user can turn rigor off by saying "rigor off".')
    return ("rigor is on for this session. For a new task that needs care, pick its rigor playbook "
            f"({SKILL}; re-read it if it's no longer in context). Back every \"done\" with evidence from this "
            "session, and never weaken a test to make it pass. Casual turn: skip rigor.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    session = re.sub(r"[^\w-]", "", str(event.get("session_id", "")))
    if not session:
        return
    name = event.get("hook_event_name", "")
    marker = STATE / session

    if name == "UserPromptSubmit":
        prompt = event.get("prompt") or ""
        if OFF.search(prompt):
            marker.unlink(missing_ok=True)
            return
        if ON.search(prompt):
            STATE.mkdir(parents=True, exist_ok=True)
            marker.touch()
            cutoff = time.time() - KEEP_DAYS * 86400
            for old in STATE.iterdir():
                if old.stat().st_mtime < cutoff:
                    old.unlink(missing_ok=True)
    elif name != "SessionStart" or event.get("source") not in ("compact", "resume"):
        return

    if not marker.exists():
        return
    text = reminder(name, event.get("source"))
    if name == "SessionStart":
        # Re-reading SKILL.md into a nearly full context can trigger the next compaction; after one
        # re-read request, fall back to the short reminder for a while so that can't loop.
        last = float(marker.read_text() or 0)
        if time.time() - last < REREAD_COOLDOWN:
            text = reminder("UserPromptSubmit", None)
        else:
            marker.write_text(str(time.time()))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": name, "additionalContext": text}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
