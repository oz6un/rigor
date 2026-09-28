# Make it yours

`/rigor` encodes one set of defaults. You can layer your own conventions on top, capture lessons from a session, write focused skills, and test skill changes before adopting them.

## `/automate-me`: your own mode skill

```text
/automate-me
```

[`/automate-me`](../../skills/automate-me/SKILL.md) reads your style from your history instead of asking you to describe it. It mines this project's Claude Code and Codex transcripts for repeated preferences (reply style, delegation, verification, code, prose, process), asks which patterns are really yours, and drafts a `<your-name>-mode` skill that routes through `/rigor` and adds your overrides. It edits the draft with `/unslop` and opens a PR so you review it like any other change.

Refresh it when your habits change:

```text
/automate-me update my mode skill with everything since its last edit
```

## `/reflect`: capture a session's lessons

```text
/reflect that took way too long. capture what we learned so the next run doesn't repeat it.
```

[`/reflect`](../../skills/reflect/SKILL.md) has several reviewers read the session in parallel; a synthesizer sorts their proposals into `Accepted`, `Rejected`, and `Backlog` and waits for your approval before changing any skill. Approve a proposal only if it would change a future decision. One odd session is an anecdote, not a rule.

## Write a focused skill

```text
/rigor write a skill for verifying database migrations in this repo
```

This matches the Authoring a skill playbook, which validates frontmatter and links and ships through the Opening a PR playbook. Agent-facing prose needs care because every sentence becomes an instruction some future agent follows. For a skill that drives your app, use `/create-verification-skill` instead ([Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill)).

## `/technical-writing`: docs to a standard

```text
/technical-writing review the readme changes
```

[`/technical-writing`](../../skills/technical-writing/SKILL.md) is for docs, RFCs, READMEs, PR descriptions, and commit messages. It picks the document type (tutorial, how-to, reference, explanation) and then works sentence by sentence toward prose a tired engineer understands on first read.

## Test a skill change blind

```text
/rigor run the eval playbook on this skill change. same task for both variants, candidates stay blind.
```

The Eval playbook guards against agents behaving differently when they know they're being tested. Candidates get a realistic task in clean directories and never see the words "eval" or "candidate" or learn about each other. One judge scores all outputs under neutral labels, and whether a candidate followed the skill is graded from which files it actually read. Read the outputs yourself before accepting the verdict; if you disagree with the judge, check the rubric first.

**Pitfall:** don't edit a skill mid-task because it's misbehaving. Fix it in its own PR and keep the task moving. A skill edit mixed into feature work is hard to review and impossible to evaluate.

Next: [Recipes and pitfalls](./10-recipes-and-pitfalls.md).
