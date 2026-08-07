"""Minimal behavior checks for setup-project's executable Python code."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class ProjectSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        TEMP_ROOT.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="setup-minimal-", dir=TEMP_ROOT)
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

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

    def test_render_agents_block_injects_project_rules(self) -> None:
        base = generator.render_agents_block("docs/workflow-rule.md")
        self.assertNotIn("领域工程纪律".encode("utf-8"), base)
        rules = "## 测试规则\n- 规则A\n- 规则B".encode("utf-8")
        with_rules = generator.render_agents_block(
            "docs/workflow-rule.md",
            {"test-provider:project-rules": rules},
        )
        self.assertIn("领域工程纪律".encode("utf-8"), with_rules)
        self.assertIn(b"BEGIN SACHA PROJECT RULES: test-provider:project-rules", with_rules)
        self.assertNotIn(generator.PROJECT_RULES_HASH.encode("utf-8"), with_rules)
        self.assertIn("## 测试规则".encode("utf-8"), with_rules)
        self.assertIn("- 规则A".encode("utf-8"), with_rules)
        self.assertTrue(with_rules.endswith(generator.AGENTS_END.encode("utf-8")))
        self.assertEqual(generator.render_agents_block("docs/workflow-rule.md", None), base)
        self.assertNotEqual(with_rules, base)
        with self.assertRaises(generator.SetupError):
            generator.render_agents_block(
                "docs/workflow-rule.md",
                {"test-provider:project-rules": generator.AGENTS_END.encode("utf-8")},
            )
        tampered = with_rules.replace(b"- \xe8\xa7\x84\xe5\x88\x99A", b"- \xe8\xa7\x84\xe5\x88\x99X")
        self.assertEqual(
            rules.replace(b"- \xe8\xa7\x84\xe5\x88\x99A", b"- \xe8\xa7\x84\xe5\x88\x99X"),
            generator._extract_project_rules(tampered)["test-provider:project-rules"],
        )

    def test_project_rules_cli_requires_canonical_asset_path(self) -> None:
        canonical = self.root / "plugin" / "skills" / "project-rules" / "assets" / "project-rules.md"
        canonical.parent.mkdir(parents=True)
        canonical.write_text("# Rules\n", encoding="utf-8")
        sources = generator._read_project_rules_sources([
            f"test-provider:project-rules::{canonical}"
        ])
        self.assertEqual("test-provider:project-rules", sources[0][0])
        with self.assertRaises(generator.SetupError):
            generator._read_project_rules_sources([
                f"test-provider:other-rules::{canonical}"
            ])
        loose = self.root / "project-rules.md"
        loose.write_text("# Loose\n", encoding="utf-8")
        with self.assertRaises(generator.SetupError):
            generator._read_project_rules_sources([
                f"test-provider:project-rules::{loose}"
            ])

    def test_project_rules_are_reconciled_by_canonical_provider(self) -> None:
        project = self.root / "project-rules-reconcile"
        project.mkdir()
        unity_rules = "# Unity discipline\n- Unity rule".encode("utf-8")
        engine_rules = "# Engine discipline\n- Engine rule".encode("utf-8")

        first = self.confirmed_setup(self.config(
            project,
            project_rules_sources=(("cgame-unity:project-rules", unity_rules),),
        ))
        self.assertEqual(["cgame-unity:project-rules"], first["project_rules_reconciliation"]["add"])

        agents = project / "AGENTS.md"
        preserved = generator.run_setup(self.config(
            project,
            expected_agents_sha256=digest(agents),
        ))
        self.assertEqual("unchanged", preserved["agents_block"]["action"])
        self.assertEqual(["cgame-unity:project-rules"], preserved["project_rules_reconciliation"]["keep"])

        merged = self.confirmed_setup(self.config(
            project,
            expected_agents_sha256=digest(agents),
            project_rules_sources=(("cgame-engine:project-rules", engine_rules),),
        ))
        self.assertEqual(["cgame-engine:project-rules"], merged["project_rules_reconciliation"]["add"])
        text = agents.read_text(encoding="utf-8")
        self.assertEqual(1, text.count(generator.AGENTS_BEGIN))
        self.assertEqual(1, text.count(generator.AGENTS_END))
        self.assertIn("cgame-unity:project-rules", text)
        self.assertIn("cgame-engine:project-rules", text)

        removed = self.confirmed_setup(self.config(
            project,
            expected_agents_sha256=digest(agents),
            remove_project_rules_skills=("cgame-engine:project-rules",),
        ))
        self.assertEqual(["cgame-engine:project-rules"], removed["project_rules_reconciliation"]["remove"])
        self.assertNotIn("cgame-engine:project-rules", agents.read_text(encoding="utf-8"))

    def test_legacy_project_rules_require_explicit_attribution(self) -> None:
        project = self.root / "legacy-project-rules"
        project.mkdir()
        agents = project / "AGENTS.md"
        agents.write_text(
            f"{generator.AGENTS_BEGIN}\n"
            "## Sacha Orchestra 接入\n\n"
            f"{generator.LEGACY_PROJECT_RULES_HEADING}\n\n"
            "# Legacy rules\n- keep only after attribution\n"
            f"{generator.AGENTS_END}\n",
            encoding="utf-8",
        )
        refused = generator.run_setup(self.config(
            project,
            expected_agents_sha256=digest(agents),
        ))
        self.assertEqual("refused", refused["status"])
        self.assertIn("unattributed legacy project rules", refused["conflicts"][0])

        no_asset = generator.run_setup(self.config(
            project,
            expected_agents_sha256=digest(agents),
            replace_legacy_project_rules=True,
        ))
        self.assertEqual("refused", no_asset["status"])
        self.assertIn("require at least one canonical project rules asset", no_asset["conflicts"][0])

        migrated = self.confirmed_setup(self.config(
            project,
            expected_agents_sha256=digest(agents),
            project_rules_sources=((
                "cgame-unity:project-rules",
                b"# Current rules\n- attributed",
            ),),
            replace_legacy_project_rules=True,
        ))
        self.assertEqual("committed", migrated["transaction"])
        text = agents.read_text(encoding="utf-8")
        self.assertNotIn(generator.LEGACY_PROJECT_RULES_HEADING, text)
        self.assertIn("cgame-unity:project-rules", text)

    def test_project_rules_legacy_source_hash_is_removed_on_refresh(self) -> None:
        project = self.root / "legacy-hashed-project-rules"
        project.mkdir()
        rules = b"# Current rules\n- attributed"
        rendered = generator.render_agents_block(
            "docs/workflow-rule.md",
            {"cgame-unity:project-rules": rules},
        )
        hash_line = (
            f"{generator.PROJECT_RULES_HASH}{generator.sha256_bytes(rules)} -->\n"
        ).encode("utf-8")
        begin_line = (
            f"{generator.PROJECT_RULES_BEGIN}cgame-unity:project-rules -->\n"
        ).encode("utf-8")
        agents = project / "AGENTS.md"
        agents.write_bytes(rendered.replace(begin_line, begin_line + hash_line, 1))

        refreshed = self.confirmed_setup(self.config(
            project,
            expected_agents_sha256=digest(agents),
        ))
        self.assertEqual("committed", refreshed["transaction"])
        self.assertNotIn(generator.PROJECT_RULES_HASH.encode("utf-8"), agents.read_bytes())
        self.assertIn(rules, agents.read_bytes())

    def test_dry_run_commit_and_idempotent_rerun(self) -> None:
        project = self.root / "basic"
        project.mkdir()

        dry_run = generator.run_setup(self.config(project))
        self.assertEqual("dry_run", dry_run["transaction"])
        for section in ("workflow_rule", "workflow_state", "agents_block"):
            self.assertNotIn("preimage_sha256", dry_run[section])
            self.assertNotIn("generated_sha256", dry_run[section])
        for target in dry_run["targets"].values():
            self.assertNotIn("generated_sha256", target)
            self.assertNotIn("current_sha256", target)
        self.assertEqual([], list(project.iterdir()))

        missing_confirmation = generator.run_setup(self.config(project), write=True)
        self.assertEqual(
            ("refused", "no_write"),
            (
                missing_confirmation["status"],
                missing_confirmation["transaction"],
            ),
        )
        self.assertEqual([], list(project.iterdir()))

        changed_config = self.config(project, spec_base="plans")
        stale_confirmation = generator.run_setup(
            changed_config,
            write=True,
            confirmed_planned_delta_sha256=dry_run["write_confirmation"][
                "planned_delta_sha256"
            ],
        )
        self.assertEqual(
            ("refused", "no_write"),
            (stale_confirmation["status"], stale_confirmation["transaction"]),
        )
        self.assertEqual([], list(project.iterdir()))

        committed = generator.run_setup(
            self.config(project),
            write=True,
            confirmed_planned_delta_sha256=dry_run["write_confirmation"][
                "planned_delta_sha256"
            ],
        )
        self.assertEqual("committed", committed["transaction"])
        self.assertTrue((project / "docs" / "workflow-rule.md").is_file())
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertFalse((project / "docs" / "plans").exists())

        repeated = generator.run_setup(
            self.config(
                project,
                expected_agents_sha256=digest(project / "AGENTS.md"),
                expected_workflow_sha256=digest(
                    project / "docs" / "workflow-rule.md"
                ),
            ),
            write=True,
        )
        self.assertEqual("no_changes", repeated["transaction"])

    def test_setup_cli_requires_exact_planned_delta_confirmation(self) -> None:
        project = self.root / "confirmation-cli"
        project.mkdir()
        command = (
            sys.executable,
            "-B",
            str(SETUP_SCRIPT),
            "--project-root",
            str(project),
            "--scm-provider",
            "none",
            "--spec-base-kind",
            "project-relative",
            "--spec-base",
            "docs",
            "--documentation-policy",
            "disabled",
        )

        dry_run_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, dry_run_process.returncode, dry_run_process.stderr)
        dry_run = json.loads(dry_run_process.stdout)
        self.assertEqual(("ready", "dry_run"), (dry_run["status"], dry_run["transaction"]))
        self.assertEqual(
            {
                "spec_storage": None,
                "documentation": None,
            },
            dry_run["write_confirmation"]["current"],
        )
        self.assertEqual("docs/plan", dry_run["write_confirmation"]["planned"]["spec_storage"]["root"])
        self.assertEqual(
            "spec.md",
            dry_run["write_confirmation"]["planned"]["spec_storage"]["file_name"],
        )
        self.assertEqual([], list(project.iterdir()))

        legacy_noun = "pla" + "n"
        rejected_legacy_cli = subprocess.run(
            (
                sys.executable,
                "-B",
                str(SETUP_SCRIPT),
                "--project-root",
                str(project),
                f"--{legacy_noun}-root-kind",
                "project-relative",
                f"--{legacy_noun}-root",
                "docs/plan",
            ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(2, rejected_legacy_cli.returncode)
        self.assertIn("unrecognized arguments", rejected_legacy_cli.stderr)
        self.assertEqual([], list(project.iterdir()))

        unconfirmed_process = subprocess.run(
            (*command, "--write"),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(2, unconfirmed_process.returncode)
        unconfirmed = json.loads(unconfirmed_process.stdout)
        self.assertEqual(
            ("refused", "no_write"),
            (unconfirmed["status"], unconfirmed["transaction"]),
        )
        self.assertEqual([], list(project.iterdir()))

        confirmed_process = subprocess.run(
            (
                *command,
                "--write",
                "--confirmed-planned-delta-sha256",
                dry_run["write_confirmation"]["planned_delta_sha256"],
            ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, confirmed_process.returncode, confirmed_process.stderr)
        confirmed = json.loads(confirmed_process.stdout)
        self.assertEqual(("ok", "committed"), (confirmed["status"], confirmed["transaction"]))
        self.assertTrue((project / "docs" / "workflow-rule.md").is_file())

    def test_setup_cli_accepts_body_assessed_project_skill(self) -> None:
        project = self.root / "project-skill-cli"
        skill = self.create_project_skill(
            project,
            "local-check",
            """
