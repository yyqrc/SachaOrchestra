"""Guard release validation from drifting into prose-presence tests."""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tests" / "validate_release_coherence.py"
CJK = re.compile(r"[\u3400-\u9fff]")


def string_literals(node: ast.AST) -> list[str]:
    return [
        item.value
        for item in ast.walk(node)
        if isinstance(item, ast.Constant) and isinstance(item.value, str)
    ]


class ReleaseValidatorDesignTests(unittest.TestCase):
    def test_semantic_contracts_are_not_encoded_as_required_prose(self) -> None:
        tree = ast.parse(VALIDATOR.read_text(encoding="utf-8"))
        violations: list[str] = []

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Compare)
                and any(isinstance(operator, ast.In) for operator in node.ops)
                and isinstance(node.left, ast.Constant)
                and isinstance(node.left.value, str)
                and CJK.search(node.left.value)
            ):
                violations.append(f"inline-required-prose:{node.lineno}")
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [target.id for target in targets if isinstance(target, ast.Name)]
            value = node.value
            if value is None or not any(name.endswith("_contract") for name in names):
                continue
            if any(CJK.search(value) for value in string_literals(value)):
                violations.extend(f"{name}:{node.lineno}" for name in names)

        self.assertEqual(
            [],
            violations,
            "release validator must not require natural-language contract sentences; "
            "use structural checks plus scenario/behavior tests",
        )

    def test_text_surface_budgets_are_advisory(self) -> None:
        tree = ast.parse(VALIDATOR.read_text(encoding="utf-8"))
        blocking_budget_checks = [
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "check"
            and any("budget" in value.casefold() or "surface exceeds" in value.casefold() for value in string_literals(node))
        ]
        prompt_surface = ROOT / "tests" / "test_prompt_surfaces.py"
        prompt_tree = ast.parse(prompt_surface.read_text(encoding="utf-8"))
        blocking_budget_checks.extend(
            node.lineno
            for node in ast.walk(prompt_tree)
            if isinstance(node, ast.Compare)
            and any(isinstance(operator, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for operator in node.ops)
            and any(
                isinstance(item, ast.Call)
                and isinstance(item.func, ast.Name)
                and item.func.id == "len"
                for item in ast.walk(node)
            )
        )
        self.assertEqual([], blocking_budget_checks)


if __name__ == "__main__":
    unittest.main()
