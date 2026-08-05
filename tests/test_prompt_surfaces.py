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

if __name__ == "__main__":
    unittest.main()
