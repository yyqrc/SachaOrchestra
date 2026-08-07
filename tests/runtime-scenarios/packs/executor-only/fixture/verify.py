import json
from pathlib import Path


root = Path(__file__).resolve().parent
actual = json.loads((root / "summary.json").read_text(encoding="utf-8"))
expected = {"count": 3, "sum": 16, "min": 3, "max": 8}

if actual != expected:
    raise SystemExit(f"summary mismatch: expected={expected!r}, actual={actual!r}")

print("executor_only_status=pass")
