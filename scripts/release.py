"""Run Sacha Orchestra's mechanical release steps.

Review, version choice, authorization, and Runtime acceptance stay with their
existing Owners. This script consumes those decisions and stops on failures.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"
DEPLOYMENT_MANIFESTS = {
    "plugin.json",
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
    "plugins/sacha-orchestra/plugin.json",
    "plugins/sacha-orchestra/.claude-plugin/plugin.json",
    "plugins/sacha-orchestra/.codex-plugin/plugin.json",
    "plugins/sacha-orchestra/.cursor-plugin/plugin.json",
}


class ReleaseError(RuntimeError):
    pass


def run(
    *args: str,
    check: bool = True,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd or ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        raise ReleaseError(f"命令无法启动：{' '.join(args)}\n{exc}") from exc
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ReleaseError(f"命令失败（{result.returncode}）：{' '.join(args)}\n{detail}")
    return result


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("git", *args, check=check)


def current_python() -> str:
    return sys.executable


def creator_script(creator: str, script: str) -> Path:
    home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    path = home / "skills" / ".system" / creator / "scripts" / script
    if not path.is_file():
        raise ReleaseError(f"未找到 Creator 脚本：{path}")
    return path


def codex_cli() -> str:
    candidates = ("codex.cmd", "codex.exe") if sys.platform == "win32" else ("codex",)
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    raise ReleaseError("未找到可执行的 Codex CLI")


def normalize_candidate_paths(expected: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw_path in expected:
        path = Path(raw_path)
        if path.is_absolute() or ".." in path.parts or raw_path in ("", "."):
            raise ReleaseError(f"`--candidate-path` 必须是仓库内精确相对 path：{raw_path}")
        normalized.append(path.as_posix())
    if len(normalized) != len(set(normalized)):
        raise ReleaseError("`--candidate-path` 不能重复")
    return sorted(normalized)


def require_staged_candidate(expected: list[str]) -> list[str]:
    staged = [line for line in git("diff", "--cached", "--name-only").stdout.splitlines() if line]
    if not staged:
        raise ReleaseError("没有已暂存的发布文件")
    expected_paths = normalize_candidate_paths(expected)
    missing = sorted(set(expected_paths) - set(staged))
    unexpected = sorted(set(staged) - set(expected_paths))
    if missing or unexpected:
        raise ReleaseError(
            "暂存区与 `--candidate-path` 指定文件不一致："
            f"missing={missing}, unexpected={unexpected}"
        )
    conflicts = git("diff", "--name-only", "--diff-filter=U").stdout.splitlines()
    if conflicts:
        raise ReleaseError(f"存在未解决冲突：{', '.join(conflicts)}")
    unstaged = {
        line for line in git("diff", "--name-only").stdout.splitlines() if line
    }
    overlap = sorted(set(staged) & unstaged)
    if overlap:
        raise ReleaseError(
            "以下发布文件暂存后又有未暂存修改：" + ", ".join(overlap)
        )
    return staged


def frontmatter(text: str | None) -> str | None:
    if text is None or not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    return None if end < 0 else text[: end + 5]


def staged_text(path: str, revision: str) -> str | None:
    result = git("show", f"{revision}:{path}", check=False)
    return result.stdout if result.returncode == 0 else None


def staged_deltas(staged: list[str]) -> dict[str, tuple[str | None, str | None]]:
    return {
        path: (staged_text(path, "HEAD"), staged_text(path, ""))
        for path in staged
    }


def changed_skill_metadata_roots(
    staged: list[str],
    deltas: dict[str, tuple[str | None, str | None]],
    plugin: Path = PLUGIN,
) -> list[Path]:
    prefix = "plugins/sacha-orchestra/skills/"
    names: set[str] = set()
    for path in staged:
        if not path.startswith(prefix) or "/" not in path[len(prefix) :]:
            continue
        relative = path[len(prefix) :]
        name, child = relative.split("/", 1)
        before, after = deltas[path]
        if child == "SKILL.md" and frontmatter(before) != frontmatter(after):
            names.add(name)
        elif child == "agents/openai.yaml":
            names.add(name)
    return [plugin / "skills" / name for name in sorted(names)]


def requires_plugin_validation(
    staged: list[str],
    deltas: dict[str, tuple[str | None, str | None]],
) -> bool:
    for path in staged:
        before, after = deltas[path]
        if path in DEPLOYMENT_MANIFESTS or path.endswith("/agents/openai.yaml"):
            return True
        if path.startswith("plugins/sacha-orchestra/") and (before is None or after is None):
            return True
    return False


def narrow_test_modules(staged: list[str]) -> list[str]:
    mappings = (
        (("scripts/release.py", "tests/test_release.py", "tests/validate_release_coherence.py"), "tests.test_release"),
        (("plugins/sacha-orchestra/skills/setup-project/scripts/", "tests/test_setup_project.py"), "tests.test_setup_project"),
        (("plugins/sacha-orchestra/skills/document-project/scripts/", "tests/test_document_project.py"), "tests.test_document_project"),
        (("plugins/sacha-orchestra/skills/document-project/assets/project-context.json",), "tests.test_document_project"),
        (("plugins/sacha-orchestra/skills/setup-agents/scripts/", "tests/test_setup_agents.py"), "tests.test_setup_agents"),
        (("plugins/sacha-orchestra/skills/setup-agents/assets/",), "tests.test_setup_agents"),
        (("plugins/sacha-orchestra/skills/setup-project/scripts/resolve_capability_queries.py", "tests/test_capability_resolution.py"), "tests.test_capability_resolution"),
    )
    modules: set[str] = set()
    machine_paths = [
        path
        for path in staged
        if Path(path).suffix.lower() in {".py", ".ps1", ".mjs", ".json", ".toml", ".yaml", ".yml"}
        and path not in DEPLOYMENT_MANIFESTS
        and not path.endswith("/agents/openai.yaml")
    ]
    for path in machine_paths:
        matched = False
        for prefixes, module in mappings:
            if any(path == prefix or path.startswith(prefix) for prefix in prefixes):
                modules.add(module)
                matched = True
        if not matched:
            raise ReleaseError(f"生产脚本缺少最窄测试映射：{path}")
    return sorted(modules)


def validation_commands(
    version: str,
    staged: list[str],
    root: Path = ROOT,
    deltas: dict[str, tuple[str | None, str | None]] | None = None,
) -> list[tuple[str, ...]]:
    if deltas is None:
        deltas = staged_deltas(staged)
    python = current_python()
    plugin = root / "plugins" / "sacha-orchestra"
    commands: list[tuple[str, ...]] = [
        (
            python,
            "-B",
            "tests/validate_release_coherence.py",
            "--version",
            version,
            "--phase",
            "candidate",
        ),
    ]
    commands.extend(
        (python, "-B", "-m", "unittest", module)
        for module in narrow_test_modules(staged)
    )
    if requires_plugin_validation(staged, deltas):
        commands.append(
            (python, "-B", str(creator_script("plugin-creator", "validate_plugin.py")), str(plugin))
        )
    skill_roots = changed_skill_metadata_roots(staged, deltas, plugin)
    skill_validator = creator_script("skill-creator", "quick_validate.py") if skill_roots else None
    commands.extend(
        (python, "-B", str(skill_validator), str(skill_root))
        for skill_root in skill_roots
    )
    return commands


@contextlib.contextmanager
def staged_snapshot() -> Iterator[tuple[Path, str]]:
    tree = git("write-tree").stdout.strip()
    temp_base = ROOT / ".temp"
    temp_base.mkdir(exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="release-", dir=temp_base) as temp_dir:
            temp_root = Path(temp_dir)
            archive = temp_root / "candidate.tar"
            snapshot = temp_root / "tree"
            snapshot.mkdir()
            git("archive", "--format=tar", f"--output={archive}", tree)
            with tarfile.open(archive, "r") as package:
                package.extractall(snapshot, filter="data")
            archive.unlink()
            yield snapshot, tree
    finally:
        try:
            temp_base.rmdir()
        except OSError:
            pass


def run_validation(
    command: tuple[str, ...],
    cwd: Path,
) -> dict[str, object]:
    started = time.perf_counter()
    result = run(*command, check=False, cwd=cwd)
    return {
        "command": list(command),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "duration_seconds": round(time.perf_counter() - started, 3),
    }


def prepare(version: str, expected: list[str]) -> None:
    started = time.perf_counter()
    staged = require_staged_candidate(expected)
    deltas = staged_deltas(staged)
    with staged_snapshot() as (snapshot, tree):
        commands = validation_commands(version, staged, snapshot, deltas)
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(commands)) as pool:
            futures = [pool.submit(run_validation, command, snapshot) for command in commands]
            results = [future.result() for future in futures]
    failures = [result for result in results if result["returncode"] != 0]
    if failures:
        raise ReleaseError("验证失败：\n" + json.dumps(failures, ensure_ascii=False))
    print(
        json.dumps(
            {
                "phase": "candidate",
                "version": version,
                "tree": tree,
                "files": staged,
                "validation": results,
                "duration_seconds": round(time.perf_counter() - started, 3),
                "status": "pass",
            },
            ensure_ascii=False,
        )
    )


def remote_commit(remote: str, reference: str) -> str:
    output = git("ls-remote", remote, reference).stdout.strip()
    return output.split("\t", 1)[0] if output else ""


def publish(version: str, review: str, message: str, remote: str, expected: list[str]) -> None:
    started = time.perf_counter()
    staged = require_staged_candidate(expected)
    timings: dict[str, float] = {}
    tag = f"v{version}"
    if git("tag", "--list", tag).stdout.strip():
        raise ReleaseError(f"Tag 已存在：{tag}")
    phase_started = time.perf_counter()
    with staged_snapshot() as (snapshot, tree):
        run(
            current_python(),
            "-B",
            "tests/validate_release_coherence.py",
            "--version",
            version,
            "--phase",
            "candidate",
            cwd=snapshot,
        )
    timings["candidate_validation"] = round(time.perf_counter() - phase_started, 3)
    phase_started = time.perf_counter()
    git("commit", "-m", message)
    timings["commit"] = round(time.perf_counter() - phase_started, 3)
    phase_started = time.perf_counter()
    git("tag", "-a", tag, "-m", f"Sacha Orchestra {version}")
    timings["tag"] = round(time.perf_counter() - phase_started, 3)
    phase_started = time.perf_counter()
    run(current_python(), "-B", "tests/validate_release_coherence.py", "--version", version, "--phase", "release")
    timings["release_validation"] = round(time.perf_counter() - phase_started, 3)
    branch = git("branch", "--show-current").stdout.strip()
    if not branch:
        raise ReleaseError("detached HEAD 不能发布")
    phase_started = time.perf_counter()
    git("push", "--atomic", remote, branch, tag)
    timings["push"] = round(time.perf_counter() - phase_started, 3)
    phase_started = time.perf_counter()
    head = git("rev-parse", "HEAD").stdout.strip()
    if remote_commit(remote, f"refs/heads/{branch}") != head or remote_commit(remote, f"refs/tags/{tag}^{{}}") != head:
        raise ReleaseError("远端分支或解引用 Tag 未指向 HEAD")
    timings["remote_verification"] = round(time.perf_counter() - phase_started, 3)
    print(
        json.dumps(
            {
                "phase": "release",
                "version": version,
                "review": review,
                "tree": tree,
                "files": staged,
                "commit": head,
                "timings": timings,
                "duration_seconds": round(time.perf_counter() - started, 3),
                "status": "pass",
            }
        )
    )


def tree_hashes(root: Path) -> dict[str, str]:
    import hashlib

    hashes: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        hashes[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def install(version: str) -> None:
    started = time.perf_counter()
    codex = codex_cli()
    helper = creator_script("plugin-creator", "read_marketplace_name.py")
    marketplace = run(
        current_python(),
        "-B",
        str(helper),
        "--marketplace-path",
        str(ROOT / ".agents" / "plugins" / "marketplace.json"),
    ).stdout.strip()
    try:
        result = run(codex, "plugin", "add", f"sacha-orchestra@{marketplace}", "--json")
    except ReleaseError as exc:
        if "拒绝访问" in str(exc) or "os error 5" in str(exc):
            raise ReleaseError("安装被拒绝访问；关闭本次发布中已终态的辅助 Agent 后，不修改 cache，重新运行 install") from exc
        raise
    payload = json.loads(result.stdout)
    installed_path = Path(payload.get("installedPath", ""))
    if payload.get("version") != version or not installed_path.is_dir():
        raise ReleaseError("安装版本或 path 与目标 release 不一致")
    listing = run(codex, "plugin", "list").stdout
    expected = re.compile(rf"^sacha-orchestra@{re.escape(marketplace)}\s+installed, enabled\s+{re.escape(version)}\s+", re.MULTILINE)
    if not expected.search(listing):
        raise ReleaseError("插件列表未显示目标安装版本")
    source_hashes = tree_hashes(PLUGIN)
    cache_hashes = tree_hashes(installed_path)
    if source_hashes != cache_hashes:
        raise ReleaseError("安装 cache 与插件源码不一致")
    print(
        json.dumps(
            {
                "phase": "install",
                "version": version,
                "path": str(installed_path),
                "files": len(source_hashes),
                "duration_seconds": round(time.perf_counter() - started, 3),
                "status": "pass",
            }
        )
    )


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="执行 Sacha Orchestra 已批准的机械发布步骤")
    commands = root.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--version", required=True)
    prepare_parser.add_argument("--candidate-path", action="append", required=True)
    publish_parser = commands.add_parser("publish")
    publish_parser.add_argument("--version", required=True)
    publish_parser.add_argument("--review", choices=("reused", "accepted"), required=True)
    publish_parser.add_argument("--message", required=True)
    publish_parser.add_argument("--remote", default="origin")
    publish_parser.add_argument("--candidate-path", action="append", required=True)
    install_parser = commands.add_parser("install")
    install_parser.add_argument("--version", required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            prepare(args.version, args.candidate_path)
        elif args.command == "publish":
            publish(args.version, args.review, args.message, args.remote, args.candidate_path)
        else:
            install(args.version)
    except (ReleaseError, json.JSONDecodeError) as exc:
        print(f"release_status=fail\n{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
