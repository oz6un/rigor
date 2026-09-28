### Shipping

You own what lands. Verify each PR independently, land only the verified run starting from the bottom of the stack, and don't rearrange the queue while it merges.

This playbook starts where `playbooks/babysit.md` ends. All PR operations use the GitHub CLI (`gh`); don't require Graphite (`gt`).

1. **Verify every PR independently.** Spawn one subagent per PR (not one for the batch), each an agent that did not write the code. Each one exercises the real surface with the matching control skill (`control-ui` or `control-cli`), comparing the PR's parent against its head, returns `PASS`, `PASS+NOTES`, or `FAIL`, and posts that verdict on its PR. Only a verdict from an agent that didn't write the code counts. Green CI and an approving bot review are not verdicts.
2. **Land only the contiguous verified run from the bottom.** Walk up from the lowest unmerged PR and stop at the first one without a passing verdict (`PASS` and `PASS+NOTES` both pass). A verified PR above an unverified one isn't landable. Report the ceiling as a PR number and say what breaks the chain.
3. **Check that each verdict still describes the patch.** For each verdict, record the head SHA, the base SHA, and the `git patch-id --stable` of that PR's base-to-head diff. A rebase or retarget rewrites SHAs and can invalidate a verdict without touching any check, so before landing a PR, compare the recorded patch-id with its current one.
   - Patch unchanged: keep the code verdict, but re-run mergeability and CI at the current head.
   - Patch differs only in tests, docs, or lint config: build what each verification lane ran, twice at the verdict SHA and once at the current head. A difference is noise if the two verdict-SHA builds also differ there, or if it is an embedded commit SHA. Judge each difference, not each file, and report each kind of noise with its files. If only noise differs, that lane's result stays valid; run checks and a review of the change fresh. A lane with no build output (for example, one run against a dev server) can't be compared this way, so rerun it.
   - Anything else changed: re-verify.

   Matching commit messages or a green check from an older SHA are not substitutes for this comparison.
4. **Prepare only the bottom PR.** Fetch trunk. If needed, rebase the lowest verified branch onto the exact trunk tip, push it, and retarget only that PR with `gh pr edit <pr> --base <trunk>`. Re-run step 3 after the push. Don't retarget, arm, or merge anything above it yet.
5. **Land one PR at a time.** If the bottom PR is mergeable now, run `gh pr merge <pr> --squash`. If its checks are still running and the user asked for merge-when-ready, arm only that PR with `gh pr merge <pr> --squash --auto`. Wait for it to merge before preparing the next one.
6. **Don't read `autoMergeRequest` as stack readiness.** It only says auto-merge was requested for that one PR. It doesn't mean a descendant is queued, that a verdict is current, or that the stack is safe. Confirm the current bottom PR's state directly, and say the state is unknown if GitHub can't report it.
7. **Recompute after every merge.** Fetch trunk, confirm the merged SHA is present, drop the merged PR from the frozen bottom-to-top list, and inspect the new bottom PR's base, head, checks, and patch-id. GitHub may retarget a child automatically, but don't assume it did. Repeat steps 3 through 6 for that PR. Independent work stays outside this chain and ships on its own.
8. **Watch the current frontier until it merges or fails, without changing the queue around it.** Use `scripts/watch-pr/watch-pr --queued-stack --stack-prs <bottom>` only as a wake-up signal. After each wake, poll `gh pr view <pr> --json state,mergedAt,mergeStateStatus,statusCheckRollup,autoMergeRequest` and ignore `READY` until `mergedAt` is set or `state` is `MERGED`; only then run step 7. Treat it as a failure only when:
   - `state` is `CLOSED` with no `mergedAt`;
   - a required check concludes `FAILURE` or `CANCELLED` and blocks the merge after auto-merge is no longer pending; or
   - `mergeStateStatus` is `UNSTABLE` or `DIRTY` with no auto-merge pending.

   `BLOCKED` while checks are pending or auto-merge is armed is not a failure. Babysit's `WAITING`/`merge-queue` stop condition doesn't apply here. Hold the watch under a self-paced loop (Claude Code: `/loop` without an interval; Codex: `/goal`). Report each merge and the new ceiling. If the queue stalls, diagnose before changing anything.
9. **Stop at the ceiling.** When the verified run has merged, report what landed, which PR is the next unverified one, and what verifying it would take. Extending the run is a new pass starting at step 1.

**Reply:** the verified run and its ceiling, each PR's verdict and which agent produced it, what you armed and how you confirmed it, what landed, and what the next gap needs.
