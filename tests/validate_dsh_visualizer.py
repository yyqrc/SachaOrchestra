"""Validate the staged DSH visualizer package without network access."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "integrations" / "dsh" / "sacha-visualizer"
REQUIRED_PACK_FILES = {
    "README.md",
    "assets/cats/cat-sacha-base.png",
    "assets/cats/cat-jojo-base.png",
    "lib/client.js",
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
    pnpm = pnpm_executable()
    run(pnpm, "install", "--offline", "--frozen-lockfile")
    run(pnpm, "verify")
    paths = packed_paths(run(pnpm, "pack", "--dry-run", "--json").stdout)
    missing = sorted(REQUIRED_PACK_FILES - paths)
    if missing:
        raise RuntimeError(f"pack dry-run 缺少必要文件：{missing}")
    print(
        json.dumps(
            {"status": "pass", "package": str(PACKAGE), "packed_files": len(paths)},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"dsh_visualizer_status=fail\n{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
