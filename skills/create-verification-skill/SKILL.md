---
name: create-verification-skill
description: Generate a project-local verification skill that launches the app and drives it the way a user does, in any language or platform. Use for /create-verification-skill, "make a verify skill for this repo", or when a project has no scripted way to prove UI, CLI, or service behavior.
---

# Create a verification skill

A project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature as a user would, and capture evidence. This skill generates that as a project-local skill tailored to the repo. The reader is the next agent, arriving cold and mid-task, who has never seen the app. Write for that reader.

## Where the generated skill lives

The generated skill must load in both Claude Code and Codex, so write it once and link it:

- Write the files to `.agents/skills/verify-<app>/` (Codex reads project skills from `.agents/skills/`).
- Symlink it for Claude Code: `mkdir -p .claude/skills && ln -s ../../.agents/skills/verify-<app> .claude/skills/verify-<app>`.
- Commit both the directory and the symlink. If the repo already keeps skills in only one of these locations and the team uses one host, follow the repo's convention instead and say so in the report.

## 1. Interview the repo, not the user

Answer these from the codebase. Ask the user only what you can't observe.

- **Surface.** What does a user touch: a web UI, CLI or TUI, desktop app, API, mobile app, library? A repo can have several. Pick the primary one and note the rest.
- **Run.** How does the app start locally? Prefer the repo's documented dev command (package scripts, Makefile, README). Note ports, env vars, seed data, and auth.
- **Drive.** How can an agent interact with it programmatically? Look for existing harnesses first: Playwright or Cypress specs, expect scripts, PTY helpers, curl-able endpoints, a debug port. Only then fall back to a generic recipe: browser automation or CDP for web and Electron (the `control-ui` skill), tmux or a PTY for CLI and TUI (the `control-cli` skill), plain HTTP for services.
- **Observe.** What evidence can be captured: screenshots, terminal transcripts, response bodies, logs, exit codes, database state?
- **Isolate.** Can two instances run side by side (separate ports, data dirs, profiles)? If not, the generated skill must say so and refuse to drive an instance it didn't start, since double-driving a shared instance can corrupt the user's session.

If the checkout doesn't build or start as-is, fix that first or report the failure precisely. A skill written against a broken base teaches wrong steps. When an irrelevant missing asset blocks startup (a static dir the API never serves, a sample config), the generated skill may create it, marked as verification scaffolding, and remove it in cleanup.

## 2. Generate the skill

Write `SKILL.md` with frontmatter (`name: verify-<app>` and a `description` naming the app, the surface, and when to use it; without frontmatter the skill doesn't register). Include these sections, each filled from what the interview found, with no placeholders left:

- **Launch.** The exact command that starts the app for verification, how to tell it's ready (a log line, a port answering, a prompt), and teardown. For a short-lived CLI or TUI there's no server to keep alive: build the binary or install dependencies once, then start each drive in its own isolated PTY or tmux session.
- **Doctor.** One read-only check that answers "is this instance worth driving?": process up, expected version or build, port owned by this run, auth valid. Agents run it first and again whenever something looks off.
- **Drive.** The harness recipe with real selectors and commands from this repo. Prefer stable handles (ARIA roles and labels, `data-*` attributes, prompt strings, route paths) over coordinates and tab order.
- **Evidence.** What to capture and where it goes. State the proof standards:
  - Exercise the real user path, not internal setters or test-only endpoints.
  - Capture the action and the resulting state, not only the final screen.
  - Verify side effects (files written, rows inserted, messages sent) alongside what's visible.
  - Use mocks only where a production boundary already isolates the external system.
  - When the safe path is a dry-run or test mode, observe what it actually skips (files, network, git refs). Some dry-runs still touch the network or open a browser.
- **Cleanup.** How to tear down what the run created. Kill processes by the PID or session you started, never by process name. Cleanup removes instances and scratch state but keeps the evidence, in a location the skill names.
- **Helpers.** Any script the skill ships is executable, and the skill body shows how to invoke it.

## 3. Seed the feature map

Create `features/README.md` inside the skill, plus one file per user-facing feature. Start with the top three to five, found from routes, commands, menus, or docs. Follow the shape in [`references/feature-map-example/`](references/feature-map-example/): a README index, then one file per feature with exactly these H2 sections:

1. `Sub-features`
2. `How to get to it (user POV)`
3. `Driving it with <harness>`
4. `Gotchas`

Each file says, from the user's point of view, what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works. The map is the repo's source of truth for verification: a proof that drives one convenient entry point is incomplete when the map lists others.

## 4. Prove the generated skill

Follow the generated skill's own instructions end to end once: launch, doctor, drive one mapped feature, capture evidence, clean up. One feature is enough; later runs use the map for the rest. After cleanup, confirm the evidence still exists at the named location. A cleanup that deletes the proof fails this step.

Fix whatever fails and rerun. Run the generated cleanup after every failed attempt too, so broken runs don't leave processes and ports behind. Don't hand over a skill that hasn't run successfully once.

## 5. Point at maintenance

Tell the user that `/maintain-verification-skill` keeps the map accurate as the app changes. Suggest a cadence only if they ask.
