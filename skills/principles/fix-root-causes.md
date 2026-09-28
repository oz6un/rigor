# Fix root causes

When debugging, trace each problem to its root cause and fix it there instead of patching the symptom.

**Why:** Symptom fixes accumulate. Each workaround makes the system harder to reason about while the real bug stays. Root-cause fixes take longer up front and less time overall.

- Reproduce the bug first.
- Keep asking "why" until you reach the cause.
- Don't add guards to silence failures. A nil check that stops a crash is a symptom fix.
- If a workaround needs a paragraph-long comment to justify it, the code is wrong. Fix the code.
- Fix the pattern, not just the instance: search for the same mistake elsewhere and fix every occurrence.
- When stuck, instrument instead of guessing. Add logging and read the actual error.

**Bugs that appear after a restart:** suspect stale persistent state before code: config files, caches, lock files, serialized state. If clearing a state file restores the behavior, make validating that state the fix.

When several fixes built on the same assumption have failed, see [attack-the-premise](attack-the-premise.md).
