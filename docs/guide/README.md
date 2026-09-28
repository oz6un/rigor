# The mstack guide

mstack works best when you describe the goal and how you'll know it's done, and let `/rigor` handle the process. It picks a playbook, calls the other skills as the steps need them, and shows you the evidence. This guide teaches that habit with example prompts. In Codex, type `$rigor` (and `$<skill>` generally) wherever the guide says `/rigor`.

1. [Set up mstack](./01-setup.md)
2. [Route work through `/rigor`](./02-rigor.md)
3. [Understand the code](./03-understand.md): `/how`, `/why`, `/teach`, `/recall`
4. [Design the change](./04-design.md): `/architect`, `/arena`, `/swarm`, `/interrogate`
5. [Build and clean the change](./05-build-and-clean.md): the build playbooks, `/tdd`, `/deslop`, `/unslop`, `/no-comments`
6. [Verify and ship](./06-verify-and-ship.md): prove behavior in the real app, open a focused PR, drive it to merged
7. [Run work while you're away](./07-overnight.md): the handoff contract, the decision log, and the multi-PR playbooks
8. [Steer with principle names](./08-principles.md)
9. [Make it yours](./09-make-it-yours.md): your own mode skill, and testing a skill change
10. [Recipes and pitfalls](./10-recipes-and-pitfalls.md)

Read in order the first time; after that each page stands alone.

## The one habit

Give the agent a goal and a way to check it, in your own words:

```text
/rigor the export writes duplicate rows when a retry lands mid-run. repro first, then fix and verify.
```

You don't need to name a playbook or list skills. "repro first" and a checkable outcome are enough for `/rigor` to pick the Bug fix playbook, copy its steps into a todo list, and call the right skills at each step.
