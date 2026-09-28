# Review rubric

Use the sections that apply to the change. Not every section applies to every diff.

## Correctness

Does the code do what the intent says?

- Edge cases: empty input, null or undefined, boundary values, concurrent access.
- Error handling: are errors caught, propagated, or silently swallowed?
- Off-by-one errors, type coercion, integer overflow, string encoding.
- State: race conditions, stale closures, dangling references.
- Both the success path and the failure path.
- Idempotency: what happens if the operation runs twice, or if a previous run crashed halfway? If the answer depends on what state was left behind, a reconciliation step is missing.
- Concurrency: if several actors can touch the same mutable state (files, branches, shared data), is access controlled by structure (locks, sequential phases, exclusive ownership) or only by convention?

When you suspect a bug, trace the execution path. Don't just say "this could be null"; show the call chain that makes it null.

## Root causes and symptoms

Does the change fix the actual problem or hide a symptom? Answering usually means reading past the changed files: callers, callees, type definitions, sibling modules. Understand why the code exists before judging whether the change is at the right layer.

- Guard clauses that mask a broken invariant.
- Retries that hide a broken contract.
- Type casts that silence a modeling error.
- A workaround: why is it needed, and what would the proper fix be?
- A fix in module A that belongs in module B's contract.
- A rule enforced only by a comment or convention ("don't do X") that could be a type constraint, lint rule, or runtime check.

## Structural integrity

Does the change fit the system it lives in?

- Boundaries: is validation done once where data enters the system, or scattered through business logic?
- Abstraction level: does the code mix high-level orchestration with low-level detail?
- Coupling: do new dependencies make future changes harder?
- Data model fit: do the data structures match the actual access patterns?
- Integration: does the change read as if the design always accounted for it, or was it patched on? If the requirement had been known from the start, would the code look like this?
- Legacy paths: does the change add a new API while keeping the old one alive? Without external consumers, callers should be migrated and the old path deleted in the same change.

Don't penalize simple code for lacking abstraction. A premature abstraction is worse than some duplication.

## Verification

Can you tell from reading it that the code works?

- Are there tests, and do they test behavior rather than implementation details?
- Are there assertions or invariants that would catch a regression?
- For a bug fix, is there a test that reproduces the bug?
- For a change at an integration boundary, is the full path tested?
- Does the code check the real value, or a proxy for it (a file's mtime, cached state)?
- For delegated or async work, does the code check the actual output, or trust a self-report?

## Complexity budget

Is the complexity justified by what the code does?

- Code that could be simpler without losing correctness or clarity.
- Abstractions with a single call site.
- Configuration or parameters for cases that don't exist yet.
- Dead code, unused imports, leftover parameters.
- Speculative code paths with no current callers.
- Compatibility scaffolding kept after the migration it served is finished.
- Features, controls, or options that don't earn their place in the user experience. A half-finished feature is worse than a missing one.

## Security

For each security finding, trace the input path through the code and show it.

- User input reaching dangerous sinks (SQL, shell, eval, innerHTML) without sanitization.
- Missing authentication or authorization on new endpoints.
- Secrets in code, logs, or error messages.
- Time-of-check to time-of-use gaps in security-sensitive paths.
