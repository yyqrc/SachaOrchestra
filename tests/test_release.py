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
            ), mock.patch.object(release, "run", side_effect=responses):
                with self.assertRaisesRegex(release.ReleaseError, "关闭本次发布中已终态的辅助 Agent"):
                    release.install("0.1.0")


if __name__ == "__main__":
    unittest.main()
