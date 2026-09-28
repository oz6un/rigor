#!/usr/bin/env python3
"""Add or remove rigor's mode hook in a host's hook config, leaving everything else alone.

Usage: hooks.py add|remove CONFIG_JSON MODE_HOOK_SCRIPT
CONFIG_JSON is ~/.claude/settings.json or ~/.codex/hooks.json; both use the same "hooks" layout.
"""
import json
import os
import sys

EVENTS = ("UserPromptSubmit", "SessionStart")

action, path, script = sys.argv[1:]
config = json.load(open(path)) if os.path.exists(path) else {}
hooks = config.setdefault("hooks", {})
for event in EVENTS:
    groups = [g for g in hooks.get(event, [])
              if not any("mode-hook.py" in h.get("command", "") for h in g.get("hooks", []))]
    if action == "add":
        groups.append({"hooks": [{"type": "command", "command": f'python3 "{script}" || true'}]})
    if groups:
        hooks[event] = groups
    else:
        hooks.pop(event, None)
if not hooks:
    del config["hooks"]

if not config:
    if os.path.exists(path):
        os.remove(path)
else:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
