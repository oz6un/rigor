# Make operations idempotent

Design operations to reach the correct state no matter how many times they run or where a previous run stopped. For every operation that changes state, answer: what happens if this runs twice, and what happens if the last run crashed halfway?

**Why:** Commands, lifecycle steps, and processing loops run in environments where crashes, restarts, and retries are normal. If leftover state changes the outcome of the next run, every restart turns into a debugging session.

Patterns:

- Convergent startup: scan for existing state, clean up stale artifacts, adopt sessions that are still alive.
- Content-based cleanup: compare by content, not by creation order.
- Self-healing locks: detect stale locks by checking whether the owning PID is still alive.
- Idempotent scheduling: failed work respawns cleanly, and fresh input is regenerated after each cycle.

Test:

1. What happens if this runs twice in a row?
2. What happens if the previous run crashed at each possible point?
3. Does rerunning reach the same end state?

If any answer is "it depends on what state was left behind", add a reconciliation step.
