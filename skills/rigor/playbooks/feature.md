# Feature

You own the design and the result.

1. Run `how` over the affected subsystem.
2. Run `architect` to explore designs in parallel.
3. Write the throughput checkpoint as four todo items. If one doesn't apply (a single file, nothing to fan out), keep the item and mark it `n/a: <reason>` instead of dropping it.
   - **Blocking first steps:** what has to finish before any fan-out.
   - **Independent workstreams:** disjoint files, services, or layers that can run in parallel. Work that writes the same place runs in sequence.
   - **Shared mutable state:** by default, split the target so actors don't share it (the `separate-before-serializing-shared-state` principle). Serialize only for real invariants.
   - **Smallest safe decomposition:** if one worker is best, say why.
4. Implement it, with tests for the new behavior's main case and for each edge case a plausible wrong implementation would get wrong (one test per distinct bug; no tests that only repeat another's coverage). Choose the data shape and its organizing structure before writing logic (the `model-the-domain` principle). Make surgical edits, and carry improvements to a shared helper over to every caller. Delegate only independent tracks, per "Subagents" in `SKILL.md`; use the `arena` skill only when the user asks for alternatives or the design is high-stakes and genuinely open.
5. Verify on the matching surface: `control-ui` or `control-cli` for UI and CLI changes, otherwise the real entry point callers use (the API, library call, or job). An inconclusive result, or a pass on a different surface, is not a pass; flag it.
6. Rebase into small, ordered commits, and stack follow-ups as separate commits or PRs. Build, verify, and commit each small unit before the next (the `sequence-verifiable-units` principle).
7. If the design is contested, run `interrogate` before shipping.
8. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`).

**Reply:** what you built, what you chose and why, the throughput checkpoint, and open decisions. Use tables for design alternatives.
