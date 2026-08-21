"""观察聚焦测试、正式 CLI 和多字节校验路径。"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
CANDIDATE = ROOT / "candidate"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", *args],
        cwd=CANDIDATE,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )


focused = run("test_exporter.py")
cli_oversize = run("cli.py", "123456789")
checked_multibyte = run("-c", "from exporter import checked_emit; print(checked_emit('界界界'))")

print(
    json.dumps(
        {
            "focused_test": {"exit_code": focused.returncode, "stderr": focused.stderr},
            "cli_oversize": {"exit_code": cli_oversize.returncode, "stdout": cli_oversize.stdout},
            "checked_multibyte": {
                "exit_code": checked_multibyte.returncode,
                "stdout": checked_multibyte.stdout,
                "utf8_bytes": len("界界界".encode("utf-8")),
            },
        },
        ensure_ascii=False,
        sort_keys=True,
    )
)
