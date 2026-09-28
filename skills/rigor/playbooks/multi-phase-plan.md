# Multi-phase plan

You own the plan, not the code. The plan is a checklist that an owner works through box by box and that the user can audit from the evidence. The plan is the deliverable; don't implement anything.

1. If the change is one or two files with an obvious approach, skip the plan. Say so and stop.
2. Settle open questions with prototypes before writing. Run `playbooks/prototype.md` for each, and keep the branch, SHA, and screenshots for Appendix A. Ask the user only about product or preference calls that no experiment can settle, and offer options (the `never-block-on-the-human` principle).
3. Explore with `rigor-agent` subagents, per the rigor skill's "Subagents" section (the `guard-the-context-window` principle). Each returns file pointers, conventions, test commands, and entry points, not pasted file contents.
4. Copy the skeleton below into the plan file and fill every placeholder. Unless the user names a path, write it to `~/.rigor/plans/<program-slug>.md`. Keep every heading and sub-block in the order shown, with one section per PR. One PR is one change with its own evidence (the `sequence-verifiable-units` principle). Name the execution playbook in **How to read this**: choose between `playbooks/autopilot-full.md` and `playbooks/autopilot-stack.md` using the rule at the top of `playbooks/autopilot-stack.md`, or use `playbooks/orchestrate.md` for a standing program.
5. Write it following `technical-writing`, then run `unslop` over it. The body is a how-to; the appendices hold explanation and reference. Each heading states the task or the finding. The check script rejects curly quotes.
6. Run `node <rigor skill dir>/scripts/check-plan.mjs <plan.md>` and fix every line it prints (the `encode-lessons-in-structure` principle).
7. Hand back the plan path and the script's output, then stop. Execution starts on the user's explicit go, under the playbook the plan names.

## Rules the skeleton encodes

**Verification.** Every verification block opens with the same sentence: "Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked." (the `prove-it-works` principle).

- **Live.** Required. Ten lanes at the PR head drive the real surface through its control skill, per the `swarm` skill, on a fast model you name in the block. Each lane is one box with a concrete scenario, the screenshot it saves, and its pass condition. Lane 1 is the regression lane against trunk: it runs the same key scenario on trunk and head. If trunk doesn't have the feature, the lane records that and checks the behavior the diff adds plus the end state the user waits for, instead of inventing a trunk result.
- **Perf.** Two-sided: trunk and head must both produce the named metric. If trunk lacks the feature, also isolate the work the diff adds and set an absolute budget for it and for the end-to-end state the user waits for. Don't claim a ratio between different scenarios. The block names the metric, the interleaved probe, the trunk baseline (measured first), and the rule with the number that fails.
- **Review gate.** A PR that changes an interaction is review-gated: the user reviews it with screenshots and a video before merge. A PR that changes no interaction writes `**Review gate.** None. <PR id> is not review-gated.` with no boxes under it.

**Control skill.** Choose by surface: `control-ui` for browser, Electron, and web UIs; `control-cli` for CLIs and TUIs; the repo's own simulator-driving skill for native mobile. A PR that touches two surfaces gets lanes on both. A surface with no control skill is a risk in Appendix C, and its live block still says how each lane drives it.

**Re-reads.** The plan tells the program to re-read its rules at every tick. Files in the repo are read from trunk with `git show origin/main:<path>`; rigor's skill files are read from where they're installed (`~/.claude/skills/` or `~/.agents/skills/`).

## Skeleton

````markdown
# <Program> plan

<Under ten lines. What changes, for whom, the rule the program enforces, and the PR ids in order.>

## How to read this

One box is one unit of work. Every box names the evidence that checks it. A nested box is a sub-step of the box above it. Check a box only when its evidence exists, a file, a log line, a screenshot, a test run, or a SHA. The body is a how-to. The appendices explain and record.

The program runs the rigor skill's `playbooks/<execution playbook>.md`. <Who merges, and which PR ids are the user's items that stop at merge-ready.>

Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist

### Arm the program

- [ ] State the protocol and this plan to the user, then stop. Start execution only on the user's explicit go.
- [ ] On the user's go, arm the objective with this exact text, as `/goal` (both hosts). "<The plan path, the PR ids in order, the verification rule, who merges, and the done condition.>"
- [ ] Read these at program start and again at every tick.
  - [ ] The rigor skill's `playbooks/<execution playbook>.md` from the installed skills
  - [ ] The `swarm` skill from the installed skills
  - [ ] `<control skill>` from the installed skills
  - [ ] The rigor skill's `playbooks/opening-a-pr.md` from the installed skills
  - [ ] `git show origin/main:<each repo file the program depends on, such as CLAUDE.md or AGENTS.md>`
- [ ] Arm the 30-minute audit tick next to the `/goal`. In Claude Code, `/loop 30m` with the tick prompt below (plain text, so `/loop` runs it). In Codex, a bounded wait under the goal: a watcher with a 30-minute timeout, or `sleep 1800` when there's nothing to watch. Never leave the cadence to memory.
- [ ] Use this tick prompt, verbatim. "Re-read the execution playbook and the armed objective. Audit the operation against both and fix drift in this tick. Probe every active lane and judge progress by side effects only. Stand down a stuck lane and dispatch its replacement now. Then post a short status message to the user only when the audit found a tracked change that no earlier status message reported, such as a PR opened, a code-ready head, a round launched or closed, a verdict, a merge, a stuck agent and the action taken, a blocker added or cleared, or a decision only the user can make. Name every such change and nothing else. Do not repeat a table, the merged list, or an unchanged blocker. If the audit found none, end the turn with no reply text. Either way, log this tick's row in your decision trail. The row names the items reported, or none."
- [ ] On the user's hold or stand-down, send every owner a zero-writes order at once.

