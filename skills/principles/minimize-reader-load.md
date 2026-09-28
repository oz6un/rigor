# Minimize reader load

Maintainability is the work a reader has to do to understand the code. Track two independent measures:

1. **Layers to trace:** how many indirections sit between a question and its answer.
2. **State to hold:** how much hidden or mutable context the reader must keep in mind.

**Why:** Code is read far more often than it's written. Line counts, cyclomatic complexity, and "clean architecture" are proxies; reader load is what matters. The two measures are independent: a flat file with 50 globals can be as hard to follow as a six-layer adapter stack. This is the human counterpart of [guard-the-context-window](guard-the-context-window.md).

- **Collapse layers that cost more than they save:** wrappers with one caller, adapters with no second implementation, indirection added for a need that never arrived. Inline them.
- **Each layer should change the abstraction.** A layer that repeats the same methods and arguments as the one below adds load without hiding anything. Collapse it.
- **Prefer narrow interfaces that hide real decisions.** A broad interface over little complexity makes readers learn both the surface and the implementation.
- **Shrink the scope of state.** Prefer pure functions (return values over mutation), locals over fields, fields over module state, module state over globals. Derive values instead of keeping copies in sync.
- **State an invariant once at the boundary,** not in every consumer.
- Before adding a layer or a piece of state, ask whether it reduces reader load elsewhere by at least as much.

Test: can a new reader answer "where does X come from?" and "what can change X?" in under 30 seconds? If not, remove layers or state.
