import json
import os
import resource
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parent.parent / "skills/rigor/scripts/second-opinion.sh"
FAKE = r'''
import json, os, pathlib, sys
args = sys.argv[1:]
cli = pathlib.Path(sys.argv[0]).name
pathlib.Path(os.environ["RECORD"]).write_text(json.dumps({
    "cli": cli, "args": args, "cwd": os.getcwd(), "prompt": sys.stdin.read(),
    "nested": os.environ.get("RIGOR_NESTED"), "tmpdir": os.environ.get("CLAUDE_CODE_TMPDIR"), "pid": os.getpid(),
    "appended": (pathlib.Path(args[args.index("--append-system-prompt-file") + 1]).read_text()
                 if "--append-system-prompt-file" in args else None)}))
mode = os.environ.get("RESPONSE", "success")
if cli == "codex":
    events = [{"type": "item.completed", "item": {"type": "agent_message", "text": "checking"}},
              {"type": "item.completed", "item": {"type": "command_execution", "command": "python3 check.py", "exit_code": 0}},
              {"type": "item.completed", "item": {"type": "agent_message", "text": "review complete"}},
              {"type": "turn.completed", "usage": {}}]
    if mode == "no_answer": events = [e for e in events if e.get("item", {}).get("type") != "agent_message"]
    if mode == "error": events[-1] = {"type": "turn.failed", "error": {"message": "provider failed"}}
    if mode == "recovered": events.insert(0, {"type": "error", "message": "Reconnecting..."})
else:
    events = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "README.md"}}]}},
              {"type": "result", "subtype": "success", "is_error": False, "result": "review complete", "permission_denials": []}]
    if mode == "denied": events[-1]["permission_denials"] = [{"tool_name": "Bash", "tool_input": {"command": "python3 check.py"}}]
    if mode == "error": events[-1].update(is_error=True, subtype="error_during_execution")
if mode == "stdout_failure":
    events[-1] = ({"type": "turn.failed", "error": {"message": "provider stdout failure"}} if cli == "codex"
                  else {"type": "result", "subtype": "error_during_execution", "is_error": True, "errors": ["provider stdout failure"]})
if mode == "missing": events.pop()
if mode == "separators":  # valid JSON may carry these unescaped
    events[-1]["result"] = "line\u2028one\x85two"
    for event in events: print(json.dumps(event, ensure_ascii=False))
    sys.exit(0)
if mode == "flood":  # a bad line, then more than a pipe buffer holds
    print("not json")
    for _ in range(5000): print(json.dumps(events[0]))
if mode == "long":
    for _ in range(5000): print(json.dumps(events[0]))
    for event in events: print(json.dumps(event))
    sys.exit(0)
if mode == "big_last":  # the line that crosses a write limit is the last one
    events[-1]["result"] = "x" * 2000
    for event in events: print(json.dumps(event))
    sys.exit(0)
if mode == "slow":  # a tool process that ignores SIGTERM, then a long wait
    import subprocess, time
    tool = subprocess.Popen([sys.executable, "-c", "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)"])
    pathlib.Path(os.environ["RECORD"] + ".tool").write_text(str(tool.pid))
    print(json.dumps(events[0]), flush=True)
    time.sleep(30)
if mode == "malformed_failure":
    print("Error: not logged in")
    print("auth token expired", file=sys.stderr)
    sys.exit(9)
if mode == "malformed":
    print("not json")
else:
    for event in events: print(json.dumps(event))
if mode == "nonzero":
    print("provider unavailable", file=sys.stderr)
    sys.exit(9)
if mode == "stdout_failure": sys.exit(9)
'''