# Local check

Inspect project state and return a bounded report.
""",
        )
        evidence = self.project_skill_evidence(
            project,
            skill,
            [{
                "id": "project.check",
                "goal": "Inspect current project state.",
                "kind": "inspect",
                "admission": "schedulable",
                "side_effect": "read_only",
                "load_policy": "on-demand",
                "evidence": ["8"],
                "required_paths": [],
                "runtime_prerequisites": [],
                "reason": "The body defines a bounded inspection and report.",
            }],
        )
        process = subprocess.run(
            (
                sys.executable,
                "-B",
                str(SETUP_SCRIPT),
                "--project-root",
                str(project),
                "--scm-provider",
                "none",
                "--spec-base-kind",
                "project-relative",
                "--spec-base",
                "docs",
                "--documentation-policy",
                "disabled",
                "--skill-root-binding",
                ".agents/skills::authority",
                "--assess-project-skills",
                "--visible-project-skill",
                "local-check",
                "--project-skill-evidence",
                evidence,
                "--reconcile-capabilities",
            ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(0, process.returncode, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(("ready", "dry_run"), (result["status"], result["transaction"]))
        self.assertEqual(
            ["project.check"],
            [item["id"] for item in result["project_capability_candidates"]],
        )
        self.assertFalse((project / "docs" / "workflow-rule.md").exists())

    def test_documentation_policy_is_explicit_and_external_root_is_preserved(self) -> None:
        project = self.root / "documentation"
        project.mkdir()
        external = self.root / "missing-iwiki"

        missing_policy = generator.run_setup(
            generator.SetupConfig(
                project_root=project,
                manage_agents=False,
                scm_provider="none",
            )
        )
        self.assertEqual("refused", missing_policy["status"])
        self.assertIn("documentation_policy", missing_policy["conflicts"][0])

        configured = self.confirmed_setup(
            self.config(
                project,
                documentation_policy="required-at-closeout",
                documentation_root_kind="external-absolute",
                documentation_root=str(external),
                documentation_write_authorization="bounded-closeout",
            ),
        )
        self.assertEqual("committed", configured["transaction"])
        self.assertFalse(external.exists())
        self.assertEqual("non-portable", configured["documentation"]["portability"])
        self.assertEqual(
            "documentation_root_unreachable",
            configured["warnings"][0]["kind"],
        )

        workflow = project / "docs" / "workflow-rule.md"
        agents = project / "AGENTS.md"
        preserved = generator.run_setup(
            generator.SetupConfig(
                project_root=project,
                manage_agents=True,
                scm_provider="none",
                expected_agents_sha256=digest(agents),
                expected_workflow_sha256=digest(workflow),
            ),
            write=True,
        )
        self.assertEqual("no_changes", preserved["transaction"])
        self.assertEqual(str(external), preserved["documentation"]["root"])
        self.assertIn(
            "- 项目文档：`required-at-closeout`",
            workflow.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "write = `bounded-closeout`",
            workflow.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "- 项目 Context：`docs/CONTEXT.md`",
            workflow.read_text(encoding="utf-8"),
        )

    def test_spec_storage_defaults_is_separate_and_preserved(self) -> None:
        missing_project = self.root / "spec-missing"
        missing_project.mkdir()
        missing = generator.run_setup(
            generator.SetupConfig(
                project_root=missing_project,
                manage_agents=False,
                scm_provider="none",
                documentation_policy="disabled",
            )
        )
        self.assertEqual(("ready", "dry_run"), (missing["status"], missing["transaction"]))
        self.assertEqual("docs/plan", missing["spec_storage"]["root"])
        self.assertEqual(
            "default",
            missing["write_confirmation"]["sources"]["spec_storage"],
        )
        generated = missing["workflow_rule"]["planned_content"]
        self.assertIn("- Spec：`docs/plan`", generated)
        self.assertIn("- 任务目录：`<YYYY-MM-DD>-<short-slug>/`", generated)
        self.assertIn("澄清决定：`decisions.md`（按需，与 Spec 同目录）", generated)
        self.assertIn("- 项目 Context：`docs/CONTEXT.md`", generated)

        project = self.root / "spec-storage"
        project.mkdir()
        external_spec = self.root / "iwiki" / "docs"
        (external_spec / "plan").mkdir(parents=True)
        configured = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                spec_base_kind="external-absolute",
                spec_base=str(external_spec),
                documentation_policy="on-request",
                documentation_root_kind="project-relative",
                documentation_root="docs/archive",
                documentation_write_authorization="per-write-confirmation",
            ),
        )
        self.assertEqual("committed", configured["transaction"])
        self.assertEqual(str(external_spec / "plan"), configured["spec_storage"]["root"])
        self.assertEqual("non-portable", configured["spec_storage"]["portability"])
        self.assertEqual("spec.md", configured["spec_storage"]["file_name"])
        self.assertEqual("docs/archive", configured["documentation"]["root"])
        self.assertNotEqual(
            configured["spec_storage"]["root"],
            configured["documentation"]["root"],
        )
        workflow = project / "docs" / "workflow-rule.md"
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("### Storage", content)
        self.assertIn(f"- Spec：`{external_spec / 'plan'}`", content)
        self.assertIn(f"- 项目 Context：`{external_spec}\\CONTEXT.md`", content)

        preserved = generator.run_setup(
            generator.SetupConfig(
                project_root=project,
                manage_agents=False,
                scm_provider="none",
                expected_workflow_sha256=digest(workflow),
            ),
            write=True,
        )
        self.assertEqual("no_changes", preserved["transaction"])
        self.assertEqual(str(external_spec / "plan"), preserved["spec_storage"]["root"])
        self.assertEqual("docs/archive", preserved["documentation"]["root"])

        nested_plan_project = self.root / "nested-plan-base"
        nested_plan_project.mkdir()
        nested_plan = generator.run_setup(
            self.config(
                nested_plan_project,
                manage_agents=False,
                spec_base_kind="project-relative",
                spec_base="plan",
            )
        )
        self.assertEqual("plan/plan", nested_plan["spec_storage"]["root"])
        self.assertIn(
            "- 项目 Context：`plan/CONTEXT.md`",
            nested_plan["workflow_rule"]["planned_content"],
        )

        missing_external = self.root / "missing-spec-base"
        warned = generator.run_setup(
            self.config(
                self.root / "spec-storage",
                manage_agents=False,
                spec_base_kind="external-absolute",
                spec_base=str(missing_external),
            )
        )
        self.assertEqual("ready", warned["status"])
        self.assertFalse(missing_external.exists())
        self.assertEqual("spec_base_unreachable", warned["warnings"][0]["kind"])

        unsafe = generator.run_setup(
            self.config(
                self.root / "spec-storage",
                manage_agents=False,
                spec_base_kind="external-absolute",
                spec_base="G:\\",
            )
        )
        self.assertEqual("refused", unsafe["status"])
        self.assertIn("spec_base", unsafe["conflicts"][0])

        legacy_project = self.root / "legacy-storage"
        legacy_rule = legacy_project / "docs" / "workflow-rule.md"
        legacy_rule.parent.mkdir(parents=True)
        legacy_label = "Pla" + "n"
        legacy_rule.write_text(
            "\n".join(
                (
                    generator.GENERATOR_MARKER,
                    generator.SCHEMA_MARKER,
                    "# Sacha Orchestra 项目接入",
                    "",
                    "### Storage",
                    "",
                    f"- {legacy_label}：`docs/plan`",
                    "- 项目文档：`disabled`",
                    "",
                )
            ),
            encoding="utf-8",
        )
        ignored_legacy_storage = generator.run_setup(
            generator.SetupConfig(
                project_root=legacy_project,
                manage_agents=False,
                scm_provider="none",
                documentation_policy="disabled",
            )
        )
        self.assertEqual("refused", ignored_legacy_storage["status"])
        self.assertIn("spec_base_kind", ignored_legacy_storage["conflicts"][0])

    def test_pi_model_routing_is_setup_confirmed_and_preserved(self) -> None:
        project = self.root / "pi-model-routing"
        project.mkdir()
        bindings = (
            "standard::local-provider/standard-model",
            "pro::local-provider/pro-model",
            "lite::local-provider/lite-model",
        )

        configured = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                pi_model_bindings=bindings,
            )
        )
        self.assertEqual("committed", configured["transaction"])
        self.assertEqual(
            ["lite", "pro", "standard"],
            [item["route"] for item in configured["pi_model_bindings"]],
        )
        workflow = project / "docs" / "workflow-rule.md"
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("### Pi one-shot model routing", content)
        self.assertIn(
            "- `standard` -> `local-provider/standard-model`",
            content,
        )
        self.assertIn("不复制到 plugin 源码", content)

        preserved = generator.run_setup(
            generator.SetupConfig(
                project_root=project,
                manage_agents=False,
                scm_provider="none",
                expected_workflow_sha256=digest(workflow),
            ),
            write=True,
        )
        self.assertEqual("no_changes", preserved["transaction"])
        self.assertEqual(
            configured["pi_model_bindings"],
            preserved["pi_model_bindings"],
        )

        cleared_preview = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                clear_pi_model_bindings=True,
            )
        )
        self.assertEqual("ready", cleared_preview["status"])
        self.assertNotIn(
            "### Pi one-shot model routing",
            cleared_preview["workflow_rule"]["planned_content"],
        )

    def test_pi_model_routing_rejects_unconfirmed_or_unsafe_values(self) -> None:
        for index, binding in enumerate(
            (
                "unknown::local-provider/model",
                "standard::model-without-provider",
                "standard:: local-provider/model",
                "standard::local-provider/model::extra",
            )
        ):
            project = self.root / f"pi-model-invalid-{index}"
            project.mkdir()
            result = generator.run_setup(
                self.config(
                    project,
                    manage_agents=False,
                    pi_model_bindings=(binding,),
                )
            )
            self.assertEqual("refused", result["status"], binding)
            self.assertFalse((project / "docs").exists())

        conflict_project = self.root / "pi-model-clear-conflict"
        conflict_project.mkdir()
        conflict = generator.run_setup(
            self.config(
                conflict_project,
                manage_agents=False,
                pi_model_bindings=("standard::local-provider/model",),
                clear_pi_model_bindings=True,
            )
        )
        self.assertEqual("refused", conflict["status"])
        self.assertIn("mutually exclusive", conflict["conflicts"][0])

    def test_documentation_root_kind_and_bounds_are_enforced(self) -> None:
        project = self.root / "documentation-bounds"
        project.mkdir()

        relative = generator.run_setup(
            self.config(
                project,
                documentation_policy="on-request",
                documentation_root_kind="project-relative",
                documentation_root="docs/iwiki",
                documentation_write_authorization="per-write-confirmation",
            )
        )
        self.assertEqual("ready", relative["status"])
        self.assertEqual("portable", relative["documentation"]["portability"])
        self.assertEqual([], relative["warnings"])
        self.assertFalse((project / "docs").exists())

        for unsafe_root in (
            "G:\\",
            "G:\\folder\\..",
            "\\\\server\\share\\folder\\..",
        ):
            with self.subTest(unsafe_root=unsafe_root):
                drive_root = generator.run_setup(
                    self.config(
                        project,
                        documentation_policy="on-request",
                        documentation_root_kind="external-absolute",
                        documentation_root=unsafe_root,
                        documentation_write_authorization="bounded-closeout",
                    )
                )
                self.assertEqual("refused", drive_root["status"])
                self.assertIn("root", drive_root["conflicts"][0])

        missing_authorization = generator.run_setup(
            self.config(
                project,
                documentation_policy="on-request",
                documentation_root_kind="project-relative",
                documentation_root="docs/iwiki",
            )
        )
        self.assertEqual("refused", missing_authorization["status"])
        self.assertIn("write authorization", missing_authorization["conflicts"][0])

    def test_generated_documents_only_add_project_integration_data(self) -> None:
        project = self.root / "document-boundary"
        project.mkdir()
        (project / "TEAM.md").write_text("# Compatibility pointer\n", encoding="utf-8")

        result = self.confirmed_setup(
            self.config(project, ignored_rule_candidates=("TEAM.md",)),
        )
        self.assertEqual("committed", result["transaction"])

        workflow = (project / "docs" / "workflow-rule.md").read_text(encoding="utf-8")
        workflow_state_path = project / "docs" / "workflow-rule.state.json"
        workflow_state = json.loads(workflow_state_path.read_text(encoding="utf-8"))
        agents = (project / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("- SCM：未配置", workflow)
        self.assertIn(
            "- Setup 不绑定为项目规则：已分类 1 项",
            workflow,
        )
        self.assertNotIn("TEAM.md", workflow)
        self.assertNotIn("Sacha ignored rule candidates", workflow)
        self.assertEqual(
            {
                "generator": "sacha-orchestra:setup-project",
                "schemaVersion": 1,
                "ignoredRuleCandidates": ["TEAM.md"],
            },
            workflow_state,
        )
        self.assertNotIn("- Setup 忽略：", workflow)
        refresh = generator.run_setup(self.config(project))
        self.assertEqual("ready", refresh["status"], refresh["conflicts"])
        self.assertEqual([], refresh["changed_files"])
        self.assertEqual(["TEAM.md"], refresh["discovery"]["ignored_rule_candidates"])
        for heading in (
            "## 项目绑定",
            "### Storage",
        ):
            self.assertIn(heading, workflow)
        for redundant_content in (
            "## 项目值",
            "### Unresolved",
            "### Conflicts",
            "### Fallback",
            "## Canonical references",
            "Ignored rule candidates",
            "fallback = `discoverable-domain-skill-or-native-role`",
            "Workflow rule：",
            "Human Guide：未配置",
        ):
            self.assertNotIn(redundant_content, workflow)
        for duplicated_contract in (
            "## 简明操作模板",
            "`L0 Local Direct`",
            "`D0 Sacha Direct`",
            "Manager Gate 开启",
            "Planner/Reviewer Gate",
            "Goal",
        ):
            self.assertNotIn(duplicated_contract, workflow)
            self.assertNotIn(duplicated_contract, agents)
        self.assertIn("`sacha-orchestra:using-sacha`", agents)

        workflow_state_path.unlink()
        html_metadata_workflow = workflow.replace(
            "- Setup 不绑定为项目规则：已分类 1 项",
            "- Setup 不绑定为项目规则：已分类 1 项；精确路径保存在生成元数据中\n"
            '<!-- Sacha ignored rule candidates: ["TEAM.md"] -->',
        )
        (project / "docs" / "workflow-rule.md").write_text(
            html_metadata_workflow,
            encoding="utf-8",
        )
        html_metadata_refresh = generator.run_setup(self.config(project))
        self.assertEqual(
            "ready",
            html_metadata_refresh["status"],
            html_metadata_refresh["conflicts"],
        )
        self.assertEqual(
            ["TEAM.md"],
            html_metadata_refresh["discovery"]["ignored_rule_candidates"],
        )

        legacy_workflow = workflow.replace(
            "- Setup 不绑定为项目规则：已分类 1 项",
            "- Setup 忽略：`TEAM.md`",
        )
        (project / "docs" / "workflow-rule.md").write_text(
            legacy_workflow,
            encoding="utf-8",
        )
        legacy_refresh = generator.run_setup(self.config(project))
        self.assertEqual("ready", legacy_refresh["status"], legacy_refresh["conflicts"])
        self.assertEqual(
            ["TEAM.md"],
            legacy_refresh["discovery"]["ignored_rule_candidates"],
        )

    def test_refuses_stale_hash_and_unsafe_target_without_writing(self) -> None:
        stale_project = self.root / "stale"
        stale_project.mkdir()
        agents = stale_project / "AGENTS.md"
        agents.write_bytes(b"human-owned\n")

        stale = generator.run_setup(
            self.config(stale_project, expected_agents_sha256="0" * 64),
            write=True,
        )
        self.assertEqual("no_write", stale["transaction"])
        self.assertEqual(b"human-owned\n", agents.read_bytes())
        self.assertFalse((stale_project / "docs").exists())

        for index, unsafe_path in enumerate(
            ("../escape.md", str((self.root / "absolute.md").resolve()))
        ):
            with self.subTest(path=unsafe_path):
                project = self.root / f"unsafe-{index}"
                project.mkdir()
                result = generator.run_setup(
                    self.config(project, workflow_rule_path=unsafe_path),
                    write=True,
                )
                self.assertEqual("no_write", result["transaction"])
                self.assertEqual([], list(project.iterdir()))

    def test_refuses_non_current_managed_schema(self) -> None:
        project = self.root / "obsolete-schema"
        workflow = project / "docs" / "workflow-rule.md"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            "<!-- Generator: sacha-orchestra:setup-project -->\n"
            "<!-- Schema Version: 2 -->\n",
            encoding="utf-8",
        )

        result = generator.run_setup(
            self.config(project, expected_workflow_sha256=digest(workflow)),
            write=True,
        )
        self.assertEqual("refused", result["status"])
        self.assertEqual("no_write", result["transaction"])
        self.assertIn("Schema Version 3", result["conflicts"][0])
        self.assertEqual(
            "<!-- Generator: sacha-orchestra:setup-project -->\n"
            "<!-- Schema Version: 2 -->\n",
            workflow.read_text(encoding="utf-8"),
        )
        self.assertFalse((project / "AGENTS.md").exists())

    def test_refuses_invalid_or_orphaned_workflow_state(self) -> None:
        project = self.root / "invalid-workflow-state"
        project.mkdir()
        self.confirmed_setup(self.config(project))
        state = project / "docs" / "workflow-rule.state.json"
        state.write_text("{}\n", encoding="utf-8")

        invalid = generator.run_setup(self.config(project))
        self.assertEqual("refused", invalid["status"])
        self.assertEqual("no_write", invalid["transaction"])
        self.assertIn("generator", invalid["conflicts"][0])

        orphan = self.root / "orphaned-workflow-state"
        orphan_state = orphan / "docs" / "workflow-rule.state.json"
        orphan_state.parent.mkdir(parents=True)
        orphan_state.write_text(
            json.dumps(
                {
                    "generator": "sacha-orchestra:setup-project",
                    "schemaVersion": 1,
                    "ignoredRuleCandidates": [],
                }
            ),
            encoding="utf-8",
        )
        orphaned = generator.run_setup(self.config(orphan))
        self.assertEqual("refused", orphaned["status"])
        self.assertEqual("no_write", orphaned["transaction"])
        self.assertIn("without its workflow rule", orphaned["conflicts"][0])

    def test_rolls_back_when_second_target_write_fails(self) -> None:
        project = self.root / "rollback"
        project.mkdir()

        def fail_second(index, _relative, _prepared):
            if index == 1:
                raise OSError("injected second replacement failure")

        result = self.confirmed_setup(
            self.config(project),
            _test_hooks={"before_replace": fail_second},
        )
        self.assertEqual("rolled_back", result["transaction"])
        self.assertFalse((project / "docs").exists())
        self.assertFalse((project / "AGENTS.md").exists())

    def test_capability_resolution_does_not_guess(self) -> None:
        catalog = {
            "providers": [
                {
                    "canonical": "cgame-unity",
                    "name": "cgame-unity",
                    "capabilities": [
                        {
                            "id": "compile.verify",
                            "skill": "cgame-unity:compile-verify",
                        }
                    ],
                }
            ],
            "skills": [
                {"canonical": "one:review", "name": "custom-review"},
                {"canonical": "two:review", "name": "custom-review"},
            ],
        }

        exact = resolver.resolve_queries(catalog, ("cgame_unity",))
        ambiguous = resolver.resolve_queries(catalog, ("custom-review",))
        missing = resolver.resolve_queries(catalog, ("does-not-exist",))
        roots = resolver.resolve_project_root(
            active_workspace_roots=("C:/work/one", "C:/work/two")
        )

        self.assertEqual("needs_decision", exact["status"])
        self.assertEqual([], exact["proposed_capability_bindings"])
        self.assertEqual(
            [{"id": "compile.verify", "skill": "cgame-unity:compile-verify"}],
            exact["policy_decisions_required"],
        )
        self.assertEqual([], exact["warnings"])
        self.assertEqual("needs_decision", ambiguous["status"])
        self.assertEqual("ambiguous", ambiguous["queries"][0]["resolution"])
        self.assertEqual("zero_match", missing["queries"][0]["resolution"])
        self.assertEqual("needs_decision", roots["status"])
        self.assertIsNone(roots["project_root"])

    def test_capability_resolution_requires_human_load_policy(self) -> None:
        catalog = {
            "providers": [
                {
                    "canonical": "review-provider",
                    "name": "review-provider",
                    "capabilities": [
                        {
                            "id": "change.review",
                            "skill": "review-provider:change-review",
                        }
                    ],
                }
            ]
        }

        undecided = resolver.resolve_queries(catalog, ("review-provider",))
        result = resolver.resolve_queries(
            catalog,
            ("review-provider",),
            load_policies={"change.review": "review-only"},
        )

        self.assertEqual("needs_decision", undecided["status"])
        self.assertEqual([], undecided["proposed_capability_bindings"])
        self.assertEqual("resolved", result["status"])
        self.assertEqual(
            [{
                "id": "change.review",
                "skill": "review-provider:change-review",
                "load_policy": "review-only",
            }],
            result["proposed_capability_bindings"],
        )
        self.assertEqual([], result["warnings"])
        with self.assertRaises(resolver.CatalogError):
            resolver.resolve_queries(
                catalog,
                ("review-provider",),
                load_policies={"change.review": "always"},
            )
        with self.assertRaises(resolver.CatalogError):
            resolver.resolve_queries(
                catalog,
                ("review-provider",),
                load_policies={"unknown.capability": "on-demand"},
            )

    def test_provider_catalog_schema_v2_validation(self) -> None:
        valid = {
            "schema_version": "2",
            "provider": "cgame-unity",
            "capabilities": [
                {
                    "id": "compile.verify",
                    "skill": "cgame-unity:compile-verify",
                    "side_effect": "project_generated_state",
                },
                {
                    "id": "project.inspect",
                    "skill": "cgame-unity:project-inspect",
                    "side_effect": "read_only",
                },
            ],
        }
        visible = (
            "cgame-unity:compile-verify",
            "cgame-unity:project-inspect",
        )

        parsed = resolver.validate_provider_catalog(
            valid,
            expected_provider="cgame-unity",
            visible_skills=visible,
        )
        self.assertEqual(2, len(parsed))

        invalid_cases = {
            "schema": {**valid, "schema_version": "1"},
            "provider": {**valid, "provider": "other-provider"},
            "extra_root": {**valid, "summary": "duplicated owner"},
            "bad_id": {
                **valid,
                "capabilities": [{**valid["capabilities"][0], "id": "Compile Verify"}],
            },
            "duplicate_id": {
                **valid,
                "capabilities": [
                    valid["capabilities"][0],
                    {**valid["capabilities"][1], "id": "compile.verify"},
                ],
            },
            "foreign_skill": {
                **valid,
                "capabilities": [{
                    **valid["capabilities"][0],
                    "skill": "other-provider:compile-verify",
                }],
            },
            "invisible_skill": {
                **valid,
                "capabilities": [{
                    **valid["capabilities"][0],
                    "skill": "cgame-unity:runtime-verify",
                }],
            },
            "side_effect": {
                **valid,
                "capabilities": [{**valid["capabilities"][0], "side_effect": "network"}],
            },
            "extra_item": {
                **valid,
                "capabilities": [{**valid["capabilities"][0], "outputs": []}],
            },
        }
        for label, candidate in invalid_cases.items():
            with self.subTest(case=label), self.assertRaises(resolver.CatalogError):
                resolver.validate_provider_catalog(
                    candidate,
                    expected_provider="cgame-unity",
                    visible_skills=visible,
                )

    def test_schema_v2_catalog_needs_policy_without_warning(self) -> None:
        provider_catalog = {
            "schema_version": "2",
            "provider": "cgame-unity",
            "capabilities": [{
                "id": "compile.verify",
                "skill": "cgame-unity:compile-verify",
                "side_effect": "project_generated_state",
            }],
        }
        catalog = {
            "providers": [{
                "canonical": "cgame-unity",
                "name": "cgame-unity",
                "visible_skills": ["cgame-unity:compile-verify"],
                "catalog": provider_catalog,
            }]
        }

        undecided = resolver.resolve_queries(catalog, ("cgame-unity",))
        confirmed = resolver.resolve_queries(
            catalog,
            ("cgame-unity",),
            load_policies={"compile.verify": "after-write-authorization"},
        )

        self.assertEqual("needs_decision", undecided["status"])
        self.assertEqual([], undecided["warnings"])
        self.assertEqual([], undecided["proposed_capability_bindings"])
        self.assertEqual(
            [{
                "id": "compile.verify",
                "skill": "cgame-unity:compile-verify",
                "side_effect": "project_generated_state",
            }],
            undecided["policy_decisions_required"],
        )
        self.assertEqual("resolved", confirmed["status"])
        self.assertEqual([], confirmed["policy_decisions_required"])
        self.assertEqual(
            [{
                "id": "compile.verify",
                "skill": "cgame-unity:compile-verify",
                "load_policy": "after-write-authorization",
            }],
            confirmed["proposed_capability_bindings"],
        )

    def test_capability_reconciliation_is_explicit_and_idempotent(self) -> None:
        project = self.root / "capabilities"
        (project / ".git").mkdir(parents=True)
        (project / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        (project / ".git" / "objects").mkdir()

        initial = (
            "change.review::old-plugin:legacy-review::review-only",
            "legacy.extra::old-plugin:extra::on-demand",
        )
        first = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                capability_bindings=initial,
                reconcile_capabilities=True,
            ),
        )
        self.assertEqual("committed", first["transaction"])

        workflow = project / "docs" / "workflow-rule.md"
        desired = (
            "change.review::my-plugin:custom-review::review-only",
            "compile.verify::cgame-unity:compile-verify::risk-matched",
        )
        updated_config = self.config(
            project,
            manage_agents=False,
            scm_provider=None,
            spec_base_kind=None,
            spec_base=None,
            documentation_policy=None,
            capability_bindings=desired,
            reconcile_capabilities=True,
            expected_workflow_sha256=digest(workflow),
        )
        before_update = workflow.read_bytes()
        update_preview = generator.run_setup(updated_config)
        self.assertEqual(
            {
                "spec_storage": "existing-binding",
                "documentation": "existing-binding",
            },
            update_preview["write_confirmation"]["sources"],
        )
        self.assertEqual(
            "docs/plan",
            update_preview["write_confirmation"]["current"]["spec_storage"]["root"],
        )
        unconfirmed = generator.run_setup(updated_config, write=True)
        self.assertEqual(
            ("refused", "no_write"),
            (unconfirmed["status"], unconfirmed["transaction"]),
        )
        self.assertEqual(before_update, workflow.read_bytes())

        updated = generator.run_setup(
            updated_config,
            write=True,
            confirmed_planned_delta_sha256=update_preview["write_confirmation"][
                "planned_delta_sha256"
            ],
        )
        content = workflow.read_text(encoding="utf-8")
        self.assertEqual("committed", updated["transaction"])
        self.assertNotIn("old-plugin", content)
        self.assertIn("cgame-unity:compile-verify", content)

        repeated = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                capability_bindings=desired,
                reconcile_capabilities=True,
            ),
            write=True,
        )
        self.assertEqual("no_changes", repeated["transaction"])

    def test_capability_binding_requires_explicit_load_policy(self) -> None:
        project = self.root / "policy-required"
        project.mkdir()

        result = generator.run_setup(
            self.config(
                project,
                capability_bindings=(
                    "compile.verify::cgame-unity:compile-verify",
                ),
                reconcile_capabilities=True,
            ),
            write=True,
        )

        self.assertEqual("refused", result["status"])
        self.assertEqual("no_write", result["transaction"])
        self.assertEqual([], list(project.iterdir()))
        self.assertIn("load-policy", result["conflicts"][0])

    def test_project_skill_mapping_requires_body_assessment(self) -> None:
        project = self.root / "project-skill-unassessed"
        skill = self.create_project_skill(
            project,
            "architecture-health",
            """
