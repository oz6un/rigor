---
name: recall
description: Rebuilds your recent working context from your own chat history, live git and PR state, and the team's shared record (user reports, earlier fixes, incidents), then returns a short brief of where things stand and what to do next. Use for "recall my work on X", "catch me up", "where did I leave off", or before starting or resuming work.
disable-model-invocation: true
---

# Recall

Before starting or resuming work, rebuild the user's recent context and return a short brief: where things stand and what to do next. Read only what the in-scope threads need, then stop.

Context lives in two places. The user's own chat history records what they did and decided. The shared record holds what happened around the same code under other names: symptoms users keep reporting, fixes that shipped and were reverted, errors still firing in production. The `why` skill searches that shared record (source control, issue tracker, team chat, docs, error tracking). A feature with a long bug history keeps most of its story there, so don't rebuild it from transcripts alone.

## Where the chat history lives

| Host | Location | Notes |
|---|---|---|
| Claude Code | `~/.claude/projects/<slug>/<session-id>.jsonl` | `<slug>` is the workspace's absolute path with every non-alphanumeric character replaced by `-` (`/Users/you/my.proj` becomes `-Users-you-my-proj`). One JSON object per line; conversation turns have `type` `user` or `assistant`. Subagent transcripts live under `<session-id>/subagents/`. |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | Sessions for all workspaces share this tree. The first line is a `session_meta` record whose `payload.cwd` is the workspace; filter on it. Messages are `response_item` records with `payload.role`. `codex resume` lists recent sessions. |

Check both locations: the user may have worked on the same thing from either host.

## Steps

1. **Route.** Resuming one specific earlier chat is the rigor skill's `playbooks/session-pickup.md`, not this. Turning habits into a durable skill is `automate-me`. A human-readable summary of your work for someone else is a different task. Recall loads working context across recent chats before you act. If the user already gave you a full state capsule (paths, branch, the change), use it and skip the mining.
2. **Fix the scope before searching.** Set the window (default: the last 7 days), the topic if one was named, and the workspace (default: the current one; read another project's history only when asked). State the scope back to the user. If they said "all", don't quietly narrow it to "recent".
3. **Mine the chat history in parallel.** Spawn subagents on a fast model, each taking a slice of the in-scope transcripts, and run them in parallel. Tell each one to:
   - Order candidates by modification time (`ls -t`, or `find -newermt`), never by file name.
   - Grep for the topic first, then read only matching transcripts and only the relevant regions.
   - Skip the current session and noise: subagent transcripts, eval runs, test sessions.
   - Return one block per chat with the same fields: topic, the user's goal, decisions, open threads, struggles and corrections, artifacts (PRs, tickets, branches), each citing the session ID.

   For one or two chats, skip the fan-out and read them yourself. Either way, raw transcripts stay out of the main thread; only findings come back.
4. **Search the shared record** whenever the topic names a feature, file, subsystem, area, or bug. This is the default, including for "my work on X". Use the `why` skill's investigators and per-source playbooks, but change their question from "why was this built this way" to "what's the current state, what's been tried and didn't hold, and what are users still reporting". Run them in parallel with the chat mining, one investigator per source; a null result is a finding, and an unavailable MCP server is skipped and reported. Skip this step only for pure activity recall with no named target ("what did I do this week"), where the user's own history and live state are the whole answer.
5. **Check live state.** Verify the PRs, branches, and tickets from steps 3 and 4 with `git` and `gh`: is the PR merged, open, or reverted; does the branch still exist; is there uncommitted work. When the answer depends on what an agent actually did (tools run, files read, errors hit), read the full transcript rather than a summary.
6. **Write the brief** to the format below, grouped by thread and limited to the named topic.

## Brief format

Capsule first, then threads, then problems, then the next move. Put deeper detail below, or cut it.

- **Capsule.** Up to 5 bullets: what this work is and where it stands overall.
- **Threads.** One line each, starting with exactly one status tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`. Every thread gets a tag.
- **Problems.** Up to 5 recurring ones, including symptoms users keep reporting and any fix that shipped and was reverted, so the next attempt starts where the last one failed.
- **Next move.** The single most useful next action, stated concretely.

Leave out adjacent features and tickets unless they block this one. If the capsule and threads grow past a screen, cut detail before cutting threads. Write through `unslop`. Cite chat findings by session ID and shared-record findings by their source (PR #, ticket ID, chat permalink, error-tracker issue). Remove private context before anything goes somewhere public.
