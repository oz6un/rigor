# Autopilot (full)

You own the verdicts, not the PRs. One owner subagent takes each PR from build to merge, and nothing merges without your clean verdict. Use this for "autopilot this queue", "full autopilot", and other one-owner-per-PR programs.

This differs from Orchestrate, where the coordinator lands verified work and workers never merge. Here each owner carries its PR through the merge, and you (the root) keep only verification, countersigns, and audits. The operator gates, audit tick, liveness, owner lifecycle, verification rounds, and countersigns are defined once in [`playbooks/orchestrate.md`, Shared program rules](orchestrate.md#shared-program-rules).

1. **Mark the user's items and wait for the go.** Note which items the user reserves for themselves; no owner merges those. If asked to state the plan, state it and stop. On an explicit go, arm the objective per Operator gates.
2. **Spawn one owner per PR.** Each follows the Owner lifecycle through merge-ready and then merges (step 5). Use `gh` for PR operations. The merge is the one step an owner may not take on its own; step 4 gates it.
3. **Run owners in parallel and don't stack.** Run many owners at once when PRs are self-contained: one writer per branch, disjoint files, and cross-PR drift absorbed by rebasing. Serialize only work that genuinely overlaps. Self-contained PRs branch from trunk; sequenced work branches after its parent merges. The one exception: an owner that must split a genuinely dependent change may keep a short private stack on its own base branch.
4. **Verify every round before its merge.** Run a verification round per Verification rounds at each code-ready or patch-changing head. A merge needs a clean verdict from the round whose patch matches the merge-ready head.
5. **On a clean verdict, the owner merges and takes the next item.**
   1. Merge prep starts only after the round's lanes have started, and ends with a rebase onto current trunk right before the merge. The owner reports the new head SHA.
   2. CI must pass on that head. The patch-id rule in `playbooks/shipping.md` decides whether the round's verdict still holds; a new head voids it unless the patch-id is unchanged. The same applies if trunk moves again before the merge.
   3. The owner squash-merges its PR with `gh pr merge --squash` and picks up its next self-contained item. The user's full-autonomy grant together with your clean verdict is the merge authorization; babysitting alone never is.
   4. Items the user reserved stop at merge-ready and wait for the user to merge.
6. **Run the root layer.** Give countersigns per Countersigns. Run the audit tick per Wake mechanics and the audit tick, re-reading this file and the armed objective each time, and probe owners and every owner's `children.tsv` per Liveness.
7. **Stand down immediately when the user says stop.** Every owner gets a zero-writes order and holds its brief until the user releases it.

**Reply:** the queue with each PR's owner, state, and head SHA; each verdict and the round that produced it; what merged and what each owner took next; countersigns given and why; open user gates; and where the collected decision logs are.
