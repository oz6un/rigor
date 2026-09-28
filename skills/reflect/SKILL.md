---
name: reflect
description: Review the current session's transcript with three independent reviewers (one on the other coding CLI), extract durable learnings, and turn each into a proposed edit to an existing skill for the user to approve. Use when the user says "reflect" or runs /reflect.
---

# Reflect

Find the durable learnings in the current session and turn them into skill edits.

Skip it when the session was trivial or off-topic, or when an existing skill already covered what happened and you followed it. A one-off isn't a learning.

## 1. Locate the transcript

Find this session's transcript before spawning anyone. Look only in the current project's transcripts; reading other projects' sessions exposes unrelated private conversations.

- **Claude Code:** `~/.claude/projects/<project-slug>/`, where the slug is the absolute project path with every character other than letters and digits replaced by `-` (`/Users/me/my_app` becomes `-Users-me-my-app`). Sessions are `<session-id>.jsonl`; subagent transcripts sit under `<session-id>/subagents/`.

  ```bash
  ls -t ~/.claude/projects/<project-slug>/*.jsonl | head -5
  ```

- **Codex:** `~/.codex/sessions/<yyyy>/<mm>/<dd>/rollout-*.jsonl`. Sessions from every project share this tree, so keep only files whose first line (a `session_meta` event) has `payload.cwd` equal to the current working directory. Skip files whose `payload.originator` is `codex_exec`; those are non-interactive runs such as `second-opinion.sh` calls.

  ```bash
  ls -t ~/.codex/sessions/*/*/*/rollout-*.jsonl | head -10
  ```

Confirm a candidate by checking that its first user message matches this session's opening prompt. If nothing matches, write a tight digest of the session and pass that instead of a path.

## 2. Run three reviewers in parallel

Each reviewer's prompt is its lens file followed by [`references/reviewer-rules.md`](references/reviewer-rules.md), with the transcript path (or digest) filled in where marked. Pass them verbatim.

| Lens | Prompt | Runs on |
|---|---|---|
| Judgment | [`references/judgment-reviewer.md`](references/judgment-reviewer.md) | Host subagent, strongest model |
| Tooling | [`references/tooling-reviewer.md`](references/tooling-reviewer.md) | The other CLI, through the `second-opinion.sh` script in the `rigor` skill's `scripts/` directory (`../rigor/scripts/second-opinion.sh`) |
| Divergent | [`references/divergent-reviewer.md`](references/divergent-reviewer.md) | Host subagent, strongest model |

- Host reviewers need to read code and use MCP tools (ticket trackers, chat, observability) to look up context the transcript references, so don't restrict them to a read-only agent type. Their prompt tells them not to edit files. In Claude Code, use a `general-purpose` agent; in Codex, the default agent.
- The tooling reviewer runs read-only (the script's default). It may not have the same MCP servers configured; that's fine, since most tooling findings come from the transcript itself.
- If the script exits 3, run the tooling reviewer as a third host subagent and mention the fallback in the summary.

## 3. Synthesize

Spawn one host subagent on your strongest model with [`references/synthesizer.md`](references/synthesizer.md), each reviewer's full output pasted where marked. Like the reviewers, it may use MCP tools to spot-check citations and must not edit files. It returns an Accepted / Rejected / Backlog list.

## 4. Check for structural enforcement

Review the Accepted list. Move any item that a lint rule, script, metadata flag, or runtime check would enforce more reliably into Backlog (the `encode-lessons-in-structure` principle).

## 5. Apply, with approval

Show the user the full Accepted / Rejected / Backlog output and wait for explicit approval before editing anything. The user chooses which rows to apply and may change their routing. Skill edits affect every future session that uses the skill, so never apply them automatically.

File Backlog items in the team's backlog tracker if one is available through an MCP tool; otherwise list them in the summary. Only the Accepted list waits for approval.

For each approved row, follow its Routing field:

- A small edit to an existing skill (one bullet, a tightened sentence, a corrected fact): make it directly.
- A substantive edit (a new section, a new table, more than about ten lines): follow the rigor skill's `playbooks/authoring-a-skill.md`, including its test-and-iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): follow the description-tuning steps in `playbooks/authoring-a-skill.md`.
- `new skill: <kebab-name>`: create it with `playbooks/authoring-a-skill.md`. Don't improvise the structure.

If the repository has a skill validator or lint, run it on every skill you touched.

## 6. Summarize

A short list, no preamble:

- Edits applied: `<skill path>`, one line each on what changed.
- New skills: `<skill path>`, one line each.
- Backlog: `<issue title>` (`<tags>`), filed or listed, one line each.
- Dropped: one line per rejected finding with the synthesizer's reason.
- Panel: whether the tooling reviewer ran on the other CLI or fell back to a host subagent.
