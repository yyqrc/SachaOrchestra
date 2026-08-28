"""Validate the Sacha DSH continuable-subagent bundle without DSH startup."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "integrations" / "dsh" / "sacha-subagents"
PACKAGE = BUNDLE / "package.json"
PATCH = BUNDLE / "cordis.patch.yml"


class ValidationError(RuntimeError):
    pass


def row(patch: str, row_id: str) -> str:
    marker = f"    - id: {row_id}\n"
    start = patch.find(marker)
    if start < 0:
        raise ValidationError(f"缺少 bundle row：{row_id}")
    next_row = patch.find("\n    - id: ", start + len(marker))
    return patch[start : len(patch) if next_row < 0 else next_row]


def require(value: bool, message: str) -> None:
    if not value:
        raise ValidationError(message)


def validate_bundle(root: Path = BUNDLE) -> dict[str, object]:
    package_path = root / "package.json"
    patch_path = root / "cordis.patch.yml"
    require(package_path.is_file(), f"缺少 {package_path}")
    require(patch_path.is_file(), f"缺少 {patch_path}")

    package = json.loads(package_path.read_text(encoding="utf-8"))
    patch = patch_path.read_text(encoding="utf-8")

    require(package.get("name") == "@sacha-orchestra/dsh-subagents", "package name 不匹配")
    require(package.get("version") == "0.1.0", "bundle version 必须为 0.1.0")
    require(package.get("dsh", {}).get("bundle", {}).get("patch") == "./cordis.patch.yml", "缺少 dsh.bundle.patch")
    require("agent-team" not in patch.lower() and "spawn_teammate" not in patch, "bundle 不得重新引入 Agent Teams")

    expected_rows = {
        "sacha-research-posix": "sacha_research",
        "sacha-research-windows": "sacha_research",
        "sacha-worker": "sacha_worker",
        "sacha-review": "sacha_review",
    }
    for row_id, tool_name in expected_rows.items():
        block = row(patch, row_id)
        require("name: '@deepseek-ai/dsh-tool-subagent'" in block, f"{row_id} 未使用官方 dsh-tool-subagent")
        require("provider: spawn" in block, f"{row_id} provider 不是 spawn")
        require(f"toolName: {tool_name}" in block, f"{row_id} toolName 不匹配")
        require("backgroundMode: continuable" in block, f"{row_id} 不是 continuable")
        require(re.search(r"\n\s+maxDepth:\s+1\s*(?:\n|$)", block) is not None, f"{row_id} maxDepth 不是 1")

    research_posix = row(patch, "sacha-research-posix")
    research_windows = row(patch, "sacha-research-windows")
    worker = row(patch, "sacha-worker")
    reviewer = row(patch, "sacha-review")

    for name, block in (("research-posix", research_posix), ("research-windows", research_windows)):
        for tool in ("write", "edit", "workflow", "subagent", "subagent_fork"):
            require(f"            - {tool}\n" in block, f"{name} 未 deny {tool}")
    require("            - bash\n" in research_posix, "POSIX research 未 deny bash")
    require("            - pwsh\n" in research_windows, "Windows research 未 deny pwsh")
    require("process.platform === 'win32'" in research_posix, "POSIX research 缺少平台 disable 条件")
    require("process.platform !== 'win32'" in research_windows, "Windows research 缺少平台 disable 条件")

    for name, block in (("worker", worker), ("review", reviewer)):
        for tool in ("workflow", "subagent", "subagent_fork"):
            require(f"            - {tool}\n" in block, f"{name} 未 deny {tool}")
    for tool in ("write", "edit"):
        require(f"            - {tool}\n" in reviewer, f"review 未 deny {tool}")
    require("            - bash\n" not in reviewer and "            - pwsh\n" not in reviewer, "review 不应移除 shell 验证能力")

    # Sibling Sacha tools are intentionally not named in deny-lists: DSH rejects
    # unknown filter names at composition time, so mutual references would make
    # registration order significant. maxDepth=1 is the runtime nesting guard.
    for block in (research_posix, research_windows, worker, reviewer):
        deny_region = block.split("toolFilter:", 1)[1]
        require("- sacha_research" not in deny_region, "deny-list 不应耦合 sibling sacha_research 注册顺序")
        require("- sacha_worker" not in deny_region, "deny-list 不应耦合 sibling sacha_worker 注册顺序")
        require("- sacha_review" not in deny_region, "deny-list 不应耦合 sibling sacha_review 注册顺序")

    return {
        "status": "pass",
        "bundle": str(root),
        "rows": sorted(expected_rows),
        "surfaces": ["sacha_research", "sacha_worker", "sacha_review"],
    }


def main() -> int:
    print(json.dumps(validate_bundle(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationError, json.JSONDecodeError) as exc:
        print(f"dsh_subagents_status=fail\n{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
