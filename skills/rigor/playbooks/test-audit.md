# Test audit

You own the test suite's value: confidence that every remaining test protects something and that nothing was lost, not a deletion count. Run it only when the user asks for an audit, never on tests that other changes on the branch touch. Criteria are in `references/test-audit.md`; read it first.

1. Read the repo's `CLAUDE.md` or `AGENTS.md`, find the test command, and run the suite once to record the baseline (all passing, or which tests fail).
2. Discover read-only. Read each candidate test in full, the production code it covers, its callers, and the overlapping tests. For a large suite, split discovery across `swarm` workers by area. Prefer a few high-confidence candidates over a long speculative list.
3. For each candidate, record every field under "Candidate evidence" in the reference file. A candidate with a missing field stays. A test that fails on the current code is never a deletion candidate: leave it out of the batch and report it as a possible product bug to handle separately (Bug fix playbook).
4. Edit one coherent batch that changes no production behavior, in its own commit: delete the chosen tests, move any check worth keeping into the stronger test, and delete test-only exports, helpers, and dead code the deletions unlock. Don't add replacement tests that restate the same thing.
5. Validate: run the tests for the touched area, then the full suite, and confirm the same tests pass as at baseline minus the deleted ones. Report test and production line counts separately (`git diff --numstat`).
6. For a batch of more than a few deletions, run `interrogate` on the diff before committing.
7. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`). For a wider audit, land one batch, then rerun discovery on the updated code for the next one.

**Reply:** each deleted test with every evidence field (including each deliberate break and the test that caught it), each candidate you kept and why, the baseline and final test results, and the test versus production line counts.
