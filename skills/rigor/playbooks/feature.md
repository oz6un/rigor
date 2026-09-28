# Feature

You own the design: plan, review, and verify. Delegate the implementation and stay in the lead.

1. Run `how` over the affected subsystem.
2. Run `architect` to explore designs in parallel.
3. Write the throughput checkpoint as four todo items. If one doesn't apply (a single file, nothing to fan out), keep the item and mark it `n/a: <reason>` instead of dropping it.
   - **Blocking first steps:** what has to finish before any fan-out.
   - **Independent workstreams:** disjoint files, services, or layers that can run in parallel. Work that writes the same place runs in sequence.
   - **Shared mutable state:** by default, split the target so actors don't share it (the `separate-before-serializing-shared-state` principle). Serialize only for real invariants.
   - **Smallest safe decomposition:** if one worker is best, say why.
4. Delegate the code-writing to a `rigor-agent` subagent. Delegate anything above the small-task threshold in `SKILL.md`, even when doing it yourself would be quicker: the point is separating the author from the reviewer, not saving lines. If you are yourself a subagent that can't spawn others, write the diff directly and keep the same review separation. Don't reply "standing by" while waiting on a nested agent.
   Give the delegate a specific scope: file paths, success criteria, and the data shape with its organizing structure chosen before any logic is written (the `model-the-domain` principle: a state machine instead of scattered booleans, a table or registry instead of branching, a typed model instead of repeated shape assumptions).
   When the implementation has several valid shapes (error handling, abstraction layer, test structure), delegate through the `arena` skill instead, so parallel attempts surface the alternatives and cross-judging guards the pick.
   Tell the delegate to: follow "Comments in code" in `SKILL.md`; make surgical edits; re-check files derived from an upstream source against that source; carry improvements to a shared primitive over to every consumer and verify each; and commit often.
5. Verify on the matching surface: `control-ui` or `control-cli` for UI and CLI changes, otherwise the real entry point callers use (the API, library call, or job). An inconclusive result, or a pass on a different surface, is not a pass; flag it.
6. Rebase into small, ordered commits, and stack follow-ups as separate commits or PRs. Build, verify, and commit each small unit before the next (the `sequence-verifiable-units` principle).
7. If the design is contested, run `interrogate` before shipping.
8. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`).

Tightly coupled work (one feature, one migration) goes to a single owner with the throughput checkpoint in its prompt; that owner fans out internally after the blocking steps. Fan out from the top level only for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at each phase boundary. To change an owner's direction substantially, start a fresh owner rather than stacking interruptions on the old one.

**Reply:** what you built, what you chose and why, the throughput checkpoint, and open decisions. Use tables for design alternatives.
