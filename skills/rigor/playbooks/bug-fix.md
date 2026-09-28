# Bug fix

You own the task: plan, review, and verify. Delegate the investigation and the fix to subagents and stay in the lead, except for small tasks as defined in `SKILL.md`.

Every line you ship should trace to runtime evidence. A defensive change that "might help" is a hypothesis, not a fix, and doesn't ship. When evidence refutes a hypothesis, revert whatever it motivated. Ship the smallest change the evidence justifies.

1. Reproduce the bug yourself on the surface where it was reported, using `control-ui` or `control-cli`. Do this even when a debugging protocol suggests asking the user to reproduce. Ask the user only after driving the surface as far as it goes, and only with a specific reason it can't reach the target. If the bug won't reproduce directly, synthesize the trigger, tighten the conditions, or add instrumentation until it fires.
2. Binary-search the cause. List candidate hypotheses (seed them with `how` over the affected subsystem and `why` for regression history), then eliminate them until one survives. On each pass, pick the test that rules out the most remaining possibilities and get runtime evidence for it. When program state is unclear, add logging or instrumentation and read it while the code runs instead of guessing. For a long or stubborn hunt, drive it with `/loop` (Claude Code) or `/goal` (Codex). Confirm the surviving mechanism with runtime evidence before planning the fix.
3. Plan the fix. If it crosses a function boundary, run `architect` first. Delegate the implementation to a `rigor-agent` subagent with a specific scope, choosing the model per "Subagents and models" in `SKILL.md`.
4. Verify on the same surface: the original repro now passes. An inconclusive result, or a pass on a different surface, is not a pass; flag it. Unit tests show how a branch behaves, not that the bug is gone.
5. Order the commits so the failing repro lands before the fix (the `sequence-verifiable-units` principle). When the bug has a cheap local test path, follow the `tdd` skill's failing-test-first cadence. Skip the test when it would be expensive, integration-heavy, or unclear, and say why.
6. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`).

**Reply:** what was broken, the root cause, the fix, and how you verified it. Paste the failing and then passing repro output verbatim.
