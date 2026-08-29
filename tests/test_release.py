from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release.py"
SPEC = importlib.util.spec_from_file_location("release_script", SCRIPT)
assert SPEC and SPEC.loader
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseScriptTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def init_release_repo(self, root: Path, remote: Path, validator_exit: int = 0) -> None:
        self.git(root, "init", "-b", "main")
        self.git(root, "config", "user.name", "Release Test")
        self.git(root, "config", "user.email", "release-test@example.invalid")
        (root / "tests").mkdir()
        (root / "tests" / "validate_release_coherence.py").write_text(
            f"raise SystemExit({validator_exit})\n", encoding="utf-8"
        )
        (root / "candidate.txt").write_text("base\n", encoding="utf-8")
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "base")
        self.git(remote, "init", "--bare")
        self.git(root, "remote", "add", "origin", str(remote))
        self.git(root, "push", "-u", "origin", "main")
        (root / "candidate.txt").write_text("release\n", encoding="utf-8")
        self.git(root, "add", "candidate.txt")

    def test_tree_hashes_detects_missing_extra_and_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left = Path(left_dir)
            right = Path(right_dir)
            (left / "same.txt").write_text("same", encoding="utf-8")
            (right / "same.txt").write_text("same", encoding="utf-8")
            self.assertEqual(release.tree_hashes(left), release.tree_hashes(right))
            (right / "same.txt").write_text("different", encoding="utf-8")
            self.assertNotEqual(release.tree_hashes(left), release.tree_hashes(right))
            (right / "extra.txt").write_text("extra", encoding="utf-8")
            self.assertNotEqual(release.tree_hashes(left), release.tree_hashes(right))

    def test_windows_codex_cli_prefers_executable_wrapper(self) -> None:
        paths = {
            "codex.cmd": r"C:\Tools\codex.cmd",
            "codex.exe": r"C:\Tools\codex.exe",
        }
        with mock.patch.object(release.sys, "platform", "win32"), mock.patch.object(
            release.shutil, "which", side_effect=paths.get
        ):
            self.assertEqual(release.codex_cli(), paths["codex.cmd"])

    def test_codex_cli_missing_is_reported(self) -> None:
        with mock.patch.object(release.shutil, "which", return_value=None), self.assertRaisesRegex(
            release.ReleaseError, "未找到可执行的 Codex CLI"
        ):
            release.codex_cli()

    def test_publish_requires_explicit_review_disposition(self) -> None:
        parser = release.parser()
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "publish",
                    "--version",
                    "0.11.0",
                    "--message",
                    "release",
                    "--candidate-path",
                    "candidate.txt",
                ]
            )
        args = parser.parse_args(
            [
                "publish",
                "--version",
                "0.11.0",
                "--review",
                "reused",
                "--message",
                "release",
                "--candidate-path",
                "candidate.txt",
            ]
        )
        self.assertEqual(args.review, "reused")

    def test_prepare_runs_validations_and_reports_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            self.git(root, "init", "-b", "main")
            self.git(root, "config", "user.name", "Release Test")
            self.git(root, "config", "user.email", "release-test@example.invalid")
            (root / "candidate.txt").write_text("candidate\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt")
            command = (release.current_python(), "-c", "print('validated')")
            with mock.patch.object(release, "ROOT", root), mock.patch.object(
                release, "validation_commands", return_value=[command]
            ):
                output = io.StringIO()
                with redirect_stdout(output):
                    release.prepare("0.1.0", ["candidate.txt"])
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["status"], "pass")
            self.assertRegex(payload["tree"], r"^[0-9a-f]{40}$")
            self.assertGreaterEqual(payload["duration_seconds"], 0)
            self.assertEqual(payload["validation"][0]["stdout"], "validated")
            self.assertGreaterEqual(payload["validation"][0]["duration_seconds"], 0)

    def test_staged_text_returns_none_for_binary_blob(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            self.git(root, "init", "-b", "main")
            (root / "asset.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff")
            self.git(root, "add", "asset.png")
            with mock.patch.object(release, "ROOT", root):
                self.assertIsNone(release.staged_text("asset.png", ""))

    def test_skill_body_only_skips_structure_validators(self) -> None:
        path = "plugins/sacha-orchestra/skills/executor/SKILL.md"
        before = "---\nname: executor\ndescription: use\n---\nold body\n"
        after = "---\nname: executor\ndescription: use\n---\nnew body\n"
        with mock.patch.object(release, "creator_script") as creator:
            commands = release.validation_commands("0.1.0", [path], deltas={path: (before, after)})
        creator.assert_not_called()
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertNotIn("validate_plugin.py", rendered)
        self.assertNotIn("quick_validate.py", rendered)
        self.assertNotIn("unittest discover", rendered)
        self.assertNotIn("install", rendered)
        self.assertNotIn("refresh", rendered.lower())

    def test_skill_frontmatter_change_runs_only_quick_validator(self) -> None:
        path = "plugins/sacha-orchestra/skills/executor/SKILL.md"
        before = "---\nname: executor\ndescription: old\n---\nbody\n"
        after = "---\nname: executor\ndescription: new\n---\nbody\n"
        with mock.patch.object(
            release, "creator_script", return_value=Path("quick_validate.py")
        ):
            commands = release.validation_commands("0.1.0", [path], deltas={path: (before, after)})
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("quick_validate.py", rendered)
        self.assertNotIn("validate_plugin.py", rendered)

    def test_project_skill_metadata_runs_only_quick_validator(self) -> None:
        paths = (
            ".agents/skills/sacha-doc-governance/SKILL.md",
            ".agents/skills/sacha-doc-governance/agents/openai.yaml",
        )
        deltas = {
            paths[0]: (None, "---\nname: sacha-doc-governance\ndescription: use\n---\nbody\n"),
            paths[1]: (None, "interface: {}\n"),
        }
        with mock.patch.object(
            release,
            "creator_script",
            side_effect=lambda _creator, script: Path(script),
        ):
            commands = release.validation_commands("0.1.0", list(paths), deltas=deltas)
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("quick_validate.py", rendered)
        self.assertIn(".agents", rendered)
        self.assertNotIn("validate_plugin.py", rendered)

    def test_deleted_skill_metadata_does_not_validate_absent_root(self) -> None:
        path = "plugins/sacha-orchestra/skills/clarify/SKILL.md"
        before = "---\nname: clarify\ndescription: old\n---\nbody\n"
        with mock.patch.object(
            release,
            "creator_script",
            side_effect=lambda _creator, script: Path(script),
        ):
            commands = release.validation_commands(
                "0.1.0",
                [path],
                deltas={path: (before, None)},
            )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertNotIn("quick_validate.py", rendered)
        self.assertIn("validate_plugin.py", rendered)

    def test_manifest_change_runs_plugin_validator(self) -> None:
        path = "plugin.json"
        with mock.patch.object(
            release, "creator_script", return_value=Path("validate_plugin.py")
        ):
            commands = release.validation_commands(
                "0.1.0", [path], deltas={path: ("{}\n", '{"version":"0.1.0"}\n')}
            )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("validate_plugin.py", rendered)

    def test_added_packaged_resource_runs_plugin_validator(self) -> None:
        path = "plugins/sacha-orchestra/assets/new.md"
        with mock.patch.object(
            release, "creator_script", return_value=Path("validate_plugin.py")
        ):
            commands = release.validation_commands(
                "0.1.0", [path], deltas={path: (None, "resource\n")}
            )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("validate_plugin.py", rendered)

    def test_unmapped_production_script_is_rejected(self) -> None:
        path = "scripts/new_producer.py"
        with self.assertRaisesRegex(release.ReleaseError, "缺少最窄测试映射"):
            release.validation_commands("0.1.0", [path], deltas={path: (None, "print('x')\n")})

    def test_dsh_companion_machine_files_select_package_validator(self) -> None:
        paths = [
            "integrations/dsh/sacha-companion/package.json",
            "integrations/dsh/sacha-companion/cordis.patch.yml",
            "integrations/dsh/sacha-companion/src/index.ts",
        ]
        commands = release.validation_commands(
            "0.1.0",
            paths,
            deltas={path: (None, "candidate\n") for path in paths},
        )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn(release.DSH_COMPANION_VALIDATOR, rendered)
        self.assertEqual(rendered.count(release.DSH_COMPANION_VALIDATOR), 1)

    def test_dsh_companion_validator_change_runs_release_tests(self) -> None:
        path = release.DSH_COMPANION_VALIDATOR
        commands = release.validation_commands(
            "0.1.0",
            [path],
            deltas={path: (None, "candidate\n")},
        )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("tests.test_release", rendered)
        self.assertNotIn(path, rendered)

    def test_retired_dsh_companion_paths_select_migration_validation(self) -> None:
        paths = [
            "integrations/dsh/sacha-visualizer/package.json",
            "integrations/dsh/sacha-visualizer/cordis.patch.yml",
            "integrations/dsh/sacha-subagents/package.json",
            "integrations/dsh/sacha-subagents/cordis.patch.yml",
            "tests/test_dsh_subagents.py",
            "tests/validate_dsh_subagents.py",
            "tests/validate_dsh_visualizer.py",
        ]
        commands = release.validation_commands(
            "0.1.0",
            paths,
            deltas={path: ("retired\n", None) for path in paths},
        )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("tests.test_dsh_companion", rendered)
        self.assertIn(release.DSH_COMPANION_VALIDATOR, rendered)
        self.assertEqual(rendered.count(release.DSH_COMPANION_VALIDATOR), 1)

    def test_production_schema_selects_its_direct_test(self) -> None:
        paths = [
            "plugins/sacha-orchestra/skills/document-project/assets/project-context.json",
            "plugins/sacha-orchestra/skills/document-project/assets/roadmap.json",
            "plugins/sacha-orchestra/skills/document-project/assets/roadmap.md",
        ]
        for path in paths:
            with self.subTest(path=path):
                commands = release.validation_commands(
                    "0.1.0",
                    [path],
                    deltas={path: ("before\n", "after\n")},
                )
                rendered = "\n".join(" ".join(command) for command in commands)
                self.assertIn("tests.test_document_project", rendered)

    def test_shared_project_test_support_selects_both_consumers(self) -> None:
        path = "tests/project_test_support.py"
        commands = release.validation_commands(
            "0.1.0",
            [path],
            deltas={path: ("before\n", "after\n")},
        )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("tests.test_setup_project", rendered)
        self.assertIn("tests.test_document_project", rendered)

    def test_runtime_scenario_paths_select_direct_tests(self) -> None:
        paths = [
            "tests/test_code_mode_batch_asset.py",
            "tests/test_runtime_scenario_verifiers.py",
            "tests/runtime-scenarios/packs/explore-shared-context-loop/fixture/verify.py",
            "tests/runtime-scenarios/packs/planner-explore-manager-reviewer/fixture/verify.py",
            "tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/verify.py",
            "tests/runtime-scenarios/packs/codex-code-mode-readonly-batch/fixture/probe.json",
            "tests/runtime-scenarios/packs/codex-code-mode-v1-batch/fixture/verify.py",
            "tests/runtime-scenarios/packs/reviewer-semantic-chain/fixture/baseline/cli.py",
        ]
        commands = release.validation_commands(
            "0.11.10",
            paths,
            deltas={path: (None, "candidate\n") for path in paths},
        )
        rendered = "\n".join(" ".join(command) for command in commands)
        self.assertIn("tests.test_code_mode_batch_asset", rendered)
        self.assertIn("tests.test_runtime_scenario_verifiers", rendered)

    def test_unrelated_tracked_working_change_does_not_block_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            self.git(root, "init", "-b", "main")
            (root / "candidate.txt").write_text("base\n", encoding="utf-8")
            (root / "unrelated.txt").write_text("base\n", encoding="utf-8")
            self.git(root, "add", ".")
            self.git(root, "commit", "-m", "base")
            (root / "candidate.txt").write_text("candidate\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt")
            (root / "unrelated.txt").write_text("working\n", encoding="utf-8")
            with mock.patch.object(release, "ROOT", root):
                self.assertEqual(release.require_staged_candidate(["candidate.txt"]), ["candidate.txt"])

    def test_unrelated_staged_change_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            self.git(root, "init", "-b", "main")
            (root / "candidate.txt").write_text("candidate\n", encoding="utf-8")
            (root / "unrelated.txt").write_text("user staged\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt", "unrelated.txt")
            with mock.patch.object(release, "ROOT", root), self.assertRaisesRegex(
                release.ReleaseError, "unexpected=.*unrelated.txt"
            ):
                release.require_staged_candidate(["candidate.txt"])

    def test_candidate_with_unstaged_delta_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            self.git(root, "init", "-b", "main")
            (root / "candidate.txt").write_text("base\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt")
            self.git(root, "commit", "-m", "base")
            (root / "candidate.txt").write_text("staged\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt")
            (root / "candidate.txt").write_text("working\n", encoding="utf-8")
            with mock.patch.object(release, "ROOT", root), self.assertRaisesRegex(
                release.ReleaseError, "暂存后又有未暂存修改"
            ):
                release.require_staged_candidate(["candidate.txt"])

    def test_prepare_uses_index_snapshot_and_cleans_temporary_tree(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            self.git(root, "init", "-b", "main")
            (root / "candidate.txt").write_text("candidate\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt")
            (root / "untracked.txt").write_text("pollution\n", encoding="utf-8")
            command = (
                release.current_python(),
                "-c",
                "from pathlib import Path; "
                "assert Path('candidate.txt').read_text() == 'candidate\\n'; "
                "assert not Path('untracked.txt').exists()",
            )
            with mock.patch.object(release, "ROOT", root), mock.patch.object(
                release, "validation_commands", return_value=[command]
            ):
                with redirect_stdout(io.StringIO()):
                    release.prepare("0.1.0", ["candidate.txt"])
            self.assertFalse((root / ".temp").exists())

    def test_prepare_failure_cleans_temporary_tree(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            self.git(root, "init", "-b", "main")
            (root / "candidate.txt").write_text("candidate\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt")
            command = (release.current_python(), "-c", "raise SystemExit(1)")
            with mock.patch.object(release, "ROOT", root), mock.patch.object(
                release, "validation_commands", return_value=[command]
            ), self.assertRaises(release.ReleaseError):
                release.prepare("0.1.0", ["candidate.txt"])
            self.assertFalse((root / ".temp").exists())

    def test_publish_creates_commit_tag_and_atomic_remote_identity(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as remote_dir:
            root = Path(root_dir)
            remote = Path(remote_dir)
            self.init_release_repo(root, remote)
            with mock.patch.object(release, "ROOT", root):
                output = io.StringIO()
                with redirect_stdout(output):
                    release.publish("0.1.0", "reused", "release", "origin", ["candidate.txt"])
            payload = json.loads(output.getvalue())
            self.assertRegex(payload["tree"], r"^[0-9a-f]{40}$")
            self.assertGreaterEqual(payload["duration_seconds"], 0)
            self.assertIn("push", payload["timings"])
            self.assertEqual(payload["branch"], "main")
            self.assertEqual(payload["tag"], "v0.1.0")
            self.assertEqual(payload["remote"], "origin")
            self.assertIs(payload["remote_verified"], True)
            head = self.git(root, "rev-parse", "HEAD").stdout.strip()
            tag = self.git(root, "rev-parse", "v0.1.0^{}").stdout.strip()
            remote_head = self.git(root, "ls-remote", "origin", "refs/heads/main").stdout.split()[0]
            remote_tag = self.git(root, "ls-remote", "origin", "refs/tags/v0.1.0^{}").stdout.split()[0]
            self.assertEqual((head, tag, remote_head, remote_tag), (head, head, head, head))

    def test_publish_preserves_unrelated_working_change(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as remote_dir:
            root = Path(root_dir)
            remote = Path(remote_dir)
            self.init_release_repo(root, remote)
            (root / "unrelated.txt").write_text("base\n", encoding="utf-8")
            self.git(root, "add", "unrelated.txt")
            self.git(root, "commit", "-m", "add unrelated")
            self.git(root, "push", "origin", "main")
            (root / "candidate.txt").write_text("release two\n", encoding="utf-8")
            self.git(root, "add", "candidate.txt")
            (root / "unrelated.txt").write_text("working\n", encoding="utf-8")
            with mock.patch.object(release, "ROOT", root), redirect_stdout(io.StringIO()):
                release.publish("0.1.0", "reused", "release", "origin", ["candidate.txt"])
            committed = self.git(root, "show", "HEAD:unrelated.txt").stdout
            self.assertEqual(committed, "base\n")
            self.assertEqual((root / "unrelated.txt").read_text(encoding="utf-8"), "working\n")
            self.assertIn("unrelated.txt", self.git(root, "diff", "--name-only").stdout.splitlines())

    def test_publish_stops_before_commit_when_candidate_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as remote_dir:
            root = Path(root_dir)
            remote = Path(remote_dir)
            self.init_release_repo(root, remote, validator_exit=1)
            before = self.git(root, "rev-parse", "HEAD").stdout.strip()
            with mock.patch.object(release, "ROOT", root), self.assertRaises(release.ReleaseError):
                release.publish("0.1.0", "accepted", "release", "origin", ["candidate.txt"])
            self.assertEqual(self.git(root, "rev-parse", "HEAD").stdout.strip(), before)
            self.assertEqual(self.git(root, "tag", "--list", "v0.1.0").stdout.strip(), "")

    def test_install_checks_list_and_source_cache_parity(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as cache_dir:
            root = Path(root_dir)
            plugin = root / "plugins" / "sacha-orchestra"
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            plugin.mkdir(parents=True)
            marketplace.parent.mkdir(parents=True)
            marketplace.write_text("{}", encoding="utf-8")
            (plugin / "plugin.txt").write_text("same", encoding="utf-8")
            cache = Path(cache_dir)
            (cache / "plugin.txt").write_text("same", encoding="utf-8")
            helper = root / "read_marketplace_name.py"
            helper.write_text("", encoding="utf-8")
            responses = [
                subprocess.CompletedProcess([], 0, "sacha\n", ""),
                subprocess.CompletedProcess(
                    [],
                    0,
                    json.dumps({"version": "0.1.0", "installedPath": str(cache)}),
                    "",
                ),
                subprocess.CompletedProcess(
                    [], 0, "sacha-orchestra@sacha  installed, enabled  0.1.0  path\n", ""
                ),
            ]
            with mock.patch.object(release, "ROOT", root), mock.patch.object(
                release, "PLUGIN", plugin
            ), mock.patch.object(release, "creator_script", return_value=helper), mock.patch.object(
                release, "codex_cli", return_value="codex.cmd"
            ), mock.patch.object(
                release, "run", side_effect=responses
            ):
                output = io.StringIO()
                with redirect_stdout(output):
                    release.install("0.1.0")
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["files"], 1)

    def test_install_access_denied_stops_without_cache_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            helper = root / "read_marketplace_name.py"
            helper.write_text("", encoding="utf-8")
            responses = [
                subprocess.CompletedProcess([], 0, "sacha\n", ""),
                release.ReleaseError("命令失败：拒绝访问。 (os error 5)"),
            ]
            with mock.patch.object(release, "ROOT", root), mock.patch.object(
                release, "creator_script", return_value=helper
            ), mock.patch.object(
                release, "codex_cli", return_value="codex.cmd"
            ), mock.patch.object(release, "run", side_effect=responses):
                with self.assertRaisesRegex(release.ReleaseError, "关闭本次发布中已终态的辅助 Agent"):
                    release.install("0.1.0")


if __name__ == "__main__":
    unittest.main()
