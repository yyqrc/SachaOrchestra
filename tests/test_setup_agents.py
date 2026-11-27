from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "sacha-orchestra" / "skills" / "setup-agents" / "scripts" / "setup_agents.py"
SPEC = importlib.util.spec_from_file_location("sacha_setup_agents", SCRIPT)
assert SPEC and SPEC.loader
setup_agents = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = setup_agents
SPEC.loader.exec_module(setup_agents)


class SetupAgentsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.codex_home = self.root / "codex-home"
        self.codex_home.mkdir()
        self.definitions = {item.name: item for item in setup_agents.AGENT_DEFINITIONS}
        self.targets = {
            name: setup_agents.resolve_target(self.codex_home, item.target_relative)
            for name, item in self.definitions.items()
        }
        self.templates = {
            name: item.template_path.read_bytes()
            for name, item in self.definitions.items()
        }
        self.primary_name = "sacha_executer"
        self.primary_target = self.targets[self.primary_name]
        self.legacy_researcher_target = setup_agents.resolve_target(
            self.codex_home,
            setup_agents.LEGACY_RESEARCHER_TARGET_RELATIVE,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def dry_run(self):
        return setup_agents.run_setup(codex_home=self.codex_home)

    def apply(self, **kwargs):
        return setup_agents.run_setup(codex_home=self.codex_home, write=True, **kwargs)

    def test_agy_targets_and_both_via_cli(self):
        config = self.root / "user" / ".gemini" / "config"
        args = [sys.executable, "-B", str(SCRIPT), "--codex-home", str(self.codex_home),
                "--agy-config", str(config)]

        def invoke(target, mode):
            process = subprocess.run([*args, "--target", target, mode], capture_output=True,
                                     check=True, encoding="utf-8")
            return json.loads(process.stdout)

        preview = invoke("both", "--dry-run")
        self.assertEqual(7, len(preview["target_paths"]))
        self.assertFalse(config.exists())
        self.assertEqual([], list(self.codex_home.iterdir()))
        unrelated = config / "agents" / "personal" / "agent.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_bytes(b"personal")
        agy = invoke("agy", "--write")
        self.assertEqual("written", agy["transaction"])
        self.assertEqual(2, len(agy["written_paths"]))
        self.assertEqual([], list(self.codex_home.iterdir()))
        self.assertEqual(b"personal", unrelated.read_bytes())
        for definition in setup_agents.AGY_DEFINITIONS:
            self.assertEqual(definition.template_path.read_bytes(),
                             (config / definition.target_relative).read_bytes())
        self.assertEqual("no_changes", invoke("agy", "--write")["transaction"])
        both = invoke("both", "--write")
        self.assertEqual(5, len(both["written_paths"]))
        self.assertEqual("no_changes", invoke("both", "--write")["transaction"])

    def test_agy_setup_verifies_once_before_saving_the_connection(self):
        path = self.root.resolve() / ".gemini" / "config" / "sacha-acp.json"
        options = {"target": "agy", "user_home": self.root, "agy_executable": sys.executable}
        roles = setup_agents.AGY_DEFINITIONS
        helper = ROOT / "plugins" / "sacha-orchestra" / "adapters" / "codex" / "scripts" / "agy_acp.py"
        saved_on_probe = []

        def launch(command, **kwargs):
            self.assertEqual(path.parent, kwargs["cwd"])
            self.assertNotIn("GEMINI_API_KEY", kwargs["env"])
            for definition in roles:
                self.assertEqual(definition.template_path.read_bytes(),
                                 (path.parent / definition.target_relative).read_bytes())
            if command == [str(Path(sys.executable).resolve()), "agents"]:
                return subprocess.CompletedProcess(command, 0, "\n".join(role.name for role in roles), "")
            self.assertEqual([sys.executable, "-B", str(helper), "--agy", str(Path(sys.executable).resolve()),
                              "--cwd", str(path.parent), "--probe"], command)
            saved_on_probe.append(path.exists())
            hello = {"protocolVersion": 1, "agentInfo": {"version": "test"},
                     "authMethods": [{"id": "oauth-personal"}]}
            return subprocess.CompletedProcess(command, 0, json.dumps({"initialize": hello}), "")

        with mock.patch.object(setup_agents.subprocess, "run", side_effect=launch) as check:
            preview = setup_agents.run_setup(**options, agy_auth="cached-login")
            self.assertEqual("dry_run", preview["transaction"])
            self.assertFalse(path.exists())
            check.assert_not_called()
            written = self.apply(**options, agy_auth="cached-login")
            self.assertEqual("written", written["transaction"], written.get("errors"))
            self.assertEqual((1, "test", "cached-login"), (written["agy_setup"]["protocol_version"],
                                                            written["agy_setup"]["cli_version"],
                                                            written["agy_setup"]["auth"]))
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("cached-login", saved["auth"])
            self.assertEqual(Path(sys.executable).resolve(), Path(saved["executable"]))
            repeated = self.apply(target="agy", user_home=self.root)
            self.assertEqual("no_changes", repeated["transaction"])
            self.assertEqual(saved, json.loads(path.read_text(encoding="utf-8")))
            self.assertEqual(2, check.call_count)
            role_path = path.parent / roles[0].target_relative
            role_path.write_bytes(role_path.read_bytes() + b"\nOld managed instructions.\n")
            refreshed = self.apply(target="agy", user_home=self.root)
            self.assertEqual([str(role_path)], refreshed["written_paths"])
            self.assertEqual(saved, json.loads(path.read_text(encoding="utf-8")))
            self.assertEqual([False, True], saved_on_probe)

    def test_unmanaged_agy_connection_is_visible_in_dry_run(self):
        path = self.root / ".gemini" / "config" / "sacha-acp.json"
        path.parent.mkdir(parents=True)
        content = b'{"unmanaged": "do not disclose in the preview"}'
        path.write_bytes(content)
        options = {"target": "both", "user_home": self.root, "agy_executable": self.root / "missing"}
        preview = setup_agents.run_setup(codex_home=self.codex_home, **options)
        self.assertEqual("dry_run", preview["transaction"])
        self.assertEqual(8, len(preview["agents"]))
        self.assertEqual("conflict", self.agent(preview, "sacha-acp")["action"])
        self.assertNotIn(content.decode(), json.dumps(preview))
        written = self.apply(**options)
        self.assertEqual(("refused", "no_write"), (written["status"], written["transaction"]))
        self.assertEqual(content, path.read_bytes())
        self.assertEqual([], list(self.codex_home.iterdir()))

    def test_agy_probe_failure_preserves_diagnostics_and_restores_managed_files(self):
        config = self.root / ".gemini" / "config"
        unrelated = config / "agy-runtime.txt"

        def launch(command, **kwargs):
            if command[1:] == ["agents"]:
                names = "\n".join(role.name for role in setup_agents.AGY_DEFINITIONS)
                return subprocess.CompletedProcess(command, 0, names, "")
            unrelated.write_bytes(b"agy side effect")
            return subprocess.CompletedProcess(command, 2, json.dumps({"error": "init failed",
                                                                         "stderr": "native diagnosis"}), "")

        with mock.patch.object(setup_agents.subprocess, "run", side_effect=launch):
            result = self.apply(target="agy", user_home=self.root, agy_executable=sys.executable)
        self.assertEqual(("refused", "rolled_back"), (result["status"], result["transaction"]))
        self.assertIn("exit 2", result["errors"][0])
        self.assertIn("init failed", result["errors"][0])
        self.assertIn("native diagnosis", result["errors"][0])
        self.assertEqual(b"agy side effect", unrelated.read_bytes())
        self.assertFalse((config / "sacha-acp.json").exists())
        self.assertFalse((config / "agents").exists())

    def test_failed_agy_discovery_leaves_no_connection_or_new_roles(self):
        for error in (setup_agents.SetupAgentsError("agent missing"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__), mock.patch.object(
                    setup_agents, "verify_agy_setup", side_effect=error):
                result = self.apply(target="agy", user_home=self.root, agy_executable=sys.executable)
                self.assertEqual("rolled_back", result["transaction"])
                self.assertFalse((self.root / ".gemini").exists())

    def test_agy_unmanaged_file_blocks_both_and_flat_collision_is_refused(self):
        config = self.root / "gemini"
        profile = config / "agents" / "sacha-reviewer" / "agent.md"
        profile.parent.mkdir(parents=True)
        content = b"---\nname: sacha-reviewer\n---\nUser configuration"
        profile.write_bytes(content)
        conflict = self.apply(target="both", agy_config=config)
        self.assertEqual(("refused", "no_write"), (conflict["status"], conflict["transaction"]))
        self.assertEqual(content, profile.read_bytes())
        self.assertEqual([], list(self.codex_home.iterdir()))
        flat = config / "agents" / "sacha-explorer.md"
        flat.write_bytes(content)
        conflict = self.apply(target="agy", agy_config=config)
        self.assertIn(str(flat.resolve()), conflict["errors"][0])
        self.assertEqual(content, flat.read_bytes())

    def test_rollback_from_agy_write_restores_codex_and_own_directories(self):
        config = (self.root / "user" / ".gemini" / "config").resolve()

        def fail_after_agy_replace(path):
            if path.is_relative_to(config):
                raise OSError("test write interruption")

        failed = self.apply(target="both", agy_config=config,
                            _test_hooks={"after_replace": fail_after_agy_replace})
        self.assertEqual("rolled_back", failed["transaction"])
        self.assertFalse(config.exists())
        self.assertEqual([], list(self.codex_home.iterdir()))

    @staticmethod
    def agent(plan, name):
        return next(agent for agent in plan["agents"] if agent["name"] == name)

    def assert_no_targets(self, *except_names: str) -> None:
        excluded = set(except_names)
        self.assertTrue(
            all(not target.exists() for name, target in self.targets.items() if name not in excluded)
        )

    def write_legacy_researcher(self, *, managed: bool = True) -> bytes:
        lines = []
        if managed:
            lines.append(setup_agents.OWNER_MARKER)
        lines.extend(
            (
                'name = "sacha_readonly_worker"',
                'description = "legacy researcher"',
                'developer_instructions = "legacy"',
            )
        )
        content = ("\n".join(lines) + "\n").encode("utf-8")
        self.legacy_researcher_target.parent.mkdir(exist_ok=True)
        self.legacy_researcher_target.write_bytes(content)
        return content

    def test_path_resolution_prefers_codex_home_and_falls_back(self) -> None:
        selected = setup_agents.resolve_codex_home(
            environ={"CODEX_HOME": str(self.codex_home)},
            user_home=self.root / "ignored",
        )
        fallback = setup_agents.resolve_codex_home(environ={}, user_home=self.root / "user")
        self.assertEqual(selected, self.codex_home.resolve())
        self.assertEqual(fallback, (self.root / "user" / ".codex").resolve())
        self.assertEqual(setup_agents.resolve_target(selected), self.primary_target)
        for name, definition in self.definitions.items():
            self.assertEqual(
                setup_agents.resolve_target(selected, definition.target_relative),
                self.targets[name],
            )

    def test_cli_dry_run_uses_temporary_codex_home(self) -> None:
        env = os.environ.copy()
        env.update(CODEX_HOME=str(self.codex_home), PYTHONUTF8="1")
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--dry-run"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["action"], "create")
        self.assertEqual(
            result["target_paths"],
            [str(self.targets[item.name]) for item in setup_agents.AGENT_DEFINITIONS],
        )
        self.assert_no_targets()

    def test_cli_conflict_always_refuses_write(self) -> None:
        self.primary_target.parent.mkdir()
        original = b'name = "custom"\n'
        self.primary_target.write_bytes(original)
        env = os.environ.copy()
        env.update(CODEX_HOME=str(self.codex_home), PYTHONUTF8="1")
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--write"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(json.loads(completed.stdout)["transaction"], "no_write")
        self.assertEqual(self.primary_target.read_bytes(), original)
        self.assert_no_targets(self.primary_name)

    def test_create_and_repeated_run_are_idempotent(self) -> None:
        plan = self.dry_run()
        self.assertEqual(plan["action"], "create")
        for name, target in self.targets.items():
            self.assertIn(str(target), plan["delta"])
            self.assertEqual(self.agent(plan, name)["action"], "create")
        result = self.apply()
        self.assertEqual((result["status"], result["transaction"]), ("ok", "written"))
        self.assertEqual(
            result["written_paths"],
            [str(self.targets[item.name]) for item in setup_agents.AGENT_DEFINITIONS],
        )
        for name, target in self.targets.items():
            self.assertEqual(target.read_bytes(), self.templates[name])

        researcher = tomllib.loads(self.targets["sacha_researcher"].read_text(encoding="utf-8"))
        executer = tomllib.loads(self.targets["sacha_executer"].read_text(encoding="utf-8"))
        reviewer = tomllib.loads(self.targets["sacha_reviewer"].read_text(encoding="utf-8"))
        self.assertEqual(
            researcher["features"],
            {
                "shell_tool": False,
                "apps": False,
                "memories": False,
                "request_permissions_tool": False,
            },
        )
        self.assertEqual(
            executer["features"],
            {"memories": False, "request_permissions_tool": False},
        )
        self.assertEqual(
            reviewer["features"],
            {"memories": False, "request_permissions_tool": False},
        )
        expected_skills = {
            "include_instructions": False,
            "bundled": {"enabled": False},
        }
        for capability in (researcher, executer, reviewer):
            self.assertNotIn("model", capability)
            self.assertNotIn("model_reasoning_effort", capability)
            self.assertNotIn("sandbox_mode", capability)
            self.assertEqual(capability["skills"], expected_skills)

        deepseek = tomllib.loads(self.targets["sacha_deepseek_worker"].read_text(encoding="utf-8"))
        deepseek_pro = tomllib.loads(self.targets["sacha_deepseek_pro_worker"].read_text(encoding="utf-8"))
        self.assertEqual(
            (deepseek["model"], deepseek["model_reasoning_effort"]),
            ("TT/deepseek-v4-flash-ioa", "max"),
        )
        self.assertEqual(
            (deepseek_pro["model"], deepseek_pro["model_reasoning_effort"]),
            ("TT/deepseek-v4-pro-ioa", "max"),
        )
        again = self.dry_run()
        self.assertEqual((again["action"], again["delta"]), ("no-op", ""))

    def test_migrates_managed_legacy_researcher(self) -> None:
        legacy = self.write_legacy_researcher()
        plan = self.dry_run()
        self.assertEqual(plan["retired_agents"][0]["action"], "remove")
        self.assertIn(str(self.legacy_researcher_target), plan["delta"])

        result = self.apply()
        self.assertEqual((result["status"], result["transaction"]), ("ok", "written"))
        self.assertEqual(result["retired_paths"], [str(self.legacy_researcher_target)])
        self.assertFalse(self.legacy_researcher_target.exists())
        self.assertEqual(
            self.targets["sacha_researcher"].read_bytes(),
            self.templates["sacha_researcher"],
        )
        self.assertNotEqual(self.templates["sacha_researcher"], legacy)
        self.assertEqual(self.dry_run()["action"], "no-op")

    def test_unmanaged_legacy_researcher_blocks_migration(self) -> None:
        legacy = self.write_legacy_researcher(managed=False)
        self.assertEqual(self.dry_run()["retired_agents"][0]["action"], "conflict")
        result = self.apply()
        self.assertEqual((result["status"], result["transaction"]), ("refused", "no_write"))
        self.assertEqual(self.legacy_researcher_target.read_bytes(), legacy)
        self.assert_no_targets()

    def test_embedded_owner_marker_does_not_authorize_legacy_removal(self) -> None:
        self.legacy_researcher_target.parent.mkdir(exist_ok=True)
        legacy = (
            'name = "sacha_readonly_worker"\n'
            'description = "unmanaged"\n'
            'developer_instructions = """\n'
            f"{setup_agents.OWNER_MARKER}\n"
            '"""\n'
        ).encode("utf-8")
        self.legacy_researcher_target.write_bytes(legacy)

        self.assertEqual(self.dry_run()["retired_agents"][0]["action"], "conflict")
        result = self.apply()
        self.assertEqual((result["status"], result["transaction"]), ("refused", "no_write"))
        self.assertEqual(self.legacy_researcher_target.read_bytes(), legacy)
        self.assert_no_targets()

    def test_semantically_identical_unmanaged_files_are_conflicts(self) -> None:
        self.primary_target.parent.mkdir()
        for name in ("sacha_executer", "sacha_reviewer"):
            manual = b"\n".join(
                line for line in self.templates[name].splitlines() if not line.startswith(b"#")
            ) + b"\n"
            self.targets[name].write_bytes(manual)
        plan = self.dry_run()
        self.assertEqual(plan["action"], "mixed")
        self.assertEqual(self.agent(plan, "sacha_executer")["action"], "conflict")
        self.assertEqual(self.agent(plan, "sacha_reviewer")["action"], "conflict")
        self.assertEqual(self.apply()["transaction"], "no_write")
        self.assert_no_targets("sacha_executer", "sacha_reviewer")

    def test_owner_marker_with_wrong_identity_is_refused(self) -> None:
        self.primary_target.parent.mkdir()
        self.primary_target.write_bytes(
            setup_agents.OWNER_MARKER.encode("utf-8") + b'\nname = "custom"\n'
        )
        plan = self.dry_run()
        self.assertEqual(self.agent(plan, self.primary_name)["action"], "conflict")
        self.assertEqual(self.apply()["transaction"], "no_write")
        self.assert_no_targets(self.primary_name)

    def test_cli_write_creates_without_second_confirmation(self) -> None:
        env = os.environ.copy()
        env.update(CODEX_HOME=str(self.codex_home), PYTHONUTF8="1")
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--write"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["transaction"], "written")
        for name, target in self.targets.items():
            self.assertEqual(target.read_bytes(), self.templates[name])

    def test_capability_only_agent_updates_without_model_fields(self) -> None:
        self.primary_target.parent.mkdir()
        self.primary_target.write_bytes(
            setup_agents.OWNER_MARKER.encode("utf-8")
            + b'\nname = "sacha_executer"\n'
            + b'description = "old"\n'
            + b'developer_instructions = "old"\n'
        )
        self.assertEqual(self.agent(self.dry_run(), self.primary_name)["action"], "update")
        result = self.apply()
        self.assertEqual((result["status"], result["transaction"]), ("ok", "written"))
        parsed = tomllib.loads(self.primary_target.read_text(encoding="utf-8"))
        self.assertNotIn("sandbox_mode", parsed)
        self.assertNotIn("model", parsed)
        self.assertNotIn("model_reasoning_effort", parsed)
        self.assertEqual(self.dry_run()["action"], "no-op")

    def test_retired_model_specific_files_are_untouched(self) -> None:
        retired = {
            "sacha-luna-worker.toml": b'name = "sacha_luna_worker"\n',
            "sacha-luna-worker-xhigh.toml": b'name = "sacha_luna_worker_xhigh"\n',
            "sacha-k3-worker.toml": b'name = "sacha_k3_worker"\n',
            "luna-worker.toml": b'name = "luna_worker"\n',
        }
        agents = self.codex_home / "agents"
        agents.mkdir()
        for filename, content in retired.items():
            (agents / filename).write_bytes(content)
        self.assertEqual(self.apply()["transaction"], "written")
        for filename, content in retired.items():
            self.assertEqual((agents / filename).read_bytes(), content)

    def test_target_change_after_planning_refuses_without_write(self) -> None:
        changed = b'name = "changed"\n'

        def change_preimage() -> None:
            self.primary_target.parent.mkdir(exist_ok=True)
            self.primary_target.write_bytes(changed)

        result = self.apply(_test_hooks={"before_preimage_check": change_preimage})
        self.assertEqual((result["status"], result["transaction"]), ("refused", "no_write"))
        self.assertEqual(self.primary_target.read_bytes(), changed)
        self.assert_no_targets(self.primary_name)

    def test_invalid_template_is_refused_without_write(self) -> None:
        bad_template = self.root / "bad.toml"
        bad_template.write_text(setup_agents.OWNER_MARKER + "\nname = [", encoding="utf-8")
        result = setup_agents.run_setup(
            codex_home=self.codex_home,
            _template_paths={self.primary_name: bad_template},
        )
        self.assertEqual(result["transaction"], "no_write")
        self.assert_no_targets()

    def test_later_target_concurrent_change_preserves_writer_and_rolls_back(self) -> None:
        first, second = setup_agents.AGENT_DEFINITIONS[:2]
        first_target, second_target = self.targets[first.name], self.targets[second.name]
        first_target.parent.mkdir()
        original = self.templates[first.name].replace(b"description =", b"# older\ndescription =", 1)
        first_target.write_bytes(original)
        concurrent = b'name = "concurrent"\n'

        def change_later_target(target: Path) -> None:
            if target == first_target:
                second_target.write_bytes(concurrent)

        result = self.apply(_test_hooks={"after_replace": change_later_target})
        self.assertEqual(("refused", "rolled_back"), (result["status"], result["transaction"]))
        self.assertEqual(original, first_target.read_bytes())
        self.assertEqual(concurrent, second_target.read_bytes())
        self.assertEqual({first_target, second_target}, set(first_target.parent.iterdir()))

    def test_replace_failure_removes_all_prepared_temporary_files(self) -> None:
        with mock.patch.object(setup_agents.os, "replace", side_effect=OSError("injected")):
            result = self.apply()
        self.assertEqual(("refused", "no_write"), (result["status"], result["transaction"]))
        self.assertEqual([], list(self.codex_home.iterdir()))

    def test_post_write_failure_rolls_back_preimage(self) -> None:
        self.primary_target.parent.mkdir()
        old = (
            setup_agents.OWNER_MARKER.encode("utf-8")
            + b'\nname = "sacha_executer"\n'
            + b'description = "old"\n'
            + b'developer_instructions = "old"\n'
        )
        self.primary_target.write_bytes(old)
        replaced = []

        def fail_after_replace(target: Path) -> None:
            replaced.append(target)
            if len(replaced) == 2:
                raise RuntimeError("injected post-write failure")

        result = self.apply(_test_hooks={"after_replace": fail_after_replace})
        self.assertEqual((result["status"], result["transaction"]), ("refused", "rolled_back"))
        self.assertEqual(self.primary_target.read_bytes(), old)
        self.assert_no_targets(self.primary_name)

    def test_failure_after_legacy_retirement_rolls_back_all_targets(self) -> None:
        legacy = self.write_legacy_researcher()

        def fail_after_retire(_target: Path) -> None:
            raise RuntimeError("injected retirement failure")

        result = self.apply(_test_hooks={"after_retire": fail_after_retire})
        self.assertEqual((result["status"], result["transaction"]), ("refused", "rolled_back"))
        self.assertEqual(self.legacy_researcher_target.read_bytes(), legacy)
        self.assert_no_targets()

    def test_capability_only_template_with_fixed_model_is_refused(self) -> None:
        bad_template = self.root / "bad-researcher.toml"
        text = self.templates["sacha_researcher"].decode("utf-8")
        bad_template.write_bytes(
            text.replace(
                'developer_instructions = """',
                'model = "gpt-5.6-luna"\n\ndeveloper_instructions = """',
                1,
            ).encode("utf-8"),
        )
        result = setup_agents.run_setup(
            codex_home=self.codex_home,
            _template_paths={"sacha_researcher": bad_template},
        )
        self.assertEqual(result["transaction"], "no_write")
        self.assert_no_targets()

    def test_capability_only_template_with_sandbox_mode_is_refused(self) -> None:
        bad_template = self.root / "bad-researcher.toml"
        text = self.templates["sacha_researcher"].decode("utf-8")
        bad_template.write_bytes(
            text.replace(
                'developer_instructions = """',
                'sandbox_mode = "read-only"\n\ndeveloper_instructions = """',
                1,
            ).encode("utf-8"),
        )
        result = setup_agents.run_setup(
            codex_home=self.codex_home,
            _template_paths={"sacha_researcher": bad_template},
        )
        self.assertEqual(result["transaction"], "no_write")
        self.assert_no_targets()

    def test_capability_only_template_requires_feature_and_skill_reductions(self) -> None:
        template = self.templates["sacha_researcher"].decode("utf-8")
        cases = (
            (
                "feature",
                template.replace("shell_tool = false", "shell_tool = true", 1),
            ),
            (
                "skills",
                template.replace(
                    "include_instructions = false",
                    "include_instructions = true",
                    1,
                ),
            ),
        )
        for label, text in cases:
            with self.subTest(label=label):
                bad_template = self.root / f"bad-researcher-{label}.toml"
                bad_template.write_bytes(text.encode("utf-8"))
                result = setup_agents.run_setup(
                    codex_home=self.codex_home,
                    _template_paths={"sacha_researcher": bad_template},
                )
                self.assertEqual(result["transaction"], "no_write")
                self.assert_no_targets()


if __name__ == "__main__":
    unittest.main()
