# Visual parity

You own pixel-exact equivalence. The baseline is the spec and you don't modify it. Equivalence is checked by image diff, not by eye.

1. Establish the baseline before any migration: a visual regression harness that screenshots the current component in each of its states, plus the target implementation when matching two of them. Without a baseline there's no parity claim, so this blocks everything else.
2. State these constraints up front and hold to them: no changes to the harness, no changes to the baseline, and no restructuring a component just to make a diff pass. If the baseline looks wrong, stop and ask the user instead of editing it.
3. Migrate one component at a time. Shared primitives migrate first, as a blocking phase. After that, parallelize across worktrees with one owner per component (the `separate-before-serializing-shared-state` principle).
4. Verify each component against its baseline by image diff on the real surface with `control-ui`. Any nonzero diff is a failure: investigate the pixel delta and iterate on that component (under `/goal`, both hosts) until the diff is zero.
5. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`) per component or per safe batch.

**Reply:** the components migrated, the diff result for each, the baseline harness location, and what's left.
