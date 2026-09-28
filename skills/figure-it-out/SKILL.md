---
name: figure-it-out
description: Design an auditable workflow for a task no narrower playbook fits, such as a large migration, an ambitious multi-part change, or work the user will review after stepping away. Scales rigor to the stakes, runs a hypothesis-and-measure loop, and keeps a decision log with show-me-your-work. Use for /figure-it-out or when no rigor playbook applies.
disable-model-invocation: true
---

# Figure it out

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` and follow it.

When a task matches no playbook, design one. The first deliverable, before any code, is the workflow: a sequence of phases sized to the task's risk, run as a series of experiments, that leaves a decision log the user can audit after stepping away.

Start a todo list whose first item is reading the `principles` skill's index. Then add the phases below.

## Phase A: Frame

Ground yourself in the code first, then commit to a plan. Don't start the run until you can state:

- The definition of done as a falsifiable check (the `prove-it-works` principle).
- The scope in numbers: rough count of units and effort, plus the blockers grounding turned up.
- The rigor level, leaning high. One-way decisions and a large blast radius get more gates; reversible, low-stakes steps get fewer. Rigor means more gates and artifacts, not more effort in the abstract.

Present the framing and tradeoffs before starting a long run. Reversible work can proceed without waiting (the `never-block-on-the-human` principle), but a run that will take hours gets one checkpoint with the user first.

## Phase B: Design the workflow

Split the work into small units that can each land on their own. Put the riskiest unknown first, and build scaffolding and verification before features (the `foundational-thinking` principle).

- Build the verification harness before the work and capture a baseline from the unchanged code, so every check reads as old value versus new value.
- For one-way design decisions, run the `architect` skill (which runs `arena`). Skip it for mechanical work whose shape is already clear; a second arena over a settled design is wasted effort (the `laziness-protocol` principle).
- Decide what runs in parallel. Parallelize only along real seams, give each worker its own worktree or branch (the `separate-before-serializing-shared-state` principle), and keep the fan-out modest.
- Write the phase list down. That list is what the user reviews.

Then execute it. Add the designed steps to the todo list as concrete items between Phase C and Phase D. Run each one with the Phase C discipline, and log a row as each step lands (Phase D) rather than writing the log at the end.

## Phase C: Run the loop

Treat each unit as an experiment: state the hypothesis, make the smallest change, measure against the done check on the real artifact, and keep the change if it moved things forward or revert it if not. Verify each unit before starting the next instead of batching checks at the end (the `sequence-verifiable-units` principle).

- Verify by inspecting the artifact, not a worker's self-report. When something passes too easily, suspect the way you're observing it before trusting the system.
- Pair delegated work with a reviewer; for high-stakes units, get that review from the other CLI through `<this skill's dir>/../rigor/scripts/second-opinion.sh`. If a worker games the check, reset its work and tighten the brief. If the check itself is wrong, fix it in its own change instead of working around it.
- Report each verdict as VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is not a pass, and negative results stay in the report.

## Phase D: Keep the decision log

Log the run with the `show-me-your-work` skill. Work that needs this skill is usually large enough that the log should be committed so the reviewer can read it in the PR. The log plus the diff is what lets the user trust the result when they come back.

## Phase E: Verify and hand back

Check the finished work against the Phase A definition of done on the real product, not only the harness. Turn any correction you made more than once into a check, lint rule, or script (the `encode-lessons-in-structure` principle).

**Reply:** the workflow you designed, the rigor level and why, the path to the decision log, what is verified against the definition of done, and what is still open.