# Architecture health

Read dependency boundaries and report structural risks without writing files.
""",
        )
        config = self.config(
            project,
            manage_agents=False,
            skill_root_bindings=(".agents/skills::authority",),
            assess_project_skills=True,
            visible_project_skills=("architecture-health",),
        )

        result = generator.run_setup(config)

        self.assertEqual(("refused", "no_write"), (result["status"], result["transaction"]))
        self.assertEqual(
            [skill.relative_to(project).as_posix()],
            result["unassessed_project_skills"],
        )
        self.assertEqual([], result["project_capability_candidates"])

        guessed = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                skill_root_bindings=(".agents/skills::authority",),
                capability_bindings=(
                    "architecture.health::architecture-health::on-demand",
                ),
                reconcile_capabilities=True,
            )
        )
        self.assertEqual("refused", guessed["status"])
        self.assertTrue(
            any("project Skill evidence" in item for item in guessed["conflicts"]),
            guessed["conflicts"],
        )

    def test_project_skill_body_can_admit_multiple_capabilities(self) -> None:
        project = self.root / "project-skill-composite"
        (project / "tools").mkdir(parents=True)
        (project / "tools" / "static.py").write_text("# static\n", encoding="utf-8")
        (project / "tools" / "remote.py").write_text("# remote\n", encoding="utf-8")
        skill = self.create_project_skill(
            project,
            "renderdoc-rdc-analysis",
            """
