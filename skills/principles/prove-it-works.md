# Prove it works

Before calling a task done, check the real result directly. Don't infer correctness from proxies, self-reports, or "it compiles".

**Why:** Unverified work has unknown correctness. Indirect signals (file modification times, output freshness, a subagent's report, an old screenshot) feel cheaper than looking, but acting on a wrong inference costs far more than checking the source.

- Check that a process is alive directly, not through state derived from it.
- Read the actual value, not a cached or derived copy.
- When a check fails, suspect the way you observed it before suspecting the system.

**Script the check when you can.** The strongest proof is a deterministic script that reruns the same comparison, not a one-time look. Write it, run it, and keep its output as something a reviewer can rerun (see [build-the-lever](build-the-lever.md)).

Keep that evidence visible to the user. Commit it only for large or complex work that needs an auditable trail later, such as a big port or migration (the `show-me-your-work` skill).
