# Design before you write code

A single attempt at a hard design locks in the first shape the model thought of. `/architect` settles types and boundaries before implementation, `/arena` runs several attempts at the same brief and combines the best parts, and `/interrogate` has other models try to break the result. When you need coverage rather than one design, `/swarm` splits the work into parallel slices and aggregates the results.

Panels in these skills are host subagents with different lenses, plus one reviewer from the other CLI (Codex from Claude Code, Claude from Codex) when it's installed. Agreement across models is the strongest signal they produce.

## `/architect`: settle the shape

```text
/architect design the import pipeline before writing any code. i care most about how callers use it.
```

[`/architect`](../../skills/architect/SKILL.md) runs `/how` over the affected code (and `/why` when ownership or layers move), then uses `/arena` to produce competing designs, each starting from the caller's usage, then types, signatures, and a module map. By default it goes straight from the chosen design into implementation. To review first:

```text
/architect with checkpoint. stop and show me before implementing.
```

## `/arena`: several attempts, then combine

```text
/arena this, 5 candidates. the cache key format is expensive to change later.
```

[`/arena`](../../skills/arena/SKILL.md) gives the same brief to several subagents, each in its own worktree or directory. A read-only judge scores every candidate against a rubric. The coordinator reads each one, picks a base, merges in the best ideas from the others, and verifies the result. Ask for more candidates when the decision matters. To test your current approach, include it: `ask /arena for a second opinion on our approach`.

## `/swarm`: coverage and races

```text
/swarm check every package under packages/ against its check.sh. one worker per package. one report.
```

[`/swarm`](../../skills/swarm/SKILL.md) spreads workers across independent slices or declared race arms. Each gets its own scope and check and reports `PASS`, `ISSUES`, or `BLOCKED`; you get one compact report. Use `/arena` when every worker should attempt the same brief; use `/swarm` when each worker covers a different slice.

## `/interrogate`: try to break it

```text
/interrogate the whole branch, skeptically. no nitpicks unless it's an actual bug or regression.
```

[`/interrogate`](../../skills/interrogate/SKILL.md) sends the same diff, intent, and rubric to reviewers on different models. Each finding is marked reproduced or reasoned. The lead sorts findings into `Act on`, `Consider`, `Noted`, and `Dismissed`, gives a reason for each dismissal, and applies nothing automatically. Read the dismissals too; you can override them.

## How much design does a task need?

Most changes need none of this. A rough guide:

- A small finished change you're unsure about: `/interrogate`.
- A change that crosses function boundaries or moves ownership: `/architect` (which runs `/arena`).
- A standalone decision such as naming, a format, or an algorithm: `/arena`.
- A coverage matrix, parallel checks, or a race: `/swarm`.
- A contested design that's expensive to reverse: `/architect`, then `/interrogate` before shipping.

`/rigor` already applies this; reach for these directly when you want more or less scrutiny than the default.

Next: [Build and clean the change](./05-build-and-clean.md).
