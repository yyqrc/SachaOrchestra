from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "tests" / "runtime-scenarios" / "packs"


def readonly_result() -> dict:
    cwd_output = "C:\\workspace\r\n"
    return {
        "asset_sha256": "0" * 64,
        "baseline": {
            "outer_call_count": 2,
            "goal_tool": "get_goal",
            "shell_tool": "exec_command",
            "goal": None,
            "cwd_exit_code": 0,
            "cwd_output": cwd_output,
        },
        "code_mode": {
            "outer_call_count": 1,
            "nested_call_count": 2,
            "payload": {
                "schema_version": 1,
                "status": "settled",
                "results": [
                    {
                        "unit_id": "goal_snapshot",
                        "status": "fulfilled",
                        "value": {"goal": None},
                        "references": {},
                    },
                    {
                        "unit_id": "cwd_snapshot",
                        "status": "fulfilled",
                        "value": {"exit_code": 0, "output": cwd_output},
                        "references": {},
                    },
                ],
            },
        },
        "retry_count": 0,
        "agent_tool_call_count": 0,
        "human_prompt_count": 0,
        "evidence_layers": {
            "source_scenario": True,
            "current_runtime": True,
            "installed_fresh_runtime": False,
        },
    }


def v1_result() -> dict:
    return {
        "template_version": "codex-code-mode-batch-v1",
        "collaboration_interface": "v1",
        "retry_count": 0,
        "human_agent_tree_prompt_count": 0,
        "projection_preflight": {
            "status": "rejected_before_tasks",
            "agent_id": None,
            "error": "code_mode_projection_fields_invalid:projection-preflight:result_fields",
        },
        "small_limit_preflight": {
            "status": "rejected_before_tasks",
            "agent_id": None,
            "error": "code_mode_output_limit_too_small:191",
        },
        "batch_results": [
            {
                "unit_id": "alpha",
                "spawn_status": "started",
                "agent_id": "agent-alpha",
                "terminal_status": "completed",
                "summary": {"count": 3, "sum": 12},
            },
            {
                "unit_id": "beta",
                "spawn_status": "started",
                "agent_id": "agent-beta",
                "terminal_status": "completed",
                "summary": {"count": 3, "sum": 18},
            },
            {
                "unit_id": "controlled-rejection",
                "spawn_status": "rejected",
                "agent_id": None,
                "error": "unknown agent_type",
            },
        ],
    }


