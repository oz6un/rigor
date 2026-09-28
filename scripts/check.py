#!/usr/bin/env python3
"""Consistency checks for rigor. Run from anywhere: python3 scripts/check.py"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
skills = root / "skills"
skill_names = {p.name for p in skills.iterdir() if (p / "SKILL.md").exists()}
principles = {p.stem for p in (skills / "principles").glob("*.md")} - {"SKILL"}
playbooks = {p.name for p in (skills / "rigor" / "playbooks").glob("*.md")}
leftover = re.compile(r"\b(cursor|poteto|pstack|grok|sicko|mstack)\b", re.I)
problems = []


def slug(heading):
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", heading.strip().lower()))


def anchors(path):
    return {slug(h) for h in re.findall(r"^#+ (.+)$", path.read_text(), re.M)}


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^([a-z-]+): *(.*)$", m.group(1), re.M)) if m else {}


for name in sorted(skill_names):
    fm = frontmatter((skills / name / "SKILL.md").read_text())
    if fm.get("name") != name:
        problems.append(f"skills/{name}/SKILL.md: name is {fm.get('name')!r}, expected {name!r}")
    if not 0 < len(fm.get("description", "")) <= 1024:
        problems.append(f"skills/{name}/SKILL.md: description missing or over 1024 chars")

hidden = set()
for name in sorted(skill_names):
    text = (skills / name / "SKILL.md").read_text()
    claude_hidden = frontmatter(text).get("disable-model-invocation") == "true"
    policy = skills / name / "agents" / "openai.yaml"
    codex_hidden = policy.exists() and "allow_implicit_invocation: false" in policy.read_text()
    if claude_hidden != codex_hidden:
        problems.append(f"skills/{name}: hidden in {'Claude Code' if claude_hidden else 'Codex'} only; "
                        "set disable-model-invocation and agents/openai.yaml together")
    if claude_hidden:
        hidden.add(name)
for name in sorted(skill_names - {"rigor"}):
    body = (skills / name / "SKILL.md").read_text().split("---\n", 2)[2]
    named = {m for m in re.findall(r"`/?([a-z0-9-]+)`", body) if m in hidden and m != name}
    if named and "<this skill's dir>/../<name>/SKILL.md" not in body:
        problems.append(f"skills/{name}/SKILL.md: names hidden skills {sorted(named)} without saying how to read them")

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
    for m in re.finditer(r"\]\(([^)#:\s]*)(?:#([^)\s]+))?\)", text):
        target = path.parent / m.group(1) if m.group(1) else path
        if m.group(1) and not re.search(r"[./]", m.group(1)):
            continue
        if not target.exists():
            problems.append(f"{rel}: broken link {m.group(1)}")
        elif m.group(2) and target.suffix == ".md" and m.group(2) not in anchors(target):
            problems.append(f"{rel}: broken anchor {m.group(1)}#{m.group(2)}")
    skill_dir = skills / rel.parts[1] if rel.parts[0] == "skills" else None
    for placeholder, base in (("<this skill's dir>/", skill_dir), ("<rigor skill dir>/", skills / "rigor")):
        for m in re.finditer(re.escape(placeholder) + r"([\w./-]+)", text):
            if base is None or not (base / m.group(1)).resolve().exists():
                problems.append(f"{rel}: script path {placeholder}{m.group(1)} doesn't exist")
    if rel.parts[0] != "README.md":
        for n, line in enumerate(text.splitlines(), 1):
            if leftover.search(line):
                problems.append(f"{rel}:{n}: leftover term: {line.strip()[:80]}")

rigor_section = re.search(r"^## Principles\n(.*?)^## ", (skills / "rigor" / "SKILL.md").read_text(), re.S | re.M).group(1)
rigor_index = dict(re.findall(r"^- `([a-z0-9-]+)`: (.*)$", rigor_section, re.M))
principles_index = dict(re.findall(r"^- \[`?([a-z0-9-]+)`?\]\([a-z0-9-]+\.md\): (.*)$", (skills / "principles" / "SKILL.md").read_text(), re.M))
for label, index in (("rigor/SKILL.md", rigor_index), ("principles/SKILL.md", principles_index)):
    if set(index) != principles:
        problems.append(f"{label} principle index differs from files: "
                        f"missing {sorted(principles - set(index))}, extra {sorted(set(index) - principles)}")
for name in sorted(set(rigor_index) & set(principles_index)):
    if rigor_index[name] != principles_index[name]:
        problems.append(f"principle {name}: summary differs between rigor/SKILL.md and principles/SKILL.md")

for md in sorted((root / "agents").glob("*.md")):
    toml = root / "codex" / "agents" / f"{md.stem}.toml"
    if not toml.exists():
        problems.append(f"agents/{md.name}: no codex/agents/{toml.name}")
        continue
    md_text, toml_text = md.read_text(), toml.read_text()
    body = re.search(r"developer_instructions = ('''|\"\"\")\n(.*?)\1", toml_text, re.S)
    desc = re.search(r'^description = "(.*)"$', toml_text, re.M)
    if not re.search(rf'^name = "{md.stem}"$', toml_text, re.M) or frontmatter(md_text).get("name") != md.stem:
        problems.append(f"agents/{md.stem}: name must equal the file name in both agents/ and codex/agents/")
    if not body or body.group(2).strip() != md_text.split("---\n", 2)[2].strip():
        problems.append(f"codex/agents/{toml.name}: instructions differ from agents/{md.name}")
    if not desc or desc.group(1) != frontmatter(md_text).get("description"):
        problems.append(f"codex/agents/{toml.name}: description differs from agents/{md.name}")

for toml in sorted((root / "codex" / "agents").glob("*.toml")):
    if not (root / "agents" / f"{toml.stem}.md").exists():
        problems.append(f"codex/agents/{toml.name}: no agents/{toml.stem}.md")

readme_skills = set(re.findall(r"^\| `([a-z0-9-]+)` \|", (root / "README.md").read_text(), re.M))
if readme_skills != skill_names:
    problems.append(f"README skills table: missing {sorted(skill_names - readme_skills)}, extra {sorted(readme_skills - skill_names)}")

print("\n".join(problems) or f"ok: {len(skill_names)} skills, {len(principles)} principles, {len(playbooks)} playbooks")
sys.exit(1 if problems else 0)
