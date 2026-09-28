# Attack the premise

When two or more fixes that share one premise have failed the same check, suspect the premise rather than the fixes. Each failure under a shared premise is evidence against that premise.

1. **Write the premise down.** It's the one sentence every failed fix assumed.
2. **Take a census before the next fix.** Measure the imbalance per actor. The census shows *which* actors hold the imbalance, not just how large it is. Write it as a rerunnable script (see [build-the-lever](build-the-lever.md)).
3. **Read the skew.** If the same few actors hold most of the imbalance on every run, something assigns them that role. Find what assigns it; that is the next "why" in [fix-root-causes](fix-root-causes.md).
4. **Remove the asymmetry instead of compensating for it** (see [laziness-protocol](laziness-protocol.md)). Rotate the role between actors, randomize the assignment, or move the role so no actor holds it on every run. A return path, shared pool, batched hand-off, or periodic rebalance leaves the assignment in place and adds work on every run.

Stop conditions:

- Don't start the next fix until the premise is written down and the census exists.
- If the census is even across actors, the premise isn't the cause. Look elsewhere and keep the census as evidence.

This differs from [redesign-from-first-principles](redesign-from-first-principles.md), which rebuilds a design around a new requirement. This one questions a fact the current design assumes.
