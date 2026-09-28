# Boundary discipline

Put validation, type narrowing, and error handling at system boundaries. Trust internal code. Keep business logic in pure functions and the framework shell thin and mechanical.

**Why:** Validation scattered through the code is noisy and redundant, and it gives a false sense of safety. Logic kept out of framework wiring can be tested without the framework.

- **At boundaries** (CLI args, config files, external APIs, network protocols): validate, return errors, handle input defensively.
- **Inside the system:** pass typed data, propagate errors, don't re-validate. Trust the types.
- **Across the boundary:** expose domain concepts, not the boundary's private representation. Keep general-purpose mechanism inside and special-purpose policy at the edge.

Applications:

- Validate config when it's parsed, not inside business logic.
- Parse raw data into domain types at the boundary (see [type-system-discipline](type-system-discipline.md)).
- Don't re-export transport, storage, framework, or wire types through the public surface.
- Skip nil checks deep in a call chain when the boundary already validated.
- Write business logic as pure functions with no framework dependencies: parsers turn raw bytes into typed state, prompt builders take structured state and return a string, scoring turns state into results.

Tests:

- Is this data crossing a system boundary right now? If not, the validation is redundant.
- Could this be a pure function the shell just calls? If so, extract it.