# RenderDoc analysis

## Static capture analysis
Run `tools/static.py` and return a structured capture report.

## Android remote replay
Run `tools/remote.py` against an explicitly selected device.
""",
        )
        evidence = self.project_skill_evidence(
            project,
            skill,
            [
                {
                    "id": "renderdoc.capture.analyze",
                    "goal": "Analyze an RDC capture without changing runtime state.",
                    "kind": "inspect",
                    "admission": "schedulable",
                    "side_effect": "read_only",
                    "load_policy": "on-demand",
                    "evidence": ["8-9"],
                    "required_paths": ["tools/static.py"],
                    "runtime_prerequisites": [],
                    "reason": "The body defines a bounded static analysis workflow and output.",
                },
                {
                    "id": "renderdoc.android.replay",
                    "goal": "Replay a capture on an explicitly selected Android device.",
                    "kind": "operate",
                    "admission": "schedulable",
                    "side_effect": "runtime_state",
                    "load_policy": "after-write-authorization",
                    "evidence": ["11-12"],
                    "required_paths": ["tools/remote.py"],
                    "runtime_prerequisites": ["selected Android device"],
                    "reason": "The body defines a separate remote replay workflow.",
                },
            ],
        )
        config = self.config(
            project,
            manage_agents=False,
            skill_root_bindings=(".agents/skills::authority",),
            assess_project_skills=True,
            visible_project_skills=("renderdoc-rdc-analysis",),
            project_skill_evidence=(evidence,),
            reconcile_capabilities=True,
        )

        preview = generator.run_setup(config)

        self.assertEqual("ready", preview["status"], preview["conflicts"])
        self.assertEqual([], preview["unassessed_project_skills"])
        self.assertEqual([], preview["project_policy_decisions_required"])
        self.assertEqual(
            [
                "renderdoc.android.replay",
                "renderdoc.capture.analyze",
            ],
            [
                item["id"]
                for item in preview["project_capability_candidates"]
            ],
        )
        self.assertEqual(
            [
                {"id": "renderdoc.android.replay", "after": {
                    "id": "renderdoc.android.replay",
                    "skill": "renderdoc-rdc-analysis",
                    "load_policy": "after-write-authorization",
                }},
                {"id": "renderdoc.capture.analyze", "after": {
                    "id": "renderdoc.capture.analyze",
                    "skill": "renderdoc-rdc-analysis",
                    "load_policy": "on-demand",
                }},
            ],
            preview["capability_reconciliation"]["add"],
        )

        written = self.confirmed_setup(config)
        workflow = (project / "docs" / "workflow-rule.md").read_text(encoding="utf-8")
        self.assertEqual("committed", written["transaction"])
        self.assertIn(
            "`after-write-authorization`：`renderdoc.android.replay` -> "
            "`renderdoc-rdc-analysis`",
            workflow,
        )
        self.assertIn(
            "`on-demand`：`renderdoc.capture.analyze` -> `renderdoc-rdc-analysis`",
            workflow,
        )

    def test_project_skill_policy_and_runtime_visibility_are_gates(self) -> None:
        project = self.root / "project-skill-gates"
        skill = self.create_project_skill(
            project,
            "local-build",
            """
