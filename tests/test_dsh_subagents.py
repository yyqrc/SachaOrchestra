from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path(__file__).with_name("validate_dsh_subagents.py")
VALIDATOR_SPEC = importlib.util.spec_from_file_location("validate_dsh_subagents", VALIDATOR)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validator)

RELEASE_SCRIPT = ROOT / "scripts" / "release.py"
RELEASE_SPEC = importlib.util.spec_from_file_location("release_for_dsh_subagents", RELEASE_SCRIPT)
assert RELEASE_SPEC and RELEASE_SPEC.loader
release = importlib.util.module_from_spec(RELEASE_SPEC)
RELEASE_SPEC.loader.exec_module(release)


class DshSubagentBundleTests(unittest.TestCase):
    def test_repository_bundle_passes(self) -> None:
        payload = validator.validate_bundle()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["surfaces"], ["sacha_research", "sacha_worker", "sacha_review"])

    def test_release_maps_bundle_machine_files_to_direct_validator(self) -> None:
        paths = [
            "integrations/dsh/sacha-subagents/package.json",
            "integrations/dsh/sacha-subagents/cordis.patch.yml",
        ]
        commands = release.validation_commands(
            "0.1.0",
            paths,
            deltas={path: (None, "candidate\n") for path in paths},
        )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("tests.test_dsh_subagents", rendered)
        self.assertIn(release.DSH_SUBAGENTS_VALIDATOR, rendered)
        self.assertEqual(rendered.count(release.DSH_SUBAGENTS_VALIDATOR), 1)

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
