# Guard the context window

The context window is finite and doesn't refill within a session. Spend it on what the main thread needs.

**Why:** When context overflows, reasoning degrades, compaction loses details, and progress can stall.

- **Isolate large payloads.** Send verbose command output, screenshots, large documents, and wide searches to subagents. The main thread gets summaries, not raw data.
- **Keep frequently used content inline.** Templates and references needed on every invocation belong in the skill file itself, not in separate files that each cost a read.
- **Size phases and cap scope.** Limit files per phase, set turn budgets, and account for what each mechanism costs in context.

[minimize-reader-load](minimize-reader-load.md) is the same idea applied to human readers.
