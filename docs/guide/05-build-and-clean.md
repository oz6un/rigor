# Build the change and clean the diff

Say what you observed and what must hold; the playbook supplies the steps you didn't type (reproduce before fixing, name the data shape before implementing, pin behavior before restructuring, profile before optimizing).

## Prompts for each build playbook

Bug fix: the symptom, and repro first.

```text
/rigor this command emits two records after a retry. repro first, then fix and verify.
```

Feature: the behavior, and what must not change.

```text
/rigor add a --json flag. text output stays byte-identical. verify both forms.
```

Refactoring: pin behavior before moving structure.

```text
/rigor move parsing into one module, zero behavior change. record the current output first and prove it's unchanged after.
```

Perf issue: a measurement, not an impression.

```text
/rigor startup takes 1.8s on this fixture. trace it, fix the measured cause, show me before and after.
```

For sustained work on one number, use the Hillclimb playbook: give it the metric, a target, and a minimum number of attempts. It tests one hypothesis at a time against a fixed measurement harness, keeps wins, and reverts the rest.

## `/tdd`: failing test first

```text
/tdd implement
```

With the bug already in context, that's enough. [`/tdd`](../../skills/tdd/SKILL.md) writes the smallest test that fails for the right reason, then the fix, then reruns it. If a test would need heavy setup or brittle mocks, it says so and uses the closest real command instead, which is often stronger evidence.

[`typescript-best-practices`](../../skills/typescript-best-practices/SKILL.md) loads on its own when the agent edits `.ts` or `.tsx` files.

## Clean before committing

The Opening a PR playbook runs [`/deslop`](../../skills/deslop/SKILL.md) on the diff before each commit and applies [`/unslop`](../../skills/unslop/SKILL.md) to the PR description and commit messages. `/deslop` removes narrating comments, unneeded guards, dead compatibility paths, and unrelated edits. `/unslop` takes a target and extra rules:

```text
/unslop the readme changes, no em dashes
```

## `/no-comments`: a second reviewer for comments

The agent that wrote a comment tends to defend it, so comments get reviewed by a different agent:

```text
/no-comments the diff
```

[`/no-comments`](../../skills/no-comments/SKILL.md) spawns the read-only `comment-reviewer` subagent, which keeps only license headers, doc comments on public APIs, links that explain what code can't, and behavior forced by an external dependency. A comment explaining surprising code in your own project comes back as a refactor flag, and `/no-comments` fixes the cause. A comment that claims a constraint ("do not remove") gets offered as a type, test, or lint rule instead.

In short: `/deslop` cleans code, `/unslop` cleans prose, `/no-comments` reviews comments with fresh eyes.

**Pitfall:** cleanup isn't optional. A padded diff reads as unfinished, and the extra code is where the next bug hides. Say `deslop it` before committing, not after a reviewer points it out.

Next: [Verify and ship](./06-verify-and-ship.md).
