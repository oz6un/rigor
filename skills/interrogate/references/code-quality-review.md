# Code-quality lens

Every reviewer applies this lens in addition to the rubric. It sets a high bar for implementation quality, maintainability, abstraction, and the health of the codebase.

Look beyond local cleanup. Actively search for restructurings that keep behavior the same while making the implementation much simpler, smaller, and more direct, often by using the existing architecture better. When a change like that is available, it is the most valuable finding you can make.

## Baseline task

> Audit the code quality of the current branch's changes in depth. Work out how the changes could be structured or implemented to meaningfully improve code quality without changing behavior: better abstractions and modularity, less tangled control flow, shorter and more readable code. If a clear improvement requires restructuring some of the surrounding codebase, propose it. Be thorough, and check your reasoning before recommending a change.

## Dimensions

Apply the ones that are relevant.

0. **Look for structural simplification first.** Don't stop at "this could be a bit cleaner". Look for a reframing that makes whole branches, helpers, modes, conditionals, or layers unnecessary. Deleting complexity beats rearranging it.
1. **File size.** A change that pushes a file from under 1,000 lines to over 1,000 needs a strong reason. Prefer extracting helpers, subcomponents, or modules first. Accept it only when there's a clear structural reason and the file stays well organized.
2. **Tangled growth in existing code.** Be suspicious of new ad-hoc conditionals, scattered special cases, and one-off branches added to unrelated flows. Treat them as a design problem, not a style nit. Prefer moving the logic into a dedicated helper, state machine, or module.
3. **Improve the design, not only the behavior.** If the structure can become meaningfully cleaner while behavior stays the same, recommend the cleaner version. Prefer simplifications that remove moving parts over refactors that spread the same complexity around.
4. **Direct over clever.** Flag brittle, ad-hoc, or implicit behavior. Be skeptical of generic mechanisms that hide simple assumptions about data shape. Flag thin abstractions, identity wrappers, and pass-through helpers that add indirection without adding clarity.
5. **Types and boundaries.** Question unnecessary optionality, `unknown`, `any`, and heavy casting when a clearer type boundary is possible. Prefer explicit typed models over loosely shaped objects. When a silent fallback covers up an unclear invariant, ask whether the boundary should be explicit.
6. **Right layer, existing helpers.** Flag feature logic leaking into shared paths and implementation details leaking through APIs. Prefer the codebase's existing utilities over new one-offs, and push code toward the package, service, or module where it belongs.
7. **Orchestration and atomicity.** When the cleaner structure is obvious, flag independent work that is serialized for no reason and related updates that can leave state half-applied. Don't chase micro-optimizations, but do flag orchestration complexity that makes the code brittle.

## Priorities

Report in this order: structural regressions and missed simplifications; tangled branching; boundary, type, and file-size problems; then smaller modularity and readability issues.

## Approval bar

Don't approve just because the behavior looks correct. Treat these as blockers unless the author can justify them:

- Significant incidental complexity remains when a restructuring would remove it.
- A file grows from under 1,000 lines to over 1,000.
- Ad-hoc branching is added to an existing flow.
- Feature checks are scattered across shared code.
- An unnecessary abstraction, wrapper, or cast-heavy contract is added.
- An existing helper is duplicated, or logic is placed in the wrong layer when there's a clear right one.

Otherwise, leave specific, actionable feedback and push for a cleaner decomposition.

## Tone

Be direct and specific. Don't be rude, and don't soften a major maintainability problem into a mild suggestion. If the change makes the codebase messier, say so. If it missed an obvious large simplification, say that. Don't settle for "maybe rename this" when the real issue is structural.
