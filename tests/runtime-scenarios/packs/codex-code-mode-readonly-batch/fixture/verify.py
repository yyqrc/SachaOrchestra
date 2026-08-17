import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_json(name):
    with (ROOT / name).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def main():
    probe = load_json("probe.json")
    result = load_json("result.json")
    errors = []

    asset_hash = result.get("asset_sha256")
    if not isinstance(asset_hash, str) or len(asset_hash) != 64:
        errors.append("asset_sha256 must be a 64-character string")
    if result.get("retry_count") != 0:
        errors.append("retry_count must be 0")
    if result.get("agent_tool_call_count") != 0:
        errors.append("agent_tool_call_count must be 0")
    if result.get("human_prompt_count") != 0:
        errors.append("human_prompt_count must be 0")

    baseline = result.get("baseline")
    if not isinstance(baseline, dict):
        errors.append("baseline must be an object")
        baseline = {}
    if baseline.get("outer_call_count") != 2:
        errors.append("baseline outer_call_count must be 2")
    if baseline.get("goal_tool") != probe["goal_tool"]:
        errors.append("baseline goal tool mismatch")
    if baseline.get("shell_tool") != probe["shell_tool"]:
        errors.append("baseline shell tool mismatch")
    if baseline.get("cwd_exit_code") != 0:
        errors.append("baseline cwd exit code must be 0")
    if not isinstance(baseline.get("cwd_output"), str) or not baseline["cwd_output"]:
        errors.append("baseline cwd output must be a non-empty string")

    code_mode = result.get("code_mode")
    if not isinstance(code_mode, dict):
        errors.append("code_mode must be an object")
        code_mode = {}
    if code_mode.get("outer_call_count") != 1:
        errors.append("Code Mode outer_call_count must be 1")
    if code_mode.get("nested_call_count") != 2:
        errors.append("Code Mode nested_call_count must be 2")

    payload = code_mode.get("payload")
    if not isinstance(payload, dict):
        errors.append("Code Mode payload must be an object")
        payload = {}
    if payload.get("schema_version") != probe["schema_version"]:
        errors.append("schema_version mismatch")
    if payload.get("status") != "settled":
        errors.append("Code Mode status must be settled")

    entries = payload.get("results")
    if not isinstance(entries, list):
        errors.append("Code Mode results must be a list")
        entries = []
    by_id = {
        entry.get("unit_id"): entry
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("unit_id"), str)
    }
    expected_ids = {probe["goal_unit_id"], probe["cwd_unit_id"]}
    if set(by_id) != expected_ids:
        errors.append(f"Code Mode unit ids mismatch: {sorted(by_id)}")

    goal_entry = by_id.get(probe["goal_unit_id"], {})
    if goal_entry.get("status") != "fulfilled":
        errors.append("goal snapshot must be fulfilled")
    goal_value = goal_entry.get("value")
    if not isinstance(goal_value, dict) or "goal" not in goal_value:
        errors.append("goal snapshot must preserve goal field")
    elif baseline.get("goal") != goal_value.get("goal"):
        errors.append("goal snapshot differs from direct baseline")

    cwd_entry = by_id.get(probe["cwd_unit_id"], {})
    if cwd_entry.get("status") != "fulfilled":
        errors.append("cwd snapshot must be fulfilled")
    cwd_value = cwd_entry.get("value")
    if not isinstance(cwd_value, dict):
        errors.append("cwd snapshot value must be an object")
        cwd_value = {}
    if cwd_value.get("exit_code") != 0:
        errors.append("cwd snapshot exit code must be 0")
    if baseline.get("cwd_output") != cwd_value.get("output"):
        errors.append("cwd output differs from direct baseline")

    layers = result.get("evidence_layers")
    if not isinstance(layers, dict):
        errors.append("evidence_layers must be an object")
        layers = {}
    if layers.get("source_scenario") is not True:
        errors.append("source_scenario must be true")
    if layers.get("current_runtime") is not True:
        errors.append("current_runtime must be true")
    if layers.get("installed_fresh_runtime") is not False:
        errors.append("installed_fresh_runtime must remain false")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: readonly Code Mode Runtime asset result verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