class RuntimeScenarioVerifierTests(unittest.TestCase):
    def run_verifier(self, pack_name: str, result: dict) -> subprocess.CompletedProcess[str]:
        fixture = PACKS / pack_name / "fixture"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            for source in fixture.iterdir():
                shutil.copy2(source, target / source.name)
            (target / "result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [sys.executable, "-B", str(target / "verify.py")],
                cwd=target,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )

    def run_explore_verifier(self, *, with_unexpected_file: bool = False) -> subprocess.CompletedProcess[str]:
        pack = PACKS / "explore-shared-context-loop"
        fixture = pack / "fixture"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            for source in fixture.iterdir():
                shutil.copy2(source, target / source.name)
            shutil.copy2(pack / "task.md", target / "instructions.md")
            shutil.copy2(ROOT / "tests" / "runtime-scenarios" / "assets" / "workspace-AGENTS.md", target / "AGENTS.md")
            if with_unexpected_file:
                (target / "unexpected.md").write_text("unexpected\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-B", str(target / "verify.py")],
                cwd=target,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )

    def run_using_sacha_semantic_turn_verifier(
        self,
        *,
        with_unexpected_file: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        pack = PACKS / "using-sacha-semantic-turn"
        fixture = pack / "fixture"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            for source in fixture.iterdir():
                shutil.copy2(source, target / source.name)
            shutil.copy2(pack / "task.md", target / "instructions.md")
            shutil.copy2(ROOT / "tests" / "runtime-scenarios" / "assets" / "workspace-AGENTS.md", target / "AGENTS.md")
            if with_unexpected_file:
                (target / "unexpected.md").write_text("unexpected\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-B", str(target / "verify.py")],
                cwd=target,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )

    def run_roadmap_verifier(self, *, with_unexpected_file: bool = False) -> subprocess.CompletedProcess[str]:
        pack = PACKS / "roadmap-self-contained-document"
        fixture = pack / "fixture"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            shutil.copytree(fixture, target, dirs_exist_ok=True)
            shutil.copy2(pack / "task.md", target / "instructions.md")
            shutil.copy2(ROOT / "tests" / "runtime-scenarios" / "assets" / "workspace-AGENTS.md", target / "AGENTS.md")
            roadmap = target / "docs" / "roadmap" / "2026-08-19-depth-fetch-roadmap.md"
            roadmap.write_text("# Roadmap fixture\n", encoding="utf-8")
            if with_unexpected_file:
                (target / "unexpected.md").write_text("unexpected\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-B", str(target / "verify.py")],
                cwd=target,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )

    def run_planner_verifier(self, *, corrupted: bool = False) -> subprocess.CompletedProcess[str]:
        fixture = PACKS / "planner-explore-manager-reviewer" / "fixture"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            for source in fixture.iterdir():
                shutil.copy2(source, target / source.name)
            for name in ("service-alpha.json", "service-beta.json"):
                path = target / name
                data = json.loads(path.read_text(encoding="utf-8"))
                timeout = data.pop("timeout_ms", data.get("request_timeout_ms"))
                data["schema_version"] = 2
                data["request_timeout_ms"] = timeout
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            if corrupted:
                path = target / "service-alpha.json"
                data = json.loads(path.read_text(encoding="utf-8"))
                data["request_timeout_ms"] = 1
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            return subprocess.run(
                [sys.executable, "-B", str(target / "verify.py")],
                cwd=target,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )

    def run_reviewer_semantic_probe(self) -> subprocess.CompletedProcess[str]:
        fixture = PACKS / "reviewer-semantic-chain" / "fixture"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            shutil.copytree(fixture, target, dirs_exist_ok=True)
            return subprocess.run(
                [sys.executable, "-B", str(target / "verify.py")],
                cwd=target,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )

    def test_bundled_verifiers_accept_valid_results(self) -> None:
        readonly = self.run_verifier("codex-code-mode-readonly-batch", readonly_result())
        self.assertEqual(readonly.returncode, 0, readonly.stdout + readonly.stderr)
        self.assertIn("OK: readonly Code Mode Runtime asset result verified", readonly.stdout)

        v1 = self.run_verifier("codex-code-mode-v1-batch", v1_result())
        self.assertEqual(v1.returncode, 0, v1.stdout + v1.stderr)
        self.assertIn("OK: canonical Code Mode batch result verified", v1.stdout)

        explore = self.run_explore_verifier()
        self.assertEqual(explore.returncode, 0, explore.stdout + explore.stderr)
        self.assertIn("OK: Explore scenario root remained read-only", explore.stdout)

        semantic_turn = self.run_using_sacha_semantic_turn_verifier()
        self.assertEqual(semantic_turn.returncode, 0, semantic_turn.stdout + semantic_turn.stderr)
        self.assertIn("OK: using-sacha semantic-turn scenario root remained read-only", semantic_turn.stdout)

        roadmap = self.run_roadmap_verifier()
        self.assertEqual(roadmap.returncode, 0, roadmap.stdout + roadmap.stderr)
        self.assertIn("OK: Roadmap created at", roadmap.stdout)

        planner = self.run_planner_verifier()
        self.assertEqual(planner.returncode, 0, planner.stdout + planner.stderr)
        self.assertIn("planner_explore_manager_reviewer_status=pass", planner.stdout)

    def test_bundled_verifiers_reject_corrupted_results(self) -> None:
        invalid_readonly = readonly_result()
        invalid_readonly["code_mode"]["nested_call_count"] = 1
        readonly = self.run_verifier("codex-code-mode-readonly-batch", invalid_readonly)
        self.assertEqual(readonly.returncode, 1)
        self.assertIn("Code Mode nested_call_count must be 2", readonly.stdout)

        invalid_v1 = v1_result()
        invalid_v1["batch_results"][1]["summary"]["sum"] = 17
        v1 = self.run_verifier("codex-code-mode-v1-batch", invalid_v1)
        self.assertEqual(v1.returncode, 1)
        self.assertIn("beta summary mismatch", v1.stdout)

        explore = self.run_explore_verifier(with_unexpected_file=True)
        self.assertEqual(explore.returncode, 1)
        self.assertIn("unexpected files", explore.stdout)

        semantic_turn = self.run_using_sacha_semantic_turn_verifier(with_unexpected_file=True)
        self.assertEqual(semantic_turn.returncode, 1)
        self.assertIn("unexpected files", semantic_turn.stdout)

        roadmap = self.run_roadmap_verifier(with_unexpected_file=True)
        self.assertEqual(roadmap.returncode, 1)
        self.assertIn("unexpected files", roadmap.stdout)

        planner = self.run_planner_verifier(corrupted=True)
        self.assertEqual(planner.returncode, 1)
        self.assertIn("request_timeout_ms must remain 30000", planner.stderr)

    def test_reviewer_semantic_fixture_exposes_claimed_failures(self) -> None:
        result = self.run_reviewer_semantic_probe()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["focused_test"]["exit_code"], 0)
        self.assertEqual(payload["cli_oversize"], {"exit_code": 0, "stdout": "123456789\n"})
        self.assertEqual(
            payload["checked_multibyte"],
            {"exit_code": 0, "stdout": "界界界\n", "utf8_bytes": 9},
        )


if __name__ == "__main__":
    unittest.main()
