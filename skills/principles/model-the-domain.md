# Model the domain

Encode the domain in a data structure instead of scattering it across conditionals.

**Why:** Scattered booleans, repeated assumptions about a shape, and branching spread across files are accidental complexity. A structure that matches the domain rules out invalid states and removes branches. Choosing it while writing the code is cheap; introducing it later looks like a refactor and tends to get postponed.

Structures to consider:

- A state machine instead of scattered booleans, phase flags, or lifecycle checks.
- A typed object or model instead of loose parameters or repeated shape assumptions.
- A map, registry, lookup table, or discriminated union instead of branching spread across files.
- A reducer or command/event model instead of ad hoc mutations.
- A module organized around one area of domain knowledge, instead of around steps like load, validate, transform, save. Execution order isn't ownership.
- A small module boundary that gathers repeated behavior, ownership, or invariants.
- A queue, cache, index, graph, tree, or normalized collection when the access pattern calls for it.
- Anything else that fits. If nothing obvious does, work out what the code must never allow and how the data is read, then pick the structure that encodes exactly that.

Don't force an abstraction. If the current code is clear, local, and unlikely to grow, leave it plain. Be skeptical of an abstraction that adds indirection without removing branches, duplicated rules, invalid states, or lifecycle risk.

Signs you skipped this step: a new feature adds one more branch to an existing if/else chain, a second boolean has to stay in sync with the first, or modules named after phases repeat the same domain rules at each step.

See also [type-system-discipline](type-system-discipline.md) and [foundational-thinking](foundational-thinking.md).
