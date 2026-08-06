"""Static prompt/adapter shape checks; these do not prove Codex runtime behavior."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"


def read(relative: str) -> str:
    return (PLUGIN / relative).read_text(encoding="utf-8")


def slice_between(text: str, start: str, end: str | None = None) -> str:
    section = text.split(start, 1)[1]
    return section if end is None else section.split(end, 1)[0]


class PromptSurfaceTests(unittest.TestCase):
    def test_clarify_entry_is_explicit(self) -> None:
        planner = read("skills/planner/SKILL.md")
        using_sacha = read("skills/using-sacha/SKILL.md")
        metadata = read("skills/clarify/agents/openai.yaml")

        self.assertRegex(planner, r"\$sacha-orchestra:clarify")
        self.assertRegex(using_sacha, r"\$sacha-orchestra:clarify")
        self.assertRegex(metadata, r"allow_implicit_invocation:\s*false")

    def test_codex_route_layers_are_ordered_and_role_neutral(self) -> None:
        codex = read("adapters/codex/runtime-adapter.md")
        layer_a = codex.index("### A. Assessment input")
        layer_b = codex.index("### B. Ordered route decision")
        layer_c = codex.index("### C. Exact `spawn_agent` mapping")
        fallback = codex.index("### 3.1 Single fallback route")
        self.assertLess(layer_a, layer_b)
        self.assertLess(layer_b, layer_c)
        self.assertLess(layer_c, fallback)

        assessment = slice_between(codex, "### A. Assessment input", "### B.")
        for token in ("exact route", "broad", "bounded", "critical / standard", "nontrivial / light", "writer", "Reviewer 独立性"):
            with self.subTest(token=token):
                self.assertRegex(assessment, re.escape(token))

        decision = slice_between(codex, "### B. Ordered route decision", "### C.")
        route_ids = re.findall(r"(?m)^\d+\.\s+`([a-z_]+)`", decision)
        self.assertEqual(
            ["human_exact", "sol_xhigh", "sol_medium", "luna_max", "luna_xhigh"],
            route_ids,
        )
        self.assertRegex(decision, r"首个命中即停止|first hit wins")
        self.assertRegex(decision, r"形态 × 负荷")
        self.assertTrue(all(role in codex for role in ("Planner", "Manager", "Reviewer", "Executor", "Clarify")))

    def test_codex_mapping_and_single_fallback_are_exact(self) -> None:
        codex = read("adapters/codex/runtime-adapter.md")
        mapping = slice_between(codex, "### C. Exact `spawn_agent` mapping", "### 3.1")
        rows = {
            match.group(1): match.group(2)
            for match in re.finditer(r"(?m)^\| `([a-z_]+)` \| (.+) \|$", mapping)
        }
        self.assertEqual({"human_exact", "sol_xhigh", "sol_medium", "luna_max", "luna_xhigh"}, set(rows))
        self.assertRegex(rows["sol_xhigh"], r'model="gpt-5\.6-sol".*reasoning_effort="xhigh"')
        self.assertRegex(rows["sol_medium"], r'model="gpt-5\.6-sol".*reasoning_effort="medium"')
        self.assertRegex(rows["luna_max"], r'agent_type="sacha_luna_worker"')
        self.assertRegex(rows["luna_xhigh"], r'agent_type="sacha_luna_worker_xhigh"')
        automatic = "\n".join(rows[name] for name in ("sol_xhigh", "sol_medium", "luna_max", "luna_xhigh"))
        self.assertNotRegex(automatic, r'gpt-5\.6-terra|reasoning_effort="(?:high|max|ultra)"')

        fallback = slice_between(codex, "### 3.1 Single fallback route")
        for pattern in (
            r"实际报告.*unavailable/failed",
            r"尚未 accepted/started",
            r"同一 Task/Scope/revision",
            r"没有写入迹象",
            r"terminal/cancelled",
            r"独立性仍明确",
            r"精确 Human/Scope 配置失败",
            r"fallback 再失败",
            r"不得连续试多档模型",
        ):
            with self.subTest(pattern=pattern):
                self.assertRegex(fallback, pattern)
        self.assertRegex(fallback, r"luna_max.*gpt-5\.6-sol.*reasoning_effort=\"medium\"")
        self.assertRegex(fallback, r"sol_xhigh.*停止，不 fallback")
        self.assertNotRegex(fallback, r"gpt-5\.6-terra|reasoning_effort=\"high\"")

    def test_readme_defers_ready_evaluation_to_manager(self) -> None:
        readme = read("README.md")
        flow = slice_between(readme, "```mermaid", "```")
        owner = flow.index("owner 发现多个候选")
        manager = flow.index("Manager：评估")
        ready = flow.index("Manager ready 评估")
        self.assertLess(owner, manager)
        self.assertLess(manager, ready)
        self.assertNotRegex(flow[:manager], r"ready")
        self.assertRegex(readme, r"Manager.*评估、拆分、依赖.*派发.*归并")
        self.assertRegex(readme, r"static|静态")


if __name__ == "__main__":
    unittest.main()
