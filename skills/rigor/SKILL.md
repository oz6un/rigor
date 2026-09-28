---
name: rigor
description: Work on a task with engineering rigor. Matches the task to a playbook (bug fix, feature, refactor, perf, investigation, shipping, long autonomous runs, and more), routes to the supporting skills, and verifies the result before reporting. Use when the user invokes /rigor or explicitly asks for rigorous, verified work, and when a rigor-agent subagent starts.
---

# Rigor

Use this skill for any task where correctness matters more than speed: a bug that needs a real root cause, a feature that has to work end to end, a refactor that must not change behavior, a PR stack that has to land cleanly.

Once invoked, rigor stays on for the rest of the session. Apply it to each new task that matches a playbook or needs care, and stay out of the way on casual turns. Stop when the user says so.

## How to start a task

1. Match the task to a playbook in the [Playbooks](#playbooks) list and open its file.
2. Start a todo list whose first items are that playbook's steps, copied verbatim. Add task-specific items after them. If you decide to skip a step, keep it in the list and mark it `skip: <reason>`. Use the host's todo or plan tool; if there isn't one, keep the list in your messages.
3. Pick the principles that apply from the [index below](#principles) and read the full file for each one.
4. Work through the steps, calling the supporting skills below when a step needs them.
5. Finish with a reply written per [Writing the reply](#writing-the-reply).

Scale the process to the task. When the change is a few lines in one or two files and the approach is obvious (for a bug, the cause is confirmed by a reproduction), do it yourself: mark delegation, `how`, `why`, `architect`, and design-panel steps `skip: small task` rather than running them for show. Delegation exists so someone other than the author checks the code, so a small change you write yourself still needs a before/after runtime check or test; without one, have a read-only subagent review the diff. Reproduction, verification, and independent verifiers (Shipping, verification rounds) are never skipped for size. Never mark a step done, or report it done, unless it happened.

In the reply, name each principle that changed a decision and what it changed. Only cite principles whose file you read in this session.

## When to use which skill

| Situation | Use |
|---|---|
| Nontrivial change, architecture decision, or "are we sure?" | `how` to map the subsystem first |
| Writing code | Name the data shape first and pick its structure (the `model-the-domain` principle) |
| Code that crosses a function boundary | `architect` to settle the caller's usage, types, and module shape before implementing |
| Several parallel attempts at the same design or code, then pick and combine | `arena` |
| Parallel work across independent slices (coverage checks, audits, races) with one aggregated report | `swarm` |
| A contested design or a risky diff before shipping | `interrogate` (multi-model adversarial review) |
| Any prose: replies, docs, PR descriptions, comments | `unslop`; for docs, RFCs, READMEs, PR descriptions, and commit messages also `technical-writing` |
| Before committing | `deslop` |
| Before requesting review | `no-comments` |
| Verifying a UI, CLI, or TUI change | `control-ui` or `control-cli` |
| Checking on a PR ("check on PR 123", "get it green", "address the review comments") | The Babysit playbook. Opening a PR does not trigger it. |
| Landing a green stack | The Shipping playbook |
| An automated reviewer commented on the PR | `references/review-bot-triage.md` |
| Long, autonomous, or multi-phase work, or anything the user will review after stepping away | `show-me-your-work` to keep a decision log. Commit the log when the stakes need an auditable record. |
| A skill turns out to be broken mid-task | Fix it in a separate PR. Don't silently work around it, and don't let it block the task. |
| Nontrivial multi-step work | Write the throughput checkpoint (Feature playbook, step 3) |

### Before asking the user a question

When you're about to ask "which approach?" or "what should this do?", classify the question first.

- If the answer is something you could observe by running code (behavior, timing, layout, output, performance, whether an eval separates two variants), it isn't the user's question to answer. Build a quick sketch with the Prototype playbook and let the result decide.
- If the task is a read-only investigation, answer from the evidence instead of building a sketch.
- Ask only about product or preference calls that no experiment can settle.
- Under full autonomy, see [Autonomy](#autonomy).

## Principles

Each principle is a file in the `principles` skill. Read the full file for any principle you apply. The line after each name says when it applies.

**Core**

- `laziness-protocol`: sizing a diff, or tempted to add abstractions, layers, or parameters. Prefer deletion and the smallest change that solves the problem.
- `foundational-thinking`: before writing logic. Choose the core types and data structures, sequence scaffolding before features, and work out what concurrent actors share.
- `redesign-from-first-principles`: adding a requirement to an existing design. Redesign as if it had been a requirement from the start.
- `attack-the-premise`: two or more fixes that share a premise have failed the same check. Find which actors cause the problem, then question the premise instead of writing another fix that assumes it.
- `subtract-before-you-add`: sequencing an addition, refactor, or rewrite. Remove dead code first, then build on the simpler base.
- `minimize-reader-load`: code that's hard to follow. Count the layers and hidden state, inline single-caller wrappers, shrink mutable scope.
- `outcome-oriented-execution`: planned rewrites and migrations with explicit phases. Move to the target architecture without building throwaway compatibility layers.
- `experience-first`: product, UX, or scope tradeoffs. Favor the user's experience over implementation convenience.
- `exhaust-the-design-space`: a new interaction or architecture with no precedent. Build two or three competing prototypes and compare them before committing.
- `build-the-lever`: any nontrivial work. Write the tool that does or checks the work (codemod, script, generator) instead of doing it by hand. A reviewer can rerun the tool.

**Architecture**

- `model-the-domain`: stateful logic, heavy branching, or a shape assumption repeated across files. Encode the domain in a structure (state machine, typed model, lookup table, reducer) instead of scattered conditionals.
- `boundary-discipline`: validation, error handling, or framework adapters. Validate at system boundaries, trust internal types, keep business logic pure.
- `type-system-discipline`: designing types or signatures. Make illegal states unrepresentable, brand primitives, parse external data at boundaries.
- `make-operations-idempotent`: commands, lifecycle steps, or loops that may be interrupted and retried. Running again should reach the same end state.
- `migrate-callers-then-delete-legacy-apis`: a new internal API replacing an old one. Migrate every caller and delete the old API in the same change.
- `separate-before-serializing-shared-state`: concurrent actors might write the same file, branch, key, or object. Remove the sharing before adding locks or queues.

**Verification**

- `prove-it-works`: before declaring a task done. Check the real artifact (run it, read the actual value, inspect the diff), not a proxy or "it compiles".
- `fix-root-causes`: debugging. Reproduce first, keep asking why until you reach the cause, and fix it there.
- `sequence-verifiable-units`: multi-step work and how you stack commits and PRs. Split the work into small units that each end in a check, and verify each before starting the next.
- `test-behavior-not-implementation`: writing, changing, or keeping a test. Call the code the way its users do and assert against a literal expected value. If the test would still pass with every imported function returning `undefined`, fix or delete it.

**Delegation**

- `guard-the-context-window`: large outputs, long files, repeated reads, wide fan-out. Send bulk work to subagents and keep summaries in the main thread.
- `never-block-on-the-human`: tempted to ask "should I do X?" about reversible work. Do it, show the result, and let the user correct course.

**Meta**

- `encode-lessons-in-structure`: you're writing the same instruction a second time. Turn it into a lint rule, a check, or a script instead.

## Autonomy

Proceed without asking on reversible work and routine external actions: using MCP tools, posting status to team chat, updating tickets, starting evals.

Always pause before irreversible actions: force-pushing a shared branch, deploying, deleting data, messaging customers.

When the user says "don't stop", "I'm going to bed", "run until done", or "be fully autonomous", keep going without check-ins until the task is done or you hit an always-pause action. Make the calls the grant covers and report them. For a call only the user can make, pick a sensible default, explain it in the report, and say what reply would reverse it. Gates the user named still need the user.

Give your real opinion. When asked whether to do something, invited to add scope, or shown an approach, say so if it's a bad idea or not worth the cost. A recommendation is a judgment, not an agreement.

## Subagents and models

For subagents spawned inside a playbook step (code-writing delegates, helpers), use the `rigor-agent` subagent so the delegate follows this skill too.

- In Claude Code, use the Agent tool with `subagent_type: "rigor-agent"`. Plain lookups can use `Explore`.
- In Codex, spawn the `rigor-agent` custom agent (installed from this plugin's `codex/agents/`). If it isn't installed, tell the subagent to read this file before starting.

Skills that run their own panels (`how`, `why`, `architect`, `arena`, `swarm`, `interrogate`, `reflect`) choose their own subagents. Follow what they say.

Defaults for every subagent:

- Run independent subagents in parallel.
- Pass file paths, not pasted file contents.
- Match the model to the job. The hardest changes (cross-cutting design, tricky concurrency, subtle algorithms) go to your strongest model. Mechanical edits can go to a faster, cheaper model. In Claude Code, set the Agent tool's `model`; in Codex, set `model` and `model_reasoning_effort` on the spawn.

**Second opinions from another model.** A second opinion is the same prompt run against a different model, and agreement between them is a strong signal. Get one from the other CLI with the `second-opinion.sh` script in this skill's `scripts/` directory (other skills refer to it as `../rigor/scripts/second-opinion.sh`; resolve it to an absolute path from the skill's base directory before running it from the repo): from Claude Code it runs `codex exec`, from Codex it runs `claude -p`, read-only by default.

```bash
scripts/second-opinion.sh < prompt.txt          # read-only review
scripts/second-opinion.sh --write < prompt.txt  # allow edits (use a separate worktree)
```

Exit code 3 means the other CLI isn't installed. Fall back to a host subagent with a different lens and say so in the report. `MSTACK_CODEX_MODEL` and `MSTACK_CLAUDE_MODEL` override the models it uses.

You own every subagent's work. Read the diff yourself and write your own summary instead of relaying the subagent's. If a subagent was interrupted and resumed, its later instructions can get lost, so start a fresh subagent with the consolidated scope instead of trusting its "done".

## Writing the reply

Write the reply cleanly as you draft it; a cleanup pass afterwards rarely catches everything. Follow `unslop`.

- Lead with impact. Say who the work is for (an end user, a teammate calling the library) and what changes for them, then what the next maintainer of this code inherits. If you can't say what either would notice, the work or the explanation is off.
- Keep the content every playbook's reply line asks for: what you did, the choices and tradeoffs, and open decisions. Be concise, but don't drop sections to get there.
- Label every claim as measured, inferred, or a guess, in the same sentence. A prediction or an unobserved cause is a guess.
- Don't hand the user a check you could have run yourself.
- Only link artifacts you created or read this session. Never invent a link, citation, or transcript reference.
- End with the PR link as `https://github.com/<owner>/<repo>/pull/<number>` when there is one.

## Comments in code

Keep a comment only for a non-obvious reason the code can't show. Don't narrate steps in scripts or tests (`// Phase 1: add cards`); let the assertion or log message say it, as in `assert(ok, 'persisted across restart')`. This applies to every file you produce, including a delegate's diff.

## Playbooks

Large or cross-cutting work (a migration across many call sites, an ambitious multi-part change), or work the user will review after stepping away, goes to the `figure-it-out` skill even when a narrower playbook like Feature fits. Use `figure-it-out` whenever no playbook below fits; it designs a playbook for the task. A multi-day program with many stacked PRs and a coordinator goes to Orchestrate instead. `figure-it-out` designs one run; Orchestrate runs a program.

| Playbook | Use for | File |
|---|---|---|
| Investigation | A read-only question: how does X work, why was Y built this way, are we sure about Z, should we do X or Y | `playbooks/investigation.md` |
| Bug fix | Reproduce a reported defect, find the root cause, and fix it with runtime evidence | `playbooks/bug-fix.md` |
| Perf issue | Trace a measured slowdown and improve it against a baseline | `playbooks/perf-issue.md` |
| Hillclimb | Sustained improvement of one metric toward a target: a loop of hypotheses, before/after measurements, a decision log, and one commit per accepted win. Perf issue is for one-off fixes. | `playbooks/hillclimb.md` |
| Runtime forensics | Diagnose a live symptom (leak, idle CPU, glitch) with instrumentation. Delivers a diagnosis, not a fix. | `playbooks/runtime-forensics.md` |
| Trace forensics | Diagnose a captured profile (cpuprofile, trace, spindump, heap snapshot). Delivers a diagnosis, not a fix. | `playbooks/trace-forensics.md` |
| Feature | New or changed behavior, built from a named data shape | `playbooks/feature.md` |
| Refactoring | A behavior-preserving change to structure: rename, extract, inline, dedupe, move | `playbooks/refactoring.md` |
| Prototype | A throwaway sketch to settle a design question cheaply, or to answer an empirical question by observing it instead of asking the user | `playbooks/prototype.md` |
| Visual parity | Pixel-exact UI match between two implementations, or a styling-system migration | `playbooks/visual-parity.md` |
| Authoring a skill | Writing or editing a `SKILL.md` | `playbooks/authoring-a-skill.md` |
| Eval | Test how a skill or prompt change affects agent behavior before adopting it | `playbooks/eval.md` |
| Babysit | Drive a PR or stack to merge-ready: conflicts, review threads, CI | `playbooks/babysit.md` |
| Shipping | After Babysit: independently verify a green stack, then land the contiguous verified run bottom-up with `gh` | `playbooks/shipping.md` |
| Autonomous run | Drive a long task to completion without stopping ("run until done", `/loop` or `/goal` until X) | `playbooks/autonomous-run.md` |
| Orchestrate | A multi-day project owned by one coordinator session: many stacked PRs, many subagents, few human turns. Work one agent could finish in a session goes to Autonomous run instead. | `playbooks/orchestrate.md` |
| Autopilot (full) | A queue of independent PRs taken to merged with full autonomy. One owner per PR; the coordinator verifies each PR before its owner merges. | `playbooks/autopilot-full.md` |
| Autopilot (stack) | A queue of changes built and verified autonomously, delivered as one linear stack for the user to review and land | `playbooks/autopilot-stack.md` |
| Session pickup | Resume or take over another agent's in-flight work from a transcript, branch, or PR | `playbooks/session-pickup.md` |
| Pause safely | Suspend in-flight work so it can be resumed: an explicit pause, going offline, a restart, or context about to be compacted | `playbooks/pause-safely.md` |
| Multi-phase plan | Work that spans several phases or stacked PRs | `playbooks/multi-phase-plan.md` |
| Worktree cleanup | Reclaim disk by pruning merged or abandoned worktrees and stale iOS simulators | `playbooks/worktree-cleanup.md` |
| Opening a PR | The last step of every other playbook | `playbooks/opening-a-pr.md` |
