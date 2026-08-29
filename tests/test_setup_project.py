"""Behavior tests for the setup-project production entrypoint."""

import json
import subprocess
import sys

if __package__:
    from .project_test_support import ProjectTestCase, SETUP_SCRIPT, digest, generator
else:
    from project_test_support import ProjectTestCase, SETUP_SCRIPT, digest, generator


class SetupProjectTests(ProjectTestCase):
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
                "roadmap_storage": None,
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
                "goal": "Inspect current project state.",
                "kind": "inspect",
                "admission": "schedulable",
                "side_effect": "read_only",
                "evidence": ["8"],
                "required_paths": [],
                "runtime_prerequisites": [],
                "reason": "The body defines a bounded inspection and report.",
            }],
            load_policy="on-demand",
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
                "--reconcile-skill-loading",
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
            ["Inspect current project state."],
            [item["goal"] for item in result["project_skill_candidates"]],
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
        self.assertIn("探索决定：`decisions.md`（按需，与 Spec 同目录）", generated)
        self.assertIn("- 项目 Context：`docs/CONTEXT.md`", generated)
        self.assertIsNone(missing["write_confirmation"]["planned"]["roadmap_storage"])
        self.assertNotIn("- Roadmap：", generated)

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

    def test_roadmap_root_is_explicit_preserved_and_independent(self) -> None:
        project = self.root / "roadmap-storage"
        project.mkdir()
        external_roadmap = self.root / "iwiki" / "docs" / "roadmap"
        external_roadmap.mkdir(parents=True)

        configured = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                roadmap_root_kind="external-absolute",
                roadmap_root=str(external_roadmap),
            )
        )
        self.assertEqual(str(external_roadmap), configured["roadmap_storage"]["root"])
        self.assertEqual("non-portable", configured["roadmap_storage"]["portability"])
        self.assertEqual(
            "<YYYY-MM-DD>-<short-slug>-roadmap.md",
            configured["roadmap_storage"]["file_pattern"],
        )
        self.assertNotEqual(
            configured["spec_storage"]["root"],
            configured["roadmap_storage"]["root"],
        )
        workflow = project / "docs" / "workflow-rule.md"
        self.assertIn(
            f"- Roadmap：`{external_roadmap}`",
            workflow.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "- Roadmap 文件：`<YYYY-MM-DD>-<short-slug>-roadmap.md`",
            workflow.read_text(encoding="utf-8"),
        )

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
        self.assertEqual(str(external_roadmap), preserved["roadmap_storage"]["root"])

        incomplete_project = self.root / "roadmap-incomplete"
        incomplete_project.mkdir()
        incomplete = generator.run_setup(
            self.config(
                incomplete_project,
                manage_agents=False,
                roadmap_root_kind="project-relative",
            )
        )
        self.assertEqual("refused", incomplete["status"])
        self.assertIn("roadmap_root is required", incomplete["conflicts"][0])

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
