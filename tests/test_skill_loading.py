"""Behavior tests for setup-project Skill loading resolution."""

if __package__:
    from .project_test_support import ProjectTestCase, digest, generator, resolver
else:
    from project_test_support import ProjectTestCase, digest, generator, resolver


class SkillLoadingTests(ProjectTestCase):
    def test_skill_loading_resolution_does_not_guess(self) -> None:
        catalog = {
            "providers": [
                {
                    "canonical": "cgame-unity",
                    "name": "cgame-unity",
                    "capabilities": [
                        {"skill": "cgame-unity:compile-verify"}
                    ],
                }
            ],
            "skills": [
                {
                    "canonical": "cgame-unity:compile-verify",
                    "name": "compile-verify",
                    "description": "Compile the current Unity project.",
                },
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
        self.assertEqual([], exact["proposed_skill_loadings"])
        self.assertEqual(
            [{
                "skill": "cgame-unity:compile-verify",
                "description": "Compile the current Unity project.",
            }],
            exact["skill_policy_decisions_required"],
        )
        self.assertEqual([], exact["warnings"])
        self.assertEqual("needs_decision", ambiguous["status"])
        self.assertEqual("ambiguous", ambiguous["queries"][0]["resolution"])
        self.assertEqual("zero_match", missing["queries"][0]["resolution"])
        self.assertEqual("needs_decision", roots["status"])
        self.assertIsNone(roots["project_root"])

    def test_skill_loading_resolution_requires_human_policy(self) -> None:
        catalog = {
            "providers": [
                {
                    "canonical": "review-provider",
                    "name": "review-provider",
                    "capabilities": [
                        {"skill": "review-provider:change-review"}
                    ],
                }
            ]
        }

        undecided = resolver.resolve_queries(catalog, ("review-provider",))
        result = resolver.resolve_queries(
            catalog,
            ("review-provider",),
            load_policies={"review-provider:change-review": "review-only"},
        )

        self.assertEqual("needs_decision", undecided["status"])
        self.assertEqual([], undecided["proposed_skill_loadings"])
        self.assertEqual("resolved", result["status"])
        self.assertEqual(
            [{
                "skill": "review-provider:change-review",
                "load_policy": "review-only",
            }],
            result["proposed_skill_loadings"],
        )
        self.assertEqual([], result["warnings"])
        with self.assertRaises(resolver.CatalogError):
            resolver.resolve_queries(
                catalog,
                ("review-provider",),
                load_policies={"review-provider:change-review": "always"},
            )
        with self.assertRaises(resolver.CatalogError):
            resolver.resolve_queries(
                catalog,
                ("review-provider",),
                load_policies={"unknown-provider:unknown-skill": "on-demand"},
            )

    def test_provider_catalog_schema_v3_and_legacy_v2_validation(self) -> None:
        valid = {
            "schema_version": "3",
            "provider": "cgame-unity",
            "capabilities": [
                {
                    "skill": "cgame-unity:compile-verify",
                    "side_effect": "project_generated_state",
                },
                {
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
        legacy = {
            "schema_version": "2",
            "provider": "cgame-unity",
            "capabilities": [
                {"id": "compile.verify", **valid["capabilities"][0]},
                {"id": "project.inspect", **valid["capabilities"][1]},
            ],
        }
        self.assertEqual(
            parsed,
            resolver.validate_provider_catalog(
                legacy,
                expected_provider="cgame-unity",
                visible_skills=visible,
            ),
        )

        invalid_cases = {
            "schema": {**valid, "schema_version": "1"},
            "provider": {**valid, "provider": "other-provider"},
            "extra_root": {**valid, "summary": "duplicated owner"},
            "duplicate_skill": {
                **valid,
                "capabilities": [
                    valid["capabilities"][0],
                    {**valid["capabilities"][1], "skill": "cgame-unity:compile-verify"},
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

    def test_schema_v2_catalog_migrates_to_skill_loading(self) -> None:
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
            }],
            "skills": [{
                "canonical": "cgame-unity:compile-verify",
                "name": "compile-verify",
                "description": "Compile the affected Unity assembly.",
            }],
        }

        undecided = resolver.resolve_queries(catalog, ("cgame-unity",))
        confirmed = resolver.resolve_queries(
            catalog,
            ("cgame-unity",),
            load_policies={"cgame-unity:compile-verify": "risk-matched"},
        )

        self.assertEqual("needs_decision", undecided["status"])
        self.assertEqual([], undecided["warnings"])
        self.assertEqual([], undecided["proposed_skill_loadings"])
        self.assertEqual(
            [{
                "skill": "cgame-unity:compile-verify",
                "description": "Compile the affected Unity assembly.",
                "side_effect": "project_generated_state",
            }],
            undecided["skill_policy_decisions_required"],
        )
        self.assertEqual("resolved", confirmed["status"])
        self.assertEqual([], confirmed["skill_policy_decisions_required"])
        self.assertEqual(
            [{
                "skill": "cgame-unity:compile-verify",
                "load_policy": "risk-matched",
            }],
            confirmed["proposed_skill_loadings"],
        )

    def test_skill_loading_reconciliation_is_explicit_and_idempotent(self) -> None:
        project = self.root / "capabilities"
        (project / ".git").mkdir(parents=True)
        (project / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        (project / ".git" / "objects").mkdir()

        initial = (
            "old-plugin:legacy-review::review-only",
            "old-plugin:extra::on-demand",
        )
        first = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                skill_loadings=initial,
                reconcile_skill_loading=True,
            ),
        )
        self.assertEqual("committed", first["transaction"])

        workflow = project / "docs" / "workflow-rule.md"
        desired = (
            "my-plugin:custom-review::review-only",
            "cgame-unity:compile-verify::risk-matched",
        )
        updated_config = self.config(
            project,
            manage_agents=False,
            scm_provider=None,
            spec_base_kind=None,
            spec_base=None,
            documentation_policy=None,
            skill_loadings=desired,
            reconcile_skill_loading=True,
            expected_workflow_sha256=digest(workflow),
        )
        before_update = workflow.read_bytes()
        update_preview = generator.run_setup(updated_config)
        self.assertEqual(
            {
                "spec_storage": "existing-binding",
                "roadmap_storage": "unconfigured",
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
                skill_loadings=desired,
                reconcile_skill_loading=True,
            ),
            write=True,
        )
        self.assertEqual("no_changes", repeated["transaction"])

    def test_schema_v3_multi_policy_skill_requires_explicit_migration(self) -> None:
        project = self.root / "legacy-schema"
        workflow = project / "docs" / "workflow-rule.md"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            """<!-- Generator: sacha-orchestra:setup-project -->
<!-- Schema Version: 3 -->
# Sacha Orchestra 项目接入

`setup-project` 生成；只记录项目差异。

## 项目绑定

- Project AGENTS：`AGENTS.md`
- SCM：未配置

### Capability bindings

- `on-demand`：`project.discover` -> `provider:operator`
- `risk-matched`：`project.operate` -> `provider:operator`
- `after-write-authorization`：`project.guard` -> `provider:guard`

### Storage

- Spec：`docs/plan`
- 任务目录：`<YYYY-MM-DD>-<short-slug>/`
- 文件：`spec.md`；探索决定：`decisions.md`（按需，与 Spec 同目录）
- 项目文档：`disabled`
- 项目 Context：`docs/CONTEXT.md`（术语与跨任务约束；setup 只记录 path，不创建正文）
""",
            encoding="utf-8",
        )

        blocked = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                spec_base_kind=None,
                spec_base=None,
                documentation_policy=None,
            )
        )
        self.assertEqual("refused", blocked["status"])
        self.assertTrue(
            any(
                "multiple load policies" in str(item.get("reason", ""))
                for item in blocked["skill_loading_reconciliation"]["warning"]
            ),
            blocked["skill_loading_reconciliation"],
        )
        legacy_guard = next(
            item
            for item in blocked["skill_loading_reconciliation"]["keep"]
            if item["skill"] == "provider:guard"
        )
        self.assertEqual("change-authorized", legacy_guard["value"]["load_policy"])

        migrated = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                spec_base_kind=None,
                spec_base=None,
                documentation_policy=None,
                skill_loadings=(
                    "provider:guard::change-authorized",
                    "provider:operator::on-demand",
                ),
                reconcile_skill_loading=True,
            )
        )
        self.assertEqual("ready", migrated["status"], migrated["conflicts"])
        content = migrated["workflow_rule"]["planned_content"]
        self.assertIn("<!-- Schema Version: 4 -->", content)
        self.assertIn("### Skill loading", content)
        self.assertIn("- `on-demand`\n  - `provider:operator`", content)
        self.assertIn("- `change-authorized`\n  - `provider:guard`", content)
        self.assertNotIn("project.discover", content)

    def test_setup_cli_exposes_only_skill_level_options(self) -> None:
        options = generator.build_parser()._option_string_actions

        for option in (
            "--skill-loading",
            "--reconcile-skill-loading",
            "--unavailable-skill",
        ):
            self.assertIn(option, options)
        for legacy in (
            "--capability-binding",
            "--reconcile-capabilities",
            "--unavailable-capability-skill",
        ):
            self.assertNotIn(legacy, options)

    def test_skill_loading_requires_explicit_policy(self) -> None:
        project = self.root / "policy-required"
        project.mkdir()

        result = generator.run_setup(
            self.config(
                project,
                skill_loadings=(
                    "cgame-unity:compile-verify",
                ),
                reconcile_skill_loading=True,
            ),
            write=True,
        )

        self.assertEqual("refused", result["status"])
        self.assertEqual("no_write", result["transaction"])
        self.assertEqual([], list(project.iterdir()))
        self.assertIn("skill_loading", result["conflicts"][0])

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
        self.assertEqual([], result["project_skill_candidates"])

        guessed = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                skill_root_bindings=(".agents/skills::authority",),
                skill_loadings=(
                    "architecture-health::on-demand",
                ),
                reconcile_skill_loading=True,
            )
        )
        self.assertEqual("refused", guessed["status"])
        self.assertTrue(
            any("project Skill evidence" in item for item in guessed["conflicts"]),
            guessed["conflicts"],
        )

    def test_project_skill_body_can_admit_multiple_units_with_one_policy(self) -> None:
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
                    "goal": "Analyze an RDC capture without changing runtime state.",
                    "kind": "inspect",
                    "admission": "schedulable",
                    "side_effect": "read_only",
                    "evidence": ["8-9"],
                    "required_paths": ["tools/static.py"],
                    "runtime_prerequisites": [],
                    "reason": "The body defines a bounded static analysis workflow and output.",
                },
                {
                    "goal": "Replay a capture on an explicitly selected Android device.",
                    "kind": "operate",
                    "admission": "schedulable",
                    "side_effect": "runtime_state",
                    "evidence": ["11-12"],
                    "required_paths": ["tools/remote.py"],
                    "runtime_prerequisites": ["selected Android device"],
                    "reason": "The body defines a separate remote replay workflow.",
                },
            ],
            load_policy="on-demand",
        )
        config = self.config(
            project,
            manage_agents=False,
            skill_root_bindings=(".agents/skills::authority",),
            assess_project_skills=True,
            visible_project_skills=("renderdoc-rdc-analysis",),
            project_skill_evidence=(evidence,),
            reconcile_skill_loading=True,
        )

        preview = generator.run_setup(config)

        self.assertEqual("ready", preview["status"], preview["conflicts"])
        self.assertEqual([], preview["unassessed_project_skills"])
        self.assertEqual([], preview["skill_policy_decisions_required"])
        self.assertEqual(
            [
                "Analyze an RDC capture without changing runtime state.",
                "Replay a capture on an explicitly selected Android device.",
            ],
            [
                item["goal"]
                for item in preview["project_skill_candidates"]
            ],
        )
        self.assertEqual(
            [
                {"skill": "renderdoc-rdc-analysis", "after": {
                    "skill": "renderdoc-rdc-analysis",
                    "load_policy": "on-demand",
                }},
            ],
            preview["skill_loading_reconciliation"]["add"],
        )

        written = self.confirmed_setup(config)
        workflow = (project / "docs" / "workflow-rule.md").read_text(encoding="utf-8")
        self.assertEqual("committed", written["transaction"])
        self.assertIn(
            "- `on-demand`\n  - `renderdoc-rdc-analysis`",
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
            "reconcile_skill_loading": True,
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
                "skill": "local-build",
                "description": "Project-local test Skill.",
                "side_effects": ["project_generated_state"],
            }],
            undecided["skill_policy_decisions_required"],
        )
        self.assertEqual([], undecided["skill_loading_reconciliation"]["add"])

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
                reconcile_skill_loading=True,
            )
        )
        self.assertEqual("ready", unavailable["status"], unavailable["conflicts"])
        self.assertEqual([], unavailable["project_skill_candidates"])
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
            "goal": "Verify the current project through its local entrypoint.",
            "kind": "verify",
            "admission": "schedulable",
            "side_effect": "read_only",
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
            load_policy="on-demand",
        )
        frontmatter = self.project_skill_evidence(
            project,
            skill,
            [{**unit, "evidence": ["2"]}],
            load_policy="on-demand",
        )
        missing_path = self.project_skill_evidence(
            project,
            skill,
            [{**unit, "required_paths": ["tools/verify.py"]}],
            load_policy="on-demand",
        )
        common = {
            "manage_agents": False,
            "skill_root_bindings": (".agents/skills::authority",),
            "assess_project_skills": True,
            "visible_project_skills": ("local-verify",),
            "reconcile_skill_loading": True,
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
                self.assertEqual([], result["project_skill_candidates"])
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
                reconcile_skill_loading=True,
            )
        )

        self.assertEqual("ready", result["status"], result["conflicts"])
        self.assertEqual([], result["unassessed_project_skills"])
        self.assertEqual([], result["project_skill_candidates"])
        self.assertEqual([], result["skill_loading_reconciliation"]["add"])
