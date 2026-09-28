---
name: principles
description: Engineering principles for design, verification, and delegation decisions. Read the index, then the file for each principle you apply.
---

# Principles

Each principle is a short file in this directory. Use the line after each name to decide whether it applies, then read the full file before applying or citing it. Other skills refer to one as "the `fix-root-causes` principle (`principles` skill)".

## Core

- [`laziness-protocol`](laziness-protocol.md): sizing a diff, or tempted to add abstractions, layers, or parameters. Prefer deletion and the smallest change that solves the problem.
- [`foundational-thinking`](foundational-thinking.md): before writing logic. Choose the core types and data structures, sequence scaffolding before features, and work out what concurrent actors share.
- [`redesign-from-first-principles`](redesign-from-first-principles.md): adding a requirement to an existing design. Redesign as if it had been a requirement from the start.
- [`attack-the-premise`](attack-the-premise.md): two or more fixes that share a premise have failed the same check. Find which actors cause the problem, then question the premise instead of writing another fix that assumes it.
- [`subtract-before-you-add`](subtract-before-you-add.md): sequencing an addition, refactor, or rewrite. Remove dead code first, then build on the simpler base.
- [`minimize-reader-load`](minimize-reader-load.md): code that's hard to follow. Count the layers and hidden state, inline single-caller wrappers, shrink mutable scope.
- [`outcome-oriented-execution`](outcome-oriented-execution.md): planned rewrites and migrations with explicit phases. Move to the target architecture without building throwaway compatibility layers.
- [`experience-first`](experience-first.md): product, UX, or scope tradeoffs. Favor the user's experience over implementation convenience.
- [`exhaust-the-design-space`](exhaust-the-design-space.md): a new interaction or architecture with no precedent. Build two or three competing prototypes and compare them before committing.
- [`build-the-lever`](build-the-lever.md): any nontrivial work. Write the tool that does or checks the work (codemod, script, generator) instead of doing it by hand. A reviewer can rerun the tool.

## Architecture

- [`model-the-domain`](model-the-domain.md): stateful logic, heavy branching, or a shape assumption repeated across files. Encode the domain in a structure (state machine, typed model, lookup table, reducer) instead of scattered conditionals.
- [`boundary-discipline`](boundary-discipline.md): validation, error handling, or framework adapters. Validate at system boundaries, trust internal types, keep business logic pure.
- [`type-system-discipline`](type-system-discipline.md): designing types or signatures. Make illegal states unrepresentable, brand primitives, parse external data at boundaries.
- [`make-operations-idempotent`](make-operations-idempotent.md): commands, lifecycle steps, or loops that may be interrupted and retried. Running again should reach the same end state.
- [`migrate-callers-then-delete-legacy-apis`](migrate-callers-then-delete-legacy-apis.md): a new internal API replacing an old one. Migrate every caller and delete the old API in the same change.
- [`separate-before-serializing-shared-state`](separate-before-serializing-shared-state.md): concurrent actors might write the same file, branch, key, or object. Remove the sharing before adding locks or queues.

## Verification

- [`prove-it-works`](prove-it-works.md): before declaring a task done. Check the real artifact (run it, read the actual value, inspect the diff), not a proxy or "it compiles".
- [`fix-root-causes`](fix-root-causes.md): debugging. Reproduce first, keep asking why until you reach the cause, and fix it there.
- [`sequence-verifiable-units`](sequence-verifiable-units.md): multi-step work and how you stack commits and PRs. Split the work into small units that each end in a check, and verify each before starting the next.
- [`test-behavior-not-implementation`](test-behavior-not-implementation.md): writing, changing, or keeping a test. Call the code the way its users do and assert against a literal expected value. If the test would still pass with every imported function returning `undefined`, fix or delete it.

## Delegation

- [`guard-the-context-window`](guard-the-context-window.md): large outputs, long files, repeated reads, wide fan-out. Send bulk work to subagents and keep summaries in the main thread.
- [`never-block-on-the-human`](never-block-on-the-human.md): tempted to ask "should I do X?" about reversible work. Do it, show the result, and let the user correct course.

## Meta

- [`encode-lessons-in-structure`](encode-lessons-in-structure.md): you're writing the same instruction a second time. Turn it into a lint rule, a check, or a script instead.
