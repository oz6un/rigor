# Test audit criteria

Adapted from OpenClaw's `test-audit` skill (MIT, OpenClaw Foundation). Used by `playbooks/test-audit.md`.

## Worth deleting

A test earns its cost by catching a credible regression in behavior someone observes. Each behavior needs one test at the strongest boundary that reaches it, usually the entry point callers use. These usually don't earn it:

- tests with no real assertion, or whose expected value comes from the code under test;
- copied fixtures, manifests, or export lists;
- greps of source, imports, or a library's own error wording;
- private-helper tests that duplicate a test at the real boundary;
- two tests of the same behavior with the same setup;
- mocks or fixtures that supply the result being asserted;
- negative tests that pass for an unrelated reason;
- tests that exist only to keep a test-only export or wrapper alive.

## Worth keeping

- Anything guarding a published contract: public API, CLI flags and defaults, wire keys, file and storage formats, migrations, security, platform behavior. A restated string or default counts when it's published, not when it's an internal constant.
- Observable call ordering (API calls made, events emitted).
- Regressions with a credible failure mode.
- A test that fails now: that's a possible bug, not a deletion.

Slow is not a reason to delete, and looking like implementation isn't proof; show the break before removing it.
