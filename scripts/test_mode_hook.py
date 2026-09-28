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
    ("a second compaction right away doesn't ask again", start("compact"), "never weaken a test"),
    ("a fresh startup says nothing", start("startup"), None),
    ("other sessions stay off", prompt("next task", session="s2"), None),
    ("$rigor turns Codex sessions on", prompt("$rigor go", session="s2"), "rigor is on for this session."),
    ("talking about rigor off doesn't turn it off", prompt("make sure users can say rigor off"), "rigor is on for this session."),
    ("/rigor-agent doesn't turn a session on", prompt("what does /rigor-agent do?", session="s4"), None),
    ("/rigor wins over a mention of rigor off", prompt('/rigor audit the "rigor off" handling', session="s5"), "rigor is on for this session."),
    ("'rigor off' turns it off and says so", prompt("rigor off, thanks"), "rigor is now off"),
    ("stays off after that", prompt("another task"), None),
    ("compaction after off says nothing", start("compact"), None),
    ("words like /rigorous don't count", prompt("the /rigorous path", session="s3"), None),
    ("bad input never blocks", subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True).returncode, 0),
]

docs = Path(__file__).resolve().parent.parent
for doc in [docs / "README.md", *sorted((docs / "docs" / "guide").glob("*.md"))]:
    for n, line in enumerate(doc.read_text().splitlines(), 1):
        if line.startswith(("/rigor", "$rigor", "/goal")) and "rigor" in line:
            steps.append((f"documented example turns rigor on: {doc.name}:{n}",
                          prompt(line, session=f"doc-{doc.stem}-{n}"), "rigor is on for this session."))

failed = 0
for label, got, want in steps:
    ok = got == want if want is None or isinstance(want, int) else (got is not None and want in got)
    failed += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}"))
sys.exit(1 if failed else 0)
