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
        self.assertIn("docs/plan", planner)
        self.assertIn("spec.md", planner)
        for adapter in (codex_adapter, claude_adapter):
            self.assertIn("Workflow Contract 12", adapter)
            self.assertIn("Artifact Protocol 6", adapter)

        old_artifact_name = "Plan" + " Artifact"
        self.assertNotIn(old_artifact_name, artifact)
        self.assertNotIn(old_artifact_name, workflow)
        self.assertNotIn(old_artifact_name, planner)

    def test_documentation_closeout_is_selective_and_keeps_publication_separate(self) -> None:
        workflow = (PLUGIN / "core" / "workflow-contract.md").read_text(encoding="utf-8")
        artifact = (PLUGIN / "core" / "artifact-protocol.md").read_text(encoding="utf-8")
        executor = (PLUGIN / "skills" / "executor" / "SKILL.md").read_text(encoding="utf-8")
        documentation = (
            PLUGIN / "skills" / "document-project" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Documentation candidate check（按需）", workflow)
        self.assertIn("候选必须有持久产品 delta", workflow)
        self.assertIn("没有上述持久知识的一行/局部修复，均静默跳过", workflow)
        self.assertIn("`on-request` 只询问一次是否生成", workflow)
        self.assertIn("`bounded-closeout | per-write-confirmation`", workflow)
        self.assertIn("只检查一次 Documentation candidate", executor)

        self.assertIn("Execution Report 只在恢复、证据索引或正式 Review 有消费者时", artifact)
        self.assertIn("`change-archive`/done 文档", artifact)
        self.assertIn("Project Documentation root", artifact)
        self.assertIn("Project Context path", artifact)

        self.assertIn("已批准复杂 Spec + 持久代码变化 + 实际 Runtime 验证", documentation)
        self.assertIn("必须形成一次候选检查", documentation)
        self.assertIn("一行修复、纯问答、无持久 delta：静默跳过", documentation)
        self.assertIn("`profiles.json`", documentation)
        self.assertIn("选择完成前不读模板正文", documentation)
        self.assertIn("不随机选择、不混合模板", documentation)
        self.assertIn("模板章节只是候选结构", documentation)
        self.assertIn("不要求复刻完整 heading skeleton", documentation)
        provider_guide = (ROOT / "docs" / "integrations" / "capability-provider-guide.md").read_text(
            encoding="utf-8"
        )
        for active_text in (workflow, artifact, executor, documentation, provider_guide):
            self.assertNotIn("CODM", active_text)
            self.assertNotIn("Rendering/Dawn", active_text)
            self.assertNotIn("G:\\COD", active_text)

    def test_setup_public_api_and_generated_output_are_spec_only(self) -> None:
        option_strings = generator.build_parser()._option_string_actions
        self.assertIn("--spec-base-kind", option_strings)
        self.assertIn("--spec-base", option_strings)
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
                    documentation_policy="disabled",
                )
            )

        self.assertEqual(("ready", "dry_run"), (result["status"], result["transaction"]))
        self.assertEqual(
            {
                "root_kind": "project-relative",
                "root": "docs/plan",
                "portability": "portable",
                "directory_pattern": "<YYYY-MM-DD>-<short-slug>/",
                "file_name": "spec.md",
            },
            result["spec_storage"],
        )
        generated = result["workflow_rule"]["planned_content"]
        self.assertIn("- Spec：`docs/plan`", generated)
        self.assertIn("- 任务目录：`<YYYY-MM-DD>-<short-slug>/`", generated)
        self.assertIn("- 文件：`spec.md`；澄清决定：`decisions.md`", generated)
        self.assertIn("- 项目 Context：`docs/CONTEXT.md`", generated)
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
            PLUGIN / "skills" / "document-project" / "SKILL.md",
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
