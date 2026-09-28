# Never block on the human

The user supervises asynchronously, so keep working. Make reasonable decisions, proceed, and let the user correct course afterwards.

**Why:** Each pause for permission stalls the work and makes the user the bottleneck. Code changes are reversible and reviewable, so a wrong call usually costs less than waiting.

- **Do it, then show it.** Instead of asking "should I do X?", do X and explain why.
- **Fix problems as you find them.** When you notice something wrong, record it and fix it in the next pass.

Limits:

- **Irreversible actions** (force-pushing a shared branch, deleting data, deploying, messaging customers or other outside parties) still need confirmation.
- **Reversible actions** (writing code, editing notes, splitting tasks) proceed without asking.
- **Product direction** comes from the user; execution shouldn't wait on them.

For detail, see the rigor skill's "Before asking the user a question" section (which questions to settle with an experiment and which product calls to ask about) and its "Autonomy" section (which actions proceed and which always pause).
