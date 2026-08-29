from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
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
        self.assertIn("must omit fixed model fields", result["errors"][0])
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
        self.assertIn("must omit sandbox_mode", result["errors"][0])
        self.assert_no_targets()

    def test_capability_only_template_requires_feature_and_skill_reductions(self) -> None:
        template = self.templates["sacha_researcher"].decode("utf-8")
        cases = (
            (
                "feature",
                template.replace("shell_tool = false", "shell_tool = true", 1),
                "unexpected feature reductions",
            ),
            (
                "skills",
                template.replace(
                    "include_instructions = false",
                    "include_instructions = true",
                    1,
                ),
                "unexpected Skill reductions",
            ),
        )
        for label, text, expected_error in cases:
            with self.subTest(label=label):
                bad_template = self.root / f"bad-researcher-{label}.toml"
                bad_template.write_bytes(text.encode("utf-8"))
                result = setup_agents.run_setup(
                    codex_home=self.codex_home,
                    _template_paths={"sacha_researcher": bad_template},
                )
                self.assertEqual(result["transaction"], "no_write")
                self.assertIn(expected_error, result["errors"][0])
                self.assert_no_targets()


if __name__ == "__main__":
    unittest.main()
