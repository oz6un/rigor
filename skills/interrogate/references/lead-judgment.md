# Lead judgment

The reviewers have reported. Your job is to filter, put findings in context, and decide, not to aggregate.

## Why this step matters

Adversarial reviewers are useful because they're aggressive, but without context aggression produces noise. The reviewers saw a slice of the codebase and the user's request. They don't know:

- What was already tried and rejected.
- Constraints outside the code (timeline, dependencies, migration plans).
- Which code is temporary scaffolding and which is permanent.
- What the next PR in the stack will address.

You have the full conversation. Use it.

## Filtering

**Filler findings.** Reviewers tend to fill the space. With no critical issues to report, they inflate nits. If a reviewer's findings are all nits and style preferences, the code is probably fine; say so.

**Hypothetical versus actual.** "What if someone passes null?" is a finding only if a caller can pass null. Trace the call site. If upstream validation or the type system prevents it, dismiss it. Reviewers working from a diff can't always see the whole call chain; you can.

**Reproduced versus reasoned.** A reproduced finding is real; the rules below decide what to do about it. Confirm a reasoned one yourself before acting on it, or put it under Consider.

**Suggestions that add code.** Reviewers lean toward adding guards and machinery. Before accepting one, ask how likely the failure it guards against is; if it isn't, put it under Noted. A suggestion to remove something deserves the opposite bias.

**Conflicts with the request.** A finding that argues with what the user asked for goes to the user, not into Act on or Dismissed.

**Premature abstraction.** Reviewers often suggest extracting functions or adding interfaces. Ask whether the code needs to vary in a second way. If not, the abstraction is premature, and simple inline code is better.

**"I would have done it differently."** The most common false positive. A different preferred approach isn't a bug or a design flaw unless the reviewer shows a concrete problem with the current one. Dismiss these and say why.

**Missing context.** Signs a reviewer lacked context:

- Suggesting changes to code the author didn't write or touch.
- Flagging a pattern that is consistent with the rest of the codebase.
- Recommending an approach that conflicts with constraints you know about.

These are honest mistakes from reviewers with limited information. Dismiss them without blame.

## When reviewers are right

Don't dismiss a finding because it's uncomfortable; catching what you'd miss is the point. A finding deserves attention when:

- Several reviewers raise it independently, especially across model families.
- It names a concrete execution path, not a hypothetical.
- It exposes a gap in your understanding of the code.
- Reading it, you realize it's right.

Be especially careful before dismissing security findings and correctness bugs, even from a single reviewer.

## Calibrating the verdict

A good verdict is useful, not exhaustive. The user should be able to fix the Act on items and ship with confidence. More than five Act on items usually means you aren't filtering hard enough.

The Dismissed section matters: showing what you rejected and why lets the user override you where they disagree.
