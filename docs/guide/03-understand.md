# Understand the code before changing it

An agent that edits code it hasn't traced tends to fix the symptom at the first plausible spot. Four skills help first: `/how` explains what the code does, `/why` finds out why it's shaped that way, `/teach` combines both into an explanation, and `/recall` rebuilds your own recent context.

## `/how`: trace behavior

```text
/how do we dedupe notifications? is there an n+1 when we look up subscribers?
```

Ask the question you actually have. [`/how`](../../skills/how/SKILL.md) explains the runtime flow, key types, and non-obvious parts, the way a senior engineer would onboard you. For a large subsystem it spawns a few read-only explorers first.

## `/why`: find the history

```text
/why was the retry limit set to five? does the reason still hold?
```

[`/why`](../../skills/why/SKILL.md) starts from git history, then searches whatever your MCP servers expose (issue tracker, docs, team chat, observability, error tracking) in parallel. It cites sources, separates evidence from inference, and reports "nobody wrote down why" when that's the answer. `do why first, then how` is a good prompt when you suspect the history explains the code.

## `/teach`: understand it properly

```text
/teach me how this PR changes retries. convince me it fixes the cause and not the symptom.
```

[`/teach`](../../skills/teach/SKILL.md) runs `/how` and `/why` as needed and builds a plain explanation step by step, with diagrams. Asking it to "convince me" turns the explanation into an argument you can challenge.

## `/recall`: catch up on your own work

```text
/recall catch me up on the export work from last week
```

[`/recall`](../../skills/recall/SKILL.md) reads your recent Claude Code and Codex sessions for this project plus the shared record (issues, prior fixes, errors still firing) and returns where things stand and what's next.

## Take over in-flight work

To continue a specific branch, PR, or session rather than a topic:

```text
/rigor take over this branch. read the decision log, figure out what's done, and continue. don't redo finished work.
```

The Session pickup playbook treats the prior trail as the source of truth: it reconstructs the branch state and decisions, names the resume point, and checks inherited claims against the original goal.

Next: [Design the change](./04-design.md).
