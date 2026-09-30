import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.base = Path(self.scratch.name)
        self.clone = self.base / "clone-$rigor_path with 'quotes'"
        shutil.copytree(ROOT, self.clone, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
        self.home = self.base / "home"
        self.env = {**os.environ, "HOME": str(self.home), "CODEX_HOME": str(self.home / ".codex")}
        self.env.pop("RIGOR_NESTED", None)
        self.env.pop("rigor_path", None)

    def install(self, *args):
        return subprocess.run([str(self.clone / "install.sh"), *args], env=self.env,
                              text=True, capture_output=True)

    def test_installed_hooks_activate_from_shell_sensitive_path(self):
        installed = self.install()
        self.assertEqual(installed.returncode, 0, installed.stderr)
        for host, path in (("claude", ".claude/settings.json"), ("codex", ".codex/hooks.json")):
            with self.subTest(host=host):
                config = json.loads((self.home / path).read_text())
                command = config["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
                result = subprocess.run(["bash", "-c", command], env=self.env, text=True,
                                        capture_output=True, input=json.dumps({
                                            "hook_event_name": "UserPromptSubmit",
                                            "session_id": host, "prompt": "$rigor audit"}))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("rigor is on", result.stdout, result.stderr)
                self.assertTrue((self.home / ".rigor/sessions" / host).is_file())

    def test_invalid_hook_groups_fail_before_installing_anything(self):
        config = self.home / ".codex/hooks.json"
        config.parent.mkdir(parents=True)
        for groups in (None, {}, [None], [{"hooks": None}], [{"hooks": [None]}]):
            with self.subTest(groups=groups):
                original = json.dumps({"hooks": {"UserPromptSubmit": groups}})
                config.write_text(original)
                result = self.install()
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("hooks.py:", result.stderr)
                self.assertEqual(config.read_text(), original)
                self.assertFalse((self.home / ".agents/skills").exists())

    def test_removed_agents_are_reconciled_without_deleting_foreign_agents(self):
        self.check_removed_agent()

    def test_uninstall_removes_agents_absent_from_current_sources(self):
        self.check_removed_agent("--uninstall")

    def check_removed_agent(self, *args):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        agents = self.home / ".codex/agents"
        foreign = agents / "personal.toml"
        foreign.write_text('name = "personal"\n')
        installed = agents / "comment-reviewer.toml"
        self.assertTrue(installed.exists())
        (self.clone / "codex/agents/comment-reviewer.toml").unlink()
        result = self.install(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(installed.exists(), "obsolete Codex agent remains installed")
        self.assertEqual(foreign.read_text(), 'name = "personal"\n')
        self.assertEqual((agents / "rigor-agent.toml").exists(), not bool(args))


if __name__ == "__main__":
    unittest.main()
