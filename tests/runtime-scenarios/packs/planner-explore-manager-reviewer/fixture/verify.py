import json
from pathlib import Path


root = Path(__file__).resolve().parent
expected = {
    "service-alpha.json": 30000,
    "service-beta.json": 45000,
}
errors: list[str] = []

for filename, timeout in expected.items():
    data = json.loads((root / filename).read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        errors.append(f"{filename}: schema_version must be 2")
    if data.get("request_timeout_ms") != timeout:
        errors.append(f"{filename}: request_timeout_ms must remain {timeout}")
    if "timeout_ms" in data:
        errors.append(f"{filename}: timeout_ms must be removed")

if errors:
    raise SystemExit("\n".join(errors))

print("planner_explore_manager_reviewer_status=pass")
