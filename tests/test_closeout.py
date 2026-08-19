"""Behavior tests for the closeout production entrypoint."""

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from project_test_support import CLOSEOUT_SCRIPT, ProjectTestCase, closeout


class CloseoutTests(ProjectTestCase):
    def create_spec(self, name: str, status: str = "Human 已批准实施") -> Path:
        spec = self.root / name / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(
            f"# 测试 Spec\n\n> 状态：{status}\n\n## Scope\n\n保持正文。\n",
            encoding="utf-8",
        )
        return spec

    def complete(self, paths, **overrides):
        values = {
            "spec_paths": paths,
            "goal_status": "goal_complete",
            "required_checks_satisfied": True,
            "context_writable": True,
        }
        values.update(overrides)
        return closeout.complete_spec(**values)

    def test_completion_requires_one_current_approved_spec_and_legal_terminal(self) -> None:
        approved = self.create_spec("approved")
        other = self.create_spec("other")
        unapproved = self.create_spec("unapproved", "待 Human Review")
        original = approved.read_bytes()

        cases = (
            self.complete([]),
            self.complete([approved, other]),
            self.complete([approved], goal_status="goal_partial"),
            self.complete([approved], required_checks_satisfied=False),
            self.complete([approved], context_writable=False),
            self.complete([unapproved]),
        )
        for result in cases:
            self.assertEqual(("refused", "no_write"), (result["status"], result["transaction"]))
        self.assertEqual(original, approved.read_bytes())
        self.assertIn("待 Human Review", unapproved.read_text(encoding="utf-8"))

    def test_cli_returns_only_the_spec_completion_plan(self) -> None:
        spec = self.create_spec("cli")
        process = subprocess.run(
            (
                sys.executable,
                "-B",
                str(CLOSEOUT_SCRIPT),
                "--spec-path",
                str(spec),
                "--goal-status",
                "goal_complete",
                "--required-checks-satisfied",
                "--context-writable",
            ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(("ready", "dry_run"), (result["status"], result["transaction"]))
        self.assertEqual("> 状态：Human 已批准实施", result["edit"]["before"])

    def test_negative_english_approval_states_fail_closed(self) -> None:
        for index, status in enumerate(("unapproved", "not approved", "disapproved")):
            with self.subTest(status=status):
                spec = self.create_spec(f"negative-{index}", status)
                before = spec.read_bytes()
                result = self.complete([spec])
                self.assertEqual(("refused", "no_write"), (result["status"], result["transaction"]))
                self.assertEqual(before, spec.read_bytes())

        approved = self.create_spec("english-approved", "Approved; revision 3")
        self.assertEqual("ready", self.complete([approved])["status"])

    def test_completion_plan_is_in_place_and_does_not_create_documentation(self) -> None:
        spec = self.create_spec("in-place")
        original_parent = spec.parent.resolve()
        original_body = spec.read_text(encoding="utf-8").split("## Scope", 1)[1]

        preview = self.complete([spec])
        self.assertEqual(("ready", "dry_run"), (preview["status"], preview["transaction"]))
        self.assertIn("Human 已批准实施", spec.read_text(encoding="utf-8"))
        self.assertEqual(
            {"line_number": 3, "before": "> 状态：Human 已批准实施", "after": "> 状态：已完成"},
            preview["edit"],
        )

        content = spec.read_text(encoding="utf-8")
        self.assertEqual(1, content.count(preview["edit"]["before"]))
        spec.write_text(
            content.replace(preview["edit"]["before"], preview["edit"]["after"], 1),
            encoding="utf-8",
        )
        self.assertEqual(original_parent, spec.parent.resolve())
        self.assertEqual(spec.resolve(), Path(preview["target"]))
        content = spec.read_text(encoding="utf-8")
        self.assertIn("> 状态：已完成", content)
        self.assertEqual(original_body, content.split("## Scope", 1)[1])
        self.assertFalse((self.root / "in-place" / "docs" / "done").exists())
        self.assertFalse((self.root / "in-place" / "docs" / "archive").exists())

        repeated = self.complete([spec])
        self.assertEqual(("no_op", "no_changes"), (repeated["status"], repeated["transaction"]))

    def test_changed_status_line_replans_exact_edit_and_read_only_fails(self) -> None:
        changed = self.create_spec("changed")
        first = self.complete([changed])
        changed.write_text(
            changed.read_text(encoding="utf-8").replace(
                "> 状态：Human 已批准实施",
                "> 状态：Human 已批准修订 2",
            ),
            encoding="utf-8",
        )
        second = self.complete([changed])
        self.assertEqual("ready", second["status"])
        self.assertNotEqual(first["edit"]["before"], second["edit"]["before"])
        self.assertEqual("> 状态：Human 已批准修订 2", second["edit"]["before"])

        readonly = self.create_spec("readonly")
        current_mode = readonly.stat().st_mode
        try:
            os.chmod(readonly, stat.S_IREAD)
            refused = self.complete([readonly])
            self.assertEqual(("refused", "no_write"), (refused["status"], refused["transaction"]))
            self.assertIn("read-only", refused["conflicts"][0])
        finally:
            os.chmod(readonly, current_mode)

    def test_missing_or_duplicate_header_status_fails_closed(self) -> None:
        missing = self.root / "missing" / "spec.md"
        missing.parent.mkdir()
        missing.write_text("# Spec\n\n## Scope\n", encoding="utf-8")
        duplicate = self.create_spec("duplicate")
        duplicate.write_text(
            "# Spec\n\n> 状态：Human 已批准实施\n- 状态：Human 已批准实施\n\n## Scope\n",
            encoding="utf-8",
        )
        for path in (missing, duplicate):
            with self.subTest(path=path):
                result = self.complete([path])
                self.assertEqual(("refused", "no_write"), (result["status"], result["transaction"]))
