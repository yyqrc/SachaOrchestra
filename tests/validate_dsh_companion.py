"""Validate the single Sacha DSH companion package and packed artifact."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "integrations" / "dsh" / "sacha-companion"
PATCH = PACKAGE / "cordis.patch.yml"
REQUIRED_PACK_FILES = {
    "README.md",
    "assets/cats/cat-sacha-base.png",
    "assets/cats/cat-jojo-base.png",
    "cordis.patch.yml",
    "lib/index.js",
    "lib/client.js",
}


class ValidationError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ValidationError(message)


def row(patch: str, row_id: str) -> str:
    marker = f"    - id: {row_id}\n"
    start = patch.find(marker)
    if start < 0:
        raise ValidationError(f"缺少 companion row：{row_id}")
    next_row = patch.find("\n    - id: ", start + len(marker))
    return patch[start : len(patch) if next_row < 0 else next_row]


def filter_items(block: str, mode: str) -> list[str]:
    marker = f"          {mode}:\n"
    start = block.find(marker)
    if start < 0:
        raise ValidationError(f"缺少 toolFilter.{mode}")
    items: list[str] = []
    for line in block[start + len(marker) :].splitlines():
        match = re.fullmatch(r"\s{12}- ([A-Za-z0-9_-]+)", line)
        if match is not None:
            items.append(match.group(1))
            continue
        if line.strip() and len(line) - len(line.lstrip()) <= 10:
            break
    return items


def validate_companion(root: Path = PACKAGE) -> dict[str, object]:
    package_path = root / "package.json"
    patch_path = root / "cordis.patch.yml"
    policy_path = root / "src" / "tool-surface-policy.ts"
    require(package_path.is_file(), f"缺少 {package_path}")
    require(patch_path.is_file(), f"缺少 {patch_path}")
    require(policy_path.is_file(), f"缺少 {policy_path}")
    package = json.loads(package_path.read_text(encoding="utf-8"))
    patch = patch_path.read_text(encoding="utf-8")

    require(package.get("name") == "@sacha-orchestra/dsh-companion", "package name 不匹配")
    require(package.get("version") == "0.1.0", "companion version 必须为 0.1.0")
    require(package.get("dsh", {}).get("bundle", {}).get("patch") == "./cordis.patch.yml", "缺少 dsh.bundle.patch")
    require(package.get("dsh", {}).get("client", {}).get("platform") == "web", "缺少 Web client 声明")
    require(
        package.get("peerDependencies", {}).get("@deepseek-ai/dsh-tool-subagent") == "^0.1.1-rc.2",
        "dsh-tool-subagent peer version 必须匹配 0.1.1-rc.2 版本线",
    )
    require("agent-team" not in patch.lower() and "spawn_teammate" not in patch, "companion 不得重新引入 Agent Teams")

    host = row(patch, "sacha-companion")
    require("name: '@sacha-orchestra/dsh-companion'" in host, "host row 未加载 companion package")
    expected_rows = {
        "sacha-research-posix": "sacha_research",
        "sacha-research-windows": "sacha_research",
        "sacha-worker": "sacha_worker",
        "sacha-review-posix": "sacha_review",
        "sacha-review-windows": "sacha_review",
    }
    blocks: dict[str, str] = {}
    for row_id, tool_name in expected_rows.items():
        block = row(patch, row_id)
        blocks[row_id] = block
        require("name: '@deepseek-ai/dsh-tool-subagent'" in block, f"{row_id} 未使用官方 dsh-tool-subagent")
        require("provider: spawn" in block, f"{row_id} provider 不是 spawn")
        require(f"toolName: {tool_name}" in block, f"{row_id} toolName 不匹配")
        require("backgroundMode: continuable" in block, f"{row_id} 不是 continuable")
        require(re.search(r"\n\s+maxDepth:\s+1\s*(?:\n|$)", block) is not None, f"{row_id} maxDepth 不是 1")

    research_allow = ["read", "read_image", "glob", "grep", "web_search", "skill"]
    review_allow = {
        "posix": ["read", "read_image", "glob", "grep", "bash", "skill"],
        "windows": ["read", "read_image", "glob", "grep", "pwsh", "skill"],
    }
    require(filter_items(blocks["sacha-research-posix"], "allow") == research_allow, "POSIX research allow-list 不匹配")
    require(filter_items(blocks["sacha-research-windows"], "allow") == research_allow, "Windows research allow-list 不匹配")
    require(filter_items(blocks["sacha-worker"], "deny") == ["workflow", "subagent", "subagent_fork"], "worker deny-list 不匹配")
    require(filter_items(blocks["sacha-review-posix"], "allow") == review_allow["posix"], "POSIX review allow-list 不匹配")
    require(filter_items(blocks["sacha-review-windows"], "allow") == review_allow["windows"], "Windows review allow-list 不匹配")
    require("process.platform === 'win32'" in blocks["sacha-research-posix"], "POSIX research 缺少平台条件")
    require("process.platform !== 'win32'" in blocks["sacha-research-windows"], "Windows research 缺少平台条件")
    require("process.platform === 'win32'" in blocks["sacha-review-posix"], "POSIX review 缺少平台条件")
    require("process.platform !== 'win32'" in blocks["sacha-review-windows"], "Windows review 缺少平台条件")

    return {
        "status": "pass",
        "package": str(root),
        "rows": sorted(expected_rows),
        "surfaces": ["sacha_research", "sacha_worker", "sacha_review"],
        "research_allow": research_allow,
        "review_allow": review_allow,
    }


def pnpm_executable() -> str:
    candidates = ("pnpm.cmd", "pnpm.exe") if sys.platform == "win32" else ("pnpm",)
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    raise RuntimeError("未找到 pnpm")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=PACKAGE,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"命令失败（{result.returncode}）：{' '.join(args)}\n{detail}")
    return result


def packed_paths(stdout: str) -> set[str]:
    payload = json.loads(stdout)
    packages = payload if isinstance(payload, list) else [payload]
    return {
        item["path"].replace("\\", "/")
        for package in packages
        for item in package.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def main() -> int:
    payload = validate_companion()
    pnpm = pnpm_executable()
    run(pnpm, "install", "--offline", "--frozen-lockfile")
    run(pnpm, "verify")
    paths = packed_paths(run(pnpm, "pack", "--dry-run", "--json").stdout)
    missing = sorted(REQUIRED_PACK_FILES - paths)
    if missing:
        raise RuntimeError(f"pack dry-run 缺少必要文件：{missing}")
    payload["packed_files"] = len(paths)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"dsh_companion_status=fail\n{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
