import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_json(name):
    with (ROOT / name).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def main():
    probe = load_json("probe.json")
    alpha = load_json("alpha.json")
    beta = load_json("beta.json")
    result = load_json("result.json")
    errors = []

    if result.get("template_version") != probe["template_version"]:
        errors.append("template_version mismatch")
    if result.get("collaboration_interface") != "v1":
        errors.append("collaboration_interface must be v1")
    if result.get("retry_count") != 0:
        errors.append("retry_count must be 0")
    if result.get("human_agent_tree_prompt_count") != 0:
        errors.append("human_agent_tree_prompt_count must be 0")

    projection_preflight = result.get("projection_preflight")
    if not isinstance(projection_preflight, dict):
        errors.append("projection_preflight must be an object")
        projection_preflight = {}
    if projection_preflight.get("status") != "rejected_before_tasks":
        errors.append("projection preflight must reject before tasks")
    if projection_preflight.get("agent_id") is not None:
        errors.append("projection preflight must not have agent_id")
    projection_error = projection_preflight.get("error")
    expected_projection_error = (
        "code_mode_projection_fields_invalid:"
        f"{probe['projection_preflight_unit_id']}:result_fields"
    )
    if projection_error != expected_projection_error:
        errors.append("projection preflight error mismatch")

    preflight = result.get("small_limit_preflight")
    if not isinstance(preflight, dict):
        errors.append("small_limit_preflight must be an object")
        preflight = {}
    if preflight.get("status") != "rejected_before_tasks":
        errors.append("small limit preflight must reject before tasks")
    if preflight.get("agent_id") is not None:
        errors.append("small limit preflight must not have agent_id")
    preflight_error = preflight.get("error")
    if not isinstance(preflight_error, str) or not preflight_error.startswith(
        "code_mode_output_limit_too_small:"
    ):
        errors.append("small limit preflight error mismatch")

    entries = result.get("batch_results")
    if not isinstance(entries, list):
        errors.append("batch_results must be a list")
        entries = []
    by_id = {
        entry.get("unit_id"): entry
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("unit_id"), str)
    }
    expected_ids = {alpha["name"], beta["name"], probe["controlled_rejection_unit_id"]}
    if set(by_id) != expected_ids:
        errors.append(f"batch_results ids mismatch: {sorted(by_id)}")

    agent_ids = []
    for source in (alpha, beta):
        unit_id = source["name"]
        entry = by_id.get(unit_id, {})
        if entry.get("spawn_status") != "started":
            errors.append(f"{unit_id} spawn_status must be started")
        if entry.get("terminal_status") != "completed":
            errors.append(f"{unit_id} terminal_status must be completed")
        if not isinstance(entry.get("agent_id"), str) or not entry["agent_id"]:
            errors.append(f"{unit_id} agent_id missing")
        else:
            agent_ids.append(entry["agent_id"])
        expected_summary = {
            "count": len(source["values"]),
            "sum": sum(source["values"]),
        }
        if entry.get("summary") != expected_summary:
            errors.append(f"{unit_id} summary mismatch")

    if len(agent_ids) != len(set(agent_ids)):
        errors.append("successful agent_ids must be unique")

    rejected = by_id.get(probe["controlled_rejection_unit_id"], {})
    if rejected.get("spawn_status") != "rejected":
        errors.append("controlled rejection must be rejected")
    if rejected.get("agent_id") is not None:
        errors.append("controlled rejection must not have agent_id")
    if not isinstance(rejected.get("error"), str) or not rejected["error"]:
        errors.append("controlled rejection error missing")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: canonical Code Mode batch result verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
