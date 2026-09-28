#!/usr/bin/env python3
"""Consistency checks for mstack. Run from anywhere: python3 scripts/check.py"""
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
skills = root / "skills"
skill_names = {p.name for p in skills.iterdir() if (p / "SKILL.md").exists()}
principles = {p.stem for p in (skills / "principles").glob("*.md")} - {"SKILL"}
playbooks = {p.name for p in (skills / "rigor" / "playbooks").glob("*.md")}
leftover = re.compile(r"\b(cursor|poteto|pstack|grok|sicko)\b", re.I)
problems = []


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^([a-z-]+): *(.*)$", m.group(1), re.M)) if m else {}


for name in sorted(skill_names):
    fm = frontmatter((skills / name / "SKILL.md").read_text())
    if fm.get("name") != name:
        problems.append(f"skills/{name}/SKILL.md: name is {fm.get('name')!r}, expected {name!r}")
    if not 0 < len(fm.get("description", "")) <= 1024:
        problems.append(f"skills/{name}/SKILL.md: description missing or over 1024 chars")

docs = [p for p in root.rglob("*.md") if "node_modules" not in p.parts and ".git" not in p.parts]
for path in docs:
    rel = path.relative_to(root)
    text = path.read_text()
    for m in re.finditer(r"playbooks/([a-z0-9-]+\.md)", text):
        if m.group(1) not in playbooks:
            problems.append(f"{rel}: unknown playbook {m.group(1)}")
    for m in re.finditer(r"the `([a-z0-9-]+)` principle", text):
        if m.group(1) not in principles:
            problems.append(f"{rel}: unknown principle {m.group(1)}")
    for m in re.finditer(r"the `([a-z0-9-]+)` skill", text):
        if m.group(1) not in skill_names:
            problems.append(f"{rel}: unknown skill {m.group(1)}")
    for m in re.finditer(r"\]\(([^)#:\s]+)(?:#[^)]*)?\)", text):
        if re.search(r"[./]", m.group(1)) and not (path.parent / m.group(1)).exists():
            problems.append(f"{rel}: broken link {m.group(1)}")
    if rel.parts[0] != "README.md":
        for n, line in enumerate(text.splitlines(), 1):
            if leftover.search(line):
                problems.append(f"{rel}:{n}: leftover term: {line.strip()[:80]}")

rigor_index = set(re.findall(r"^- `([a-z0-9-]+)`:", (skills / "rigor" / "SKILL.md").read_text(), re.M))
principles_index = set(re.findall(r"^- \[[^\]]+\]\(([a-z0-9-]+)\.md\)", (skills / "principles" / "SKILL.md").read_text(), re.M))
for label, index in (("rigor/SKILL.md", rigor_index), ("principles/SKILL.md", principles_index)):
    if index != principles:
        problems.append(f"{label} principle index differs from files: "
                        f"missing {sorted(principles - index)}, extra {sorted(index - principles)}")

for md in sorted((root / "agents").glob("*.md")):
    toml = root / "codex" / "agents" / f"{md.stem}.toml"
    if not toml.exists():
        problems.append(f"agents/{md.name}: no codex/agents/{toml.name}")
        continue
    md_text, toml_text = md.read_text(), toml.read_text()
    body = re.search(r"developer_instructions = ('''|\"\"\")\n(.*?)\1", toml_text, re.S)
    desc = re.search(r'^description = "(.*)"$', toml_text, re.M)
    if not body or body.group(2).strip() != md_text.split("---\n", 2)[2].strip():
        problems.append(f"codex/agents/{toml.name}: instructions differ from agents/{md.name}")
    if not desc or desc.group(1) != frontmatter(md_text).get("description"):
        problems.append(f"codex/agents/{toml.name}: description differs from agents/{md.name}")

versions = {p: json.loads((root / p).read_text()).get("version") for p in (".claude-plugin/plugin.json", "plugin.json")}
if len(set(versions.values())) != 1:
    problems.append(f"manifest versions differ: {versions}")

print("\n".join(problems) or f"ok: {len(skill_names)} skills, {len(principles)} principles, {len(playbooks)} playbooks")
sys.exit(1 if problems else 0)
