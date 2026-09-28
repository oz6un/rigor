# Hillclimb

You own the metric and the integrity of the experiment. Delegate the attempts; supervise and review them. Use this for sustained, iterative improvement of one measurable quantity toward a target. A one-off fix belongs in Bug fix or Perf issue.

The rule for every iteration: one change, one measurement, then keep or revert. Don't stack untested changes, and don't claim a win from reading code (the `prove-it-works` principle).

1. Understand the workload and architecture before choosing the metric. Run `how` over the target, list the workload dimensions that can move the result (data size, history, state, concurrency), and pick a case that reproduces the user's complaint. If no case reproduces it, fix the repro before hillclimbing. Then fix one metric, which direction counts as better, and a checkable stop condition that pairs a target with a minimum number of attempts, so a lucky early win can't end the run (for example, "at least 50% better than baseline and at least 10 iterations"). Use the user's numbers if they gave any; otherwise agree on them.
2. Build the measurement harness, show that it's sensitive, then freeze it (the `build-the-lever` principle). Run contrasting realistic workloads and confirm the target case reproduces the symptom while easier cases come out as expected. If the harness can't tell them apart, revise the workload or the metric. Once frozen, one repeatable command should print the metric, sampled enough to clear noise (the median of N runs, not a single run). Before any change, record the baseline metric and a passing run of the regression gate (the tests that must keep passing).
3. Start the decision log with the `show-me-your-work` skill: a `decision.tsv` with one row per attempt and columns id, hypothesis, change, before, after, delta, tests, verdict (kept or reverted), note. Read it before each attempt. Keep it out of the repo (gitignored).
4. Ground each hypothesis in the architecture from step 1, so it names a specific mechanism ("defer X off the boot path because it blocks first paint") rather than "try memoizing something".
5. Loop, one hypothesis per iteration:
   - Hand the change to a `rigor-agent` subagent with a tight scope, and review its diff rather than writing it yourself (the `guard-the-context-window` principle). When several independent hypotheses are open, run them in parallel subagents, each in its own worktree (the `separate-before-serializing-shared-state` principle).
   - Measure before and after with the frozen harness, and run the regression gate.
   - Keep the change only when the metric moves by more than the noise and the gate stays green. Otherwise revert it completely; a tweak that "might help" is not kept.
   - Make one commit per accepted change, staging only the files you changed (`git add <files>`, not `git add -A`). Log the row whether the change was kept or reverted.
   Finish each iteration's check before starting the next (the `sequence-verifiable-units` principle). If the run is unattended, take only the wake-up mechanism from the Autonomous run playbook (`playbooks/autonomous-run.md`), not its stop rule.
6. Push past the first plateau. After several rejects in a row, switch to a different category of idea, combine near-misses, re-read the source, or try something more radical before concluding there's nothing left. Correctness and simplicity outrank the number: revert a win that breaks behavior, and keep a simplification that holds the number (the `laziness-protocol` principle).
7. Stop when the stop condition is met, or when the remaining ideas are marginal and not worth their cost. Don't relax the condition to meet it, and don't stop while cheap untried hypotheses remain. If you're stuck, say so instead of spinning.
8. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`) with the accepted commits stacked in the order they were made.

**Reply:** the metric and target; baseline to final value with the percent change; iterations run (kept vs. reverted); each accepted change on one line; the `decision.tsv` path; and the most promising idea you'd try next.
