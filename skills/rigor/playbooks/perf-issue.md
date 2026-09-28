# Perf issue

You own the measurements: plan, review, and verify the numbers. Tie every fix to a measurement; reading source is not a substitute for measuring.

For sustained improvement of a metric rather than a one-off fix, use the Hillclimb playbook (`playbooks/hillclimb.md`).

1. Capture a baseline trace on the affected surface with `control-ui` or `control-cli`.
2. Run `how` over the slow path to ground your hypotheses. Don't claim a performance ceiling without measuring it.
   Most fixes fall into one of the strategy families below. Use them to generate hypotheses, not as a checklist: a family is worth trying only when the trace shows the signal it names.
   - **Elimination.** Before optimizing the hot path, ask whether it needs to exist: a computation nobody reads, a feature gate that's always off for this user, a sync that mirrors state redundantly, a legacy path kept just in case. A trace shows what's slow, not what's deletable, so this family comes from the `how` pass rather than the profiler.
   - **Divide and conquer.** The dominant cost grows with input size. Split the work so each piece touches less (chunk, shard, prune the search space), or so independent pieces run in parallel.
   - **Caching.** The same computation or fetch repeats on identical inputs. Store and reuse the result, and name what invalidates the cache before claiming the win.
   - **Indirection.** The hot path does expensive work that a cheaper intermediate could absorb: an index instead of a scan, a queue that moves work off the interactive thread, a handle that lets a cheaper implementation swap in. Add the extra step only when it removes more from the critical path than it adds.
   - **Batching.** Many small operations each pay a fixed overhead (RPC, query, syscall, draw call). Combine them so the overhead is paid once per batch.
   - **Redundancy.** The wait depends on one slow instance or attempt. Duplicate the work (replicas, hedged requests, speculative execution) and take the fastest result. Only when the trace shows that wait dominates and the system has spare capacity.
   - **Lazy evaluation.** Work is done for results that are never used or not needed yet (eager init on the boot path, rendering offscreen items). Defer it until first use.
   - **Scheduling.** The work has to happen, but not while the user is waiting. Move it to idle callbacks, a background warmup after boot, precomputation before the user arrives, or cleanup after the frame commits. The gain is perceived latency, so measure the interactive path, not total work.
3. Plan the fix from the trace. If it crosses a function boundary, run `architect` first. Delegate the implementation to a `rigor-agent` subagent, review the diff, and capture a post-fix trace. Verify each attempt before starting the next (the `sequence-verifiable-units` principle).
4. Parse and compare the before and after artifacts (for example, load the JSON into sqlite and diff). An inconclusive result, or a measurement from a different surface, is not a pass; flag it.
5. Cite the measurements in the PR description.
6. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`).

**Reply:** the baseline number, the post-fix number, the delta, and the artifact paths.
