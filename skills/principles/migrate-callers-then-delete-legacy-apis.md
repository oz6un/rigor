# Migrate callers, then delete legacy APIs

Once a new internal API is the chosen design, migrate every caller and delete the old API in the same change instead of keeping a compatibility layer.

- Don't keep an old API path just because internal callers still use it.
- List the callers, migrate them, and delete the old API.
- Treat temporary adapters as exceptions with a deadline, not as architecture.
- Re-point tests at the new contract. Delete a test only when its behavior is gone, and name it.

Applies when:

- No external users depend on backward compatibility.
- The project can absorb a coordinated breaking change.
- The new API is part of a simplification or refactor.

Keeping both APIs means two code paths to maintain, slower cleanup, and a codebase that only ever grows.
