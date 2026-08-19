"""Shared fixtures for project setup and documentation behavior tests."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SETUP_SCRIPT = (
    ROOT
    / "plugins"
    / "sacha-orchestra"
    / "skills"
    / "setup-project"
    / "scripts"
    / "generate_project_integration.py"
)
RESOLVER_SCRIPT = SETUP_SCRIPT.with_name("resolve_capability_queries.py")
DOCUMENT_SCRIPT = (
    ROOT
    / "plugins"
    / "sacha-orchestra"
    / "skills"
    / "document-project"
    / "scripts"
    / "generate_project_document.py"
)
CLOSEOUT_SCRIPT = (
    ROOT
    / "plugins"
    / "sacha-orchestra"
    / "skills"
    / "closeout"
    / "scripts"
    / "closeout.py"
)
TEMP_ROOT = ROOT / ".temp"


def fill_bundled_template(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    while "<!--" in rendered:
        start = rendered.index("<!--")
        end = rendered.find("-->", start + 4)
        if end < 0:
            raise AssertionError("bundled template contains an unterminated comment")
        rendered = rendered[:start] + rendered[end + 3 :].lstrip()

    while "{" in rendered:
        start = rendered.index("{")
        end = rendered.find("}", start + 1)
        if end < 0 or "\n" in rendered[start:end]:
            raise AssertionError("bundled template contains an invalid placeholder")
        rendered = rendered[:start] + "已填写" + rendered[end + 1 :]
    return rendered


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generator = load_module("sacha_project_setup", SETUP_SCRIPT)
resolver = load_module("sacha_capability_resolver", RESOLVER_SCRIPT)
document_generator = load_module("sacha_project_documentation", DOCUMENT_SCRIPT)
closeout = load_module("sacha_closeout", CLOSEOUT_SCRIPT)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class ProjectTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEMP_ROOT.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="setup-minimal-", dir=TEMP_ROOT)
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()
        try:
            TEMP_ROOT.rmdir()
        except OSError:
            pass

    @staticmethod
    def config(project: Path, **overrides):
        values = {
            "project_root": project,
            "manage_agents": True,
            "scm_provider": "none",
            "spec_base_kind": "project-relative",
            "spec_base": "docs",
            "documentation_policy": "disabled",
        }
        values.update(overrides)
        return generator.SetupConfig(**values)

    def confirmed_setup(self, config, **kwargs):
        dry_run = generator.run_setup(config)
        self.assertEqual("ready", dry_run["status"], dry_run["conflicts"])
        return generator.run_setup(
            config,
            write=True,
            confirmed_planned_delta_sha256=dry_run["write_confirmation"][
                "planned_delta_sha256"
            ],
            **kwargs,
        )

    @staticmethod
    def create_project_skill(
        project: Path,
        name: str,
        body: str,
        *,
        root: str = ".agents/skills",
    ) -> Path:
        skill = project / root / name / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(
            "\n".join(
                (
                    "---",
                    f"name: {name}",
                    "description: Project-local test Skill.",
                    "---",
                    "",
                    body.strip(),
                    "",
                )
            ),
            encoding="utf-8",
        )
        return skill

    @staticmethod
    def project_skill_evidence(
        project: Path,
        skill: Path,
        units: list[dict[str, object]],
        *,
        skill_sha256: str | None = None,
    ) -> str:
        return json.dumps(
            {
                "skill": skill.parent.name,
                "skill_path": skill.relative_to(project).as_posix(),
                "skill_sha256": skill_sha256 or digest(skill),
                "units": units,
            },
            ensure_ascii=False,
        )

    @staticmethod
    def document_input(**overrides):
        sections = {
            key: f"{heading}的公开、自包含说明。"
            for key, heading in document_generator.SECTIONS
        }
        value = {
            "schema_version": "1",
            "document_type": "change-archive",
            "title": "功能变更存档",
            "trigger": "human-request",
            "persistent_product_delta": True,
            "output_path": "changes/feature.md",
            "sections": sections,
        }
        value.update(overrides)
        return value

    @staticmethod
    def documentation_generation_policy(**overrides):
        value = {
            "minimum_section_count": 0,
            "minimum_word_count": 0,
            "structure_rule": "模板章节是候选结构。",
            "required_topics_rule": "required_topics 必须得到回答。",
            "optional_sections_rule": "没有实质内容时删除可选章节。",
            "section_admission_test": ["是否回答独立问题", "是否包含独立事实", "删除是否损失信息"],
            "section_admission_rule": "未通过时合并或删除。",
            "compression_rule": "短小或重复章节必须合并。",
            "navigation_rule": "只有长文才保留导航。",
            "revision_history_rule": "新文档不生成空修订记录。",
            "output_gate": ["不得残留占位符", "不得残留生成说明", "不得存在空章节"],
        }
        value.update(overrides)
        return value

    @staticmethod
    def context_input(**overrides):
        value = {
            "schema_version": "1",
            "document_type": "project-context",
            "trigger": "goal-closeout",
            "persistent_product_delta": True,
            "expected_target_sha256": None,
            "entries": [
                {
                    "term": "账号",
                    "definition": "表示登录身份，由认证模块拥有。",
                    "excluded_meanings": "不表示角色存档或游戏内角色数据。",
                    "scope": "登录、会话恢复和身份迁移。",
                    "evidence": "src/auth/account.py 的 Account owner。",
                    "consumers": "登录流程、会话恢复工具和身份迁移任务。",
                }
            ],
        }
        value.update(overrides)
        return value

    def configured_document_project(
        self,
        name: str,
        *,
        policy: str,
        authorization: str,
        root_kind: str = "project-relative",
        documentation_root: str = "docs/archive",
    ) -> tuple[Path, Path]:
        project = self.root / name
        project.mkdir()
        if root_kind == "project-relative":
            document_root = project / documentation_root
        else:
            document_root = Path(documentation_root)
        document_root.mkdir(parents=True, exist_ok=True)
        (document_root / "changes").mkdir(exist_ok=True)
        result = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                documentation_policy=policy,
                documentation_root_kind=root_kind,
                documentation_root=documentation_root,
                documentation_write_authorization=authorization,
            ),
        )
        self.assertEqual("committed", result["transaction"])
        return project, document_root
