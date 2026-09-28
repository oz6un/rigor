---
name: show-me-your-work
description: Keep a reviewable decision log for long-running or unattended work, as a TSV with one row per decision (what, why, evidence, result), then audit it and get a review from another model before handing back. Use for /show-me-your-work, autonomous or multi-phase runs, or work the user will review after stepping away.
disable-model-invocation: true
---

# Show me your work

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` (with symlinks in this skill's path resolved) and follow it.

Keep one decision log per effort.

## Format

A single TSV file with one row per decision. Every cell is one line, and evidence is a pointer, not prose. Start a log by copying `references/decision-log-template.tsv` (the header row), or let `<this skill's dir>/scripts/log.sh` create it.

| Column | Contents |
|---|---|
| `ts` | ISO 8601 timestamp |
| `phase` | The phase or workstream |
| `decision` | What was chosen or done, in one line |
| `why` | The reason in plain words. If a principle drove it, describe the reason rather than naming the principle. |
| `evidence` | A pointer that proves it: commit SHA, PR number, `file:line`, or the path to an artifact, trace, or screenshot |
| `result` | The outcome or check state: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open` |

Example:

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first: about 100 components, roughly 75 hours	needed the size before committing to a long run	commit 3a9f1c2	found 5 blockers to resolve first
2026-05-24T09:40:00Z	harness	took screenshots of the old UI before changing anything	to compare old against new and catch any visual change	scripts/snapshot.sh, baseline/	saved 120 reference screenshots
2026-05-24T11:15:00Z	widget	moved the widget styles without changing how it looks	keep the change small and the output identical	commit 7c21e0a, pixel-diff 0	identical, tests pass
2026-05-24T12:30:00Z	widget	discarded a subagent's work because its screenshots were blank	checked the files instead of trusting its summary	worktree reset	reverted; tightened the brief
```

## Logging a row

Write each row the way you'd tell a teammate what you did: plain words and concrete actions (the `unslop` skill applies to log text too).

```bash
<this skill's dir>/scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

The script stamps `ts`, writes the header on first use, replaces tabs and newlines inside cells with spaces, and prefixes any cell that starts with `=`, `+`, `-`, or `@` with a single quote so spreadsheets don't evaluate it as a formula. Appending with `printf` also works, but handle the same characters yourself when cells contain generated or user-supplied text.

Log decision points and checkpoints, not every action: a fork chosen, a unit finished with its verification result, a pivot or revert and what triggered it, a blocker, a fixed check. In a loop, log one row per iteration. Skip the trivial and self-evident.

### Runs and `start` rows

A run is one agent session, including its later turns. Picking up someone else's work, a replacement agent, or a new session is a new run.

- When a run adds to a log that already has rows, its first row uses phase `start`. So does its first row after a `start` row written by another run. A run returning to the log in a later turn therefore reads the last few rows first to see whether another run has written since.
- A `start` row's `decision` names the `ts` range of the earlier rows this run didn't write, and its `evidence` identifies this run (a session or agent ID).
- Use phase `start` for nothing else.

## Where the log lives

By default the log is a working file, not committed: `decisions.tsv` in the work directory, or `.audit/<task-slug>.tsv` when several efforts run at once. Keep it out of git (add it to `.git/info/exclude` if it isn't ignored).

Commit it when the work is large enough that a reviewer needs the log to trust the result.

## Rules

- The log is append-only. Correct a wrong call with a new row that supersedes it; never edit or delete rows.
- Prefer evidence produced by committed scripts over one-off manual checks (the `encode-lessons-in-structure` principle).

## Audit the log against the transcript

Before handing back, check that the log matches what happened. Read this session's transcript: in Claude Code, the newest `~/.claude/projects/<project-slug>/*.jsonl` for this session; in Codex, this session's `~/.codex/sessions/**/rollout-*.jsonl` (match on `payload.cwd` in the first line). Don't browse other projects' transcripts. The `reflect` skill's step 1 has the details.

Compare this run's rows with the transcript. This run's rows start at each of its `start` rows (or the first row, if this run created the log) and end at the next `start` row written by another run.

- Every row maps to a real decision or action.
- Every row's evidence resolves and shows what the row claims.
- A fork, pivot, or abandoned approach that shaped the work but has no row is a gap. Add a row for it.

Fix the log by adding rows, never by editing. When a row records something that didn't happen, or its claim or evidence is wrong, add a row that supersedes it with what actually happened and evidence that resolves. The audit covers only this run's rows. If this run's work shows another run's row is wrong, supersede it the same way.

## Review by another model

Before handing back, have a model other than the one that did the work review the log. Self-review doesn't substitute. Run the review through `<this skill's dir>/../rigor/scripts/second-opinion.sh`, read-only, giving it the log path and the transcript path. The reviewer doesn't redo the work; it scans for what the user should look at:

- Decisions with weak or missing evidence.
- Verification that was skipped, or claimed without proof in the transcript.
- Choices that look risky in hindsight: premature, expanding scope, or covering a symptom.
- Anything the user would miss on a quick skim.

Every reply for a run that kept a log ends with an **Attention** section. Its first line names the reviewer (`reviewed by <CLI and model>`, or `reviewed by host subagent (<model>), other CLI not installed`). Then list each flag with the rows or moments it refers to. "No flags" is a valid result; the reviewer line is always required.

## Reading the log

Read it top to bottom, follow the evidence pointers, and spot-check. GitHub renders a committed TSV as a table; in a terminal, use `column -s$'\t' -t decisions.tsv`.

## Using this skill from other skills

Other skills that need a decision log point here instead of defining their own format. Refer to this skill by name and don't restate the columns.
