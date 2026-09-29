# Test audit

You own the test suite's value: fewer tests that each protect something, and nothing lost. Criteria are in `references/test-audit.md`; read it first.

1. Read the repo's `CLAUDE.md` or `AGENTS.md`, find the test command, and run the suite once to record the baseline (all passing, or which tests fail).
2. Discover read-only. Read each candidate test in full, the production code it covers, its callers, and the overlapping tests. For a large suite, split discovery across `swarm` workers by area. Prefer a few high-confidence candidates over a long speculative list.
3. For each candidate, record every field under "Candidate evidence" in the reference file. A candidate with a missing field stays. A test that fails on the current code is never a deletion candidate: reproduce it and fix the code.
4. Edit one coherent batch: delete the chosen tests, move any check worth keeping into the stronger test, and delete test-only exports, helpers, and dead code the deletions unlock. Don't add replacement tests that restate the same thing.
5. Validate: run the tests for the touched area, then the full suite, and confirm the same tests pass as at baseline minus the deleted ones. Report test and production line counts separately (`git diff --numstat`).
6. For a batch of more than a few deletions, run `interrogate` on the diff before committing.
7. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`). For a wider audit, land one batch, then rerun discovery on the updated code for the next one.

**Reply:** each deleted test with its evidence (what it detected, the stronger test that still catches it), each candidate you kept and why, the baseline and final test results, and the test versus production line counts.
