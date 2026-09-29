# Test audit

You own the test suite's value: every remaining test protects something, and nothing was lost. Optimize for confidence, not deletion count. Criteria are in `references/test-audit.md`; read it first.

1. Find the test command in `CLAUDE.md` or `AGENTS.md` and run the suite once to record the baseline.
2. Read each candidate test, the code it covers, and the tests that overlap it. For a large suite, split this across `swarm` workers by area.
3. For each candidate, show it's redundant: for each assertion, make a small break of the covered code in a scratch copy and confirm a remaining test also fails. If none does, keep it or move the check into the remaining test first. A test that fails at baseline isn't a candidate; report it as a possible bug.
4. Delete the chosen tests in one commit that changes no production behavior, along with test-only helpers, exports, and code the deletions leave unused.
5. Run the full suite and confirm the same tests pass as at baseline, minus the deleted ones.
6. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`).

**Reply:** each deleted test with the break you tried and the test that caught it, candidates you kept and why, and the baseline and final results.
