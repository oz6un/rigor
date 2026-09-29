# rigor

Skills for doing careful engineering work with coding agents in Claude Code and Codex. The goal is less code of higher quality: reproduce before fixing, settle the design before writing it, verify on the real artifact, and review with more than one model.

rigor is a port of [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, originally built for Cursor. The workflows and principles come from pstack. The port removes the Cursor-specific machinery, adapts subagents and model routing to Claude Code and Codex, and rewrites the prose in a plainer voice.

## Install

Requirements: `git`, `python3`, and `bash` (macOS or Linux). The PR playbooks need `gh` and Node (the plan checker runs on `node`; `watch-pr` and `orch` use `bun`, or fetch it with `npx`). Optional: `tmux` for `control-cli`, and the other CLI (`codex` or `claude`) for cross-model second opinions.

One clone serves both Claude Code and Codex:

```bash
git clone https://github.com/oz6un/rigor.git ~/.local/share/rigor
~/.local/share/rigor/install.sh
```

`install.sh` symlinks every skill into `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex), symlinks the subagents into `~/.claude/agents/`, and copies the Codex agents into `~/.codex/agents/`. It also registers rigor's stay-on hook in `~/.claude/settings.json` and `~/.codex/hooks.json`, next to any hooks you already have. It never overwrites a skill or agent it didn't create; it skips it and says so.

Codex runs a hook only after you approve it: open Codex, run `/hooks`, and trust rigor's two hooks (again whenever an update changes them). Claude Code needs no extra step. Start a new session afterwards.

To update, pull and rerun the script (the rerun matters when a pull adds or removes a skill or agent, or changes the Codex agents):

```bash
git -C ~/.local/share/rigor pull && ~/.local/share/rigor/install.sh
```

To remove everything it installed, run `install.sh --uninstall`. If you move the clone, rerun `install.sh` from the new location to repair the links.

### Cross-model review (optional)

Skills that run review panels (`interrogate`, `arena`, `architect`, `reflect`, and others) get a second opinion from the other CLI: Claude Code calls `codex exec`, and Codex calls `claude -p`. Install and log in to both CLIs to get this. If the other CLI is missing, the panels run with the host's own subagents and say so in the report.

To pick the model used for second opinions, set `RIGOR_CODEX_MODEL` or `RIGOR_CLAUDE_MODEL`.

## Usage

Start a task with `/rigor` (Codex: `$rigor`):

```
/rigor the list scrolls by a few pixels every 750ms even when idle. Reproduce it first, then fix and verify.
```

```
/rigor I'm going to bed. Land the stack even if CI flakes; I want everything merged by morning.
```

Every "done" is backed by a command run in the session. The agent never weakens a test to make it pass; it changes a test only where your request changes the behavior the test checks and names each one, and it reports a test that contradicts your request as blocked instead of forcing it green. It deletes a test only when your request removes the behavior it checks or another test already catches everything it catches, and never deletes a failing one.

`rigor` matches the task to a playbook, copies the playbook's steps into a todo list, and calls the other skills when a step needs them. It stays on for the rest of the session: a hook adds a one-line reminder to every later turn, so a new task in the same session gets the same treatment. After compaction or a resume, the hook tells the model to re-read the rigor skill, since compaction drops the skill's text (Codex) or can cut it short (Claude Code). Start a message with "rigor off" to turn it off; that's recorded outside the conversation, so compaction can't undo it.

For long work, combine it with `/goal` (both hosts), which keeps the session going until a condition you can check holds:

```
/goal Use /rigor to migrate billing to the Period type. Done when python3 -m pytest exits 0 and no existing test is modified.
```

`/loop /rigor ...` does not work: `/loop` passes user-invoked skills through as plain text. `/goal` works because rigor's hook sees `/rigor` in the goal text and turns rigor on.

Like pstack, rigor runs only when you type it, and every other skill except `recall` is hidden from the model's skill list, so none of them fire on their own in unrelated work. `rigor` reads the ones its playbooks use; the rest (`/blast-radius`, `/reflect`, `/automate-me`, `/create-verification-skill`, `/maintain-verification-skill`, `/typescript-best-practices`) run only when you type them. `recall` can trigger on its own when you ask to catch up on your work.

The other skills can also be used on their own:

```
/how do we cancel runs? Is there an N+1 when we look up each run to cancel?
/interrogate review this PR
/why is this feature flag still off?
```

See [docs/guide](docs/guide/README.md) for a longer walkthrough.

## Playbooks

| Playbook | Use for |
|---|---|
| Investigation | Read-only questions: how does X work, why was Y built this way |
| Bug fix | Reproduce, find the root cause, fix, verify with runtime evidence |
| Perf issue | Trace a measured slowdown and improve it against a baseline |
| Hillclimb | Improve one metric toward a target, one measured commit at a time |
| Runtime forensics | Diagnose a live symptom (leak, idle CPU, glitch) from instrumentation |
| Trace forensics | Diagnose a captured profile or trace |
| Feature | New or changed behavior, built from a named data shape |
| Refactoring | Structure changes that preserve behavior |
| Prototype | A throwaway sketch to settle a design question |
| Visual parity | Pixel-exact match between two UI implementations |
| Authoring a skill | Writing or editing a `SKILL.md` |
| Eval | Measure how a skill or prompt change affects agent behavior |
| Test audit | Prune redundant or low-value tests, with evidence for each deletion |
| Babysit | Get a PR or stack to merge-ready: conflicts, review threads, CI |
| Shipping | Verify each PR in a green stack independently, then land it bottom-up |
| Autonomous run | Drive a long task to completion without stopping |
| Orchestrate | A multi-day project run by one coordinator session |
| Autopilot (full / stack) | A queue of changes taken to merged, or to a reviewed stack |
| Session pickup | Take over another session's in-flight work |
| Pause safely | Suspend work so it can be resumed cleanly |
| Multi-phase plan | Work that spans phases or stacked PRs |
| Worktree cleanup | Reclaim disk from merged worktrees and old simulators |
| Opening a PR | The last step of every other playbook |

## Skills

| Skill | Use it when |
|---|---|
| `rigor` | You're starting any nontrivial task. |
| `principles` | You want the engineering principles `rigor` applies (23 of them, one file each). |
| `how` | You want a walkthrough of how a subsystem works. |
| `why` | You want to know why something was built this way. Queries git history plus whatever MCP servers you have (issue tracker, docs, chat, error tracking, observability). |
| `recall` | You're resuming work and want your recent context rebuilt from your own session history. |
| `blast-radius` | You want to know what else a small-looking change could break. |
| `architect` | You're about to write code that crosses a function boundary and want the interface settled first. |
| `arena` | You want several independent attempts at the same thing, then the best parts combined. |
| `swarm` | You want parallel workers across independent slices and one aggregated report. |
| `interrogate` | You want several models to try to break a diff. |
| `reflect` | A long task landed and you want the lessons captured as skill edits. |
| `figure-it-out` | No playbook fits; design one for this task. |
| `show-me-your-work` | You want a reviewable decision log for long or autonomous work. |
| `tdd` | You're fixing a bug with a cheap local test path. |
| `deslop` | You want AI-generated clutter removed from the branch's diff. |
| `no-comments` | You want unnecessary comments stripped before review. |
| `unslop` | You're cleaning up prose. |
| `technical-writing` | You're writing docs, RFCs, READMEs, PR descriptions, or commit messages. |
| `typescript-best-practices` | You're writing TypeScript and type it by hand; it doesn't load on its own. |
| `control-ui` | You need to drive a browser or Electron UI to verify a change. |
| `control-cli` | You need to drive a CLI or TUI to verify a change. |
| `create-verification-skill` | Your project has no scripted way to prove app behavior. |
| `maintain-verification-skill` | Your project's verification skill has drifted from the app. |
| `automate-me` | You want your own `<name>-mode` skill drafted from how you've worked. |

## Subagents

- `rigor-agent` works on a step of a rigor playbook. It reads `rigor` before starting.
- `comment-reviewer` is a read-only reviewer that flags unnecessary comments. `no-comments` runs it.

## Repository layout

```
install.sh             Installs skills and agents for both hosts
skills/                Skills, shared by both hosts
agents/                Claude Code subagents
codex/agents/          Codex custom agents (same content as agents/)
scripts/check.py       Repo consistency checks
docs/guide/            Walkthrough
```

## Development

- `scripts/smoke.sh` runs every script the skills call (install, hooks, orch, watch-pr, log and audit helpers) in a throwaway directory, with no model calls. Run it before pushing.
- `python3 scripts/test_mode_hook.py` runs the stay-on hook through a session's life (on, reminders, compaction, off).
- `python3 scripts/check.py` checks skill frontmatter, links between skills, playbooks and principles, the principle index, the Claude Code and Codex agent files, and the README skills table all agree.
- Because the installed skills are symlinks into your clone, edits show up in the next session with no reinstall step. Rerun `install.sh` after adding or removing a skill or agent.

## License

MIT. Includes work from pstack (Lauren Tan), cursor-team-kit (Cursor), and OpenClaw's test-audit skill (OpenClaw Foundation), all MIT.