### Spawn owners

- [ ] Spawn one owner per PR with the full lifecycle the execution playbook names.
- [ ] Follow this dependency graph. Start dependent work only after its parent merges, or base it on the parent branch when the execution playbook stacks.
  - [ ] <PR id> and <PR id> are independent and first. Both branch from `main`.
  - [ ] <PR id> after <PR id>.
- [ ] Hold the file boundaries. <PR id or class> touches only `<glob>`.
- [ ] Hold the review gate. <PR ids> change an interaction. They wait for the user's review with screenshots and a video before merge.

### PR mechanics, for every PR

- [ ] Use `gh` for every PR operation. Never require `gt`.
- [ ] Open the PR ready, never draft, with `gh pr create --base <base-branch>`. A stack child targets its parent branch.
- [ ] Run the repo's lint and typecheck once before the PR-facing push. Push with hooks on.
- [ ] Run `deslop` before each commit and `no-comments` before review.
- [ ] Triage every automated reviewer comment per the rigor skill's `references/review-bot-triage.md`.
- [ ] Rebase onto current trunk before the code-ready report and babysit (Autopilot (stack) owners skip this; the root reshapes the stack). Keep that merge base in fix rounds. Rebase again only at merge prep, on a `git merge-tree` conflict with trunk, or on a CI failure that comes from a change on trunk.

### Verdict and merge, for every PR

- [ ] At the code-ready head SHA and at each later push that changes the patch, run the swarm per the `swarm` skill. One gates lane. The ten live lanes from the PR's **Verify, live** block. The perf lane from its **Verify, perf** block. Two or more audit lanes, each with its own focus, that read the diff and the receipts and distrust the PR body. The root audits the receipts in the merge-ready report before the verdict.
- [ ] Clean only when every lane is `PASS`. Findings go back to the owner, including a defect that a lane filed as a note. A new head gets a fresh swarm and a fresh verdict, except for results that stay valid under the patch-id rule in the rigor skill's `playbooks/shipping.md`.
- [ ] <The merge or append rule from the execution playbook, with the patch-id rule from `playbooks/shipping.md`.>

### Boot recipe, for every live lane

Each live lane runs in its own worktree at the PR head, or its own VM or container when the surface needs isolation. Drive it through `control-ui` or `control-cli`.

- [ ] `git fetch origin <head-branch> && git checkout <head SHA>`.
- [ ] <Start the backend and the surface. Wait for ready.>
- [ ] <Deliver input only through the control skill's commands. Name the read-only diagnostics.>
- [ ] Save every screenshot to `/tmp/swarm-<pr-id>/worker-<n>/<slug>.png` and return the paths with the report.

## <Task as a verb phrase> (<PR id>)

**Depends on.** <PR id, or None.>

**Files.**

- [ ] Edit `<path>`.
- [ ] Create `<path>`.
- [ ] Delete `<path>`.

**Build.**

- [ ] <One change. Name the symbol and the file.>

**You see.**

- [ ] <One observable result, with the exact log line or screen state.>

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] <Test file and the case it gains.> Run `<command>`.

**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Ten lanes on `<fast model>` at the PR head, per the boot recipe.

- [ ] Lane 1. Regression lane against trunk. Run <the same load-bearing scenario> at trunk and head. If trunk lacks the feature, record that and gate <the behavior the diff adds plus the end state the user waits for>. Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 2. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 3. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 4. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 5. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 6. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 7. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 8. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 9. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 10. <Scenario.> Save `<slug>.png`. Pass when <predicate>.

**Verify, perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Metric. <What is measured at both trunk and head. If trunk lacks the feature, also name the diff-added work and the end-to-end state the user waits for.>
- [ ] Probe. <The command or procedure, run at trunk and at the head, interleaved. Both sides must produce the metric.>
- [ ] Baseline. Record the trunk <value> first.
- [ ] Rule. <Head against trunk, with the number that fails. If the scenarios differ, add absolute budgets for the diff-added work and the user-visible end state instead of an invalid ratio.>

**Review gate.** The operator reviews before merge.

- [ ] Copy lane <n> screenshots into `<media path>/<pr-id>-review-<slug>.png`.
- [ ] Record a 30 to 60 second video of the change in a lane environment. Save it as `<media path>/<pr-id>-review.mp4`.
- [ ] Post the screenshots and the video in chat. Stop at merge-ready. Wait for the operator to merge.

**Merge.**

- [ ] Root's clean verdict at the exact head SHA.
- [ ] Automated reviewer triage done.
- [ ] Rebased onto current trunk after the verdict, patch-id unchanged.
- [ ] <The owner squash-merges its own PR, or the root appends it to the stack and the user lands it bottom-up.>

## Close the program

- [ ] Every box above is checked with its evidence.
- [ ] Reply to the user with the report the execution playbook names.

## Appendix A. Prototype evidence

<Each open question a prototype answered, with the branch, the SHA, and the artifact links. Each question that stays unproven.>

## Appendix B. Alternatives rejected

<Each approach weighed and why it lost.>

## Appendix C. Risks

<Each risk with the PR it lands in and what the owner watches.>

## Appendix D. Links and reading list

<Docs to read before editing. Which PRs get the `how` and `interrogate` skills. The decision trail per the `show-me-your-work` skill.>
````

**Reply:** the plan path, the PR ids with their dependencies and the review-gated set, what the prototypes proved and what stays unproven, and the check script's output.