class SecondOpinionTests(unittest.TestCase):
    def setUp(self):
        # A write candidate can write /tmp and $TMPDIR, so traces the runner should accept live
        # elsewhere; on Linux the default temp folder is /tmp. TMPDIR is inherited unless a test sets it.
        self.scratch = tempfile.TemporaryDirectory(dir="/var/tmp")
        self.addCleanup(self.scratch.cleanup)
        self.base = Path(self.scratch.name).resolve()  # macOS's /var is a symlink to /private/var
        self.bin = self.base / "bin"
        self.bin.mkdir()
        for name, target in (("python3", sys.executable), ("bash", shutil.which("bash")), ("dirname", shutil.which("dirname"))):
            (self.bin / name).symlink_to(target)
        for cli in ("claude", "codex"):
            executable = self.bin / cli
            executable.write_text(f"#!{sys.executable}\n" + FAKE)
            executable.chmod(0o755)
        self.record = self.base / "record.json"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("CODEX_", "RIGOR_")) and k != "CLAUDECODE"}
        self.env.update(PATH=str(self.bin),
                        HOME=str(self.base), RECORD=str(self.record),
                        CODEX_THREAD_ID="host")
        (self.base / "tmpdir").mkdir()

    def run_cli(self, *args, **env):
        return subprocess.run([str(SCRIPT), *args], input="review this\n", text=True,
                              capture_output=True, env={**self.env, **env})

    def test_success_prints_only_answer_for_each_cli(self):
        (self.base / "CLAUDE.md").write_text("Run tests with make check.\n")
        for cli in ("claude", "codex"):
            with self.subTest(cli=cli):
                result = self.run_cli("--cli", cli, "--cd", str(self.base))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "review complete\n")
                recorded = json.loads(self.record.read_text())
                self.assertEqual(recorded["prompt"], "review this\n")
                self.assertEqual(recorded["nested"], "1")
                if cli == "claude":
                    # A read-only review stays in plan mode, with no auto-run sandbox, and loads only
                    # the user's own settings: the reviewed repo's hooks never run, and no MCP servers.
                    args = recorded["args"]
                    self.assertEqual(args[args.index("--permission-mode") + 1], "plan")
                    self.assertEqual(args[args.index("--setting-sources") + 1], "user")
                    self.assertIn("--strict-mcp-config", args)
                    # No hooks (the user's and plugins' run unsandboxed) and no memory writes; no sandbox.
                    settings = json.loads(args[args.index("--settings") + 1])
                    self.assertEqual(settings, {"disableAllHooks": True, "autoMemoryEnabled": False})
                    self.assertIsNone(recorded["tmpdir"])
                    # The repo's CLAUDE.md, which --setting-sources user drops, comes back as text.
                    self.assertEqual(recorded["appended"], "Run tests with make check.\n")
                    self.assertEqual(Path(recorded["cwd"]).resolve(), self.base.resolve())

    def test_a_denied_tool_still_returns_the_answer(self):
        # The answer says what the CLI couldn't run; the caller reads it and verifies the work.
        result = self.run_cli("--write", RESPONSE="denied")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "review complete\n")

    def test_recovered_codex_error_does_not_override_completion(self):
        result = self.run_cli("--cli", "codex", RESPONSE="recovered")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "review complete\n")

    def test_provider_stdout_errors_remain_visible_without_a_trace(self):
        for cli in ("claude", "codex"):
            with self.subTest(cli=cli):
                result = self.run_cli("--cli", cli, RESPONSE="stdout_failure")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("provider stdout failure", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_malformed_failed_output_preserves_exit_and_both_diagnostics(self):
        for cli in ("claude", "codex"):
            with self.subTest(cli=cli):
                result = self.run_cli("--cli", cli, RESPONSE="malformed_failure")
                self.assertEqual(result.returncode, 1)
                self.assertIn("exited 9", result.stderr)
                self.assertIn("auth token expired", result.stderr)
                self.assertIn("not logged in", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_invalid_or_failed_completion_is_not_success(self):
        for cli in ("claude", "codex"):
            for response in ("error", "missing", "malformed", "nonzero"):
                with self.subTest(cli=cli, response=response):
                    result = self.run_cli("--cli", cli, RESPONSE=response)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("second-opinion:", result.stderr)

    def test_trace_keeps_tool_events(self):
        for cli, response, status in (("claude", "success", 0), ("claude", "denied", 0), ("codex", "success", 0)):
            with self.subTest(cli=cli, response=response):
                trace = self.base / f"{cli}-{response}.jsonl"
                result = self.run_cli("--cli", cli, "--trace", str(trace), RESPONSE=response)
                self.assertEqual(result.returncode, status, result.stderr)
                events = [json.loads(line) for line in trace.read_text().splitlines()]
                self.assertEqual(len(events), 2 if cli == "claude" else 4)  # every event the fake printed
                if cli == "claude":
                    self.assertEqual(events[0]["message"]["content"][0]["name"], "Read")
                    self.assertEqual(events[-1]["type"], "result")
                else:
                    self.assertEqual(events[1]["item"]["command"], "python3 check.py")
                self.assertEqual(trace.stat().st_mode & 0o777, 0o600)

    def test_existing_trace_is_never_overwritten(self):
        trace = self.base / "existing.jsonl"
        trace.write_text("previous evidence\n")
        result = self.run_cli("--trace", str(trace))
        self.assertEqual(result.returncode, 2, result.stderr)  # a usage mistake: nothing ran
        self.assertEqual(trace.read_text(), "previous evidence\n")
        self.assertFalse(self.record.exists())
        dangling = self.base / "dangling.jsonl"
        dangling.symlink_to(self.base / "missing")
        self.assertEqual(self.run_cli("--trace", str(dangling)).returncode, 2)
        self.assertEqual(self.run_cli("--trace", str(self.base / "missing" / "run.jsonl")).returncode, 2)

    def test_write_mode_keeps_the_trace_where_the_candidate_cant_write(self):
        work, tmpdir, safe = self.base / "work", self.base / "tmpdir", self.base / "safe"
        work.mkdir(); safe.mkdir()
        in_tmp = Path(tempfile.mkdtemp(dir="/tmp")).resolve()  # the real path, so only the /tmp rule applies
        self.addCleanup(shutil.rmtree, in_tmp)
        # Symlinks are refused outright: one the candidate can re-point, even mid-chain, would
        # redirect whoever reads the trace later.
        (work / "link").symlink_to(safe)
        (safe / "into-tmp").symlink_to(in_tmp)
        (safe / "entry").symlink_to(work / "link")
        refused = [work / "run.jsonl", in_tmp / "run.jsonl", tmpdir / "run.jsonl",
                   work / "link" / "run.jsonl", safe / "into-tmp" / "run.jsonl", safe / "entry" / "run.jsonl"]
        if Path(str(work).swapcase()).is_dir():  # a case-insensitive file system
            refused.append(Path(str(work).swapcase()) / "run.jsonl")
        for trace in refused:
            with self.subTest(trace=trace):
                result = self.run_cli("--write", "--cd", str(work), "--trace", str(trace), TMPDIR=str(tmpdir))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(self.record.exists())
                self.assertFalse(trace.exists())
        result = self.run_cli("--write", "--cd", str(work), "--trace", str(work / ".." / "safe" / "run.jsonl"),
                              TMPDIR=str(tmpdir))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((safe / "run.jsonl").exists())

    def test_events_split_only_on_newlines(self):
        result = self.run_cli("--cli", "claude", RESPONSE="separators")
        self.assertEqual((result.returncode, result.stdout), (0, "line\u2028one\x85two\n"), result.stderr)

    def test_a_killed_run_keeps_its_events_and_stops_its_child_and_tools(self):
        trace = self.base / "killed.jsonl"
        runner = subprocess.Popen([str(SCRIPT), "--cli", "claude", "--write", "--trace", str(trace)], stdin=subprocess.PIPE,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=self.base / "tmpdir",
                                  env={**self.env, "RESPONSE": "slow"}, start_new_session=True)
        self.addCleanup(lambda: runner.poll() is None and os.killpg(runner.pid, signal.SIGKILL))
        runner.stdin.write(b"review this\n"); runner.stdin.close()
        for _ in range(100):
            if trace.exists() and trace.stat().st_size:
                break
            time.sleep(0.1)
        self.assertTrue(trace.stat().st_size)  # readable while the run is still going
        runner.terminate()
        self.assertEqual(runner.wait(timeout=15), 143)
        self.assertEqual(json.loads(trace.read_text())["type"], "assistant")
        recorded = json.loads(self.record.read_text())
        for pid in (recorded["pid"], int(Path(str(self.record) + ".tool").read_text())):
            with self.assertRaises(ProcessLookupError):  # the fake CLI and the tool it started
                os.kill(pid, 0)
        self.assertFalse(Path(recorded["tmpdir"]).exists())

    def test_a_bad_line_before_a_long_stream_fails_without_hanging(self):
        trace = self.base / "flood.jsonl"
        result = subprocess.run([str(SCRIPT), "--cli", "claude", "--trace", str(trace)], input="review this\n",
                                text=True, capture_output=True, env={**self.env, "RESPONSE": "flood"}, timeout=30)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("invalid event JSON", result.stderr)
        self.assertEqual(len(trace.read_text().splitlines()), 5003)

    def test_a_trace_that_cant_be_written_fails_the_run(self):
        for response, limit in (("long", 65536), ("big_last", 1500)):
            with self.subTest(response=response):
                def small_files():  # writes past the limit fail with EFBIG
                    resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
                    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
                trace = self.base / f"{response}.jsonl"
                result = subprocess.run([str(SCRIPT), "--cli", "claude", "--trace", str(trace)], input="review this\n",
                                        text=True, capture_output=True, env={**self.env, "RESPONSE": response},
                                        preexec_fn=small_files, timeout=30)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("trace write failed", result.stderr)

    def test_codex_answer_is_its_last_message_and_none_is_incomplete(self):
        result = self.run_cli("--cli", "codex")
        self.assertEqual((result.returncode, result.stdout), (0, "review complete\n"), result.stderr)
        result = self.run_cli("--cli", "codex", RESPONSE="no_answer")
        self.assertEqual(result.returncode, 4, result.stderr)

    def test_ambiguous_host_needs_explicit_cli(self):
        result = self.run_cli(CLAUDECODE="1")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--cli", result.stderr)
        self.assertFalse(self.record.exists())
        explicit = self.run_cli("--cli", "claude", CLAUDECODE="1")
        self.assertEqual(explicit.returncode, 0, explicit.stderr)
        self.assertEqual(json.loads(self.record.read_text())["cli"], "claude")

    def test_configuration_alone_does_not_identify_host(self):
        result = self.run_cli(CODEX_THREAD_ID="", CODEX_HOME=str(self.base))
        self.assertEqual(result.returncode, 2)
        self.assertIn("--cli", result.stderr)

    def test_project_instructions_reach_claude_from_a_relative_cd_and_both_locations(self):
        repo = self.base / "repo"
        (repo / ".claude").mkdir(parents=True)
        (repo / "CLAUDE.md").write_text("root rule\n")
        (repo / ".claude/CLAUDE.md").write_text("dot-claude rule\n")
        result = subprocess.run([str(SCRIPT), "--cli", "claude", "--cd", "repo"], input="review this\n",
                                text=True, capture_output=True, cwd=self.base, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        recorded = json.loads(self.record.read_text())
        self.assertEqual(recorded["appended"], "root rule\n\ndot-claude rule\n")

    def test_no_claude_md_means_no_appended_prompt(self):
        result = self.run_cli("--cli", "claude", "--cd", str(self.base))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--append-system-prompt", json.loads(self.record.read_text())["args"])

    def test_claude_write_runs_commands_only_inside_a_required_sandbox(self):
        # A candidate can run its tests, but only sandboxed: no fallback when the sandbox can't
        # start, and no unsandboxed retries.
        result = self.run_cli("--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        args = json.loads(self.record.read_text())["args"]
        self.assertIn("acceptEdits", args)
        self.assertNotIn("bypassPermissions", args)
        self.assertNotIn("--dangerously-skip-permissions", args)
        settings = json.loads(args[args.index("--settings") + 1])
        self.assertTrue(settings["disableAllHooks"])
        self.assertFalse(settings["autoMemoryEnabled"])
        sandbox = settings["sandbox"]
        self.assertEqual(sandbox, {"enabled": True, "autoAllowBashIfSandboxed": True,
                                   "failIfUnavailable": True, "allowUnsandboxedCommands": False})
        # The worktree's own settings and hooks don't apply, no MCP servers load, and Claude's temp
        # root is private to this run (the shared one holds other sessions' files).
        self.assertEqual(args[args.index("--setting-sources") + 1], "user")
        self.assertIn("--strict-mcp-config", args)
        # Skills like `how` need subagents, and rigor keeps a todo list.
        self.assertEqual(args[args.index("--tools") + 1], "Bash,Read,Edit,Write,Glob,Grep,Agent,TodoWrite")
        tmpdir = json.loads(self.record.read_text())["tmpdir"]
        self.assertTrue(tmpdir and not tmpdir.startswith(("/tmp/claude-", "/private/tmp/claude-")), tmpdir)
        # Claude puts Unix sockets in it; past macOS's ~104-byte socket path limit it silently falls
        # back to the shared root. Live: a 74-char /var/folders path fell back, /tmp/rc-xxxxxxxx didn't.
        self.assertLessEqual(len(tmpdir), 32, tmpdir)

    def test_missing_cli_retains_fallback_status(self):
        (self.bin / "claude").unlink()
        result = self.run_cli()
        self.assertEqual(result.returncode, 3)
        self.assertIn("host subagent", result.stderr)

    def test_missing_option_values_are_usage_errors(self):
        for option in ("--cli", "--cd", "--trace"):
            with self.subTest(option=option):
                self.assertEqual(self.run_cli(option).returncode, 2)


if __name__ == "__main__":
    unittest.main()
