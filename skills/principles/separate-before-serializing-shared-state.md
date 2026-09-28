# Separate before serializing shared state

When concurrent actors might share mutable state, first ask whether they need the same object at all. If not, remove the sharing. If they do, enforce serialization structurally (lockfiles, sequential phases, exclusive ownership). Instructions and conventions are not concurrency control.

**Why:** Concurrent writes to shared state cause race conditions that are intermittent, hard to reproduce, and expensive to debug.

1. **Find the shared mutable state:** files that several actors read and write, branches they all push to, APIs one defines while another consumes.
2. **By default, remove the shared write target.** Do the actors need one canonical object, or are they each publishing independent facts? Give each actor its own file, key, branch, or state directory, and merge only where the results are read or reported. Two workers each writing their own `lastX` field into one `state.json` is still shared mutation; `indexer-state.json` plus `metrics-state.json` is not.
3. **Serialize only when a single shared target is a real invariant.** Use a lockfile, sequential phases, a single-writer actor, or atomic compare-and-swap. Treat "we need a lock" as a design smell to check, not the default answer.

This applies to agents too: parallel subagents should each own separate files, branches, or worktrees.
