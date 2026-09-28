# Autonomous run

You own the exit condition. Define what "done" means, then keep working until it's true without stopping to check in.

1. Before the first iteration, write the exit condition as a predicate you can check: tests green, repro no longer reproduces, all N PRs merged, pixel diff zero.
2. Pick how you get woken up. If there's an event to wait on (CI finishing, a merge, a ref advancing), run a watcher that wakes you when it fires, with a long time-based heartbeat as a fallback. If there's no event, use a fixed interval sized to how often the result is worth re-checking.
   - In Claude Code, use `/loop`: `/loop <interval> <prompt>` for a fixed interval, or `/loop <prompt>` with no interval to let the session pace itself. Put event watchers in a background agent or a background shell command (for example `gh pr checks <pr> --watch`) so its completion notification wakes you.
   - In Codex, use `/goal <exit condition>` so the session keeps working across turns until the goal is met. Wait on events by running the watcher command in the foreground, and use a plain `sleep` as the heartbeat when there's nothing to watch.
3. In each iteration, make the smallest change the evidence supports, check it against the predicate, commit it if the predicate moved, and discard it if it didn't. Revert "might help" extras rather than leaving them in. Order the work per the `sequence-verifiable-units` principle: verify each unit before starting the next instead of batching checks at the end.
4. Handle what you find along the way yourself, under rigor: broken skills, related bugs, flaky verifiers, review-bot noise, tooling failures, orphaned follow-ups, fixable drift. Put fixes that are outside the task in their own PR. Don't park reversible work for the user or stop to ask. Raise only irreversible actions, product or preference calls no experiment can settle, and genuine dead ends. After each side fix, go back to the predicate.
5. Log every iteration with the `show-me-your-work` skill: one row for what changed and whether the predicate moved.
6. Stop when the predicate is met. A plateau isn't a reason to stop; change approach and keep going. If you hit a real dead end, report it instead of spinning. Never loosen the predicate to declare success.

**Reply:** the exit condition, how many iterations ran, what landed, what was discarded, and the final state of the predicate.
