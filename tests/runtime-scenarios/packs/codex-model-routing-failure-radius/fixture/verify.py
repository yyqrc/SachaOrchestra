from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path.cwd()


def run(*args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == expected, (
        f"unexpected exit {result.returncode}: {args}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return result


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


for required in (ROOT / "plan_sync.py", ROOT / "apply_sync.py"):
    assert required.is_file(), f"missing {required.name}"

temp_base = ROOT / ".temp"
temp_base.mkdir(exist_ok=True)

with tempfile.TemporaryDirectory(prefix="routing-", dir=temp_base) as raw_temp:
    case_root = Path(raw_temp)
    source = case_root / "source"
    target = case_root / "target"
    shutil.copytree(ROOT / "input" / "source", source)
    shutil.copytree(ROOT / "input" / "target", target)
    plan = case_root / "plan.json"

    source_before = snapshot(source)
    target_before = snapshot(target)

    run(
        "plan_sync.py",
        "--source",
        str(source),
        "--target",
        str(target),
        "--output",
        str(plan),
    )

    assert snapshot(source) == source_before, "planner modified source"
    assert snapshot(target) == target_before, "planner modified target"
    assert json.loads(plan.read_text(encoding="utf-8")) == {
        "schema_version": 1,
        "copy": ["alpha.txt", "nested/beta.txt"],
        "delete": ["obsolete.txt"],
        "same": [],
    }

    run(
        "apply_sync.py",
        "--source",
        str(source),
        "--target",
        str(target),
        "--plan",
        str(plan),
    )
    assert snapshot(target) == target_before, "default apply modified target"

    run(
        "apply_sync.py",
        "--source",
        str(source),
        "--target",
        str(target),
        "--plan",
        str(plan),
        "--apply",
    )
    assert snapshot(target) == source_before, "applied target does not match source"

    (source / "gamma.txt").write_text("gamma\n", encoding="utf-8")
    escaped_source = case_root / "escape.txt"
    escaped_source.write_text("outside-source\n", encoding="utf-8")
    malicious = case_root / "malicious.json"
    malicious.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "copy": ["gamma.txt", "z/../../escape.txt"],
                "delete": [],
                "same": [],
            }
        ),
        encoding="utf-8",
    )
    target_after_apply = snapshot(target)
    failed = subprocess.run(
        [
            sys.executable,
            "apply_sync.py",
            "--source",
            str(source),
            "--target",
            str(target),
            "--plan",
            str(malicious),
            "--apply",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert failed.returncode != 0, "malicious plan unexpectedly succeeded"
    assert snapshot(target) == target_after_apply, "failed plan partially modified target"
    assert escaped_source.read_text(encoding="utf-8") == "outside-source\n", (
        "path escaped target"
    )

print("verification passed")
