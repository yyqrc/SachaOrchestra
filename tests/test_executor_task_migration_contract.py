"""Static migration/coordination invariants; Runtime behavior is unverified here."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"


def read(relative: str) -> str:
    return (PLUGIN / relative).read_text(encoding="utf-8")


def section(text: str, start: str, end: str | None = None) -> str:
    value = text.split(start, 1)[1]
    return value if end is None else value.split(end, 1)[0]


class ExecutorTaskMigrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = read("core/workflow-contract.md")
        cls.coordination = read("core/coordination-contract.md")
        cls.artifact = read("core/artifact-protocol.md")
        cls.codex = read("adapters/codex/runtime-adapter.md")
        cls.claude = read("adapters/claudecode/runtime-adapter.md")

    def test_explicit_migration_has_single_owner_transfer_and_no_source_join(self) -> None:
        feedback = section(self.codex, "### 2.2 Explicit Feedback repair transport", "### 2.3")
        migration = section(self.codex, "### 2.3 User-visible task migration", "## 3.")
        for transport in ("list_threads", "read_thread", "create_thread", "wait_threads"):
            self.assertIn(f"`{transport}`", feedback)
        self.assertRegex(feedback, r"唯一匹配.*复用")
        self.assertRegex(feedback, r"无匹配.*恰好一次 `create_thread`")
        self.assertRegex(feedback, r"上游 return consumer.*不得再进入.*migration")
        for pattern in (
            r"Task/Scope revision",
            r"批准 Spec reference",
            r"workflow transfer",
            r"恰好一次 `create_thread`",
            r"尚未产生 target owner",
            r"最小 handoff",
            r"Source.*结束",
            r"不调用 `wait_agent`",
            r"不.*terminal join",
            r"重复批准、重试或恢复.*同一 target reference",
        ):
            with self.subTest(pattern=pattern):
                self.assertRegex(migration, pattern)
        self.assertNotRegex(migration, r"Source.*等待.*return")
        self.assertRegex(self.coordination, r"target 接管 workflow owner")
        self.assertRegex(self.coordination, r"原 owner.*不 join、不等待 return")
        self.assertRegex(self.coordination, r"Feedback Source.*上游 return consumer")
        self.assertRegex(self.coordination, r"target 保持 workflow owner.*不得再做用户可见 task migration")
        self.assertRegex(migration, r"没有上游 return consumer")

    def test_plain_approval_and_dependency_wave_dispatch_are_distinct(self) -> None:
        self.assertRegex(self.workflow, r"普通.*批准.*同一任务")
        self.assertRegex(self.workflow, r"只有 Human 明确选择新开")
        self.assertRegex(self.workflow, r"Spec 已持久化且可达")
        self.assertRegex(self.workflow, r"没有可靠信号时不得伪造占用遥测")
        self.assertRegex(self.coordination, r"runtime-neutral assessment")
        dispatch = section(self.coordination, "## 3. 派发", "## 4.")
        flow = re.search(r"```text\s+([^`]+)```", dispatch)
        self.assertIsNotNone(flow)
        wave_flow = flow.group(1)
        positions = [wave_flow.index(token) for token in ("评估当前波次", "聚合本波结果", "重算剩余依赖图", "下一波")]
        self.assertEqual(positions, sorted(positions))
        self.assertRegex(dispatch, r"串行结论只约束当前波次")
        self.assertRegex(dispatch, r"同一 Task/Scope revision.*重算剩余依赖图")
        self.assertRegex(dispatch, r"该波次首次 wait 前.*(?:实际派发|实际启动)至少两个")
        self.assertRegex(dispatch, r"没有 ready.*返回阻塞与恢复条件")

        route = section(self.codex, "## 3. Subagent route contract", "## 4.")
        self.assertNotRegex(route, r"Manager Gate")
        self.assertNotRegex(route, r"普通.*批准")
        self.assertRegex(route, r"实际 readiness.*Core/Skill 负责")

    def test_dedup_single_writer_pi_boundary_and_static_limit(self) -> None:
        for pattern in (
            r"Task/Scope revision、批准 Spec reference 与 workflow transfer",
            r"不得再次创建",
            r"旧写入者未 terminal",
            r"不得复制完整对话",
            r"full-history helper",
        ):
            with self.subTest(pattern=pattern):
                self.assertRegex(self.coordination, pattern)
        for field in ("route identity", "scope", "artifact/evidence", "risk/entry"):
            self.assertRegex(self.artifact, re.escape(field))
        self.assertNotRegex(self.codex, r"(?i)pi(?: one-shot|_once\.ps1)")
        self.assertRegex(self.codex, r"static source/test.*不能证明.*Runtime")
        self.assertRegex(self.claude, r"不把 Codex `create_thread`.*Agent helper")


if __name__ == "__main__":
    unittest.main()
