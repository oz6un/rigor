# Build the lever

For any nontrivial work (edits, migrations, analyses, checks), build the tool that does or checks it instead of doing it by hand.

**Why:** A codemod, generator, or script does the work the same way every time and reruns for free. It's also one artifact a reviewer can read and rerun to check the work; hand-made changes can only be re-verified by redoing them.

Build the tool by default. Skip it only when the task is trivial: a couple of obvious edits you can check at a glance. The bar is triviality, not repetition. A one-off still earns a tool when the tool is what makes the work checkable.

- Do the first unit by hand to learn the recipe, then build the tool. Prove it by running it on that unit and diffing against your hand-made version. Make it safe to rerun.
- Use a codemod or script for edits, a generator for repetitive files, a query over a dump (for example into SQLite) for analysis, and a rerunnable check for verification.
- If a deterministic tool can process every unit in one pass, run it yourself instead of fanning out subagents to apply the change by hand.
- When you do fan work out to subagents, write the recipe, the verification contract, and the files they must not touch into one skill or instructions file they all read. Keep it outside their write scope so they can't edit the contract.
- Applying this principle produces a file. If you cite it and the diff has no codemod, script, generator, or delegate instructions, you didn't apply it.
- Commit the tool when the work outlives the session.
- Build the smallest script that does or checks the job, not a framework (see [laziness-protocol](laziness-protocol.md)).

Related: [encode-lessons-in-structure](encode-lessons-in-structure.md) turns a recurring instruction into a lasting guardrail; this principle is about throughput and reviewability for the work in front of you. For scripting verification, see [prove-it-works](prove-it-works.md).
