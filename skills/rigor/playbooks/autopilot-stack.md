# Autopilot (stack)

You own the stack, not the landing. Build and verify the queue with full autonomy, then hand the user one linear stack of PRs to review and land. This is the sibling of `playbooks/autopilot-full.md`; the shared machinery (operator gates, audit tick, liveness, owner lifecycle, verification rounds, countersigns) is in [`playbooks/orchestrate.md`, Shared program rules](orchestrate.md#shared-program-rules).

**Choosing between the autopilots.** Use Autopilot (full) when the PRs are independent and the user has granted merge authority. Use Autopilot (stack) when the user wants to review before landing, the work is sequenced or coupled, or merge authority is withheld.

1. **Run the owner loop.** One owner subagent per PR follows the Owner lifecycle through babysit to green. Owners run in parallel when the work is self-contained.
2. **Audit on a timer.** Run the audit tick per Wake mechanics and the audit tick, re-reading this file and the armed objective each time, and probe owners and every owner's `children.tsv` per Liveness.
3. **Hold the user's gates.** A request to state the plan is not a go. On an explicit go, arm the objective per Operator gates. On a stop, every owner holds with zero writes immediately.
4. **Verify each round.** Owners report the code-ready head SHA once the code is final, and STACK-READY with the exact head SHA when their loop is green. Run a verification round per Verification rounds, with STACK-READY in place of merge-ready. Nothing enters the stack unverified.
5. **Append on a clean verdict; never ship.** No owner merges, enables auto-merge, or closes a PR. A clean verdict appends the PR to the single linear stack, in verified order or the order the user specified.
6. **Keep one writer for the stack's shape.** Owners push only their own branches and report the tip, current base, and intended parent. Only you change the stack's topology. To append a PR:
   1. Fetch the intended parent and rebase the child branch onto that exact parent tip.
   2. Check the remote head with `git ls-remote`, then push with `--force-with-lease`.
   3. Point the PR at the parent branch: `gh pr create --base <parent-branch>` for a new PR, `gh pr edit <pr> --base <parent-branch>` for an existing one. Only the bottom PR targets trunk. Don't submit or register the chain through `gt`.
7. **Absorb trunk drift yourself, then re-verify what moved.** Fetch current trunk and rebase the chain bottom to top. When a rebase conflicts in an owner's files, that owner fixes its own slice and you push the result. A rebase rewrites every SHA above it and voids the verdicts at the old SHAs, so apply the patch-id rule in `playbooks/shipping.md` at each verdict SHA and send anything no longer valid back through step 4. Re-run mergeability and CI after every rewritten push, even when the patch-id is unchanged. Countersigns work as in Autopilot (full).
8. **Deliver the chain.** The deliverable is one linear chain of verified PRs, reviewable bottom-up on GitHub, each carrying its verdict in the PR body or a comment. The user reviews and lands it, by merging each PR or by enabling auto-merge.

**Reply:** links to the bottom and top of the stack, a one-line verdict summary per PR, and anything parked or excluded with the reason.
