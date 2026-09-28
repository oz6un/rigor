---
name: architect
description: Sketch the caller's usage, types, signatures, and module structure before writing implementation, using several independent design candidates, then implement against the chosen sketch. Use for /architect, "design this", or nontrivial work where jumping straight to code would lock in the wrong shape.
---

# Architect

Design before implementing. Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Compare several independent candidates, combine them into one sketch, then fill in code against it. If implementation shows the sketch is wrong, discard it and redesign.

Start a todo list with one item per phase: Ground, Sketch, Agree, Implement, Scrap.

## Phase A: Ground the problem

Build an accurate model of every system the new code touches by running the `how` skill over the relevant subsystems. Naming a file isn't grounding; produce the traced model `how` describes. If the design changes ownership or layering, also run the `why` skill on the existing shape so its rationale becomes a known constraint instead of a guess.

Skip this phase only for greenfield work with no surrounding system to integrate with.

## Phase B: Sketch

Run the `arena` skill with the design-sketch task and the Phase A artifacts. Use [`references/runner-prompt.md`](references/runner-prompt.md) as each candidate's prompt. Each candidate produces a design package shaped by [`references/rationale-template.md`](references/rationale-template.md).

Panel: arena's default, including its other-CLI candidate. A design sketch is code, so each candidate gets its own worktree as arena describes. For architect, give each host candidate a different structural starting direction in its prompt so the panel explores whole alternative shapes rather than variations on one.

- Require at least two structurally distinct candidates before combining, even if the first looks sufficient (the `exhaust-the-design-space` principle). Distinct means a different overall shape, not a point fix inside the same shape.
- Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md) before combining. Reject or revise shallow modules, information leakage, temporal decomposition, and pass-through methods.
- Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A capable interface keeps call chains short by concentrating behavior instead of spreading it across layers.

Arena returns one combined design package. Its pick-and-combine record fills the rationale's "Synthesis decision" section.

## Phase C: Agree (opt-in)

By default, go straight to implementation with the combined design.

Add a checkpoint only when the user asks for one ("/architect with checkpoint", "show me before implementing"). Then present the design and wait for sign-off.

Either way, the sketch can land as its own commit, as the scaffold-first approach in the `foundational-thinking` principle. Planned, scoped breakage while filling it in is fine (the `outcome-oriented-execution` principle). For adversarial pressure on the design before implementing, run the `interrogate` skill on the sketch.

If the user pushes back on the shape at any point, treat that as new Phase A evidence: re-ground and rerun Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code and pseudocode with logic. The sketch is the contract.

Surface deviations instead of absorbing them. If a function needs a parameter the sketch didn't anticipate, decide whether the sketch was wrong, a requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, discard the sketch. Don't bolt fixes onto a wrong design (the `redesign-from-first-principles` and `fix-root-causes` principles).

Look for a pattern, not a single instance:

- The same kind of workaround appears repeatedly in unrelated code.
- Several unrelated edge cases each need a special-case branch.
- Types need escape hatches (`any`, casts, optional fields that are always set in practice) to compile.
- You reach for a lock when the sketch said the state wasn't shared.
- Callers need to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations have the same shape.

A few edge cases don't condemn a design, and some problems are genuinely complex. Complexity in the data is not complexity in the design.

To scrap:

1. Rerun `how` over what has been built.
2. Redesign as if the new constraints had been known from the start.
3. Remove before adding (the `subtract-before-you-add` principle). The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and rerun the arena.

## Output

The caller's usage, written first, and the type sketch derived from it. For small changes, one file with the new types and signatures; for larger work, a module map plus type definitions. The rationale ships alongside, following `references/rationale-template.md`, including the usage sketch and the synthesis decision.
