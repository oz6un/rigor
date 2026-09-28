---
name: control-cli
description: Build or reuse a local harness to drive, inspect, and profile an interactive CLI or TUI. Use for CLI UX checks, reproducing terminal bugs, startup regressions, memory leaks, hangs, prompt flows, or terminal demos.
disable-model-invocation: true
---

# Control CLI

Exercise an interactive CLI through a repeatable harness instead of by hand. Reuse the repo's own test or demo harness if it has one; otherwise assemble a temporary one from standard local tools.

Use it for:

- Reproducing CLI and TUI bugs with deterministic input.
- Verifying keyboard flows, prompts, interrupts, resize behavior, and terminal layout.
- Capturing before and after transcripts for a fix.
- Profiling startup time, slow operations, hangs, or memory growth.
- Recording a short terminal demo when showing is clearer than explaining.

Your shell tool can't answer interactive prompts or read a full-screen TUI directly, so anything that needs a TTY goes through tmux or a PTY script.

## Harness loop

1. Identify the command under test and the smallest workspace that reproduces the behavior.
2. Look for existing harnesses: package scripts, e2e tests, demo recorders, expect scripts, PTY helpers. They already know the app's startup, env, and prompts.
3. If there's none, launch the CLI in an isolated terminal session with deterministic env vars (fixed `TERM`, locale, size, and a temp `HOME` or config dir if the CLI writes state).
4. Capture the screen before interacting.
5. Send one action at a time: text, Enter, arrows, Escape, Ctrl-C, resize.
6. Wait for a specific screen pattern or prompt before the next action.
7. Save the transcript and any profile artifacts.
8. End the session cleanly.

## Harness options

- **Repo-native harness**: preferred when it exists.
- **tmux**: named sessions, `capture-pane`, `send-keys`, resize.
- **PTY script**: a short Python, Node, or expect script when tmux isn't available or you need exact waits.
- **Runtime inspector**: the Node or Bun inspector for CPU profiles, heap snapshots, and live evaluation.
- **Terminal recorder**: the repo's demo tooling or an asciinema-compatible recorder when the user asks for a demo.

## Minimal tmux harness

```bash
SESSION="cli-harness-$(date +%s)"
tmux new-session -d -s "$SESSION" -x 120 -y 40 -- <command-under-test>
tmux capture-pane -pt "$SESSION"
tmux send-keys -t "$SESSION" "help" Enter
until tmux capture-pane -pt "$SESSION" | grep -q "<expected text>"; do sleep 0.2; done
tmux capture-pane -pt "$SESSION"
tmux kill-session -t "$SESSION"
```

Bound the `until` loop with a timeout in real use so a missing prompt fails instead of hanging.

For a Node CLI that needs profiling, start it with the inspector on a random port:

```bash
NODE_OPTIONS="--inspect=127.0.0.1:0" tmux new-session -d -s "$SESSION" -- <node-cli-command>
```

Read the inspector URL from the pane output, then attach DevTools-compatible tooling.

## Minimal PTY harness

Use this when you need deterministic waits and tmux isn't available. Keep it temporary unless the user asks for a reusable test.

```python
import os
import pty
import select
import subprocess
import time

master_fd, slave_fd = pty.openpty()
proc = subprocess.Popen(
    ["<command>", "<arg>"],
    stdin=slave_fd,
    stdout=slave_fd,
    stderr=slave_fd,
    close_fds=True,
)
os.close(slave_fd)

deadline = time.time() + 30
buffer = b""
while time.time() < deadline:
    ready, _, _ = select.select([master_fd], [], [], 0.25)
    if not ready:
        continue
    chunk = os.read(master_fd, 4096)
    buffer += chunk
    if b"<ready text>" in buffer:
        os.write(master_fd, b"help\n")
        break

print(buffer.decode(errors="replace"))
proc.terminate()
os.close(master_fd)
```

For richer terminal control, use `pty.fork()` or an existing PTY library (`node-pty`, `pexpect`).

## Profiling recipes

- **Startup regression**: time baseline and changed builds on the same machine, env, and command, several runs each.
- **Slow operation**: start a CPU profile, perform the operation, stop the profile, and compare the top self-time functions.
- **Memory leak**: force GC if available, take a heap snapshot, repeat the operation many times, force GC again, take another snapshot, and compare retained objects.
- **Hang**: capture the screen, active handles and resources, and a stack or CPU sample before interrupting.

## Guardrails

- Wait for a specific output instead of sleeping. If a fixed sleep is unavoidable, say why.
- Don't type credentials or destructive commands into a controlled session.
- Keep the harness in a temp directory unless the repo already has a testing or demo harness.
- Adapt commands to this repo's scripts and runtime; don't copy paths from another project.
- Clean up tmux sessions, temp dirs, inspector processes, and demo artifacts unless the user asks to keep them.
