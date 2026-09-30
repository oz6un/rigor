---
name: arena
description: Run several independent attempts at the same task in parallel (host subagents plus one from the other coding CLI), pick the strongest as the base, and fold in the best parts of the others. Use for /arena, "arena this", or when a single attempt at a nontrivial design or piece of code would lock in the wrong shape.
disable-model-invocation: true
---

# Arena

Run N independent attempts at the same task. Read every candidate end to end, pick the strongest as the base, fold the best ideas from the others into it, and verify the result.

Start a todo list with one item per phase before launching anything: Frame, Fan out, Cross-judge, Pick, Combine, Verify.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract. The one exception is a direction line when the arena explores several design directions (step 3).

1. State the artifact each candidate produces.
2. Write the rubric: what success looks like for this task, as 3-6 concrete criteria you can score. The rubric is for you and the judge in Phases C and D. Candidates only see the task.
3. Choose the panel. The default is three candidates:
   - Two or more host subagents on your strongest model. Give each the identical prompt when the work is generation-bound. When the arena should explore several design directions, add one candidate per direction and name the direction in its prompt.
   - One candidate from the other CLI, run through `<this skill's dir>/../rigor/scripts/second-opinion.sh`. A different model family is the main source of real diversity, so keep this seat whenever the other CLI is installed.
4. Give each candidate its own output location so no two attempts share state (the `separate-before-serializing-shared-state` principle). See [Isolating candidates](#isolating-candidates).

## Phase B: Fan out

Launch all candidates at once and let them run in parallel. Each prompt includes the task, the path to any shared grounding, the candidate's own output location, and a request for both the artifact and a short rationale that names the alternatives it considered and why it rejected them.

- Host subagents: in Claude Code, spawn them in one message with the Agent tool (`run_in_background: true`; add `isolation: "worktree"` when they write code). In Codex, spawn them together; each one's prompt names its worktree.
- The other CLI: write the prompt to a file and run the script in the background, capturing stdout to the candidate's output location:

  ```bash
  <this skill's dir>/../rigor/scripts/second-opinion.sh --write --cd "$wt" < prompt.txt > "$out/candidate-3.md"
  ```

  Drop `--write --cd` for a candidate that only returns text (a written design, a plan); its final message is the artifact. If the script exits 3, the other CLI isn't installed: start a host candidate for that seat instead (not a dropout) and note it in the synthesis record.

  Name the verification command in the candidate's prompt. With `--write`, the candidate runs commands in a sandbox: it writes in its worktree and the CLI's temp folder (for Claude, `/tmp/claude-<uid>`), and has no network except localhost. Install its dependencies first, and keep the other candidates' worktrees and your output files outside that temp folder. Exit 4 means the run didn't finish (no completion reported, or no answer); treat it as unfinished even if files were produced. Exit 0 confirms only that the run finished: read the answer, which says what the candidate couldn't run, and verify its work yourself.

If a candidate produces nothing usable, continue with N-1 and record the dropout.

Tell each candidate to leave its changes uncommitted, because the other CLI's sandbox may not be able to write the repo's `.git`.

### Isolating candidates

When candidates write code, each needs its own git worktree:

- Claude Code host subagents: pass `isolation: "worktree"` to the Agent tool. The result reports the worktree path and branch when the agent left changes.
- Codex host subagents and the other-CLI candidate: create the worktree yourself and point the candidate at it.

  ```bash
  git worktree add -b "arena/<slug>/<n>" "../arena-<slug>-<n>" HEAD
  ```

  Use a specific branch or commit instead of `HEAD` when the attempt must start from one.

  Pass that path in the subagent's prompt, or as `--cd` to `second-opinion.sh --write`. Read a candidate's full change with `git -C <worktree> add -A && git -C <worktree> diff --cached`.

For text artifacts, use `/tmp/arena-<slug>/candidate-<n>/`. When the arena is done, remove the worktrees you created (`git worktree remove <path>`) and delete their branches unless a candidate's branch became the base.

## Phase C: Cross-judge

After every candidate has finished, get one independent judge from a different model family than yours: run it through `<this skill's dir>/../rigor/scripts/second-opinion.sh` (read-only, the default). Give it the rubric and the candidates by path label. It scores each criterion per candidate and recommends a base with reasons. It runs while you do your own reading in Phase D. Don't start it while candidates are still writing.

If the other CLI isn't installed, the judge is a read-only host subagent (Claude Code: a `general-purpose` agent told not to edit; Codex: `rigor-reviewer`; per the rigor skill's Subagents section); note that it shares your model family.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on overall impression. Then compare with the judge. If you agree on the base, the pick is confirmed. If you disagree, one of you is biased or the rubric was ambiguous; read both rationales before deciding.

Choose the candidate a future maintainer can extend most easily without breaking invariants. When two are tied, take the one with the cleaner boundary or smaller API (the `laziness-protocol` principle).

Record the pick, the reason, and the judge's verdict in a short synthesis note next to the base artifact.

## Phase E: Combine

Go through each losing candidate once more and list what is worth bringing into the base. Usually that is one or two things per candidate.

Fold each one in by hand so the result still reads as one design (the `redesign-from-first-principles` principle). Don't paste sections across mechanically. Record what came from which candidate, and what you rejected and why.

If the candidates converged on the same shape, that is strong agreement: note it and ship that shape without combining. If they diverged wildly, the framing in Phase A was underspecified. Reframe and rerun instead of averaging them.

## Phase F: Verify

Verify the combined artifact the same way you would any other output (the `prove-it-works` principle). If verification finds a problem no candidate caught, the framing was wrong: reframe and rerun. If a candidate did catch it and you missed it, go back to Phase E.

## Output

One combined artifact, plus a short synthesis note naming the panel (which seats were host subagents and which ran on the other CLI, and any fallback), the base, what was brought in from each other candidate, what was rejected, any dropouts, and the verification result.
