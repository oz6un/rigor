### Authoring or modifying a skill

You own the skill's wording. Claude Code and Codex read the same `SKILL.md` format, so write one skill that works in both.

1. **Decide whether it should be a skill.** A skill is for a workflow that recurs and that an agent would otherwise get wrong. A one-off instruction belongs in the prompt; a rule that applies to every task in a repo belongs in `CLAUDE.md` / `AGENTS.md`; something a script or lint rule can enforce should be that script or lint rule (the `encode-lessons-in-structure` principle). If an existing skill nearly covers it, extend that skill instead.
2. **Lay out the directory.** One directory per skill, named in kebab-case:

   ```
   <skill-name>/
     SKILL.md          # required: frontmatter + instructions
     references/       # optional: detail loaded only when a step needs it
     scripts/          # optional: executable helpers the agent runs instead of retyping logic
     assets/           # optional: templates or files copied into output
   ```

   Where it lives: in a skill collection like this one, `skills/<name>/`. For a single project, Claude Code reads `.claude/skills/<name>/` and Codex reads `.agents/skills/<name>/`. For one user, `~/.claude/skills/` and `~/.agents/skills/`.
3. **Write the frontmatter.** Only these fields:

   ```yaml
   ---
   name: <skill-name>            # kebab-case, equal to the directory name, 64 chars max
   description: <what it does and when to use it>
   ---
   ```

   The description is the only part both hosts keep in context before the skill is invoked, so it decides whether the skill triggers. Write one or two plain sentences: what the skill does, then the situations and user phrasings that should trigger it. Stay under 1024 characters. To make a skill run only when the user types it, set both `disable-model-invocation: true` (Claude Code) and an `agents/openai.yaml` containing `policy:` / `allow_implicit_invocation: false` (Codex); `scripts/check.py` fails if only one is set. A skill that names a hidden skill must also say how to read it (copy the "Other skills named here..." line from an existing skill).
4. **Write the body for progressive disclosure.** `SKILL.md` loads in full when the skill triggers, so keep it to what every run needs: when to use it, the steps, the gates, and the output shape. Aim for under about 300 lines. Move detail that only some runs need (long rubrics, API notes, worked examples) into `references/<topic>.md` and link it from the step that needs it, saying when to read it. Put deterministic logic (parsing, validation, API calls) in `scripts/` and tell the agent to run the script rather than read it. Reference files by relative path from the skill directory.
5. **Edit for decisions.** Keep only prose that changes what the agent does. State the instruction; add a reason only when the rule would be misapplied without one. Point at structural sources (types, READMEs, config) instead of restating them. Delegate to other skills by name instead of copying their content. Match the length to the scope of the task.
6. **Validate.** Check that `name` matches the directory, `description` is present and specific, every referenced file exists, every script runs, and cross-skill references name skills that exist. For a skill whose behavior can be checked (it produces a file, a format, a command sequence), run it on one or two realistic prompts and read the output. For a skill whose effect on agent behavior is uncertain, run the Eval playbook (`playbooks/eval.md`). Skip behavioral testing only for purely stylistic skills, and say so.
7. Run the Opening a PR playbook (`playbooks/opening-a-pr.md`).

If you keep hitting a workflow that no skill captures, propose a new skill in the reply.

**Reply:** what the skill does and when it triggers, the key design decisions (what went in `SKILL.md` versus `references/` and `scripts/`), and validation notes.
