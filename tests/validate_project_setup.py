"""Minimal behavior checks for setup-project's executable Python code."""

from __future__ import annotations

import hashlib
import importlib.util
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
        }
        values.update(overrides)
        return generator.SetupConfig(**values)

    def test_dry_run_commit_and_idempotent_rerun(self) -> None:
        project = self.root / "basic"
        project.mkdir()

        dry_run = generator.run_setup(self.config(project))
        self.assertEqual("dry_run", dry_run["transaction"])
        self.assertEqual([], list(project.iterdir()))

        committed = generator.run_setup(self.config(project), write=True)
        self.assertEqual("committed", committed["transaction"])
        self.assertTrue((project / "docs" / "workflow-rule.md").is_file())
        self.assertTrue((project / "AGENTS.md").is_file())

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

    def test_generated_documents_only_add_project_integration_data(self) -> None:
        project = self.root / "document-boundary"
        project.mkdir()

        result = generator.run_setup(self.config(project), write=True)
        self.assertEqual("committed", result["transaction"])

        workflow = (project / "docs" / "workflow-rule.md").read_text(encoding="utf-8")
        agents = (project / "AGENTS.md").read_text(encoding="utf-8")
        for heading in (
            "## 项目值",
            "## 项目绑定",
            "### Unresolved",
            "### Conflicts",
            "### Fallback",
            "## Canonical locators",
        ):
            self.assertIn(heading, workflow)
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

        result = generator.run_setup(
            self.config(project),
            write=True,
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

        self.assertEqual("resolved", exact["status"])
        self.assertEqual(
            [{"id": "compile.verify", "skill": "cgame-unity:compile-verify"}],
            exact["proposed_capability_bindings"],
        )
        self.assertEqual("needs_decision", ambiguous["status"])
        self.assertEqual("ambiguous", ambiguous["queries"][0]["resolution"])
        self.assertEqual("zero_match", missing["queries"][0]["resolution"])
        self.assertEqual("needs_decision", roots["status"])
        self.assertIsNone(roots["project_root"])

    def test_capability_reconciliation_is_explicit_and_idempotent(self) -> None:
        project = self.root / "capabilities"
        (project / ".git").mkdir(parents=True)

        initial = (
            "change.review::old-plugin:legacy-review::review-only",
            "legacy.extra::old-plugin:extra::on-demand",
        )
        first = generator.run_setup(
            self.config(
                project,
                manage_agents=False,
                scm_provider=None,
                capability_bindings=initial,
                reconcile_capabilities=True,
            ),
            write=True,
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
            capability_bindings=desired,
            reconcile_capabilities=True,
            expected_workflow_sha256=digest(workflow),
        )
        updated = generator.run_setup(updated_config, write=True)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
