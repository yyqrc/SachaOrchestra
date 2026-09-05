from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path(__file__).with_name("validate_dsh_companion.py")
VALIDATOR_SPEC = importlib.util.spec_from_file_location("validate_dsh_companion", VALIDATOR)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validator)

RELEASE_SCRIPT = ROOT / "scripts" / "release.py"
RELEASE_SPEC = importlib.util.spec_from_file_location("release_for_dsh_companion", RELEASE_SCRIPT)
assert RELEASE_SPEC and RELEASE_SPEC.loader
release = importlib.util.module_from_spec(RELEASE_SPEC)
RELEASE_SPEC.loader.exec_module(release)


def copy_candidate(root: Path) -> None:
    source = validator.PACKAGE
    (root / "src").mkdir(parents=True)
    (root / "package.json").write_bytes((source / "package.json").read_bytes())
    (root / "cordis.patch.yml").write_bytes((source / "cordis.patch.yml").read_bytes())
    (root / "src" / "tool-surface-policy.ts").write_bytes(
        (source / "src" / "tool-surface-policy.ts").read_bytes()
    )


class DshCompanionTests(unittest.TestCase):
    def test_repository_companion_passes(self) -> None:
        payload = validator.validate_companion()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["surfaces"], ["sacha_research", "sacha_worker", "sacha_review"])

    def test_release_maps_companion_machine_files_to_direct_validator(self) -> None:
        paths = [
            "integrations/dsh/sacha-companion/package.json",
            "integrations/dsh/sacha-companion/cordis.patch.yml",
            "integrations/dsh/sacha-companion/src/tool-surface-policy.ts",
        ]
        commands = release.validation_commands(
            "0.1.0",
            paths,
            deltas={path: (None, "candidate\n") for path in paths},
        )
        unittest_commands = {
            command[4]
            for command in commands
            if len(command) == 5 and command[1:4] == ("-B", "-m", "unittest")
        }
        self.assertIn("tests.test_dsh_companion", unittest_commands)
        validator_command = (release.current_python(), "-B", release.DSH_COMPANION_VALIDATOR)
        self.assertEqual(commands.count(validator_command), 1)

    def test_missing_depth_guard_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_candidate(root)
            patch = (root / "cordis.patch.yml").read_text(encoding="utf-8")
            (root / "cordis.patch.yml").write_text(
                patch.replace("        maxDepth: 1\n", "", 1), encoding="utf-8"
            )
            with self.assertRaises(validator.ValidationError):
                validator.validate_companion(root)

    def test_agent_team_reintroduction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_candidate(root)
            patch = (root / "cordis.patch.yml").read_text(encoding="utf-8") + "\n# spawn_teammate\n"
            (root / "cordis.patch.yml").write_text(patch, encoding="utf-8")
            with self.assertRaises(validator.ValidationError):
                validator.validate_companion(root)

    def test_research_allowlist_expansion_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_candidate(root)
            patch = (root / "cordis.patch.yml").read_text(encoding="utf-8")
            patch = patch.replace("            - skill\n", "            - skill\n            - mcp_untrusted\n", 1)
            (root / "cordis.patch.yml").write_text(patch, encoding="utf-8")
            with self.assertRaises(validator.ValidationError):
                validator.validate_companion(root)

    def test_stale_dsh_peer_range_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_candidate(root)
            package = json.loads((root / "package.json").read_text(encoding="utf-8"))
            package["peerDependencies"]["@deepseek-ai/dsh-tool-subagent"] = "^0.1.0-rc.6"
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            with self.assertRaises(validator.ValidationError):
                validator.validate_companion(root)

    def test_empty_machine_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_candidate(root)
            package_path = root / "package.json"
            package = json.loads(package_path.read_text(encoding="utf-8"))
            package["version"] = ""
            package_path.write_text(json.dumps(package), encoding="utf-8")
            with self.assertRaises(validator.ValidationError):
                validator.validate_companion(root)

    def test_packed_identity_must_match_package_machine_fields(self) -> None:
        package = validator.packed_package(
            json.dumps(
                {
                    "name": "@sacha-orchestra/dsh-companion",
                    "version": "0.2.0",
                    "files": [{"path": "package.json"}],
                }
            )
        )
        validator.validate_packed_identity(
            package, "@sacha-orchestra/dsh-companion", "0.2.0"
        )
        self.assertEqual(validator.packed_paths(package), {"package.json"})
        with self.assertRaises(validator.ValidationError):
            validator.validate_packed_identity(
                package, "@sacha-orchestra/dsh-companion", "0.2.1"
            )


if __name__ == "__main__":
    unittest.main()
