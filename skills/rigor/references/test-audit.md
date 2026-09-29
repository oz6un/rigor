# Test audit criteria

Adapted from OpenClaw's `test-audit` skill (MIT, OpenClaw Foundation). Used by `playbooks/test-audit.md`. The deletion criteria here apply only in a Test audit the user asked for; elsewhere, the rigor skill's Evidence rules govern.

## Value bar

Optimize for confidence, not deletion count: an uncertain candidate stays. A test justifies its maintenance cost by protecting observable behavior, a credible regression, or an independently meaningful contract. Each contract has one primary test at the strongest boundary that can reach it (usually the entry point callers use). Another test of the same contract needs its own distinct risk, such as a transport or lifecycle failure the primary test can't reach. Prefer adding a case to a table-driven test over a near-duplicate test.

A test that breaks under a behavior-preserving refactor is asserting implementation. In an audit that makes it suspect, not automatically deletable.

## Junk patterns

- assertion-free coverage probes;
- self-comparisons, and expected values produced by the code under test;
- copied fixtures, inventories, manifests, or export lists;
- exact source, import, or string greps, including a library's own error wording;
- private-helper or call-shape tests that duplicate a test at the real boundary;
- two tests invoking the same contract with the same setup;
- tests whose only purpose is keeping a test-only export, global, or wrapper alive;
- production code whose only callers are tests;
- mocks that implement the behavior being asserted;
- fixtures that supply the result the code under test should produce;
- negative tests that pass for an unrelated reason (a different guard rejects the input);
- names that promise more than the test exercises.

## Retention bar

Keep a test that independently enforces a public API, protocol, config, storage format, migration, security, platform, default, or release contract. A default or string counts when it's published (a CLI default, a wire key, a file format), not when it's a hand-tuned internal constant. Where the `test-behavior-not-implementation` principle and this file disagree, this file wins. Also keep:

- call ordering when the order is observable (API calls made, events emitted);
- regressions with a credible failure mode;
- a source or string check when it's the cheapest independent guard of a user-facing key, byte, or path;
- a test that fails on the current code: report it as a possible product bug to handle outside the audit, never by deleting the test.

Slow or static is not a reason to delete. Resembling implementation is not proof; show it before removing.

## Candidate evidence

Record every field before deleting a test. A missing field means the candidate isn't ready:

- exact test name and location;
- what failure it can actually detect;
- non-test callers of the code it covers;
- for each assertion in the test, the smallest break of the covered code that makes that assertion fail (made in a scratch copy), and the remaining test that also fails on it, with the command output. A break no remaining test catches means the candidate stays, or its check moves to another test first;
- relevant history (why the test or its seam exists);
- what the deletion unlocks (test-only exports, helpers, dead code);
- risk, and the focused command that validates the change.
