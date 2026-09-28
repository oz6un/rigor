---
name: why
description: Investigates why code is shaped the way it is (design rationale, tradeoffs, regressions, postmortems, where a threshold came from) by searching every available evidence source in parallel and returning a confidence-graded, cited answer. Use for "why does X work this way" or "why did we pick Y". For how the code behaves at runtime, use `how`.
---

# Why

Find the motivation behind a piece of code. `how` explains what code does; `why` explains the forces that gave it its shape. That motivation lives outside the code, in commits, PRs, tickets, docs, chat, and production telemetry, all of it incomplete, so the answer has to separate what the record states from what you infer.

Be a careful investigator. `references/epistemics.md` defines the confidence tiers and phrasing; the synthesizer must follow it.

## 1. Pin down the target and the question

The **target** is usually a block of code, a pattern, a feature, or a named decision. The **question** is usually a rationale, a tradeoff, a motivating edge case, an external constraint, dead code, or a broad history sweep.

If the target is vague ("why do we do it this way?"), infer it from context (open files, recent edits, what was just discussed), state your reading in one line, and proceed.

## 2. Anchor it in code

Before spawning anyone, collect:

- The file paths and line ranges
- The key symbols (functions, classes, constants)
- The last few commits touching the target
- PR numbers from commit subjects (the `(#1234)` pattern) and any ticket IDs in commits or PR bodies

```bash
git blame -L <start>,<end> <file>        # last-touch commits for the lines
git log --oneline -20 -- <file>          # recent commits, PR numbers visible
git log --follow -p -- <file>            # full history with patches, through renames
git log -1 --format=%B <commit>          # full message, for PR and ticket IDs
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

This code anchor is the seed context for every investigator.

## 3. Run one investigator per evidence source

The default is the full parallel investigation.

### Discover the available sources

List the MCP servers available in this session. In Claude Code, their tools appear as `mcp__<server>__<tool>`; in Codex, they're the servers configured under `mcp_servers` in `config.toml` and exposed as tools in the session. Map each server to one evidence category:

| Category | Examples | What it uniquely surfaces |
|---|---|---|
| Source control | git, `gh` (always available) | Rationale captured at implementation and review time |
| Issue tracker | Linear, Jira, GitHub Issues, Shortcut | The product or business forcing function |
| Long-form docs | Notion, Confluence, Google Docs | Design rationale written down before it became code |
| Team chat | Slack, Discord, Teams | Deliberation that never reached a doc, especially when the paper trail is thin |
| Infrastructure observability | Datadog, Grafana, Honeycomb, New Relic | Runtime conditions behind timeouts, retries, rate limits, circuit breakers |
| Error tracking | Sentry, Rollbar, Bugsnag | The exceptions that motivated catch blocks, guards, retries, fallbacks |
| Analytics warehouse | Snowflake, BigQuery, Databricks, ClickHouse, dbt | Product and data reality: flag-gated code, experiments, data migrations, "where did this number come from" |

Classify each server by its name, instructions, and tool names. If one fits two categories, pick the one matching its primary evidence and note the ambiguity. Aim for a complete coverage map: search each available category and record null results rather than skipping.

### Spawn the investigators

Spawn one investigator per category that has a source, all in parallel. Each owns exactly one source; don't give one agent several.

Investigators need MCP access, so don't use an agent type that strips it. In Claude Code, use `general-purpose` on a fast model; in Codex, the default agent (subagents inherit the session's MCP servers). Tell each investigator not to write files or change external state.

Each investigator gets:

1. The base prompt in `references/investigator-prompt.md`
2. The playbook for its category from `references/sources/` (index in `references/source-playbook.md`), adapted to the actual server
3. `references/sources/incident-postmortem.md` as well, if the target looks defensive (null checks, retries, timeouts, rate limits, feature flags, egress guards, OOM handlers)
4. The code anchor from step 2
5. The user's question

### When to skip a category

Skip only with a written reason, which goes in the final Sources consulted section. Two reasons are valid:

- **No source is available** for that category. Report it as a gap: "Team chat not searched: no chat MCP server in this session, so the conversational record wasn't available."
- **The source is provably irrelevant**, which is a high bar: "Error tracking skipped: the target is a build-time script with no runtime path."

If the target is a single trivial commit whose PR description fully answers the question, you may answer inline, but only after confirming the other searches would be redundant, and say so. This should be rare.

## 4. Synthesize

Spawn one synthesizer on your strongest model, again with MCP access so it can spot-check citations, and again told not to write anything. Give it:

1. All investigator findings, including null results and skipped categories with reasons
2. The code anchor
3. The user's question
4. `references/epistemics.md`
5. The prompt in `references/synthesizer-prompt.md`

For a contested or high-stakes answer, get a cross-model check: send the synthesis, the code anchor, and `references/epistemics.md` to `../rigor/scripts/second-opinion.sh` and ask it to find claims whose tier is higher than the cited evidence supports. Move any claim it successfully challenges down a tier.

## 5. Present

Give the user the synthesizer's output. You may lightly edit for clarity or add context from the conversation, but don't change the confidence language. If the cross-model check fell back to a host subagent, say so.

The output follows `references/synthesizer-prompt.md`: The question, The code in question, What we found, What we can reasonably infer, Competing hypotheses, What we don't know, Sources consulted, Confidence summary. Keep the tiers separate, and keep Sources consulted to one line per category, including the ones that returned nothing or were skipped, with the reason.

If the question is a precursor to changing the code, end with a constraint set for planning the change: what to **Preserve**, what's safe to **Change**, what to **Avoid**, and the **Risks**.

## Failure mode to watch for

Recency bias: treating the latest commit as the explanation. The current shape is usually the accumulation of earlier decisions, so trace back past the last touch.

## Reference files

- `references/epistemics.md`: confidence tiers and phrasing.
- `references/investigator-prompt.md`: base prompt for investigators.
- `references/source-playbook.md`: index of per-category playbooks.
- `references/sources/*.md`: one example playbook per category, plus the cross-cutting `incident-postmortem.md`.
- `references/synthesizer-prompt.md`: synthesizer prompt and output format.
