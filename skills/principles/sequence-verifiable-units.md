# Sequence verifiable units

Order work as a series of small units, each ending in a state you can check, and don't move on until the current unit passes.

**Why:** A break caught at the unit that caused it is easy to locate. A break caught after a batch is buried, and you've already built on top of it. Ordering the same units into a delivery a reviewer can replay lets them watch the check fail and then pass instead of taking your word.

**While working.** In a sweep, migration, or run of similar edits, verify each change before starting the next: start from a known-good state, make one change, run the check, then continue. Rebase onto a clean main branch first so every check measures against the real baseline. When a script does the edits (see [build-the-lever](build-the-lever.md)), the per-unit check is nearly free; run it anyway.

**When delivering.** Stack commits and PRs in the order that proves the work. The standard shape is the failing test first, then the fix on top. Other useful orders: removal before a reshape, a baseline measurement before the change, scaffolding before the feature. Each commit should stand on its own, and the sequence should read as an argument.

[prove-it-works](prove-it-works.md) keeps each check real; [build-the-lever](build-the-lever.md) makes it cheap.
