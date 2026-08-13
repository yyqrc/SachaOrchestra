"""Behavior tests for the document-project production entrypoint."""

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

from project_test_support import (
    DOCUMENT_SCRIPT,
    ProjectTestCase,
    digest,
    document_generator,
    fill_bundled_template,
    generator,
)


class DocumentProjectTests(ProjectTestCase):
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
