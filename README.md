# mstack

Skills for doing careful engineering work with coding agents in Claude Code and Codex. The goal is less code of higher quality: reproduce before fixing, settle the design before writing it, verify on the real artifact, and review with more than one model.

mstack is a port of [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, originally built for Cursor. The workflows and principles come from pstack. The port removes the Cursor-specific machinery, adapts subagents and model routing to Claude Code and Codex, and rewrites the prose in a plainer voice.

## Install

### Claude Code

```
/plugin marketplace add oz6un/mstack
/plugin install mstack@mstack
```

### Codex

```bash
codex plugin marketplace add oz6un/mstack
codex plugin add mstack@mstack
./codex/install-agents.sh          # installs rigor-agent and comment-reviewer into ~/.codex/agents
```

Codex plugins don't ship custom agents, so the last step copies them into `~/.codex/agents/`. Use `--project <dir>` to install them into a single project's `.codex/agents/` instead. Run it from a clone of this repo.

### Cross-model review (optional)

Skills that run review panels (`interrogate`, `arena`, `architect`, `reflect`, and others) get a second opinion from the other CLI: Claude Code calls `codex exec`, and Codex calls `claude -p`. Install and log in to both CLIs to get this. If the other CLI is missing, the panels run with the host's own subagents and say so in the report.

To pick the model used for second opinions, set `MSTACK_CODEX_MODEL` or `MSTACK_CLAUDE_MODEL`.

## Usage

Start a task with `/rigor` (Codex: `$rigor`):

```
/rigor the list scrolls by a few pixels every 750ms even when idle. Reproduce it first, then fix and verify.
```

```
/rigor I'm going to bed. Land the stack even if CI flakes; I want everything merged by morning.
```

`rigor` matches the task to a playbook, copies the playbook's steps into a todo list, and calls the other skills when a step needs them. It stays on for the rest of the session, and you can turn it off by saying so.

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
| `teach` | You want to understand a change or subsystem, built up step by step. |
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
| `bro` | You want the last message restated in plain language. |
| `typescript-best-practices` | You're reading or writing TypeScript. |
| `control-ui` | You need to drive a browser or Electron UI to verify a change. |
| `control-cli` | You need to drive a CLI or TUI to verify a change. |
| `create-verification-skill` | Your project has no scripted way to prove app behavior. |
| `maintain-verification-skill` | Your project's verification skill has drifted from the app. |
| `automate-me` | You want your own `<name>-mode` skill drafted from how you've worked. |

## Subagents

- `rigor-agent` works on a step of a rigor playbook. It reads `rigor` (which includes the principle index) before starting.
- `comment-reviewer` is a read-only reviewer that flags unnecessary comments. `no-comments` runs it.

## Repository layout

```
.claude-plugin/        Claude Code plugin manifest and marketplace
.agents/plugins/       Codex marketplace
plugin.json            Portable plugin manifest (Codex)
skills/                Skills, shared by both hosts
agents/                Claude Code subagents
codex/agents/          Codex custom agents, plus install-agents.sh
docs/guide/            Walkthrough
```

## Development

- `python3 scripts/check.py` checks skill frontmatter, links between skills, playbooks and principles, that the two principle indexes, the Claude Code and Codex agent files, the README skills table, and the manifest versions all agree.
- `scripts/reinstall.sh` runs the check, bumps the patch version, and refreshes the installed plugin in each host whose `mstack` marketplace was added from this clone (`claude plugin marketplace add <path>`, `codex plugin marketplace add <path>`). Both hosts cache the plugin by version, so edits don't show up until the version changes. Hosts installed from GitHub pick up changes after you push and update the marketplace.

## License

MIT. Includes work from pstack (Lauren Tan) and cursor-team-kit (Cursor), both MIT.
