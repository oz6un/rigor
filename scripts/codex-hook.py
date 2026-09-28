#!/usr/bin/env python3
"""Add or remove rigor's stay-on hook in Codex's hooks.json, leaving other hooks alone.

Usage: codex-hook.py add|remove HOOKS_JSON MODE_HOOK_SCRIPT
"""
import json
import os
import sys

action, path, script = sys.argv[1:]
config = json.load(open(path)) if os.path.exists(path) else {}
groups = config.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
groups[:] = [g for g in groups if not any("mode-hook.py" in h.get("command", "") for h in g.get("hooks", []))]
if action == "add":
    groups.append({"hooks": [{"type": "command", "command": f'python3 "{script}" || true'}]})
if not groups:
    del config["hooks"]["UserPromptSubmit"]
if not config["hooks"]:
    del config["hooks"]
if not config:
    if os.path.exists(path):
        os.remove(path)
else:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
