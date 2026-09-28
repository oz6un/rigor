# Trace forensics

You own the diagnosis from an existing capture: load it, make it queryable, narrow to the cause, and attribute it to source.

This differs from Runtime forensics, which instruments a live process. Here the artifact already exists and is a fixed dataset: read it, don't re-run it. Use generic tooling: a DevTools or trace parser for `.cpuprofile` and `.json.gz` traces, a text editor for a spindump, your usual heap tooling for a `.heapsnapshot`.

1. Identify the format and load it with the right tool. Parse large artifacts in a subagent and keep only the reduced finding in the main thread (the `guard-the-context-window` principle).
2. Transform the raw artifact into something you can query before you start reading it, for example sqlite with one row per sample, frame, or node.
3. Narrow to the cause. For CPU, query for the frames holding the most time and walk the call tree to the hot path. For a leak, follow the retainer chain from the leaked object to a GC root. For a spindump, find the thread that's stuck on-CPU or blocked, and its wait reason.
4. Attribute to source: map the hot frame to file, symbol, and line using the artifact's own symbols. A frame with no source mapping isn't a diagnosis yet; resolve the symbols, or say plainly that the artifact doesn't carry them.
5. Confirm against a paired capture if you have one by diffing the before and after artifacts. Without one, present the finding as the strongest hypothesis the artifact supports, not a confirmed cause.
6. Hand back a cited diagnosis without a fix unless asked, and route to the Bug fix or Perf issue playbook once the cause is known. Write the throughput checkpoint as one line: `throughput checkpoint: n/a, read-only forensics`.

**Reply:** the artifact and its format, the reduced finding, the source location, the artifact paths, and whether a paired capture confirmed it.
