from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_dsh_subagents.py")
SPEC = importlib.util.spec_from_file_location("validate_dsh_subagents", VALIDATOR)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class DshSubagentBundleTests(unittest.TestCase):
    def test_repository_bundle_passes(self) -> None:
        payload = validator.validate_bundle()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["surfaces"], ["sacha_research", "sacha_worker", "sacha_review"])

    def test_missing_depth_guard_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = validator.BUNDLE
            (root / "package.json").write_bytes((source / "package.json").read_bytes())
            patch = (source / "cordis.patch.yml").read_text(encoding="utf-8")
            patch = patch.replace("        maxDepth: 1\n", "", 1)
            (root / "cordis.patch.yml").write_text(patch, encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "maxDepth"):
                validator.validate_bundle(root)

    def test_agent_team_reintroduction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = validator.BUNDLE
            (root / "package.json").write_bytes((source / "package.json").read_bytes())
            patch = (source / "cordis.patch.yml").read_text(encoding="utf-8") + "\n# spawn_teammate\n"
            (root / "cordis.patch.yml").write_text(patch, encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "Agent Teams"):
                validator.validate_bundle(root)


if __name__ == "__main__":
    unittest.main()
