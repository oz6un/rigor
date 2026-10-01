#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import shutil
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
        if args.write and writable_by_candidate(args.trace, args.cd):
            parser.error("with --write, --trace must be outside --cd, /tmp and $TMPDIR, where the candidate can write")
    return args


def writable_by_candidate(trace, cd):
    # By default a write candidate can write --cd, /tmp and $TMPDIR. A trace there, or reached
    # through a folder there, could be rewritten before anyone reads it. Folders are compared by
    # identity, since one folder has several spellings (letter case, symlinks, macOS firmlinks).
    roots = [os.stat(p) for p in (cd, "/tmp", os.environ.get("TMPDIR") or "/tmp") if os.path.isdir(p)]
    folders = [*trace.parents, *trace.resolve().parents]
    return any(os.path.samestat(os.stat(folder), root) for folder in folders for root in roots)


def completion(cli, events):
    result = None
    terminal = None
    problem = ""
    text = ""
    for line in events:
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError("expected JSON event objects")
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
    # The verdict and answer are read from the child's output pipe, and the prompt and its error
    # output go through unnamed files, so nothing a candidate writes to disk changes the report.
    with tempfile.TemporaryDirectory(prefix="rc-", dir="/tmp") as child_tmp, \
            tempfile.TemporaryFile() as stdin, tempfile.TemporaryFile() as stderr:
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
            instructions = [p.read_text() for p in (args.cd / "CLAUDE.md", args.cd / ".claude" / "CLAUDE.md") if p.is_file()]
            if instructions:
                command += ["--append-system-prompt", "\n".join(instructions)]
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
        trace = os.fdopen(os.open(args.trace, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") if args.trace else None
        child = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE, stderr=stderr, cwd=args.cd, env=env)
        events = lines(child.stdout, trace)
        try:
            status, message = completion(args.cli, events)
        except json.JSONDecodeError as error:
            status, message = 1, f"invalid event JSON: {error}\n{error.doc[:2000]}"
        except ValueError as error:
            status, message = 1, str(error)
        for _ in events:  # keep reading so the child never blocks on a full pipe
            pass
        child.wait()
        if trace:
            trace.close()
        if child.returncode != 0:
            stderr.seek(0)
            detail = message if status else f"Partial answer: {message.strip()}"
            return 1, "\n".join(part for part in (
                f"{args.cli} exited {child.returncode}", detail, stderr.read().decode(errors="replace").strip()) if part)
        return status, message


def lines(stream, trace):
    # Split on "\n" only: JSON strings may hold other line separators. Each line reaches the trace
    # as it arrives, so a killed run keeps what it already received.
    for line in stream:
        if trace:
            trace.write(line)
            trace.flush()
        yield line.decode(errors="replace")


def main():
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
