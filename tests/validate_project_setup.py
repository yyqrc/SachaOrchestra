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
    / "project-documentation"
    / "scripts"
    / "generate_project_document.py"
)
TEMP_ROOT = ROOT / ".temp"


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
            "plan_root_kind": "project-relative",
            "plan_root": "docs/plans",
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

    def test_dry_run_commit_and_idempotent_rerun(self) -> None:
        project = self.root / "basic"
        project.mkdir()

        dry_run = generator.run_setup(self.config(project))
        self.assertEqual("dry_run", dry_run["transaction"])
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

        changed_config = self.config(project, plan_root="plans")
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
            "--plan-root-kind",
            "project-relative",
            "--plan-root",
            "docs/plans",
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
                "plan_storage": None,
                "documentation": None,
            },
            dry_run["write_confirmation"]["current"],
        )
        self.assertEqual("docs/plans", dry_run["write_confirmation"]["planned"]["plan_storage"]["root"])
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
                "--plan-root-kind",
                "project-relative",
                "--plan-root",
                "docs/plans",
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

    def test_plan_storage_is_explicit_separate_and_preserved(self) -> None:
        missing_project = self.root / "plan-missing"
        missing_project.mkdir()
        missing = generator.run_setup(
            generator.SetupConfig(
                project_root=missing_project,
                manage_agents=False,
                scm_provider="none",
                documentation_policy="disabled",
            )
        )
        self.assertEqual("refused", missing["status"])
        self.assertIn("plan_root_kind", missing["conflicts"][0])

        project = self.root / "plan-storage"
        project.mkdir()
        external_plan = self.root / "iwiki" / "docs"
        external_plan.mkdir(parents=True)
        configured = self.confirmed_setup(
            self.config(
                project,
                manage_agents=False,
                plan_root_kind="external-absolute",
                plan_root=str(external_plan),
                documentation_policy="on-request",
                documentation_root_kind="project-relative",
                documentation_root="docs/archive",
                documentation_write_authorization="per-write-confirmation",
            ),
        )
        self.assertEqual("committed", configured["transaction"])
        self.assertEqual(str(external_plan), configured["plan_storage"]["root"])
        self.assertEqual("non-portable", configured["plan_storage"]["portability"])
        self.assertEqual("docs/archive", configured["documentation"]["root"])
        self.assertNotEqual(
            configured["plan_storage"]["root"],
            configured["documentation"]["root"],
        )
        workflow = project / "docs" / "workflow-rule.md"
        content = workflow.read_text(encoding="utf-8")
        self.assertIn("### Storage", content)
        self.assertIn(f"- Plan：`{external_plan}`", content)

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
        self.assertEqual(str(external_plan), preserved["plan_storage"]["root"])
        self.assertEqual("docs/archive", preserved["documentation"]["root"])

        missing_external = self.root / "missing-plan-root"
        warned = generator.run_setup(
            self.config(
                self.root / "plan-storage",
                manage_agents=False,
                plan_root_kind="external-absolute",
                plan_root=str(missing_external),
            )
        )
        self.assertEqual("ready", warned["status"])
        self.assertFalse(missing_external.exists())
        self.assertEqual("plan_root_unreachable", warned["warnings"][0]["kind"])

        unsafe = generator.run_setup(
            self.config(
                self.root / "plan-storage",
                manage_agents=False,
                plan_root_kind="external-absolute",
                plan_root="G:\\",
            )
        )
        self.assertEqual("refused", unsafe["status"])
        self.assertIn("plan_root", unsafe["conflicts"][0])

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
        agents = (project / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("- SCM：未配置", workflow)
        self.assertIn("- Setup 忽略：`TEAM.md`", workflow)
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
            "## Canonical locators",
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
        self.assertIn("Human 接受 Sacha 后", agents)
        self.assertIn("plugin canonical contract", agents)

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
            plan_root_kind=None,
            plan_root=None,
            documentation_policy=None,
            capability_bindings=desired,
            reconcile_capabilities=True,
            expected_workflow_sha256=digest(workflow),
        )
        before_update = workflow.read_bytes()
        update_preview = generator.run_setup(updated_config)
        self.assertEqual(
            {
                "plan_storage": "existing-binding",
                "documentation": "existing-binding",
            },
            update_preview["write_confirmation"]["sources"],
        )
        self.assertEqual(
            "docs/plans",
            update_preview["write_confirmation"]["current"]["plan_storage"]["root"],
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

    def test_project_documentation_refuses_unreachable_escape_and_root_boundaries(self) -> None:
        project = self.root / "documents-unreachable"
        project.mkdir()
        missing = self.root / "missing-publication-root"
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

    def test_project_documentation_rejects_internal_locators_and_invalid_integration(self) -> None:
        project, _ = self.configured_document_project(
            "documents-content",
            policy="on-request",
            authorization="per-write-confirmation",
        )
        forbidden_values = (
            "详情见 docs/plans/x/spec.md。",
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
                    "internal or machine-local locator",
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
