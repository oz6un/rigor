---
name: interrogate
description: Adversarial multi-model code review. Independent reviewers (host subagents plus one from the other coding CLI) challenge a diff against a shared rubric and code-quality lens, and you deliver a filtered verdict. Use for "interrogate", "adversarial review", "multi-model review", "challenge this", "stress test this code", or "find blind spots".
disable-model-invocation: true
---

# Interrogate

Have several independent reviewers attack a change, then deliver one verdict. Every reviewer gets the same prompt, rubric, and code-quality lens; the host reviewers add a focus line so two runs of the same model don't just agree. The strongest signal comes from a reviewer on a different model family, so the panel always includes one from the other CLI when it's installed.

The deliverable is a verdict. Don't apply any changes.

## Step 1: Determine the scope

- If the user points at files or a diff, review that.
- On a feature branch, review the full changeset: `git diff main...HEAD` (or the right base branch).
- If the user refers to recent work, collect the relevant files.

Write the diff to a file (for example `/tmp/interrogate-<slug>/diff.patch`) and list the surrounding files reviewers need for context. Reviewers get paths, not pasted contents, and can read the rest of the repo themselves.

## Step 2: State the intent

Write one paragraph stating what the change is for, drawn from the user's message, commit messages, the PR description, and the code. If you're unsure of the intent, ask the user before continuing.

## Step 3: Spawn the reviewers

Build the prompt from [`references/reviewer-prompt.md`](references/reviewer-prompt.md), filling in the intent, the diff path and context files, [`references/rubric.md`](references/rubric.md), and [`references/code-quality-review.md`](references/code-quality-review.md). Every reviewer applies the code-quality lens.

Default panel, all launched at once:

| Reviewer | Runs on | Focus line |
|---|---|---|
| A | Host subagent, read-only, strongest model | Correctness, root causes, and security first |
| B | Host subagent, read-only, strongest model | Structure, complexity, and the code-quality lens first |
| C | The other CLI via `second-opinion.sh` | None; the full prompt as written |

- Host reviewers: Claude Code, the Agent tool with `subagent_type: "Explore"` or a `general-purpose` agent told not to edit; Codex, spawn with `sandbox_mode = "read-only"`. Two host reviewers on the same model agree more often than two different models would, which is why A and B each get a focus line. The focus sets what to examine first; each still covers the whole rubric.
- Reviewer C: write the filled prompt to a file and run it read-only from the repository root, in the background alongside the host reviewers: `<this skill's dir>/../rigor/scripts/second-opinion.sh --cd "$(git rev-parse --show-toplevel)" < prompt.txt`. If the other CLI isn't installed, C is a third host reviewer with no focus line.

The user can ask for more or fewer reviewers; extend or shrink the table, keeping one seat on the other CLI.

## Step 4: Synthesize

As results arrive:

1. Parse every finding.
2. Find the consensus: findings raised independently by two or more reviewers are the strongest signal, especially when one of them is reviewer C.
3. Note single-reviewer findings. Read them, and weight them accordingly.
4. Merge duplicates that describe the same issue differently, and record who raised each.
5. Note direct disagreements, where one reviewer flags something another explicitly says is fine.

## Step 5: Judge

You are the lead reviewer: a pragmatic senior engineer, not a neutral aggregator. Apply [`references/lead-judgment.md`](references/lead-judgment.md) and put every finding into one bucket:

- **Act on:** real problems with correctness, security, or maintainability given the actual goals. These would block a PR.
- **Consider:** legitimate points where you're unsure the fix is worth the cost right now. Worth the user's attention.
- **Noted:** technically valid but not actionable: context-dependent, premature, or low-impact at this stage.
- **Dismissed:** wrong, a nitpick, or missing context, with a short reason.

For each finding, give the reviewers who raised it, the bucket, and a one-line reason.

## Output format

```
### Intent
> <the paragraph from step 2>

### Reviewers
- A: host subagent (<model>), focus: correctness/security, <N> findings
- B: host subagent (<model>), focus: structure/code quality, <N> findings
- C: <other CLI and model, or "host fallback: other CLI not installed">, <N> findings

### Act on
<each: the problem, who raised it, why it matters>

### Consider
<each: the point, who raised it, the tradeoff>

### Noted
<short list>

### Dismissed
<each: the finding and why it was rejected>

### Agreement map
<where reviewers agreed and diverged, and what that pattern suggests>
```
