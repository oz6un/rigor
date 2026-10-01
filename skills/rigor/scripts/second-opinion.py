#!/usr/bin/env python3
import argparse
import contextlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile


def parse_args():
    parser = argparse.ArgumentParser(
        prog="second-opinion",
        description="Run a stdin prompt through the other CLI; print its final answer.",
        epilog="RIGOR_CODEX_MODEL and RIGOR_CLAUDE_MODEL pick the model. Exit codes: 0 completed, "
               "1 CLI/output failure, 2 usage, 3 missing CLI, 4 incomplete run (no completion reported, or no answer).")
    parser.add_argument("--cli", choices=("codex", "claude"), help="explicit target CLI")
    parser.add_argument("--write", action="store_true", help="allow edits and sandboxed commands; use a separate worktree")
    parser.add_argument("--cd", type=Path, default=Path.cwd(), help="working directory")
    parser.add_argument("--trace", type=Path, help="create a private JSONL event trace; never overwrite")
    args = parser.parse_args()
    if args.cli is None:
        claude = bool(os.environ.get("CLAUDECODE"))
        codex = bool(os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_SESSION_ID"))
        if claude == codex:
            parser.error("ambiguous or unknown host; pass --cli codex or --cli claude")
        args.cli = "codex" if claude else "claude"
    if not args.cd.is_dir():
        parser.error(f"working directory does not exist: {args.cd}")
    if sys.stdin.isatty():
        parser.error("pipe the prompt on stdin")
    if args.trace is not None:
        args.trace = args.trace.absolute()
        if os.path.lexists(args.trace):
            parser.error(f"trace already exists, never overwritten: {args.trace}")
        if not args.trace.parent.is_dir():
            parser.error(f"trace folder does not exist: {args.trace.parent}")
        if args.write:
            # A symlink on the way could be re-pointed by the candidate, redirecting later readers.
            real = args.trace.parent.resolve()
            if args.trace.parent != real:
                parser.error(f"with --write, give --trace as a real path, without symlinks or '..': {real}")
            if writable_by_candidate(real, args.cd):
                parser.error("with --write, --trace must be outside --cd, /tmp and $TMPDIR, where the candidate can write")
    return args


def writable_by_candidate(folder, cd):
    # By default a write candidate can write --cd, /tmp and $TMPDIR, and could rewrite a trace
    # there before anyone reads it. Folders are compared by identity, since one folder has several
    # spellings (letter case, macOS firmlinks).
    roots = [os.stat(p) for p in (cd, "/tmp", os.environ.get("TMPDIR") or "/tmp") if os.path.isdir(p)]
    return any(os.path.samestat(os.stat(f), root) for f in (folder, *folder.parents) for root in roots)


def completion(cli, events):
    result = None
    terminal = None
    problem = ""
    text = ""
    invalid = ""
    for line in events:  # read to the end even after a bad line, so the child never blocks on the pipe
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            invalid = invalid or f"invalid event JSON: {error}\n{line[:2000]}"
            continue
        if not isinstance(event, dict):
            invalid = invalid or "expected JSON event objects"
            continue
        if cli == "claude" and event.get("type") == "result":
            result = event
        if cli == "codex":
            item = event.get("item")
            if event.get("type") == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
                text = item.get("text")
            if event.get("type") in ("turn.completed", "turn.failed"):
                terminal = event["type"]
            if event.get("type") == "turn.failed":
                error = event.get("error")
                problem = str(error.get("message", "")) if isinstance(error, dict) else str(error)
            elif event.get("type") == "error":
                problem = str(event.get("message", ""))
    if invalid:
        return 1, invalid
    if cli == "codex":
        if terminal == "turn.failed":
            return 1, f"Codex reported a failed run: {problem}"
        if terminal != "turn.completed":
            return 4, "Codex did not report completion" + (f": {problem}" if problem else "")
    else:
        if result is None:
            return 4, "Claude did not report completion"
        if result.get("is_error") is not False or result.get("subtype") != "success":
            errors = result.get("errors") or result.get("result") or ""
            detail = "; ".join(map(str, errors)) if isinstance(errors, list) else str(errors)
            return 1, "Claude reported a failed run" + (f": {detail}" if detail else "")
        text = result.get("result")
    if not isinstance(text, str) or not text.strip():
        return 4, f"{cli} returned no final answer"
    return 0, text.rstrip() + "\n"


def run(args):
    executable = shutil.which(args.cli)
    if executable is None:
        return 3, f"{args.cli} not installed; run this seat as a host subagent instead and say so in your report"
    prompt = sys.stdin.read()
    # The verdict and answer are read from the child's output pipe, and everything else passes
    # through unnamed files, so nothing a candidate writes to disk changes the report.
    with tempfile.TemporaryDirectory(prefix="rc-", dir="/tmp") as child_tmp, tempfile.TemporaryFile() as stdin, \
            tempfile.TemporaryFile() as stderr, tempfile.TemporaryFile() as instructions:
        env = {**os.environ, "RIGOR_NESTED": "1"}
        if args.cli == "codex":
            command = [executable, "exec", "-s", "workspace-write" if args.write else "read-only",
                       "-C", str(args.cd.resolve()), "--skip-git-repo-check", "--ephemeral", "--json"]
            model = os.environ.get("RIGOR_CODEX_MODEL")
            if model:
                command += ["-m", model]
            command += ["-"]
        else:
            # Only the user's own settings load (the checked-out repo's settings and hooks would run
            # with the user's privileges), with no hooks, MCP servers or memory writes. The repo's
            # CLAUDE.md, dropped with its settings, comes back as plain text.
            settings = {"disableAllHooks": True, "autoMemoryEnabled": False}
            command = [executable, "-p", "--permission-mode", "acceptEdits" if args.write else "plan",
                       "--no-session-persistence", "--output-format", "stream-json", "--verbose",
                       "--setting-sources", "user", "--strict-mcp-config"]
            text = "\n".join(p.read_text() for p in (args.cd / "CLAUDE.md", args.cd / ".claude" / "CLAUDE.md") if p.is_file())
            if text:
                instructions.write(text.encode())
                instructions.seek(0)
                command += ["--append-system-prompt-file", f"/dev/fd/{instructions.fileno()}"]
            model = os.environ.get("RIGOR_CLAUDE_MODEL")
            if model:
                command += ["--model", model]
            if args.write:
                # Like Codex's workspace-write: commands run without approval, but only in Claude's
                # sandbox (no network), and the run fails if the sandbox can't start.
                command += ["--tools", "Bash,Read,Edit,Write,Glob,Grep,Agent,TodoWrite"]
                settings["sandbox"] = {"enabled": True, "autoAllowBashIfSandboxed": True,
                                       "failIfUnavailable": True, "allowUnsandboxedCommands": False}
                # Claude's sandbox can write its temp root, shared by every session; give it its own.
                # Keep the path short: Claude puts sockets in it, and past macOS's ~104-byte socket
                # path limit it silently falls back to the shared root.
                env["CLAUDE_CODE_TMPDIR"] = child_tmp
            command += ["--settings", json.dumps(settings)]
        stdin.write(prompt.encode())
        stdin.seek(0)
        trace = open(args.trace, "xb", opener=lambda path, flags: os.open(path, flags, 0o600)) if args.trace else None
        child = None
        try:
            child = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE, stderr=stderr, cwd=args.cd,
                                     env=env, pass_fds=(instructions.fileno(),))
            status, message = completion(args.cli, lines(child.stdout, trace))
            child.wait()
            if trace:
                trace.close()
        except BaseException:
            if child and child.poll() is None:
                stop(child)
            if trace:
                with contextlib.suppress(OSError):  # the error being raised already covers it
                    trace.close()
            raise
        if child.returncode != 0:
            stderr.seek(0)
            detail = message if status else f"Partial answer: {message.strip()}"
            return 1, "\n".join(part for part in (
                f"{args.cli} exited {child.returncode}", detail, stderr.read().decode(errors="replace").strip()) if part)
        return status, message


def stop(child):
    # TERM lets the CLI stop its own tools (Claude does; Codex leaves the commands it started
    # running), then KILL if it hasn't exited. A second Ctrl-C or TERM mustn't cut this short.
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    child.terminate()
    with contextlib.suppress(subprocess.TimeoutExpired):
        child.wait(timeout=5)
    child.kill()
    child.wait()


def lines(stream, trace):
    # Split on "\n" only: JSON strings may hold other line separators. Each line reaches the trace
    # as it arrives; a failed write stops the run.
    for line in stream:
        if trace:
            try:
                trace.write(line)
                trace.flush()
            except OSError as error:
                raise OSError(f"trace write failed: {error}") from error
        yield line.decode(errors="replace")


def main():
    # On SIGTERM, unwind like Ctrl-C: stop the child CLI and remove temp files.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    args = parse_args()
    try:
        status, message = run(args)
    except (OSError, ValueError) as error:
        status, message = 1, str(error)
    if status:
        print(f"second-opinion: {message}", file=sys.stderr)
        if args.trace is not None and args.trace.is_file():
            print(f"second-opinion: trace: {args.trace}", file=sys.stderr)
    else:
        print(message, end="")
    return status


if __name__ == "__main__":
    sys.exit(main())