# Local build

Run the project wrapper and report compile and link results.
""",
        )
        unit = {
            "id": "project.build",
            "goal": "Build the current project through its wrapper.",
            "kind": "build",
            "admission": "schedulable",
            "side_effect": "project_generated_state",
            "evidence": ["8"],
            "required_paths": [],
            "runtime_prerequisites": [],
            "reason": "The body defines an executable build goal.",
        }
        evidence = self.project_skill_evidence(project, skill, [unit])
        common = {
            "manage_agents": False,
            "skill_root_bindings": (".agents/skills::authority",),
            "assess_project_skills": True,
            "project_skill_evidence": (evidence,),
            "reconcile_capabilities": True,
        }

        invisible = generator.run_setup(self.config(project, **common))
        self.assertEqual("refused", invisible["status"])
        self.assertTrue(
            any("not visible" in item for item in invisible["conflicts"]),
            invisible["conflicts"],
        )

        undecided = generator.run_setup(
            self.config(
                project,
                **common,
                visible_project_skills=("local-build",),
            )
        )
        self.assertEqual("refused", undecided["status"])
        self.assertEqual(
            [{
                "id": "project.build",
                "skill": "local-build",
                "side_effect": "project_generated_state",
            }],
            undecided["project_policy_decisions_required"],
        )
        self.assertEqual([], undecided["capability_reconciliation"]["add"])

        unavailable_evidence = self.project_skill_evidence(
            project,
            skill,
            [{
                "goal": "Build the current project through its wrapper.",
                "kind": "build",
                "admission": "unavailable",
                "side_effect": "project_generated_state",
                "evidence": ["8"],
                "required_paths": ["tools/missing-build-wrapper.py"],
                "runtime_prerequisites": [],
                "reason": "The body goal exists, but its required static entrypoint is absent.",
            }],
        )
        unavailable = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                skill_root_bindings=(".agents/skills::authority",),
                assess_project_skills=True,
                project_skill_evidence=(unavailable_evidence,),
                reconcile_capabilities=True,
            )
        )
        self.assertEqual("ready", unavailable["status"], unavailable["conflicts"])
        self.assertEqual([], unavailable["project_capability_candidates"])
        self.assertEqual(
            ["tools/missing-build-wrapper.py"],
            unavailable["project_skill_assessments"][0]["units"][0][
                "missing_required_paths"
            ],
        )

    def test_project_skill_evidence_must_match_body_and_required_paths(self) -> None:
        project = self.root / "project-skill-evidence"
        skill = self.create_project_skill(
            project,
            "local-verify",
            """
# Local verify

Run `tools/verify.py` and return its pass/fail evidence.
""",
        )
        unit = {
            "id": "project.verify",
            "goal": "Verify the current project through its local entrypoint.",
            "kind": "verify",
            "admission": "schedulable",
            "side_effect": "read_only",
            "load_policy": "on-demand",
            "evidence": ["8"],
            "required_paths": [],
            "runtime_prerequisites": [],
            "reason": "The body defines a bounded verification goal and output.",
        }
        stale = self.project_skill_evidence(
            project,
            skill,
            [unit],
            skill_sha256="0" * 64,
        )
        frontmatter = self.project_skill_evidence(
            project,
            skill,
            [{**unit, "evidence": ["2"]}],
        )
        missing_path = self.project_skill_evidence(
            project,
            skill,
            [{**unit, "required_paths": ["tools/verify.py"]}],
        )
        common = {
            "manage_agents": False,
            "skill_root_bindings": (".agents/skills::authority",),
            "assess_project_skills": True,
            "visible_project_skills": ("local-verify",),
            "reconcile_capabilities": True,
        }

        for label, evidence, expected in (
            ("stale", stale, "SHA-256 is stale"),
            ("frontmatter", frontmatter, "body, not frontmatter"),
            ("missing-path", missing_path, "required path is missing"),
        ):
            with self.subTest(label=label):
                result = generator.run_setup(
                    self.config(
                        project,
                        **common,
                        project_skill_evidence=(evidence,),
                    )
                )
                self.assertEqual("refused", result["status"])
                self.assertEqual([], result["project_capability_candidates"])
                self.assertTrue(
                    any(expected in item for item in result["conflicts"]),
                    result["conflicts"],
                )

    def test_support_only_project_skill_is_assessed_without_mapping(self) -> None:
        project = self.root / "project-skill-support"
        skill = self.create_project_skill(
            project,
            "handoff",
            """
