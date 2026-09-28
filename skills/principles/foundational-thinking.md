# Foundational thinking

Structural decisions protect option value; code-level decisions protect simplicity.

**Data structures first.** Get the shape of the data right before writing logic. Define the core types early, trace every access pattern, and choose structures that fit the dominant paths. See [model-the-domain](model-the-domain.md).

At the code level, deduplicate structure, not every line. Types and data models should converge on one definition, but three similar statements still beat a premature abstraction. Prefer explicit code to clever code.

**Concurrency.** Before sharing state between actors, ask what happens if another actor modifies it concurrently. If the answer isn't "nothing", isolate it (see [separate-before-serializing-shared-state](separate-before-serializing-shared-state.md)).

**Scaffolding first.** If something helps every later phase, do it first. CI, linting, test infrastructure, and shared types are scaffolding. Order for option value: setup before features, tests before fixes. Keep commits small and single-purpose.

Each increment should add a coherent abstraction or deepen an existing one. Don't spread a new capability across callers as special-case coordination.

Removal comes before scaffolding: delete dead code first, then lay foundations (see [subtract-before-you-add](subtract-before-you-add.md)).
