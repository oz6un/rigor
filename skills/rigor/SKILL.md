---
name: rigor
description: Work on a task with engineering rigor. Matches the task to a playbook (bug fix, feature, refactor, perf, investigation, shipping, long autonomous runs, and more), routes to the supporting skills, and backs every "done" with evidence. Invoked by the user as /rigor (Codex: $rigor); stays on for the rest of the session.
disable-model-invocation: true
---

# Rigor

Rigor stays on for the rest of the session once invoked; a hook reminds you each turn and after compaction. Apply it to each new task that matches a playbook, stay out of the way on casual turns, and stop when the user starts a message with "rigor off".

## Start a task

1. Pick the playbook below and read its file (paths are relative to this skill's directory).
2. Put its steps in a todo list, verbatim. A step you skip stays in the list as `skip: <reason>`. Never mark or report a step done unless it happened.
3. Work the steps. When a step names a supporting skill or a principle, read that file then.

Scale to the task. For a change of a few lines with an obvious approach, do it yourself and skip the design, delegation, and review steps. Reproducing a bug and checking the result at runtime still apply at every size.

| Playbook | Use for |
|---|---|
| `playbooks/investigation.md` | Read-only questions: how does X work, why is Y this way, should we do X or Y |
| `playbooks/bug-fix.md` | Reproduce a defect, find the root cause, fix it |
| `playbooks/feature.md` | New or changed behavior |
| `playbooks/refactoring.md` | Structure changes that preserve behavior |
| `playbooks/perf-issue.md` | A measured slowdown, fixed against a baseline |
| `playbooks/hillclimb.md` | Push one metric toward a target, one measured commit at a time |
| `playbooks/runtime-forensics.md` | Diagnose a live symptom (leak, idle CPU, glitch); diagnosis only |
| `playbooks/trace-forensics.md` | Diagnose a captured profile or trace; diagnosis only |
| `playbooks/prototype.md` | A throwaway sketch to settle a design or empirical question |
| `playbooks/visual-parity.md` | Pixel-exact UI match between two implementations |
| `playbooks/authoring-a-skill.md` | Writing or editing a `SKILL.md` |
| `playbooks/eval.md` | Measure how a skill or prompt change affects agent behavior |
| `playbooks/test-audit.md` | Prune a test suite: redundant, low-value, or implementation-coupled tests |
| `playbooks/babysit.md` | Get a PR or stack merge-ready ("check on PR 123", "get it green") |
| `playbooks/shipping.md` | Verify each PR in a green stack independently, then land it |
| `playbooks/autonomous-run.md` | A long task driven to completion without check-ins |
| `playbooks/orchestrate.md` | A multi-day program with many PRs and one coordinator |
| `playbooks/autopilot-full.md`, `autopilot-stack.md` | A queue of changes taken to merged, or to a reviewed stack |
| `playbooks/multi-phase-plan.md` | Work spanning several phases or stacked PRs |
| `playbooks/session-pickup.md`, `pause-safely.md` | Resume another session's work; suspend work cleanly |
| `playbooks/worktree-cleanup.md` | Reclaim disk from merged worktrees and old simulators |
| `playbooks/opening-a-pr.md` | The last step of every playbook that changes code |

No playbook fits, or the work is large and cross-cutting: use the `figure-it-out` skill.

## Supporting skills

They don't appear in your skill list; to use one, read `<rigor skill dir>/../<name>/SKILL.md` and follow it, where `<rigor skill dir>` is this skill's directory with symlinks resolved (the reminder hook gives the resolved path), so a same-named skill of the user's isn't read by mistake. The playbooks say when: `how`, `why`, `architect`, `arena`, `swarm`, `interrogate`, `tdd`, `deslop`, `no-comments`, `unslop`, `technical-writing`, `control-ui`, `control-cli`, `show-me-your-work`, `figure-it-out`, and `principles` (one file per principle; read one when a step or the user names it).

## Evidence

These hold at every size because they are what makes the result trustworthy, and a capable model skips them under pressure.

- Back each claim in the final report with the command and output from this session that shows it, or label it inferred or a guess. Don't hand the user a check you could have run.
- Never weaken a test to make it pass: don't delete or loosen assertions, skip tests, or special-case the code under test. Update a test's expected value only where the user's request changes the behavior it checks, and name each such test in the report. Deleting a passing test is fine when it makes the suite simpler without losing protection: the code it tests was deleted, or it's redundant or low-value by `references/test-audit.md` and you record what it detects and which test still catches that. Name each deleted test. Deleting a failing test is weakening it. If a test conflicts with the request in a way the request doesn't clearly settle, report it as blocked instead of forcing it green; this holds under `/goal` and "don't stop" too (park it and continue other work).
- Only link artifacts you created or read this session.

## The user's rules

- Proceed without asking on reversible work. Always pause before irreversible actions: force-pushing a shared branch, deploying, deleting data, messaging customers or other outside parties.
- Ask the user only about product or preference calls. If a question can be settled by running something, run it (the Prototype playbook).
- Under "don't stop", "I'm going to bed", or an active `/goal`: keep going, make the calls the grant covers, and list them in the report with what reply would reverse each. Pauses and gates the user named still apply.
- Give your real opinion. Say so when something isn't worth doing.

## Subagents

Delegate only large, independent tracks of work, such as a wide investigation or separate slices in parallel. Don't delegate what you can finish in a few tool calls, keep one writer per file or branch, and don't spawn a subagent just to re-check a small change. The independent verifiers a playbook requires (Shipping, verification rounds, a decision-log review) still run. Use the `rigor-agent` subagent for delegated work (Claude Code: `subagent_type: "rigor-agent"`; Codex: spawn the `rigor-agent` custom agent). You own its output: read its diff yourself.

For a second opinion from another model family, pipe a prompt to `<rigor skill dir>/scripts/second-opinion.sh` (Claude Code calls `codex exec`, Codex calls `claude -p`; `--help` for options). Treat another reviewer's findings as hypotheses: act on one when you can reproduce it or it comes with a failing test.

## Reply

Lead with what changed for the user, then the choices and anything left open. Write it per the `unslop` skill. End with the PR link when there is one.
