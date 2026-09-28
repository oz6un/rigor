---
name: automate-me
description: Turn the user's working conventions into a personal <name>-mode skill that routes work through rigor, mined from their Claude Code and Codex transcripts plus a few direct questions. Use for "automate me", "create/update my -mode skill", or "capture how I work in a skill".
disable-model-invocation: true
---

# Automate me

Produce one `<handle>-mode` skill (for example `jay-mode`) that tells agents how this user works. The mode skill layers the user's preferences on top of `rigor`: it invokes rigor for playbooks, principles, and verification, and adds only what differs for this user.

This skill sequences three things: mining the user's history (step 1), the rigor skill's `playbooks/authoring-a-skill.md` (authoring), and the `unslop` skill (prose). It doesn't replace any of them.

## Flow

### 0. Check for an existing mode skill

Search for `*-mode/SKILL.md` matching the user's handle under `.agents/skills/`, `.claude/skills/`, `~/.claude/skills/`, and `~/.agents/skills/` (or `~/.codex/skills/`), recursively, since mode skills can sit in a personal category directory. If one exists and the user hasn't already said "update", ask the user:

- Update the existing skill (default for repeat runs)
- Start fresh (rare; ask why first)

In update mode:

- Step 1 mines only history since the skill was last edited (`git log -1 --format=%cI <path>`, or the file's mtime if it's untracked).
- Step 2 asks what has changed or is missing, not what to capture from scratch.
- Step 4 edits the file in place. Keep sections the user hasn't contradicted, revise ones with new evidence, and add sections only for new rules.

### 1. Mine the user's history

Scope transcripts to the current project. Reading every project's history pulls in private conversations unrelated to this work.

- **Claude Code:** `~/.claude/projects/<slug>/*.jsonl`, where `<slug>` is the project's absolute path with `/` (and `.`) replaced by `-`, for example `/Users/jay/code/app` becomes `-Users-jay-code-app`.
- **Codex:** `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`. Sessions aren't grouped by project, so keep only files whose first line (a `session_meta` event) has `payload.cwd` inside this project.

Both formats are JSON lines with one event per line. Check a few lines before writing extraction code, since the schemas change between versions. User turns are the main signal (Claude Code: `"type":"user"` entries; Codex: `response_item` messages with `role: "user"`), and the agent's replies give the context for each correction.

Split the last two to four weeks into about three slices and spawn one subagent per slice, in parallel. Give each the exact file list for its slice. Each returns a short list of patterns with evidence pointers (file and timestamp). Signals to look for:

- Response preferences: length, tone, format, "simplify this" corrections.
- Delegation habits: subagents, models, parallelism, specialized workflows.
- Verification posture: what "done" means, unit tests versus live repro, reviewers.
- Code and prose discipline: style, principles cited, lint and format tools.
- Process: worktrees, commits, PRs, review and merge tooling.
- Meta: fixing skills mid-task, proposing new skills.

Cross-check slices before keeping a signal. A pattern seen in two or more slices is high confidence. A lone signal is weak and usually gets dropped.

### 2. Ask the user

Mining misses intent that hasn't come up yet. Ask one or two multiple-choice questions with four to six options each (Claude Code: AskUserQuestion with multi-select; Codex: a numbered list in the reply). Start broad ("Which areas matter most?"), then follow up on the areas they pick. Finish with one open question for anything the options missed. Don't send twenty questions.

### 3. Cluster findings

Group the signals into sections, using only the ones that apply:

- **Response style**: length, tone, format.
- **Autonomy**: what to do without asking, MCP tool use.
- **Understand first**: which skills to use when scoping or investigating.
- **Subagents**: defaults, parallelism, model per task.
- **Prose and code discipline**: principles, lint tools, style guides.
- **Review and verify**: repro posture, verification skills, live-testing tools.
- **Process**: worktrees, commits, PRs, review and merge tooling.
- **Skills**: authoring habits, fixing a skill first, proposing new ones.

Read the `rigor` skill for the level of granularity. Don't copy its content; anything rigor already says belongs in rigor, not the mode skill.

### 4. Draft the skill

Follow the rigor skill's `playbooks/authoring-a-skill.md`.

- **Placement.** Keep an existing mode skill's location. For a new project-level mode, write `.agents/skills/<handle>-mode/SKILL.md` and symlink `.claude/skills/<handle>-mode` to it, the same layout `create-verification-skill` uses. Use a personal category directory if the repo already has one for this handle. For a personal skill across projects, write `~/.claude/skills/<handle>-mode/` and symlink it from `~/.agents/skills/` (or `~/.codex/skills/` on older Codex versions).
- **Handle.** The user's first name or chosen identifier.
- **Routing.** The body opens by telling the agent to invoke `rigor` and follow it, then lists this user's overrides and additions. Point to the rigor playbooks and principles that matter most to them by name instead of restating them.
- **Description.** Trigger on the user's name, `/<handle>-mode`, and "work in <name>'s style", not generic phrases like "write code" or "review PR". Keep it one YAML scalar; quote it or use `description: >-` when punctuation or wrapping requires it.
- **Invocation.** Set `disable-model-invocation: true` unless the user explicitly wants the mode applied on every turn.

### 5. Edit the prose

Apply `unslop` to every line. Show the draft to the user and take feedback; expect a few rounds. A mode skill is a short list of rules, not a manual.

### 6. Land it

Work in a worktree off the default branch, commit, and open a PR through the rigor skill's `playbooks/opening-a-pr.md`. Don't push to the default branch. For a personal skill outside any repo, show the final file path instead.

## Guardrails

- **Don't overfit.** A preference stated once and contradicted elsewhere is noise. Require repeated instances before writing it down.
- **Keep it operational.** No metaphors or restating other skills' contents; each line should change what an agent does.
- **Reference, don't inline.** Refer to skills and principle docs by name or path instead of pasting excerpts.
- **Keep sections minimal.** Add a section only for a specific non-default rule. "Communicate clearly" isn't a rule. "Short paragraphs. Tables when comparing options. Bullets only for parallel items." is.
- **Use generic names.** Write "the user" in imperatives, not the user's first name.
- **Skip empty sections.** If the user has no process rules worth writing down, leave out the Process section.

## Evaluation

A mode skill is subjective, so a benchmark loop isn't useful. Check with the user: does it read like them, and did it miss anything? Then ship. Tune the description only if the skill triggers wrongly in practice.

## When not to use

- A task-specific skill, not working conventions: use the rigor skill's `playbooks/authoring-a-skill.md` directly, with no mining.
- One narrow workflow ("how I write commit messages"): that's a regular skill, not a mode skill.
