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
        self.target = self.codex_home / "agents" / "sacha-luna-worker.toml"
        self.xhigh_target = self.codex_home / "agents" / "sacha-luna-worker-xhigh.toml"
        self.deepseek_target = self.codex_home / "agents" / "sacha-deepseek-worker.toml"
        self.deepseek_pro_target = self.codex_home / "agents" / "sacha-deepseek-pro-worker.toml"
        self.k3_target = self.codex_home / "agents" / "sacha-k3-worker.toml"
        self.template = setup_agents.DEFAULT_TEMPLATE.read_bytes()
        self.xhigh_template = setup_agents.XHIGH_TEMPLATE.read_bytes()
        self.deepseek_template = setup_agents.DEEPSEEK_TEMPLATE.read_bytes()
        self.deepseek_pro_template = setup_agents.DEEPSEEK_PRO_TEMPLATE.read_bytes()
        self.k3_template = setup_agents.K3_TEMPLATE.read_bytes()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def dry_run(self):
        return setup_agents.run_setup(codex_home=self.codex_home)

    def apply(self, _plan=None, **kwargs):
        return setup_agents.run_setup(
            codex_home=self.codex_home,
            write=True,
            **kwargs,
        )

    @staticmethod
    def agent(plan, name):
        return next(agent for agent in plan["agents"] if agent["name"] == name)

    def test_path_resolution_prefers_codex_home_and_falls_back(self) -> None:
        selected = setup_agents.resolve_codex_home(environ={"CODEX_HOME": str(self.codex_home)}, user_home=self.root / "ignored")
        fallback = setup_agents.resolve_codex_home(environ={}, user_home=self.root / "user")
        self.assertEqual(selected, self.codex_home.resolve())
        self.assertEqual(fallback, (self.root / "user" / ".codex").resolve())
        self.assertEqual(setup_agents.resolve_target(selected), self.target.resolve())
        self.assertEqual(
            setup_agents.resolve_target(selected, setup_agents.XHIGH_TARGET_RELATIVE),
            self.xhigh_target.resolve(),
        )
        self.assertEqual(
            setup_agents.resolve_target(selected, setup_agents.DEEPSEEK_TARGET_RELATIVE),
            self.deepseek_target.resolve(),
        )
        self.assertEqual(
            setup_agents.resolve_target(selected, setup_agents.DEEPSEEK_PRO_TARGET_RELATIVE),
            self.deepseek_pro_target.resolve(),
        )
        self.assertEqual(
            setup_agents.resolve_target(selected, setup_agents.K3_TARGET_RELATIVE),
            self.k3_target.resolve(),
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
            [
                str(self.target.resolve()),
                str(self.xhigh_target.resolve()),
                str(self.deepseek_target.resolve()),
                str(self.deepseek_pro_target.resolve()),
                str(self.k3_target.resolve()),
            ],
        )
        self.assertFalse(self.target.exists())
        self.assertFalse(self.xhigh_target.exists())
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())

    def test_cli_conflict_always_refuses_write(self) -> None:
        self.target.parent.mkdir()
        original = b'name = "custom"\n'
        self.target.write_bytes(original)
        env = os.environ.copy()
        env.update(CODEX_HOME=str(self.codex_home), PYTHONUTF8="1")
        write = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--write"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        self.assertEqual(write.returncode, 2)
        self.assertEqual(json.loads(write.stdout)["transaction"], "no_write")
        self.assertEqual(self.target.read_bytes(), original)
        self.assertFalse(self.xhigh_target.exists())
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())

    def test_create_and_repeated_run_are_idempotent(self) -> None:
        plan = self.dry_run()
        self.assertEqual(plan["action"], "create")
        self.assertNotIn("planned_delta_sha256", plan)
        self.assertNotIn("current_sha256", self.agent(plan, "sacha_luna_worker"))
        self.assertNotIn("generated_sha256", self.agent(plan, "sacha_luna_worker"))
        self.assertIn(str(self.target.resolve()), plan["delta"])
        self.assertIn(str(self.xhigh_target.resolve()), plan["delta"])
        self.assertIn(str(self.deepseek_target.resolve()), plan["delta"])
        self.assertIn(str(self.deepseek_pro_target.resolve()), plan["delta"])
        self.assertIn(str(self.k3_target.resolve()), plan["delta"])
        self.assertGreaterEqual(
            len(plan["delta"].splitlines()),
            len(self.template.decode("utf-8").splitlines())
            + len(self.xhigh_template.decode("utf-8").splitlines())
            + len(self.deepseek_template.decode("utf-8").splitlines())
            + len(self.deepseek_pro_template.decode("utf-8").splitlines())
            + len(self.k3_template.decode("utf-8").splitlines())
            + 4,
        )
        self.assertFalse(self.target.exists())
        self.assertFalse(self.xhigh_target.exists())
        result = self.apply(plan)
        self.assertEqual((result["status"], result["transaction"]), ("ok", "written"))
        self.assertEqual(
            result["written_paths"],
            [
                str(self.target.resolve()),
                str(self.xhigh_target.resolve()),
                str(self.deepseek_target.resolve()),
                str(self.deepseek_pro_target.resolve()),
                str(self.k3_target.resolve()),
            ],
        )
        self.assertNotIn("installed_sha256", result)
        self.assertEqual(self.target.read_bytes(), self.template)
        self.assertEqual(self.xhigh_target.read_bytes(), self.xhigh_template)
        self.assertEqual(self.deepseek_target.read_bytes(), self.deepseek_template)
        self.assertEqual(self.deepseek_pro_target.read_bytes(), self.deepseek_pro_template)
        self.assertEqual(self.k3_target.read_bytes(), self.k3_template)
        parsed = tomllib.loads(self.target.read_text(encoding="utf-8"))
        xhigh_parsed = tomllib.loads(self.xhigh_target.read_text(encoding="utf-8"))
        deepseek_parsed = tomllib.loads(self.deepseek_target.read_text(encoding="utf-8"))
        deepseek_pro_parsed = tomllib.loads(self.deepseek_pro_target.read_text(encoding="utf-8"))
        k3_parsed = tomllib.loads(self.k3_target.read_text(encoding="utf-8"))
        self.assertEqual(parsed, tomllib.loads(self.template.decode("utf-8")))
        self.assertEqual((parsed["name"], parsed["model_reasoning_effort"]), ("sacha_luna_worker", "max"))
        self.assertEqual(
            (xhigh_parsed["name"], xhigh_parsed["model_reasoning_effort"]),
            ("sacha_luna_worker_xhigh", "xhigh"),
        )
        self.assertEqual(parsed["model"], xhigh_parsed["model"])
        self.assertEqual(
            (deepseek_parsed["name"], deepseek_parsed["model"], deepseek_parsed["model_reasoning_effort"]),
            ("sacha_deepseek_worker", "TT/deepseek-v4-flash-ioa", "max"),
        )
        self.assertEqual(
            (
                deepseek_pro_parsed["name"],
                deepseek_pro_parsed["model"],
                deepseek_pro_parsed["model_reasoning_effort"],
            ),
            ("sacha_deepseek_pro_worker", "TT/deepseek-v4-pro-ioa", "max"),
        )
        self.assertEqual(
            (k3_parsed["name"], k3_parsed["model"], k3_parsed["model_reasoning_effort"]),
            ("sacha_k3_worker", "TT/kimi-k3-ioa", "max"),
        )
        again = self.dry_run()
        self.assertEqual((again["action"], again["delta"]), ("no-op", ""))

    def test_semantically_identical_unmanaged_file_is_conflict(self) -> None:
        self.target.parent.mkdir()
        manual = b"\n".join(line for line in self.template.splitlines() if not line.startswith(b"#")) + b"\n"
        xhigh_manual = b"\n".join(line for line in self.xhigh_template.splitlines() if not line.startswith(b"#")) + b"\n"
        self.target.write_bytes(manual)
        self.xhigh_target.write_bytes(xhigh_manual)
        plan = self.dry_run()
        self.assertEqual(plan["action"], "mixed")
        self.assertEqual(self.agent(plan, "sacha_luna_worker")["action"], "conflict")
        self.assertEqual(self.agent(plan, "sacha_luna_worker_xhigh")["action"], "conflict")
        result = setup_agents.run_setup(codex_home=self.codex_home, write=True)
        self.assertEqual(result["transaction"], "no_write")
        self.assertEqual(self.target.read_bytes(), manual)
        self.assertEqual(self.xhigh_target.read_bytes(), xhigh_manual)
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())

    def test_unmanaged_conflict_is_refused(self) -> None:
        self.target.parent.mkdir()
        original = b'name = "custom"\nmodel = "custom"\n'
        self.target.write_bytes(original)
        plan = self.dry_run()
        self.assertEqual(self.agent(plan, "sacha_luna_worker")["action"], "conflict")
        self.assertEqual(self.agent(plan, "sacha_luna_worker_xhigh")["action"], "create")
        self.assertEqual(self.agent(plan, "sacha_deepseek_worker")["action"], "create")
        self.assertEqual(self.agent(plan, "sacha_deepseek_pro_worker")["action"], "create")
        self.assertEqual(self.agent(plan, "sacha_k3_worker")["action"], "create")
        result = self.apply(plan)
        self.assertEqual((result["status"], result["transaction"]), ("refused", "no_write"))
        self.assertEqual(self.target.read_bytes(), original)
        self.assertFalse(self.xhigh_target.exists())
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())

    def test_owner_marker_with_wrong_identity_is_refused(self) -> None:
        self.target.parent.mkdir()
        self.target.write_bytes(setup_agents.OWNER_MARKER.encode() + b'\nname = "custom"\n')
        plan = self.dry_run()
        self.assertEqual(self.agent(plan, "sacha_luna_worker")["action"], "conflict")
        result = self.apply(plan)
        self.assertEqual(result["transaction"], "no_write")
        self.assertFalse(self.xhigh_target.exists())
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())

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
        result = json.loads(completed.stdout)
        self.assertEqual((result["status"], result["transaction"]), ("ok", "written"))
        self.assertEqual(self.target.read_bytes(), self.template)
        self.assertEqual(self.xhigh_target.read_bytes(), self.xhigh_template)
        self.assertEqual(self.deepseek_target.read_bytes(), self.deepseek_template)
        self.assertEqual(self.deepseek_pro_target.read_bytes(), self.deepseek_pro_template)
        self.assertEqual(self.k3_target.read_bytes(), self.k3_template)

    def test_managed_update_runs_on_explicit_write(self) -> None:
        self.target.parent.mkdir()
        old = setup_agents.OWNER_MARKER.encode() + b'\nname = "sacha_luna_worker"\nmodel = "old"\n'
        self.target.write_bytes(old)
        plan = self.dry_run()
        self.assertEqual(self.agent(plan, "sacha_luna_worker")["action"], "update")
        self.assertEqual(self.agent(plan, "sacha_luna_worker_xhigh")["action"], "create")
        self.assertEqual(self.agent(plan, "sacha_deepseek_worker")["action"], "create")
        self.assertEqual(self.agent(plan, "sacha_deepseek_pro_worker")["action"], "create")
        self.assertEqual(self.agent(plan, "sacha_k3_worker")["action"], "create")
        updated = self.apply(plan)
        self.assertEqual(updated["transaction"], "written")
        self.assertEqual(self.target.read_bytes(), self.template)
        self.assertEqual(self.xhigh_target.read_bytes(), self.xhigh_template)
        self.assertEqual(self.deepseek_target.read_bytes(), self.deepseek_template)
        self.assertEqual(self.deepseek_pro_target.read_bytes(), self.deepseek_pro_template)
        self.assertEqual(self.k3_target.read_bytes(), self.k3_template)

    def test_legacy_generic_files_are_untouched(self) -> None:
        legacy = self.codex_home / "agents" / "luna-worker.toml"
        legacy.parent.mkdir()
        original = b'name = "luna_worker"\n'
        legacy.write_bytes(original)
        result = self.apply()
        self.assertEqual(result["transaction"], "written")
        self.assertEqual(legacy.read_bytes(), original)

    def test_target_change_after_planning_refuses_without_write(self) -> None:
        changed = b'name = "changed"\n'

        def change_preimage() -> None:
            self.target.parent.mkdir(exist_ok=True)
            self.target.write_bytes(changed)

        result = self.apply(_test_hooks={"before_preimage_check": change_preimage})
        self.assertEqual((result["status"], result["transaction"]), ("refused", "no_write"))
        self.assertEqual(self.target.read_bytes(), changed)
        self.assertFalse(self.xhigh_target.exists())
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())

    def test_invalid_template_is_refused_without_write(self) -> None:
        bad_template = self.root / "bad.toml"
        bad_template.write_text(setup_agents.OWNER_MARKER + "\nname = [", encoding="utf-8")
        result = setup_agents.run_setup(
            codex_home=self.codex_home,
            _template_paths={"sacha_luna_worker": bad_template},
        )
        self.assertEqual(result["transaction"], "no_write")
        self.assertFalse(self.target.exists())
        self.assertFalse(self.xhigh_target.exists())
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())

    def test_post_write_failure_rolls_back_preimage(self) -> None:
        self.target.parent.mkdir()
        old = setup_agents.OWNER_MARKER.encode() + b'\nname = "sacha_luna_worker"\nmodel = "old"\n'
        self.target.write_bytes(old)
        plan = self.dry_run()

        replaced = []

        def fail_after_replace(target: Path) -> None:
            replaced.append(target)
            if len(replaced) == 2:
                raise RuntimeError("injected post-write failure")

        result = self.apply(plan, _test_hooks={"after_replace": fail_after_replace})
        self.assertEqual((result["status"], result["transaction"]), ("refused", "rolled_back"))
        self.assertEqual(self.target.read_bytes(), old)
        self.assertFalse(self.xhigh_target.exists())
        self.assertFalse(self.deepseek_target.exists())
        self.assertFalse(self.deepseek_pro_target.exists())
        self.assertFalse(self.k3_target.exists())


if __name__ == "__main__":
    unittest.main()
