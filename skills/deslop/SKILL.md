---
name: deslop
description: Remove AI-generated clutter from the current branch's code changes before committing. Use before a commit or when asked to clean up a diff.
disable-model-invocation: true
---

# Deslop

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` (with symlinks in this skill's path resolved) and follow it.

Review the diff against the base branch (default `main`) and remove clutter that this branch introduced. Existing code outside the diff is out of scope.

## What to remove

- Comments that are unnecessary or don't match the file's style. The `no-comments` skill covers comments in depth.
- Defensive checks and `try`/`catch` blocks that are unusual for a trusted internal code path.
- Casts to `any` (or `as` casts) that exist only to silence a type error.
- Deep nesting that early returns would flatten.
- Tests this branch added that don't each catch a regression no other test catches: ones that repeat existing coverage, test trivial code, or check implementation instead of behavior. Keep the bug's reproduction, one test per added behavior, and a refactor's behavior pin. Never remove existing tests here.
- Anything else inconsistent with the file and the surrounding code: naming, error handling, logging, helper patterns.

## Constraints

- Keep behavior unchanged unless you're fixing a clear bug, and say so if you do.
- Make small, focused edits rather than broad rewrites.
- Finish with a one-to-three-sentence summary of what you removed.
