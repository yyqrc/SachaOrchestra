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


class RuntimeScenarioVerifierTests(unittest.TestCase):
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
