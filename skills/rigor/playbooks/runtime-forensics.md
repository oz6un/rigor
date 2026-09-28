# Runtime forensics

You own the diagnosis. Instrument the live process instead of theorizing from source. The deliverable is a cited diagnosis, not a fix.

1. Capture the live signal on the affected surface with `control-ui` or `control-cli`: a CPU profile for a spinning process, a heap snapshot for a leak, a Chrome DevTools Protocol (CDP) trace for a visual glitch. Get a real artifact, not a guess.
2. Reduce the artifact to the specific cause: the function on the hot path, the retainer chain from the leaked object to a GC root, the loop that fires without input. Parse large artifacts in a subagent and keep only the reduced finding in the main thread (the `guard-the-context-window` principle).
3. Confirm the mechanism before relying on it. Inject instrumentation into the running process (for example, CDP `Runtime.evaluate`) or hot-patch the live code without reloading, to test the hypothesis cheaply.
4. Map the finding back to source: file, symbol, and the line that allocates or schedules.
5. Write the throughput checkpoint as one line: `throughput checkpoint: n/a, read-only forensics`.

**Reply:** the signal captured, the reduced finding, how you confirmed the mechanism, the source location, and artifact paths. Don't fix it unless asked; once the cause is known, hand off to the Bug fix or Perf issue playbook.
