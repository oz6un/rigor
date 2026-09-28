# Verify the result and ship it

"It compiles" isn't evidence. The [`prove-it-works`](../../skills/principles/prove-it-works.md) principle makes the agent check the real artifact before reporting success. Your part is to make the real artifact checkable.

## State the finish condition up front

The agent won't weaken a test to reach it: no deleted or loosened assertions, skips, or special cases. It changes a test only where your request changes the behavior the test checks, and names each such test. A test that contradicts your request gets reported as blocked.

```text
/rigor add json output to this command. text output stays byte-identical, the json parses, both run against the sample project. show me the evidence.
```

Now the agent has three checks to run. The reply should include the exact commands and outputs. If a check couldn't run, it should say "inconclusive"; treat a confident reply without evidence as a warning sign.

Match the check to the change:

- CLI change: run the real command.
- UI change: walk the changed flow in the running app.
- Parser or migration: replay a saved input.
- Perf change: compare before and after profiles.
- Storage change: read back the written value.

For a small diff you don't fully trust, [`/blast-radius`](../../skills/blast-radius/SKILL.md) finds what else it could break. It identifies the one fact the change's safety depends on and proves it by running code.

## Create a project verification skill

Walking a UI flow needs a scripted way to drive the app. If your project doesn't have one:

```text
/create-verification-skill
```

[`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md) works out from the repo what a user touches, how the app launches, what can drive it (an existing harness, else browser automation or CDP, a PTY, or HTTP), what evidence proves behavior, and whether two instances can run side by side. It asks you only what the code can't answer.

It writes `.agents/skills/verify-<app>/`, symlinked from `.claude/skills/` so both Claude Code and Codex load it. The skill has Launch, Doctor, Drive, Evidence, and Cleanup sections, plus a feature map under `features/` describing each feature and the result that proves it works ([example](../../skills/create-verification-skill/references/feature-map-example/)). The generator runs the skill once end to end before handing it over. From then on, "verify it in the app" is a step any agent can do in this repo, and `/swarm` can split a full pass by feature.

## Keep it accurate

```text
/maintain-verification-skill
```

[`/maintain-verification-skill`](../../skills/maintain-verification-skill/SKILL.md) reads each feature's source in parallel, then drives every mapped feature live. It ends as `clean` (nothing to change), `changed` (one PR of proven fixes to the verification skill only), or `blocked` (with the reason). It never edits product code; a product regression gets reported, not documented away.

## Open the PR

```text
/rigor open the pr. small ordered commits, evidence in the description.
```

The Opening a PR playbook works from a worktree, arranges small ordered commits, cleans the diff and prose, and returns the link. Several narrow PRs are easier to review than one large one, and stacked follow-ups beat a growing branch.

## Babysit: get the PR to merge-ready

```text
/rigor babysit this pr. get it green.
```

The Babysit playbook handles blockers in order: conflicts, review threads, CI. Known fixes go out in one push so CI restarts once. Review comments, from humans or automated reviewers, get assessed on their merits: real findings get fixed, and noise gets a reply explaining why it doesn't apply. For status only:

```text
/rigor check on pr 123. anything outstanding?
```

Babysit stops at merge-ready and doesn't merge.

## Shipping: land the stack

```text
/rigor land the stack.
```

A passing CI run doesn't prove the change is correct. The Shipping playbook has a fresh agent (never the author) verify each PR's behavior live, then merges only the contiguous verified run from the bottom of the stack with `gh`, and reports the first PR that breaks the chain. A verified PR above an unverified one waits, because merging it would pull the unverified change in underneath.

Next: [Run work while you're away](./07-overnight.md).
