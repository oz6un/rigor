# Outcome-oriented execution

Optimize for a correct, verifiable end state rather than keeping every intermediate state smooth.

**Why:** Keeping each intermediate step fully working often means writing temporary compatibility code, which tends to become permanent. Move straight to the target architecture and prove correctness at explicit verification points.

- Put end-state integrity ahead of transitional stability.
- Intermediate breakage is acceptable when it's planned, scoped, and reversible.

Guardrails:

- Use this only for planned rewrites and migrations with explicit phase boundaries.
- Say up front where temporary breakage is acceptable.
- Keep fast, high-signal checks running on the areas you're actively changing.
- Run full static and runtime verification when the plan completes.

See also [migrate-callers-then-delete-legacy-apis](migrate-callers-then-delete-legacy-apis.md).