# Handoff helper

Format evidence for another workflow; this is not a standalone execution goal.
""",
        )
        evidence = self.project_skill_evidence(
            project,
            skill,
            [{
                "goal": "Format supporting handoff context.",
                "kind": "coordinate",
                "admission": "support_only",
                "side_effect": "read_only",
                "evidence": ["8"],
                "required_paths": [],
                "runtime_prerequisites": [],
                "reason": "The body explicitly describes a helper, not a schedulable goal.",
            }],
        )

        result = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                skill_root_bindings=(".agents/skills::authority",),
                assess_project_skills=True,
                project_skill_evidence=(evidence,),
                reconcile_capabilities=True,
            )
        )

        self.assertEqual("ready", result["status"], result["conflicts"])
        self.assertEqual([], result["unassessed_project_skills"])
        self.assertEqual([], result["project_capability_candidates"])
        self.assertEqual([], result["capability_reconciliation"]["add"])

    def test_invalid_root_git_marker_uses_valid_ancestor_marker(self) -> None:
        repository = self.root / "repository"
        project = repository / "nested-project"
        (repository / ".git" / "objects").mkdir(parents=True)
        (repository / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        (project / ".git").mkdir(parents=True)

        result = generator.run_setup(
            self.config(project, manage_agents=False, scm_provider=None),
            write=False,
        )

        self.assertEqual("git", result["discovery"]["scm"]["provider"])
        self.assertEqual(
            [{"provider": "git", "source": "../.git"}],
            result["discovery"]["scm"]["evidence"],
        )

    def test_project_documentation_policy_trigger_and_authorization(self) -> None:
        disabled = self.root / "documents-disabled"
        disabled.mkdir()
        self.confirmed_setup(self.config(disabled, manage_agents=False))
        refused = document_generator.generate_project_document(
            project_root=disabled,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(),
        )
        self.assertEqual(("refused", "no_write"), (refused["status"], refused["transaction"]))

        requested, _ = self.configured_document_project(
            "documents-requested",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        wrong_trigger = document_generator.generate_project_document(
            project_root=requested,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(trigger="goal-closeout"),
            per_write_confirmed=True,
        )
        self.assertEqual("refused", wrong_trigger["status"])
        needs_confirmation = document_generator.generate_project_document(
            project_root=requested,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(),
        )
        self.assertEqual("refused", needs_confirmation["status"])
        ready = document_generator.generate_project_document(
            project_root=requested,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(),
            per_write_confirmed=True,
        )
        self.assertEqual(("ready", "dry_run"), (ready["status"], ready["transaction"]))

        required, _ = self.configured_document_project(
            "documents-required",
            policy="required-at-closeout",
            authorization="bounded-closeout",
        )
        not_persistent = document_generator.generate_project_document(
            project_root=required,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(
                trigger="goal-closeout",
                persistent_product_delta=False,
            ),
        )
        self.assertEqual("refused", not_persistent["status"])
        bounded = document_generator.generate_project_document(
            project_root=required,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(trigger="goal-closeout"),
        )
        self.assertEqual(("ready", "dry_run"), (bounded["status"], bounded["transaction"]))

    def test_document_template_catalog_binding_and_profile_selection_are_deterministic(self) -> None:
        option_strings = generator.build_parser()._option_string_actions
        for option in (
            "--documentation-template-catalog-path-kind",
            "--documentation-template-catalog-path",
            "--clear-documentation-template-catalog",
        ):
            self.assertIn(option, option_strings)
        project = self.root / "documents-catalog-bound"
        project.mkdir()
        (project / "docs" / "archive" / "changes").mkdir(parents=True)
        catalog = project / "docs" / "templates"
        catalog.mkdir(parents=True)
        implementation = catalog / "change-archive-implementation-record-v1.md"
        implementation.write_text(
            "# {变更标题} — 实施记录\n\n## 背景与目标\n\n{目标}\n\n"
            "## 实现与数据流\n\n{实现}\n\n## 验证结果\n\n{验证}\n",
            encoding="utf-8",
        )
        pipeline = catalog / "system-guide-pipeline-overview-v1.md"
        pipeline.write_text(
            "# {系统名称} 管线全景\n\n## 阅读导航\n\n{导航}\n\n"
            "## 输入到运行时\n\n{管线}\n\n## 验证与维护\n\n{验证}\n",
            encoding="utf-8",
        )
        profiles = [
            {
                "id": "rendering-implementation-record-v1",
                "document_type": "change-archive",
                "primary_purpose": "record",
                "primary_question": "这次改了什么，为什么这样改，如何验证",
                "choose_when": ["重点是实施和验证"],
                "avoid_when": ["重点是完整系统管线"],
                "required_topics": ["目标", "结果", "验证边界"],
                "optional_sections": ["目录", "文件表"],
                "template": implementation.name,
                "reference_samples": [],
            },
            {
                "id": "rendering-pipeline-overview-v1",
                "document_type": "system-guide",
                "primary_purpose": "explain",
                "primary_question": "这个系统或管线现在如何工作",
                "choose_when": ["存在端到端生命周期"],
                "avoid_when": ["只记录一次改动"],
                "required_topics": ["用途与边界", "数据流", "验证边界"],
                "optional_sections": ["导航", "历史"],
                "template": pipeline.name,
                "reference_samples": [],
            },
        ]
        manifest = catalog / "profiles.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "selection": {
                        "strategy": "manifest-ranked",
                        "read_templates_before_selection": False,
                        "tie_policy": "ask-human",
                        "allow_profile_merge": False,
                        "fallback_profile": "rendering-implementation-record-v1",
                    },
                    "generation_policy": self.documentation_generation_policy(),
                    "profiles": profiles,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        config = self.config(
            project,
            manage_agents=False,
            documentation_policy="on-request",
            documentation_root_kind="project-relative",
            documentation_root="docs/archive",
            documentation_write_authorization="per-write-confirmation",
            documentation_template_catalog_path_kind="project-relative",
            documentation_template_catalog_path="docs/templates",
        )
        dry_run = generator.run_setup(config)
        approved_delta = dry_run["write_confirmation"]["planned_delta_sha256"]
        original_pipeline_before_setup = pipeline.read_text(encoding="utf-8")
        pipeline.write_text(
            original_pipeline_before_setup + "\n<!-- independent template update -->\n",
            encoding="utf-8",
        )
        configured = generator.run_setup(
            config,
            write=True,
            confirmed_planned_delta_sha256=approved_delta,
        )
        self.assertEqual("ok", configured["status"], configured["conflicts"])
        pipeline.write_text(original_pipeline_before_setup, encoding="utf-8")
        binding = configured["documentation"]["template_catalog"]
        self.assertEqual(
            {"path_kind": "project-relative", "path": "docs/templates"},
            binding,
        )
        workflow = project / "docs" / "workflow-rule.md"
        workflow_text = workflow.read_text(encoding="utf-8")
        self.assertIn(
            "- document-template catalog：path kind = `project-relative`；"
            "path = `docs/templates`",
            workflow_text,
        )
        self.assertNotIn("manifest sha256", workflow_text)
        self.assertNotIn("document-template profile", workflow_text)

        rendered = (
            "# 功能变更 — 实施记录\n\n## 背景与目标\n\n完成持久功能。\n\n"
            "## 实现与数据流\n\n入口到持久化。\n\n## 验证结果\n\n运行验证通过。\n"
        )
        ready = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input={
                key: value
                for key, value in {
                    **self.document_input(),
                    "title": "功能变更 — 实施记录",
                    "template_profile": "rendering-implementation-record-v1",
                    "rendered_markdown": rendered,
                }.items()
                if key != "sections"
            },
            per_write_confirmed=True,
        )
        self.assertEqual(("ready", "dry_run"), (ready["status"], ready["transaction"]))
        self.assertEqual("project-catalog", ready["template"]["source"])
        self.assertEqual("rendering-implementation-record-v1", ready["template"]["profile"])
        self.assertNotIn("sha256", ready["template"])

        system_ready = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input={
                key: value
                for key, value in {
                    **self.document_input(
                        document_type="system-guide",
                        title="烘焙管线 管线全景",
                        output_path="changes/pipeline.md",
                    ),
                    "template_profile": "rendering-pipeline-overview-v1",
                    "rendered_markdown": (
                        "# 烘焙管线 管线全景\n\n"
                        "## 结论、边界与主链路\n\n"
                        "本系统覆盖资产输入、核心处理到运行消费；当前只验证主路径，"
                        "未覆盖异常恢复。\n"
                    ),
                }.items()
                if key != "sections"
            },
            per_write_confirmed=True,
        )
        self.assertEqual("ready", system_ready["status"])
        self.assertEqual("rendering-pipeline-overview-v1", system_ready["template"]["profile"])
        self.assertEqual(
            ["用途与边界", "数据流", "验证边界"],
            system_ready["template"]["required_topics"],
        )

        template_instruction = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input={
                key: value
                for key, value in {
                    **self.document_input(title="功能变更 — 实施记录"),
                    "template_profile": "rendering-implementation-record-v1",
                    "rendered_markdown": (
                        "# 功能变更 — 实施记录\n\n<!-- 生成说明：不要保留 -->\n\n"
                        "## 结果\n\n已经完成。\n"
                    ),
                }.items()
                if key != "sections"
            },
            per_write_confirmed=True,
        )
        self.assertEqual("refused", template_instruction["status"])
        self.assertIn("template-author instructions", template_instruction["conflicts"][0])

        original_template = implementation.read_text(encoding="utf-8")
        implementation.write_text(original_template + "\n<!-- drift -->\n", encoding="utf-8")
        drift = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input={
                key: value
                for key, value in {
                    **self.document_input(),
                    "title": "功能变更 — 实施记录",
                    "template_profile": "rendering-implementation-record-v1",
                    "rendered_markdown": rendered,
                }.items()
                if key != "sections"
            },
            per_write_confirmed=True,
        )
        self.assertEqual("ready", drift["status"])
        self.assertEqual(str(implementation.resolve()), drift["template"]["path"])
        implementation.write_text(original_template, encoding="utf-8")

        original_pipeline = pipeline.read_text(encoding="utf-8")
        pipeline.write_text(original_pipeline + "\n<!-- unrelated update -->\n", encoding="utf-8")
        unrelated_template_update = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input={
                key: value
                for key, value in {
                    **self.document_input(),
                    "title": "功能变更 — 实施记录",
                    "template_profile": "rendering-implementation-record-v1",
                    "rendered_markdown": rendered,
                }.items()
                if key != "sections"
            },
            per_write_confirmed=True,
        )
        self.assertEqual("ready", unrelated_template_update["status"])
        self.assertEqual(
            str(implementation.resolve()),
            unrelated_template_update["template"]["path"],
        )
        pipeline.write_text(original_pipeline, encoding="utf-8")

        preserve = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                spec_base_kind=None,
                spec_base=None,
                documentation_policy=None,
                documentation_root_kind=None,
                documentation_root=None,
                documentation_write_authorization=None,
            )
        )
        self.assertEqual(binding, preserve["documentation"]["template_catalog"])

        workflow_hash = digest(workflow)
        cleared = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                spec_base_kind=None,
                spec_base=None,
                documentation_policy=None,
                documentation_root_kind=None,
                documentation_root=None,
                documentation_write_authorization=None,
                clear_documentation_template_catalog=True,
                expected_workflow_sha256=workflow_hash,
            )
        )
        self.assertNotIn("template_catalog", cleared["documentation"])

    def test_change_archive_canonical_fallback_ignores_document_root_style_samples(self) -> None:
        project, document_root = self.configured_document_project(
            "documents-canonical-template",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        decoy = document_root / "random-implementation-style.md"
        decoy.write_text("# 随机抽样风格\n\n这不是已绑定模板。\n", encoding="utf-8")
        rendered = fill_bundled_template(
            document_generator.CANONICAL_CHANGE_ARCHIVE_TEMPLATE.read_text(
                encoding="utf-8"
            ),
            {"{变更标题}": "功能变更"},
        )
        fallback_input = {
            key: value
            for key, value in {
                **self.document_input(title="功能变更 — 实施记录"),
                "template_profile": document_generator.CANONICAL_CHANGE_ARCHIVE_PROFILE,
                "rendered_markdown": rendered,
            }.items()
            if key != "sections"
        }
        first = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=fallback_input,
            per_write_confirmed=True,
        )
        decoy.write_text("# 另一个随机风格\n", encoding="utf-8")
        second = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=fallback_input,
            per_write_confirmed=True,
        )
        self.assertEqual("bundled-fallback", first["template"]["source"])
        self.assertEqual(
            document_generator.CANONICAL_CHANGE_ARCHIVE_PROFILE,
            first["template"]["profile"],
        )
        self.assertNotIn("sha256", first["template"])
        self.assertNotIn("sha256", second["template"])
        self.assertEqual(first["sha256"], second["sha256"])

        system_rendered = fill_bundled_template(
            document_generator.CANONICAL_SYSTEM_GUIDE_TEMPLATE.read_text(
                encoding="utf-8"
            ),
            {"{系统名称}": "文档系统", "{系统}": "文档系统"},
        )
        system = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input={
                key: value
                for key, value in {
                    **self.document_input(
                        document_type="system-guide",
                        title="文档系统 系统全景",
                        output_path="changes/system.md",
                    ),
                    "template_profile": document_generator.CANONICAL_SYSTEM_GUIDE_PROFILE,
                    "rendered_markdown": system_rendered,
                }.items()
                if key != "sections"
            },
            per_write_confirmed=True,
        )
        self.assertEqual("ready", system["status"], system["conflicts"])
        self.assertEqual("bundled-fallback", system["template"]["source"])

    def test_document_template_catalog_rejects_implicit_scan_without_binding(self) -> None:
        project, document_root = self.configured_document_project(
            "documents-no-catalog-scan",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        (document_root / "profiles.json").write_text("{}", encoding="utf-8")
        legacy = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(),
            per_write_confirmed=True,
        )
        self.assertEqual("legacy-structured-default", legacy["template"]["source"])
        selected = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input={
                key: value
                for key, value in {
                    **self.document_input(),
                    "template_profile": "rendering-implementation-record-v1",
                    "rendered_markdown": "# 功能变更存档\n",
                }.items()
                if key != "sections"
            },
            per_write_confirmed=True,
        )
        self.assertEqual("refused", selected["status"])
        self.assertIn("requires a bound project catalog", selected["conflicts"][0])

    def test_document_template_catalog_rejects_preselection_reads_and_missing_files(self) -> None:
        for name, preselect, create_template, expected in (
            ("preselect", True, True, "selection contract"),
            ("missing", False, False, "absent file"),
            ("quota", False, True, "must not impose section or word quotas"),
        ):
            with self.subTest(name=name):
                project = self.root / f"documents-catalog-{name}"
                project.mkdir()
                catalog = project / "templates"
                catalog.mkdir()
                if create_template:
                    (catalog / "record.md").write_text(
                        "# {标题}\n\n## 结果\n\n{内容}\n",
                        encoding="utf-8",
                    )
                (catalog / "profiles.json").write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "selection": {
                                "strategy": "manifest-ranked",
                                "read_templates_before_selection": preselect,
                                "tie_policy": "ask-human",
                                "allow_profile_merge": False,
                                "fallback_profile": "record-v1",
                            },
                            "generation_policy": self.documentation_generation_policy(
                                minimum_section_count=1 if name == "quota" else 0
                            ),
                            "profiles": [
                                {
                                    "id": "record-v1",
                                    "document_type": "change-archive",
                                    "primary_purpose": "record",
                                    "primary_question": "这次改了什么",
                                    "choose_when": ["存在持久改动"],
                                    "avoid_when": ["纯问答"],
                                    "required_topics": ["目标", "结果"],
                                    "optional_sections": ["目录"],
                                    "template": "record.md",
                                    "reference_samples": [],
                                }
                            ],
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                result = generator.run_setup(
                    self.config(
                        project,
                        manage_agents=False,
                        documentation_policy="on-request",
                        documentation_root_kind="project-relative",
                        documentation_root="docs/archive",
                        documentation_write_authorization="per-write-confirmation",
                        documentation_template_catalog_path_kind="project-relative",
                        documentation_template_catalog_path="templates",
                    )
                )
                self.assertEqual("refused", result["status"])
                self.assertIn(expected, result["conflicts"][0])

    def test_project_documentation_cli_dry_run_create_parse_and_no_overwrite(self) -> None:
        project, document_root = self.configured_document_project(
            "documents-cli",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        input_path = project / "document-input.json"
        input_path.write_text(
            json.dumps(self.document_input(), ensure_ascii=False),
            encoding="utf-8",
        )
        command = (
            sys.executable,
            "-B",
            str(DOCUMENT_SCRIPT),
            "--project-root",
            str(project),
            "--input-json",
            str(input_path),
            "--per-write-confirmed",
        )
        dry_run = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, dry_run.returncode, dry_run.stderr)
        self.assertEqual("ready", json.loads(dry_run.stdout)["status"])
        target = document_root / "changes" / "feature.md"
        self.assertFalse(target.exists())

        created = subprocess.run(
            (*command, "--write"),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, created.returncode, created.stderr)
        result = json.loads(created.stdout)
        self.assertEqual(("ok", "committed"), (result["status"], result["transaction"]))
        parsed = document_generator.parse_generated_document(target.read_bytes())
        self.assertEqual("功能变更存档", parsed["title"])
        original = target.read_bytes()

        guide = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(
                document_type="system-guide",
                title="系统使用指南",
                output_path="changes/system-guide.md",
            ),
            write=True,
            per_write_confirmed=True,
        )
        self.assertEqual(("ok", "committed"), (guide["status"], guide["transaction"]))
        self.assertEqual(
            "系统使用指南",
            document_generator.parse_generated_document(
                (document_root / "changes" / "system-guide.md").read_bytes()
            )["title"],
        )

        repeated = subprocess.run(
            (*command, "--write"),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(2, repeated.returncode)
        self.assertEqual("refused", json.loads(repeated.stdout)["status"])
        self.assertEqual(original, target.read_bytes())

    def test_project_documentation_atomic_failure_is_not_reported_as_ready(self) -> None:
        project, document_root = self.configured_document_project(
            "documents-atomic-failure",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        with mock.patch.object(
            document_generator.os,
            "link",
            side_effect=PermissionError("fault injection"),
        ):
            failed = document_generator.generate_project_document(
                project_root=project,
                workflow_rule_path="docs/workflow-rule.md",
                document_input=self.document_input(),
                write=True,
                per_write_confirmed=True,
            )
        self.assertEqual(("failed", "no_write"), (failed["status"], failed["transaction"]))
        self.assertIn("atomic new-file creation failed", failed["conflicts"][0])
        self.assertFalse((document_root / "changes" / "feature.md").exists())

    def test_project_context_create_merge_and_definition_change_requirements(self) -> None:
        project, document_root = self.configured_document_project(
            "project-context",
            policy="required-at-closeout",
            authorization="bounded-closeout",
        )
        target = project / "docs" / "CONTEXT.md"

        dry_run = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(),
        )
        self.assertEqual(("ready", "dry_run"), (dry_run["status"], dry_run["transaction"]))
        self.assertIsNone(dry_run["preimage_sha256"])
        self.assertFalse(target.exists())

        created = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(),
            write=True,
        )
        self.assertEqual(("ok", "committed"), (created["status"], created["transaction"]))
        created_text = target.read_text(encoding="utf-8")
        self.assertIn("### 账号", created_text)
        self.assertIn("- 明确排除：不表示角色存档", created_text)

        target.write_text(
            created_text + "\n## 人工维护内容\n\n此段必须保留。\n",
            encoding="utf-8",
        )
        preimage = digest(target)
        second_entry = {
            "term": "完成",
            "definition": "表示全部 blocking 验收已有直接证据。",
            "excluded_meanings": "不表示代码已经写完但仍缺必需 Runtime 证据。",
            "scope": "任务 closeout 与完成声明。",
            "evidence": "项目验证规则与验收输出。",
            "consumers": "Executor、Reviewer 和发布收尾任务。",
        }
        merged = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(
                expected_target_sha256=preimage,
                entries=[second_entry],
            ),
            write=True,
        )
        self.assertEqual(
            ("ok", "committed"),
            (merged["status"], merged["transaction"]),
            merged["conflicts"],
        )
        merged_text = target.read_text(encoding="utf-8")
        self.assertIn("### 账号", merged_text)
        self.assertIn("### 完成", merged_text)
        self.assertIn("## 人工维护内容", merged_text)
        self.assertIn("此段必须保留。", merged_text)

        current_hash = digest(target)
        changed_account = self.context_input()["entries"][0]
        changed_account["definition"] = "表示新的业务定义。"
        requires_human = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(
                expected_target_sha256=current_hash,
                entries=[changed_account],
            ),
        )
        self.assertEqual("refused", requires_human["status"])
        self.assertIn("explicit per-write confirmation", requires_human["conflicts"][0])

        confirmed = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(
                expected_target_sha256=current_hash,
                entries=[changed_account],
            ),
            write=True,
            per_write_confirmed=True,
        )
        self.assertEqual(("ok", "committed"), (confirmed["status"], confirmed["transaction"]))
        self.assertIn("新的业务定义", target.read_text(encoding="utf-8"))

        stale = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(
                expected_target_sha256=current_hash,
                entries=[second_entry],
            ),
        )
        self.assertEqual("refused", stale["status"])
        self.assertIn("preimage SHA-256 changed", stale["conflicts"][0])

    def test_project_context_uses_spec_base_not_documentation_root(self) -> None:
        project, document_root = self.configured_document_project(
            "project-context-spec-base",
            policy="required-at-closeout",
            authorization="bounded-closeout",
            documentation_root="iwiki",
        )
        context_root = project / "context-store"
        context_root.mkdir()
        workflow = project / "docs" / "workflow-rule.md"
        refreshed = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                spec_base_kind="project-relative",
                spec_base="context-store",
                documentation_policy="required-at-closeout",
                documentation_root_kind="project-relative",
                documentation_root="iwiki",
                documentation_write_authorization="bounded-closeout",
                expected_workflow_sha256=digest(workflow),
            ),
        )
        self.assertEqual("context-store/plan", refreshed["spec_storage"]["root"])
        self.assertEqual("iwiki", refreshed["documentation"]["root"])
        workflow = project / "docs" / "workflow-rule.md"
        self.assertIn(
            "- 项目 Context：`context-store/CONTEXT.md`",
            workflow.read_text(encoding="utf-8"),
        )

        created = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(),
            write=True,
        )

        target = context_root / "CONTEXT.md"
        self.assertEqual(("ok", "committed"), (created["status"], created["transaction"]))
        self.assertEqual(target, Path(created["target"]))
        self.assertTrue(target.is_file())

    def test_external_storage_bases_are_derived_independently(self) -> None:
        project = self.root / "independent-storage-bases"
        project.mkdir()
        documentation_root = self.root / "documentation-root"
        documentation_root.mkdir(parents=True)
        spec_base = self.root / "separate-spec-storage"
        (spec_base / "plan").mkdir(parents=True)

        configured = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                spec_base_kind="external-absolute",
                spec_base=str(spec_base),
                documentation_policy="on-request",
                documentation_root_kind="external-absolute",
                documentation_root=str(documentation_root),
                documentation_write_authorization="per-write-confirmation",
            ),
        )

        self.assertEqual(str(spec_base / "plan"), configured["spec_storage"]["root"])
        self.assertEqual(str(documentation_root), configured["documentation"]["root"])
        workflow = project / "docs" / "workflow-rule.md"
        content = workflow.read_text(encoding="utf-8")
        self.assertIn(f"- Spec：`{spec_base / 'plan'}`", content)
        self.assertIn(f"- 项目文档：`on-request` -> `{documentation_root}`", content)
        self.assertIn(
            f"- 项目 Context：`{spec_base}\\CONTEXT.md`",
            content,
        )

    def test_project_context_rejects_unqualified_or_implicit_existing_updates(self) -> None:
        project, document_root = self.configured_document_project(
            "project-context-rejections",
            policy="required-at-closeout",
            authorization="bounded-closeout",
        )
        empty_consumer = self.context_input()["entries"][0]
        empty_consumer["consumers"] = ""
        refused = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(entries=[empty_consumer]),
        )
        self.assertEqual("refused", refused["status"])

        created = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(),
            write=True,
        )
        self.assertEqual("ok", created["status"])
        target = project / "docs" / "CONTEXT.md"
        missing_preimage = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.context_input(),
        )
        self.assertEqual("refused", missing_preimage["status"])
        self.assertIn("requires expected_target_sha256", missing_preimage["conflicts"][0])

    def test_project_context_cli_uses_integration_fixed_target(self) -> None:
        project, document_root = self.configured_document_project(
            "project-context-cli",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        input_path = project / "context-input.json"
        input_path.write_text(
            json.dumps(
                self.context_input(trigger="human-request"),
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        process = subprocess.run(
            (
                sys.executable,
                "-B",
                str(DOCUMENT_SCRIPT),
                "--project-root",
                str(project),
                "--input-json",
                str(input_path),
                "--per-write-confirmed",
                "--write",
            ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(("ok", "committed"), (result["status"], result["transaction"]))
        self.assertEqual(project / "docs" / "CONTEXT.md", Path(result["target"]))
        self.assertTrue((project / "docs" / "CONTEXT.md").is_file())

    def test_project_documentation_refuses_unreachable_escape_and_root_boundaries(self) -> None:
        project = self.root / "documents-unreachable"
        project.mkdir()
        missing = self.root / "missing-documentation-root"
        setup = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                documentation_policy="on-request",
                documentation_root_kind="external-absolute",
                documentation_root=str(missing),
                documentation_write_authorization="per-write-confirmation",
            ),
        )
        self.assertEqual("committed", setup["transaction"])
        unreachable = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(),
            per_write_confirmed=True,
        )
        self.assertEqual("refused", unreachable["status"])
        self.assertIn("absent or unreachable", unreachable["conflicts"][0])

        bounded, _ = self.configured_document_project(
            "documents-bounds",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        escaped = document_generator.generate_project_document(
            project_root=bounded,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(output_path="../outside.md"),
            per_write_confirmed=True,
        )
        self.assertEqual("refused", escaped["status"])
        self.assertFalse((bounded / "outside.md").exists())

        workflow = bounded / "docs" / "workflow-rule.md"
        original = workflow.read_text(encoding="utf-8")
        for unsafe_root in ("G:\\", "\\\\server\\share\\"):
            with self.subTest(unsafe_root=unsafe_root):
                workflow.write_text(
                    original.replace(
                        "-> `docs/archive`",
                        f"-> `{unsafe_root}`",
                    ),
                    encoding="utf-8",
                )
                refused = document_generator.generate_project_document(
                    project_root=bounded,
                    workflow_rule_path="docs/workflow-rule.md",
                    document_input=self.document_input(),
                    per_write_confirmed=True,
                )
                self.assertEqual("refused", refused["status"])
                self.assertIn("drive or share root", refused["conflicts"][0])
        workflow.write_text(original, encoding="utf-8")

    def test_project_documentation_rejects_internal_references_and_invalid_integration(self) -> None:
        project, _ = self.configured_document_project(
            "documents-content",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        forbidden_values = (
            "详情见 docs/plan/x/spec.md。",
            "详情见 spec.md。",
            "详情见 `execution-report.md`。",
            "证据位于 cache/evidence.json。",
            "内部任务 SO-CONTEXT-BUDGET-2026-07-27。",
            "Codex thread 019fa2ed-c03f-7b42-8962-cb9c4bed6416。",
            "缓存位于 plugins/cache/sacha-orchestra。",
            "本机路径 C:\\Users\\name\\evidence.txt。",
        )
        for forbidden in forbidden_values:
            with self.subTest(forbidden=forbidden):
                sections = self.document_input()["sections"]
                sections["implementation"] = forbidden
                internal = document_generator.generate_project_document(
                    project_root=project,
                    workflow_rule_path="docs/workflow-rule.md",
                    document_input=self.document_input(sections=sections),
                    per_write_confirmed=True,
                )
                self.assertEqual("refused", internal["status"])
                self.assertIn(
                    "internal or machine-local reference",
                    internal["conflicts"][0],
                )

        workflow = project / "docs" / "workflow-rule.md"
        content = workflow.read_text(encoding="utf-8")
        workflow.write_text(
            content.replace(
                "### Storage",
                "### Unresolved\n\n- documentation policy\n\n### Storage",
            ),
            encoding="utf-8",
        )
        unresolved = document_generator.generate_project_document(
            project_root=project,
            workflow_rule_path="docs/workflow-rule.md",
            document_input=self.document_input(),
            per_write_confirmed=True,
        )
        self.assertEqual("refused", unresolved["status"])
        self.assertIn("unresolved decisions", unresolved["conflicts"][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
