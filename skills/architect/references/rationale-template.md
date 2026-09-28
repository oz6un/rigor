# Rationale template

The prose that ships with the type sketch. Keep it to about one page, with sentence-case headings. Replace each italic note with real content.

## Problem

*One paragraph: what we're trying to do, and what about the existing system or constraints makes the shape non-obvious. Name the constraints [Phase A](../SKILL.md#phase-a-ground-the-problem) surfaced (existing types to interoperate with, callers we can't break, invariants that cross our boundary) so the reader sees what you saw.*

## Usage (caller's view)

*Write this before the type sketch. Show the README or quickstart a consumer would read, plus two or three realistic call sites in their code: what they import, what they call, what comes back. The sketch in [Shape](#shape) is derived from this, and the two must agree. When they diverge, change the sketch to fit the usage, not the reverse.*

## Shape

*The recommended architecture. Data structures first, then how data flows through the signatures. Name the decisions everything else depends on. State which invariants the types encode, where validation happens, and what the system deliberately doesn't do. Assess interface depth explicitly: what complexity the public surface hides, what stays exposed to callers, and why the interface is no larger than it needs to be. Cite the principle behind each decision (for example, "per `boundary-discipline`") without restating it.*

## Synthesis decision

*Filled in from the [arena](../../arena/SKILL.md) run: which candidate became the base and why, what was brought in from each of the others, and what was rejected and why.*

## Tradeoffs accepted

*One bullet per tradeoff, in the form "we accept X in exchange for Y". Include anything a future reader might mistake for an oversight, such as something that looks like premature optimization or premature simplification.*

## Alternatives considered

*Required. Name at least one concrete alternative shape and one line on why it lost, judged on interface depth and not only implementation simplicity: what complexity it would expose to callers and what it would hide. List two or three when the design space had real contenders. One is fine when the constraints forced the answer; phrase it as "this was the only viable shape because...". Don't list variations of the same shape. This section is about design alternatives, not the other arena candidates.*

## Open questions and risks

*Decisions the user needs to weigh in on, and risks worth flagging before implementation. Phrase them as questions so the user's answer resolves them.*

## Next implementation step

*One sentence: the first thing you'd build against the sketch, right after synthesis (or after sign-off, if a checkpoint was requested).*
