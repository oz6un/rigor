# Recipes and pitfalls

Prompts worth copying, then common mistakes. Swap in your own paths and finish conditions. Informal wording is fine; the skills read intent from terse prompts.

## Recipes

Understand an unfamiliar subsystem, mechanics first, then history:

```text
use /how first to understand how this initialization works. then use /why to figure out why it broke recently.
```

Get a second opinion on a design. Your approach becomes one candidate among several:

```text
ask /arena for a second opinion on this thread and our approach
```

Check independent slices in parallel and get one report:

```text
/swarm check every package under packages/ against its check.sh. one worker per package. one report.
```

Review a branch skeptically. "don't change anything yet" keeps it read-only; the nitpick rule filters noise:

```text
/interrogate the whole branch, skeptically. don't change anything yet. no nitpicks unless it's an actual bug or regression in behavior.
```

Fix a bug through a failing test, without forcing one through brittle mocks:

```text
/rigor repro the duplicate write first. if there's a cheap test path, /tdd it. then fix and rerun.
```

Keep a run honest while you're away (full version in [the overnight page](./07-overnight.md)):

```text
/goal Use /rigor to get every fixture passing; i'm going to bed. done when the fixture suite passes. keep a decision log i can audit in the morning.
```

Redirect a drifting run with one line:

```text
i said the goal is to repro. i did not ask for a fix yet.
```

```text
apply prove it works. show me the real output, not the build log.
```

```text
/unslop that, no em dashes
```

## Pitfalls

- **Listing skills in the prompt.** It reorders steps the playbook already sequences. State the goal and constraints; name a skill only to override a default.
- **A vague finish condition.** "make it better" gives a loop nothing to check. Give a command or artifact that can pass or fail.
- **Parallel agents in one worktree.** They overwrite each other. Ask for one worktree per attempt.
- **Using `/arena` for coverage.** `/arena` repeats one brief and combines the results; `/swarm` splits slices and aggregates a report.
- **Accepting every review comment.** Humans and review bots both mix real findings with noise. `/interrogate` and the Babysit playbook sort them with reasons, and you can override either way.
- **Accepting success from a green build.** A build proves it compiles. Ask for the real command, flow, stored value, or profile, and expect the evidence in the reply.
- **Writing a `SKILL.md` freehand.** Use the Authoring a skill playbook so validation and review happen.

Back to the [guide index](./README.md).
