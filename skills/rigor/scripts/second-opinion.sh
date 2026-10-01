#!/usr/bin/env python3
import argparse
import contextlib
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
        epilog="RIGOR_CODEX_MODEL and RIGOR_CLAUDE_MODEL pick the model. Read-only Claude runs in plan mode "
               "and may use web lookup tools. Exit codes: 0 completed, 1 CLI/output failure, 2 usage, "
               "3 missing CLI, 4 incomplete run (no completion reported, or no answer).")
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
        if args.trace.exists():
            parser.error(f"trace already exists, never overwritten: {args.trace}")
        if args.write and args.trace.resolve().is_relative_to(args.cd.resolve()):
            parser.error("with --write, --trace must be outside --cd, where the target can't rewrite it")
    return args


def completion(cli, events, answer):
    result = None
    terminal = None
    problem = ""
    for line in events.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError("expected JSON event objects")
        if cli == "claude" and event.get("type") == "result":
            result = event
        if cli == "codex":
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
        text = answer.read_text() if answer.exists() else ""
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
    # Files a CLI must write for us (Codex's answer, Claude's instructions) live under the home
    # folder, which neither CLI's sandbox can write, so a candidate can't rewrite what gets reported.
    home_tmp = Path.home() / ".rigor" / "tmp"
    home_tmp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opinion-", dir=home_tmp) as scratch, contextlib.ExitStack() as cleanup:
        env = {**os.environ, "RIGOR_NESTED": "1"}
        answer = Path(scratch) / "answer.txt"
        if args.cli == "codex":
            command = [executable, "exec", "-s", "workspace-write" if args.write else "read-only",
                       "-C", str(args.cd.resolve()), "--skip-git-repo-check", "--ephemeral", "--json", "-o", str(answer)]
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
                # An absolute path: Claude starts inside --cd, so a relative one would resolve twice.
                (Path(scratch) / "CLAUDE.md").write_text("\n".join(instructions))
                command += ["--append-system-prompt-file", str((Path(scratch) / "CLAUDE.md").resolve())]
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
                env["CLAUDE_CODE_TMPDIR"] = cleanup.enter_context(tempfile.TemporaryDirectory(prefix="rc-", dir="/tmp"))
            command += ["--settings", json.dumps(settings)]
        trace = os.fdopen(os.open(args.trace, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") if args.trace else None
        child = subprocess.run(command, input=prompt, text=True, cwd=args.cd, env=env, capture_output=True)
        if trace:
            with trace:
                trace.write(child.stdout)
        try:
            status, message = completion(args.cli, child.stdout, answer)
        except json.JSONDecodeError as error:
            status, message = 1, f"invalid event JSON: {error}\n{error.doc[:2000]}"
        except (OSError, ValueError) as error:
            status, message = 1, str(error)
        if child.returncode != 0:
            detail = message if status else f"Partial answer: {message.strip()}"
            return 1, "\n".join(part for part in (
                f"{args.cli} exited {child.returncode}", detail, child.stderr.strip()) if part)
        return status, message


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
