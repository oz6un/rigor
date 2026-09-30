#!/usr/bin/env python3
"""Add, remove, or check rigor's mode hook in a host's hook config, leaving everything else alone.

Usage: hooks.py check|add|remove CONFIG_JSON MODE_HOOK_SCRIPT
CONFIG_JSON is ~/.claude/settings.json or ~/.codex/hooks.json; both use the same "hooks" layout.
Only hook entries whose command runs rigor's own script are touched. The file is rewritten only
when something changed, atomically, and never deleted.
Exit status: 0 changed (or check passed), 1 nothing to change, 2 unreadable config.
"""
import json
import os
import shlex
import sys
import tempfile

EVENTS = ("UserPromptSubmit", "SessionStart")
MARK = "skills/rigor/scripts/mode-hook.py"

action, path, script = sys.argv[1:]


def fail(message):
    print(f"hooks.py: {path}: {message}; fix it, then rerun install.sh", file=sys.stderr)
    sys.exit(2)


def load():
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
    except (ValueError, OSError) as e:
        fail(str(e))
    if not isinstance(data, dict) or not isinstance(data.get("hooks", {}), dict):
        fail("expected a JSON object with a hooks object")
    for event in EVENTS:
        groups = data.get("hooks", {}).get(event, [])
        if not isinstance(groups, list):
            fail(f"hooks.{event} must be a list")
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks", []), list):
                fail(f"hooks.{event} must contain objects with hook lists")
            if any(not isinstance(hook, dict) for hook in group.get("hooks", [])):
                fail(f"hooks.{event} handlers must be objects")
    return data


def ours(hook):
    return MARK in str(hook.get("command", ""))


config = load()
if action == "check":
    sys.exit(0)

before = json.dumps(config, sort_keys=True)
hooks = config.setdefault("hooks", {})
for event in EVENTS:
    groups = []
    for group in hooks.get(event, []):
        kept = [h for h in group.get("hooks", []) if not ours(h)]
        if kept:
            groups.append({**group, "hooks": kept})
        elif not group.get("hooks"):
            groups.append(group)
    if action == "add":
        groups.append({"hooks": [{"type": "command", "command": f"python3 {shlex.quote(script)} || true"}]})
    if groups:
        hooks[event] = groups
    else:
        hooks.pop(event, None)
if not hooks:
    del config["hooks"]

if json.dumps(config, sort_keys=True) == before:
    sys.exit(1)
tmp = None
try:
    target = os.path.realpath(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(target), prefix=".rigor-")
    with os.fdopen(fd, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")
    if os.path.exists(target):
        os.chmod(tmp, os.stat(target).st_mode & 0o777)
    os.replace(tmp, target)
except OSError as e:
    fail(str(e))
finally:
    if tmp is not None and os.path.exists(tmp):
        os.unlink(tmp)
