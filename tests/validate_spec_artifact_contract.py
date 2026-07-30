"""Contract and production-entry regressions for Spec Artifact persistence."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"
GENERATOR_PATH = (
    PLUGIN
    / "skills"
    / "setup-project"
    / "scripts"
    / "generate_project_integration.py"
)
TEMP_ROOT = ROOT / ".temp"


def load_generator():
    module_spec = importlib.util.spec_from_file_location(
        "sacha_spec_storage_generator",
        GENERATOR_PATH,
    )
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    return module


generator = load_generator()


class SpecArtifactContractTests(unittest.TestCase):
    def test_core_workflow_and_planner_have_one_persistence_term(self) -> None:
        artifact = (PLUGIN / "core" / "artifact-protocol.md").read_text(encoding="utf-8")
        workflow = (PLUGIN / "core" / "workflow-contract.md").read_text(encoding="utf-8")
        planner = (PLUGIN / "skills" / "planner" / "SKILL.md").read_text(encoding="utf-8")
        codex_adapter = (PLUGIN / "adapters" / "codex" / "runtime-adapter.md").read_text(
            encoding="utf-8"
        )
        claude_adapter = (
            PLUGIN / "adapters" / "claudecode" / "runtime-adapter.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Spec Artifact", artifact)
        self.assertIn("Spec Artifact", workflow)
        self.assertIn("Plan 只表示按需规划活动或 inline plan", workflow)
        self.assertIn("Spec storage", planner)
        self.assertIn("默认写入 `spec.md`", planner)
        for adapter in (codex_adapter, claude_adapter):
            self.assertIn("Workflow Contract 10", adapter)
            self.assertIn("Artifact Protocol 4", adapter)

        old_artifact_name = "Plan" + " Artifact"
        self.assertNotIn(old_artifact_name, artifact)
        self.assertNotIn(old_artifact_name, workflow)
        self.assertNotIn(old_artifact_name, planner)

    def test_setup_public_api_and_generated_output_are_spec_only(self) -> None:
        option_strings = generator.build_parser()._option_string_actions
        self.assertIn("--spec-root-kind", option_strings)
        self.assertIn("--spec-root", option_strings)
        old_option_prefix = "--" + "pla" + "n-root"
        self.assertNotIn(old_option_prefix, option_strings)
        self.assertNotIn(old_option_prefix + "-kind", option_strings)

        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="spec-contract-", dir=TEMP_ROOT) as raw:
            project = Path(raw)
            result = generator.run_setup(
                generator.SetupConfig(
                    project_root=project,
                    manage_agents=False,
                    scm_provider="none",
                    spec_root_kind="project-relative",
                    spec_root="docs/plans",
                    documentation_policy="disabled",
                )
            )

        self.assertEqual(("ready", "dry_run"), (result["status"], result["transaction"]))
        self.assertEqual(
            {
                "root_kind": "project-relative",
                "root": "docs/plans",
                "portability": "portable",
                "directory_pattern": "<YYYY-MM-DD>-<short-slug>/",
                "file_name": "spec.md",
            },
            result["spec_storage"],
        )
        generated = result["workflow_rule"]["planned_content"]
        self.assertIn("- Spec：`docs/plans`", generated)
        old_label = "- " + "Pla" + "n："
        self.assertNotIn(old_label, generated)

    def test_active_consumers_do_not_reintroduce_old_storage_identifiers(self) -> None:
        active_paths = (
            PLUGIN / "core" / "artifact-protocol.md",
            PLUGIN / "core" / "workflow-contract.md",
            PLUGIN / "adapters" / "codex" / "runtime-adapter.md",
            PLUGIN / "adapters" / "claudecode" / "runtime-adapter.md",
            PLUGIN / "skills" / "planner" / "SKILL.md",
            PLUGIN / "skills" / "executor" / "SKILL.md",
            PLUGIN / "skills" / "setup-project" / "SKILL.md",
            PLUGIN / "skills" / "project-documentation" / "SKILL.md",
            GENERATOR_PATH,
            ROOT / "docs" / "integrations" / "capability-provider-guide.md",
        )
        old_noun = "pla" + "n"
        forbidden = (
            old_noun + "_storage",
            old_noun + "_root",
            "--" + old_noun + "-root",
            "Plan" + " storage",
            "Plan" + " Artifact",
            old_noun + ".md",
        )
        for path in active_paths:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{token!r} remains in {path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
