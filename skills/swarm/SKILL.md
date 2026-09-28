---
name: swarm
description: Fan out N parallel workers (host subagents plus at least one from the other coding CLI) over separate slices or identical briefs, wait for all of them, and return one consolidated report. Use for /swarm, "swarm this", or parallel coverage checks, audits, races, and exploration.
---

# Swarm

Run N parallel workers. They can each cover a separate slice, race on the same brief, or a mix of both. You wait for all of them, aggregate, and return one report.

Start a todo list with one item per phase before launching anything: Frame, Fan out, Aggregate, Report.

## Phase A: Frame

1. State the done condition and the artifact or report the swarm returns.
2. Choose the shape: partition the work into slices, race N workers on identical briefs, or mix both. For a race or mix, declare the selection rule before spawning: `first pass`, `rank all`, or `best-of`.
3. Set N from the user's request or derive it from the shape. N is the total number of workers.
4. Assign workers:
   - Most workers are host subagents. Use a fast model for mechanical checks and your strongest model for judgment-heavy slices (Claude Code: the Agent tool's `model`; Codex: `model` on the spawn).
   - Run at least one worker through the other CLI with `../rigor/scripts/second-opinion.sh`. In a race, make it one arm. In a coverage swarm, give it one slice, or have it independently re-check a slice a host worker also covers, so the report includes a cross-model check.
   - For a model race, name each arm's model up front.
5. Give every worker that writes its own worktree, set up as in the `arena` skill's [Isolating candidates](../arena/SKILL.md#isolating-candidates), with branch `swarm/<slug>/<n>` at `../swarm-<slug>-<n>`.
6. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method: the sample count, what one sample is, and the run order. The worker records both in its result.

## Phase B: Fan out

Launch every worker at once and let them run in parallel (Claude Code: one message of Agent calls with `run_in_background: true`, plus the script run in the background; Codex: spawn them together and background the script with its output redirected to a file).

Every brief stands alone. It includes the goal, the scope, the exact slice or race arm, how to verify, and what to report. Results start with `PASS`, `ISSUES`, or `BLOCKED` and include evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, continue with N-1 and note it.

## Phase C: Aggregate

Read every final result. If a result doesn't record the SHAs and method its brief asked for, discard it and rerun that worker once. After a second miss, record a gap. A gap is not a pass.

For coverage, every required slice needs a result. For a race, apply the selection rule you declared. Where a host worker and the other-CLI worker covered the same slice, note whether they agreed. Don't paste raw worker output.

Keep a compact results table, one-line issues with evidence, and an explicit list of gaps and dropouts.

## Phase D: Report

Return one report in the reply: the results table, the issue one-liners, gaps and dropouts, the selection rule if it was a race, and which workers ran on the other CLI (or that the seat fell back to a host subagent). Remove any worktrees you created once their results are captured.
