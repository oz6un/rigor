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
        epilog="Exit codes: 0 completed, 1 CLI/output failure, 2 usage, 3 missing CLI, 4 denied or incomplete run.")
    parser.add_argument("--cli", choices=("codex", "claude"), help="explicit target CLI")
    parser.add_argument("--write", action="store_true", help="allow edits; use a separate worktree")
    parser.add_argument("--cd", type=Path, default=Path.cwd(), help="working directory")
    parser.add_argument("--trace", type=Path, help="create a private JSONL event trace; never overwrite")
    parser.add_argument("--claude-allow-tool", action="append", default=[], metavar="RULE",
                        help="Claude permission rule, repeatable; requires --write; ignored for Codex")
    args = parser.parse_args()
    if args.cli is None:
        claude = bool(os.environ.get("CLAUDECODE"))
        codex = bool(os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_SESSION_ID"))
        if claude == codex:
            parser.error("ambiguous or unknown host; pass --cli codex or --cli claude")
        args.cli = "codex" if claude else "claude"
    if args.claude_allow_tool and not args.write:
        parser.error("--claude-allow-tool requires --write")
    if any(not rule.strip() for rule in args.claude_allow_tool):
        parser.error("--claude-allow-tool requires a nonempty rule")
    if not args.cd.is_dir():
        parser.error(f"working directory does not exist: {args.cd}")
    if sys.stdin.isatty():
        parser.error("pipe the prompt on stdin")
    return args


def completion(cli, trace, answer):
    result = None
    completed = False
    failed = False
    with trace.open() as events:
        for line in events:
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("expected JSON event objects")
            if cli == "claude" and event.get("type") == "result":
                result = event
            if cli == "codex":
                completed |= event.get("type") == "turn.completed"
                failed |= event.get("type") in ("turn.failed", "error")
    if cli == "codex":
        if failed:
            return 1, "Codex reported a failed run"
        if not completed:
            return 4, "Codex did not report completion"
        text = answer.read_text() if answer.exists() else ""
    else:
        if result is None:
            return 4, "Claude did not report completion"
        denials = result.get("permission_denials", [])
        if not isinstance(denials, list):
            raise ValueError("invalid Claude permission_denials")
        if denials:
            names = sorted({str(denial.get("tool_name", "unknown")) for denial in denials if isinstance(denial, dict)})
            return 4, f"Claude denied tools ({', '.join(names)}); required work may be incomplete"
        if result.get("is_error") is not False or result.get("subtype") != "success":
            return 1, "Claude reported a failed run"
        text = result.get("result")
    if not isinstance(text, str) or not text.strip():
        return 4, f"{cli} returned no final answer"
    return 0, text.rstrip() + "\n"


def run(args):
    executable = shutil.which(args.cli)
    if executable is None:
        return 3, f"{args.cli} not installed; run this seat as a host subagent instead and say so in your report"
    prompt = sys.stdin.read()
    with tempfile.TemporaryDirectory(prefix="rigor-opinion-") as scratch:
        answer = Path(scratch) / "answer.txt"
        trace = args.trace if args.trace is not None else Path(scratch) / "events.jsonl"
        log = Path(scratch) / "stderr.txt"
        if args.cli == "codex":
            command = [executable, "exec", "-s", "workspace-write" if args.write else "read-only",
                       "-C", str(args.cd.resolve()), "--skip-git-repo-check", "--ephemeral", "--json", "-o", str(answer)]
            model = os.environ.get("RIGOR_CODEX_MODEL")
            if model:
                command += ["-m", model]
            command += ["-"]
        else:
            command = [executable, "-p", "--permission-mode", "acceptEdits" if args.write else "plan",
                       "--no-session-persistence", "--output-format", "stream-json", "--verbose"]
            model = os.environ.get("RIGOR_CLAUDE_MODEL")
            if model:
                command += ["--model", model]
            if args.claude_allow_tool:
                command += ["--allowedTools", *args.claude_allow_tool]
        fd = os.open(trace, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as events, log.open("w") as errors:
            child = subprocess.run(command, input=prompt, text=True, cwd=args.cd,
                                   env={**os.environ, "RIGOR_NESTED": "1"}, stdout=events, stderr=errors)
        if child.returncode != 0:
            return 1, f"{args.cli} exited {child.returncode}: {log.read_text().strip()}"
        return completion(args.cli, trace, answer)


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
