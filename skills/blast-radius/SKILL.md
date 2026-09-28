---
name: blast-radius
description: Finds what a change could break outside its own diff before it ships, and proves the one fact its safety depends on by running real code. Use for "what's the blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.
disable-model-invocation: true
---

# Blast radius

Other skills named here don't appear in the model's skill list. To use one, read `<this skill's dir>/../<name>/SKILL.md` and follow it.

Find what a change breaks elsewhere, before it ships. `how` explains what code does and `why` explains why it's shaped that way; blast radius finds what a change to it breaks somewhere else.

Listing callers isn't the job; a grep does that in seconds. The job is the breakage a grep won't show.

## Prove the claim, don't just write it up

A plausible writeup reads the same whether or not it's true. So find the one or two facts the change's safety depends on and prove them by running code.

For each such fact, take it as far down this ladder as is cheap, and report where it stopped:

1. **Asserted.** You said so. Not evidence on its own.
2. **Located.** You pointed at a real `file:line`, or the library's own source.
3. **Reasoned.** You walked the failure case step by step and showed it can't be reached.
4. **Executed.** A script or test calls the real code and fails loudly if you're wrong.
5. **Reproduced.** You saw it in the running app.

Level 4 is usually one small script that imports the same library version the app ships and calls the exact function you're worried about.

## Steps

1. **Read the change.** The diff; the symbols it adds, changes, and removes; and what now behaves differently, including what the diff doesn't spell out. Pull the PR and commits as in the `why` skill's step 2.
2. **Find the fact it's safe because of.** Most changes that look risky are safe because of a single fact, such as "this call only evicts cache entries that are already dead". If that fact holds, most of the risky cases are cleared at once. Spend your time here rather than on a long list of maybes.
3. **Look where grep stops.**
   - Read the source of the libraries the change calls, at the pinned version, including any local patches.
   - Work out when things run: microtask ordering, unmount and teardown, framework-specific scheduling (for example, React versus Solid).
   - Follow references a symbol search misses: JSON an API returns, a database column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. **Assess each risk honestly.** Give each a realistic likelihood and cost. Keep the confirmed risks, and list the ones you checked and cleared separately. Follow `why`'s evidence rules: cite a real `file:line`, a search that finds nothing is still a result, and never invent a caller or an API.
5. **Prove the key fact.** Write a script or test that runs the real code, run it, and include the output.
6. **For a large or wide change, get several independent reviewers.** Run `interrogate` on the diff, or `swarm` to put one question to several reviewers and merge the answers. Both include a reviewer on the other model; different models catch different real bugs.

## What to hand back

- **What it does.** What changed, including the non-obvious part.
- **The fact it's safe because of.** State it, give the ladder level you reached, and show the proof. If you couldn't prove it, mark it unproven.
- **Risks.** For each: how it breaks, the `file:line`, likelihood and cost, and how to check. Include the proof output for the ones that matter.
- **Cleared.** What you checked and why it's fine.
- **Before you merge.** The cheapest test or repro that would catch the real bug, including the script you wrote.

Write it through `unslop`, cite real code, and remove private details before it goes anywhere public.
