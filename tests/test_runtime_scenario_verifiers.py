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

    def test_bundled_verifiers_accept_valid_results(self) -> None:
        readonly = self.run_verifier("codex-code-mode-readonly-batch", readonly_result())
        self.assertEqual(readonly.returncode, 0, readonly.stdout + readonly.stderr)
        self.assertIn("OK: readonly Code Mode Runtime asset result verified", readonly.stdout)

        v1 = self.run_verifier("codex-code-mode-v1-batch", v1_result())
        self.assertEqual(v1.returncode, 0, v1.stdout + v1.stderr)
        self.assertIn("OK: canonical Code Mode batch result verified", v1.stdout)

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


if __name__ == "__main__":
    unittest.main()
