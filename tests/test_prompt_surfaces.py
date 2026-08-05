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

    def test_clarify_flow_preserves_human_dialogue_and_artifacts(self) -> None:
        using_sacha = (PLUGIN / "skills" / "using-sacha" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        clarify = (PLUGIN / "skills" / "clarify" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        planner = (PLUGIN / "skills" / "planner" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("只证明表面 Scope，不证明数据语义", using_sacha)
        self.assertIn("决定权属于 Human", clarify)
        self.assertIn("多选工具的自由输入仍是普通 Human 对话", clarify)
        self.assertIn("疑问或调查请求先回答，再回到原问题", clarify)
        self.assertIn("第一个会影响方案的决定一经确认", clarify)
        self.assertIn("在提出下一问题前写入", clarify)
        self.assertIn("先把完整方案写入 `spec.md` 并回读", planner)
        self.assertIn("对话中的完整或简化 Spec 都不能替代落盘文件", planner)

if __name__ == "__main__":
    unittest.main()
