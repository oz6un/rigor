#!/usr/bin/env python3
"""Runs mode-hook.py through a session's life and checks what it tells the model at each step."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "skills" / "rigor" / "scripts" / "mode-hook.py"
home = tempfile.mkdtemp()


def hook(event, session="s1", **fields):
    payload = {"hook_event_name": event, "session_id": session, **fields}
    run = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True,
                         text=True, env={**os.environ, "HOME": home})
    assert run.returncode == 0, f"exit {run.returncode}: {run.stderr}"
    return json.loads(run.stdout)["hookSpecificOutput"]["additionalContext"] if run.stdout else None


def prompt(text, session="s1"):
    return hook("UserPromptSubmit", session, prompt=text)


def start(source, session="s1"):
    return hook("SessionStart", session, source=source)


steps = [
    ("off before invocation", prompt("fix the bug"), None),
    ("compaction before invocation", start("compact"), None),
    ("/rigor turns it on", prompt("/rigor fix the bug"), "rigor is on for this session."),
    ("later turn keeps it on", prompt("now the next task"), "rigor is on for this session."),
    ("compaction asks for a re-read", start("compact"), "just compacted"),
    ("a second compaction right away doesn't ask again", start("compact"), "rigor is on for this session. New task"),
    ("a fresh startup says nothing", start("startup"), None),
    ("other sessions stay off", prompt("next task", session="s2"), None),
    ("$rigor turns Codex sessions on", prompt("$rigor go", session="s2"), "rigor is on for this session."),
    ("'rigor off' turns it off", prompt("ok, rigor off please"), None),
    ("stays off after that", prompt("another task"), None),
    ("compaction after off says nothing", start("compact"), None),
    ("words like /rigorous don't count", prompt("the /rigorous path", session="s3"), None),
    ("bad input never blocks", subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True).returncode, 0),
]

failed = 0
for label, got, want in steps:
    ok = got == want if want is None or isinstance(want, int) else (got is not None and want in got)
    failed += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}"))
sys.exit(1 if failed else 0)
