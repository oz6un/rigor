---
name: no-comments
description: Remove unneeded comments from a diff. Spawns the read-only comment-reviewer subagent, applies the findings you accept, fixes the code the comments were explaining, and offers to encode claimed constraints as checks. Use before requesting review.
disable-model-invocation: true
---

# No comments

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` (with symlinks in this skill's path resolved) and follow it.

The `comment-reviewer` subagent decides which comments go. It sees the code without your context, which is the point, so give its findings weight and don't argue them back to what you wrote. Your job is to check its report, apply it, and fix the code behind the comments.

## Scope

Use the files or diff the caller names. Otherwise use the current diff against the base branch (default `main`), including uncommitted changes.

## Steps

1. **Spawn the reviewer.** Pass it the scope and nothing else; its rules live in its own definition, so don't restate them.
   - In Claude Code, use the Agent tool with `subagent_type: "comment-reviewer"`.
   - In Codex, spawn the `comment-reviewer` custom agent (installed by rigor's `install.sh`). If it isn't installed, spawn a read-only subagent and tell it to follow this plugin's `agents/comment-reviewer.md`.

2. **Check the report.** Reject findings that fall outside the scope, propose application code, delete a comment that matches one of the reviewer's keep exceptions, misstate a `needs-refactor` reason, or treat deliberately kept code as a defect. Then check what it missed and what it kept:
   - A `needs-refactor` flag on a surprise in our own code stays actionable, and the comment stays deleted.
   - A kept comment survives only with evidence that it describes something outside our control.
   - Look for lint and TypeScript suppressions in scope that the reviewer missed. A suppression of a rule that protects correctness or safety becomes a `needs-refactor` finding.
   - Keep a comment the reviewer marked for deletion only if you can name the exact exception it matches and show it applies within the scope.
   - Before accepting a thinly argued decision on an `IMPORTANT` or `do not remove` comment, run the `how` or `why` skill on its symbol. If a deletion is still ambiguous, delete. If a keep is refuted or still ambiguous, delete it too.
   - If the report is unusable, rerun the reviewer once with the problem stated. If the second report is also unusable, stop, report the scope as open, and report that `no-comments` failed.

3. **Apply the deletions** you accepted.

4. **Fix the flagged code.** Handle trivial flags directly: delete the dead path, drop the unused parameter, call the real API. If any fix needs a new shape, run the `architect` skill once for the whole accepted set and the code around it, and stop at its sketch. Step 5 implements it.

5. **Implement the smallest root-cause fix within the scope,** and remove every workaround the flags named. If the root cause lies outside the scope, land the smallest in-scope fix and report the rest as open. The `fix-root-causes` and `redesign-from-first-principles` principles (in the `principles` skill) tell you what a good fix looks like; they don't license widening the scope, so list other instances in the report instead of fixing them here. Don't add guards that only hide the symptom.

6. **Handle constraint comments.** These say `do not remove`, `do not change wording`, `talk to X before changing`, and similar. Leave kept comments about things we can't change. For the rest, offer the cheapest in-scope way to enforce the constraint instead: a type, a runtime check, a test, or a CI lint rule.
   - In an interactive session, ask the user and wait. In an unattended run or an eval, proceed only if the caller approved encodings up front.
   - If approved, add the enforcement, then delete the comment. Otherwise delete the comment, report the constraint as unenforced, and sketch the out-of-scope work.

7. **Report** the number of comments deleted, any restored, reruns of the reviewer, the architect sketch, fixes made, encodings offered and added, constraints left unenforced, and other open work.
