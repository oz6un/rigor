# Autonomous run

You own the exit condition. Define what "done" means, then keep working until it's true without stopping to check in.

1. Before the first iteration, write the exit condition as a predicate you can check: tests green, repro no longer reproduces, all N PRs merged, pixel diff zero.
2. Keep the session going with `/goal <exit condition>`, in both Claude Code and Codex. If the user hasn't set one, give them the exact line to paste, including the check that proves it ("`python3 -m pytest` exits 0") and anything that must not change on the way ("no test file is modified"). The goal's checker only sees what you show in the conversation, so run the check and show its output each iteration. To wait on an event (CI, a merge), run the watcher (for example `gh pr checks <pr> --watch`) in the foreground or as a background command; don't add your own sleep loops.
3. In each iteration, make the smallest change the evidence supports, check it against the predicate, commit it if the predicate moved, and discard it if it didn't. Revert "might help" extras rather than leaving them in. Order the work per the `sequence-verifiable-units` principle: verify each unit before starting the next instead of batching checks at the end.
4. Handle what you find along the way yourself, under rigor: broken skills, related bugs, flaky verifiers, review-bot noise, tooling failures, orphaned follow-ups, fixable drift. Put fixes that are outside the task in their own PR. Don't park reversible work for the user or stop to ask. Raise only irreversible actions, product or preference calls no experiment can settle, and genuine dead ends. After each side fix, go back to the predicate.
5. Log every iteration with the `show-me-your-work` skill: one row for what changed and whether the predicate moved.
6. Stop when the predicate is met. A plateau isn't a reason to stop; change approach and keep going. If you hit a real dead end, report it instead of spinning. Never loosen the predicate to declare success.

**Reply:** the exit condition, how many iterations ran, what landed, what was discarded, and the final state of the predicate.
