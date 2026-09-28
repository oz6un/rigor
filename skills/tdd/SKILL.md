---
name: tdd
description: Fix a bug test-first, with a focused regression test that fails before the fix and passes after. Use when the user asks for TDD, a failing test, or a regression test, or when the bug has an obvious, cheap local test target. Skip it when the test path is unclear, expensive, or integration-heavy and nobody asked for it.
disable-model-invocation: true
---

# TDD bug fix

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` and follow it.

When a bug has a clear, cheap test path, make the broken behavior executable before changing production code. The goal is one focused regression test that fails before the fix and passes after it.

Don't force a test when it's impractical. If the test would need broad harness setup, brittle mocks, slow end-to-end infrastructure, production-only state, vague reproduction steps, or large unrelated fixture changes, skip the new test and use the closest useful check instead (see below).

## Steps

1. Understand the bug: the intended behavior, the current behavior, the code path involved, and the smallest observable reproduction.
2. Pick the narrowest executable check. Prefer the kind of test the codebase already uses for that code path (unit, component, integration, regression). If there's no practical test path, don't build one from scratch just to follow this skill.
3. Write the smallest test that would have caught the bug. Assert the intended behavior, not the current implementation (the `test-behavior-not-implementation` principle in the `principles` skill).
4. Run it before fixing. Confirm it fails, and fails for the reason you expect. If it passes, or fails for another reason, fix the test or the reproduction before touching the implementation.
5. Make the smallest production change that produces the intended behavior without breaking nearby contracts.
6. Rerun the test and confirm it passes.

## When a failing test is impractical

Use the closest executable check instead: a targeted script, a reproduction command, browser automation, a snapshot comparison, a log assertion, or a focused integration check.

No new test is better than a bad one. A bad test mostly exercises mocks, encodes implementation details, depends on timing or unrelated global state, needs expensive infrastructure for a small fix, or would be deleted right after proving the fix.

## Constraints

- Don't change a test to match a wrong implementation.
- Don't weaken existing assertions unless the expected behavior has actually changed, and say why.
- Keep the test focused on the bug. Avoid unrelated fixture changes or coverage expansion.
- If the bug is flaky, make the test deterministic where possible and say which signal it locks down.
- If the bug belongs to a broader class of failures, land the focused regression test first, then consider tests for the related cases.

## Report

- Name the test or check that failed before the fix, and the failure it produced.
- Name the passing run after the fix, and any nearby checks you ran.
- If you couldn't show a failure before the fix, say why and describe the check you used instead.
