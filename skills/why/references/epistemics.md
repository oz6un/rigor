# Epistemics

How to judge and communicate confidence when the evidence is historical, partial, and sometimes contradictory.

You can read what code does, but not why it exists. The why lives in commits, PRs, tickets, docs, and conversations, and any of those can be incomplete, biased, or missing. A confident answer built on guesses misleads the user, because they'll act on it.

## Confidence tiers

Every claim in the final output belongs to one tier. The tier decides which section it goes in and how it's worded.

| Tier | Meaning | Example | Wording |
|---|---|---|---|
| **Direct** | Something an author wrote that states the reason | A PR description: "fixes the bug where users with >1000 items couldn't paginate". A comment: `// clamp to 100 because the upstream API rejects larger values`. A chat message from the author: "switching approach since the old one was flaky in tests". | Plain, present tense, source cited: "This exists because X [PR #123]." |
| **Supported** | Several indirect pieces converge; none states it outright | The PR title says "improve performance", the ticket is labeled `perf`, and neighboring commits all touch the same hot path. | Confident but visibly derived: "The evidence points strongly to X: A, B, and C." |
| **Inferred** | A reasonable reading with no explicit support | The PR gives no reason, but the incident channel shows the error in production that day and the fix merged same-day, so it was likely a hotfix. | Hedged, with the reasoning shown: "Given A and B, C seems likely because D." |
| **Speculative** | Plausible, but thin evidence and other explanations fit as well | "This might work around a since-fixed browser bug, but we found no contemporary evidence." | Explicitly a guess: "One possibility is X, but there's no direct evidence." Usually under Competing hypotheses. |
| **Unknown** | You looked and couldn't find out | — | Say what you searched and for what: "We searched the tracker for A and B, read the 6 PRs touching this file since 2023, and grepped for the threshold literal. None gave a rationale." |

"Unknown" is a valid and useful result. Being specific about what was searched makes it actionable.

## Wording

**Words that assert cause or intent** need a citation right next to them, and belong only to Direct or Supported claims: "because", "the reason is", "was designed to", "fixes"/"addresses"/"solves", "the team decided".

**Hedging words** mark interpretation and belong in the inferred section: "appears to", "seems to", "likely", "suggests", "is consistent with", "one reading is", "plausibly", "may have been", "the evidence points toward".

**Avoid**: "obviously", "clearly", "of course" (if it were obvious the user wouldn't ask), dismissive "just" ("it's just for performance"), and "I think"/"I believe" (say "the evidence suggests").

## Don't rationalize

Code that makes sense today may have been written for reasons that no longer apply, or were wrong at the time. Don't:

- Assume the author did the right thing and work backward to a justification.
- Assume a pattern repeated across the codebase was deliberate; it may be copy-paste.
- Treat absence of evidence as evidence of absence ("nobody mentioned security, so it wasn't a concern").

## The user's hypothesis is a candidate

Users often embed a guess: "Why do we do this, I assume for performance?" Check it independently like any other hypothesis. If the evidence supports it, say so with citations. If not, say so and present what the evidence does support.

## Contradictions

When sources disagree (the ticket says "needed for customer X's compliance requirement", the PR says "cleaning up tech debt"), show both with citations. Both may be true (the ticket drove the work, the PR is the author's framing), or one may be wrong. Don't pick the one that makes a neater story; let the user decide.

## Missing evidence

An honest "we don't know" tells the user the answer isn't in the obvious places and that they need to ask a person (the author, the product owner, the team lead) or drop the question. Filling the gap with a confident guess does harm.

Name each gap concretely: the question you were trying to answer, the sources searched, what you searched for in each, and what turned up (nothing, or only tangential material).

## Calibration check before finalizing

Review every claim in What we found and What we can reasonably infer:

1. Does it have a citation? If not, add one or move it to inferred or hypotheses.
2. Does the wording match the tier? Direct may say "because"; Inferred may not.
3. Is the code being cited as evidence of its own intent? That isn't evidence. Remove or reclassify it.
4. Is there a What we don't know section? If there are no gaps, either the record was unusually complete or something is being glossed over.
