---
name: how
description: Explains how a part of the codebase works (architecture, runtime flow, where things live) at the level a senior engineer needs to start working in it. Use for "how does X work", a walkthrough before changing something, or placement questions like "where should this live" and "which package owns this". For why the code is shaped the way it is, use `why`.
---

# How

Answer "how does X work?" with an architectural explanation: enough for a senior engineer new to the subsystem to build a working mental model, without turning into annotated source.

## 1. Size the question

If the scope is ambiguous, state your reading of it and proceed. The user can redirect.

- **Simple**: one module, a small utility, a narrow question ("how does `parseConfig` work"). Go to step 2b.
- **Complex**: a subsystem spanning several files or services, a cross-cutting feature, or a full architectural overview. Go to step 2a.

When unsure, treat it as simple.

## 2a. Explore in parallel (complex questions)

Split the question into two to four exploration angles, each a distinct slice of the subsystem (for example: the entry point and request flow, the persistence layer, the integration with service Y). Spawn one read-only explorer per angle, all in parallel, each with `references/explorer-prompt.md` and its angle filled in.

- In Claude Code, use the `Explore` agent, or `general-purpose` on a fast model.
- In Codex, spawn subagents with `sandbox_mode = "read-only"` on a fast model.

For a cross-model check, run one of the angles through the `second-opinion.sh` script in the `rigor` skill's `scripts/` directory (read-only by default) instead of a host subagent. If it exits with code 3, use a host subagent for that angle and note it.

Then go to step 3.

## 2b. Explain directly (simple questions)

Spawn one read-only subagent on your strongest model that explores and explains in one pass. Build its prompt from `references/explainer-prompt.md`, leaving out the explorer-findings section. Go to step 4.

## 3. Synthesize (complex questions)

When every explorer has returned, spawn one read-only subagent on your strongest model with `references/explainer-prompt.md` and all explorer findings filled in. It reconciles overlaps and contradictions and writes the explanation.

## 4. Present

Give the user the explainer's output. Light edits for clarity or to connect it to the conversation are fine; don't rewrite it.

The explanation uses the sections from `references/explainer-prompt.md`, dropping any that don't apply: Overview, Key concepts, How it works, Where things live, Gotchas.
