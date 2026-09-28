# Set up rigor

Installation for Claude Code and Codex is covered in the [project README](../../README.md). Come back here once rigor is installed.

## Optional: a verification skill for your app

If your project has no scripted way to drive the app and prove behavior, run `/create-verification-skill` once. It writes a project-local `verify-<app>` skill and proves it works before handing it over. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) explains when it's worth it.

## Run a first task

Pick something real but small and describe it as you would to a colleague:

```text
/rigor add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps (Feature, for this prompt). A step the agent skips stays in the list as `skip: <reason>`, so you can see what it chose not to do.

After that, type normal follow-ups. `/rigor` stays on for the session until you say otherwise.

Next: [Route work through `/rigor`](./02-rigor.md).
