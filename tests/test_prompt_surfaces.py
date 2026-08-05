"""Structural budgets for resident discovery prompts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"
SKILL_DOCUMENTS = tuple(sorted((PLUGIN / "skills").glob("*/SKILL.md")))
SKILL_METADATA = tuple(sorted((PLUGIN / "skills").glob("*/agents/openai.yaml")))


class PromptSurfaceTests(unittest.TestCase):
    def test_discovery_surfaces_only_carry_bounded_entry_text(self) -> None:
        violations = []
        for path in SKILL_DOCUMENTS:
            content = path.read_text(encoding="utf-8")
            match = re.search(r"(?m)^description: (.+)$", content)
            if match is None or len(match.group(1)) > 100:
                violations.append(f"{path.relative_to(ROOT)}:description")
        for path in SKILL_METADATA:
            content = path.read_text(encoding="utf-8")
            match = re.search(r'(?m)^  default_prompt: "([^"]+)"$', content)
            if match is None or len(match.group(1)) > 90:
                violations.append(f"{path.relative_to(ROOT)}:default_prompt")
        self.assertEqual([], violations, "discovery text must remain an entrypoint, not a workflow summary")

    def test_active_planner_has_a_canonical_clarify_route(self) -> None:
        planner = (PLUGIN / "skills" / "planner" / "SKILL.md").read_text(encoding="utf-8")
        using_sacha = (PLUGIN / "skills" / "using-sacha" / "SKILL.md").read_text(encoding="utf-8")
        clarify_metadata = (
            PLUGIN / "skills" / "clarify" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")

        self.assertIn("$sacha-orchestra:clarify", planner)
        self.assertIn("$sacha-orchestra:clarify", using_sacha)
        self.assertIn("allow_implicit_invocation: false", clarify_metadata)

    def test_clarify_keeps_adaptive_intents_and_dialogue_loop(self) -> None:
        clarify = (PLUGIN / "skills" / "clarify" / "SKILL.md").read_text(encoding="utf-8")
        planner = (PLUGIN / "skills" / "planner" / "SKILL.md").read_text(encoding="utf-8")
        artifact = (PLUGIN / "core" / "artifact-protocol.md").read_text(encoding="utf-8")

        for intent in ("`brainstorm`", "`survey`", "`grill`"):
            self.assertIn(intent, clarify)
        self.assertIn("不是让 Human 选择的模式、固定阶段或顺序", clarify)
        self.assertRegex(clarify, r"猜想与推测.*调查线索")
        self.assertRegex(clarify, r"先调查真实来源再解释")
        self.assertRegex(clarify, r"回到刚才尚未解决的决策")
        self.assertRegex(clarify, r"反例和具体场景.*可证伪验收")
        self.assertRegex(clarify, r"澄清锚点.*原始问题/目标.*阻塞性未决项.*暂存的新思路")
        self.assertRegex(clarify, r"新思路不能静默替换澄清锚点")
        self.assertRegex(clarify, r"够了.*开始吧.*阻塞性未决项")
        self.assertIn("Clarify 返回本身不等于澄清完成", planner)
        self.assertRegex(artifact, r"多轮/分支/压缩恢复.*澄清锚点")

    def test_clarify_context_and_frontier_keep_cross_context_consumers(self) -> None:
        clarify = (PLUGIN / "skills" / "clarify" / "SKILL.md").read_text(encoding="utf-8")
        planner = (PLUGIN / "skills" / "planner" / "SKILL.md").read_text(encoding="utf-8")
        artifact = (PLUGIN / "core" / "artifact-protocol.md").read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "integrations" / "capability-provider-guide.md").read_text(
            encoding="utf-8"
        )

        for token in ("有界挑战图", "最小可恢复 frontier", "尚未询问", "project-context 候选"):
            self.assertIn(token, clarify)
        self.assertIn("不遍历历史任务目录", clarify)
        self.assertIn("相关项目 `CONTEXT.md`", planner)
        self.assertIn("项目 context 候选不因记录而成为项目事实", artifact)
        self.assertRegex(guide, r"术语 owner/locator.*代码/文档冲突.*跨版本压力场景")
        self.assertIn("不创建项目词典", guide)


if __name__ == "__main__":
    unittest.main()
