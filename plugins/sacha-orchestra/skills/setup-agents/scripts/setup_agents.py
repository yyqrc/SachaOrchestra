"""Safely plan and install Sacha-owned Codex custom Agents."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping


OWNER_MARKER = "# managed-by: sacha-orchestra/setup-agents"
DEEPSEEK_TARGET_RELATIVE = Path("agents") / "sacha-deepseek-worker.toml"
DEEPSEEK_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "sacha-deepseek-worker.toml"
DEEPSEEK_PRO_TARGET_RELATIVE = Path("agents") / "sacha-deepseek-pro-worker.toml"
DEEPSEEK_PRO_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "sacha-deepseek-pro-worker.toml"
RESEARCHER_TARGET_RELATIVE = Path("agents") / "sacha-researcher.toml"
RESEARCHER_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "sacha-researcher.toml"
LEGACY_RESEARCHER_TARGET_RELATIVE = Path("agents") / "sacha-readonly-worker.toml"
LEGACY_RESEARCHER_NAME = "sacha_readonly_worker"
REVIEWER_TARGET_RELATIVE = Path("agents") / "sacha-reviewer.toml"
REVIEWER_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "sacha-reviewer.toml"
EXECUTER_TARGET_RELATIVE = Path("agents") / "sacha-executer.toml"
EXECUTER_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "sacha-executer.toml"
CORE_REQUIRED_FIELDS = ("name", "description", "developer_instructions")
MODEL_FIELDS = ("model", "model_reasoning_effort")


class SetupAgentsError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    target_relative: Path
    template_path: Path
    model: str | None = None
    reasoning_effort: str | None = None
    disabled_features: tuple[str, ...] = ()
    disable_automatic_skills: bool = False


AGENT_DEFINITIONS = (
    AgentDefinition(
        "sacha_researcher",
        RESEARCHER_TARGET_RELATIVE,
        RESEARCHER_TEMPLATE,
        disabled_features=("shell_tool", "apps", "memories", "request_permissions_tool"),
        disable_automatic_skills=True,
    ),
    AgentDefinition(
        "sacha_executer",
        EXECUTER_TARGET_RELATIVE,
        EXECUTER_TEMPLATE,
        disabled_features=("memories", "request_permissions_tool"),
        disable_automatic_skills=True,
    ),
    AgentDefinition(
        "sacha_reviewer",
        REVIEWER_TARGET_RELATIVE,
        REVIEWER_TEMPLATE,
        disabled_features=("memories", "request_permissions_tool"),
        disable_automatic_skills=True,
    ),
    AgentDefinition("sacha_deepseek_worker", DEEPSEEK_TARGET_RELATIVE, DEEPSEEK_TEMPLATE, "TT/deepseek-v4-flash-ioa", "max"),
    AgentDefinition("sacha_deepseek_pro_worker", DEEPSEEK_PRO_TARGET_RELATIVE, DEEPSEEK_PRO_TEMPLATE, "TT/deepseek-v4-pro-ioa", "max"),
)


@dataclass(frozen=True)
class AgentPlan:
    definition: AgentDefinition
    target: Path
    template: bytes
    current: bytes | None
    action: str
    delta: str
    current_parse_error: str | None


@dataclass(frozen=True)
class RetiredAgentPlan:
    name: str
    target: Path
    current: bytes | None
    action: str
    delta: str
    current_parse_error: str | None


@dataclass(frozen=True)
class Plan:
    codex_home: Path
    agents: tuple[AgentPlan, ...]
    retired_agents: tuple[RetiredAgentPlan, ...]


def resolve_codex_home(
    explicit: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
) -> Path:
    env = os.environ if environ is None else environ
    raw = explicit or env.get("CODEX_HOME")
    home = Path(raw).expanduser() if raw else (user_home or Path.home()) / ".codex"
    home = home.resolve(strict=False)
    if home == Path(home.anchor):
        raise SetupAgentsError("Codex home cannot be a filesystem root")
    return home


def resolve_target(codex_home: Path, target_relative: Path = EXECUTER_TARGET_RELATIVE) -> Path:
    home = codex_home.resolve(strict=False)
    target = (home / target_relative).resolve(strict=False)
    try:
        target.relative_to(home)
    except ValueError as exc:
        raise SetupAgentsError("Agent target escapes Codex home") from exc
    return target


def parse_toml(data: bytes) -> dict[str, object]:
    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise SetupAgentsError(f"TOML parse failed: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SetupAgentsError("TOML root must be a table")
    return parsed


def validate_agent(
    data: bytes,
    expected_identity: Mapping[str, object] | None = None,
) -> dict[str, object]:
    parsed = parse_toml(data)
    missing = [field for field in CORE_REQUIRED_FIELDS if not isinstance(parsed.get(field), str)]
    if missing:
        raise SetupAgentsError("missing string fields: " + ", ".join(missing))
    mismatched = [
        key for key, value in (expected_identity or {}).items() if parsed.get(key) != value
    ]
    if mismatched:
        raise SetupAgentsError("unexpected Agent identity: " + ", ".join(mismatched))
    return parsed


def expected_identity(definition: AgentDefinition) -> dict[str, object]:
    identity: dict[str, object] = {"name": definition.name}
    if definition.model is not None:
        identity["model"] = definition.model
    if definition.reasoning_effort is not None:
        identity["model_reasoning_effort"] = definition.reasoning_effort
    return identity


def validate_definition(data: bytes, definition: AgentDefinition) -> dict[str, object]:
    parsed = validate_agent(data, expected_identity(definition))
    if definition.model is None:
        fixed_model_fields = [field for field in MODEL_FIELDS if field in parsed]
        if fixed_model_fields:
            raise SetupAgentsError(
                "capability-only Agent must omit fixed model fields: "
                + ", ".join(fixed_model_fields)
            )
        if "sandbox_mode" in parsed:
            raise SetupAgentsError(
                "capability-only Agent must omit sandbox_mode"
            )
    if definition.disabled_features:
        expected_features = {feature: False for feature in definition.disabled_features}
        if parsed.get("features") != expected_features:
            raise SetupAgentsError(
                f"unexpected feature reductions for {definition.name}"
            )
    if definition.disable_automatic_skills:
        expected_skills = {
            "include_instructions": False,
            "bundled": {"enabled": False},
        }
        if parsed.get("skills") != expected_skills:
            raise SetupAgentsError(
                f"unexpected Skill reductions for {definition.name}"
            )
    return parsed


def has_owner_marker(data: bytes) -> bool:
    try:
        lines = data.decode("utf-8").splitlines()
        return bool(lines) and lines[0] == OWNER_MARKER
    except UnicodeDecodeError:
        return False


def render_delta(target: Path, current: bytes | None, generated: bytes) -> str:
    before = [] if current is None else current.decode("utf-8", errors="replace").splitlines(keepends=True)
    after = generated.decode("utf-8").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            before,
            after,
            fromfile=str(target) if current is not None else "/dev/null",
            tofile=str(target),
        )
    )


def render_removal_delta(target: Path, current: bytes) -> str:
    before = current.decode("utf-8", errors="replace").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            before,
            [],
            fromfile=str(target),
            tofile="/dev/null",
        )
    )


def build_agent_plan(
    home: Path,
    definition: AgentDefinition,
    *,
    _template_path: Path | None = None,
) -> AgentPlan:
    target = resolve_target(home, definition.target_relative)
    template_path = (_template_path or definition.template_path).resolve(strict=True)
    template = template_path.read_bytes()
    if not has_owner_marker(template):
        raise SetupAgentsError("template owner marker is missing")
    validate_definition(template, definition)

    current = target.read_bytes() if target.is_file() else None
    current_parse_error: str | None = None
    if current is None:
        action = "create"
    else:
        try:
            current_semantics = parse_toml(current)
        except SetupAgentsError as exc:
            current_semantics = None
            current_parse_error = str(exc)
        if current == template:
            action = "no-op"
        elif (
            has_owner_marker(current)
            and current_semantics is not None
            and current_semantics.get("name") == definition.name
        ):
            action = "update"
        else:
            action = "conflict"

    delta = "" if action == "no-op" else render_delta(target, current, template)
    return AgentPlan(
        definition,
        target,
        template,
        current,
        action,
        delta,
        current_parse_error,
    )


def build_retired_agent_plan(home: Path) -> RetiredAgentPlan:
    target = resolve_target(home, LEGACY_RESEARCHER_TARGET_RELATIVE)
    current = target.read_bytes() if target.is_file() else None
    current_parse_error: str | None = None
    if current is None:
        action = "no-op"
    else:
        try:
            current_semantics = parse_toml(current)
        except SetupAgentsError as exc:
            current_semantics = None
            current_parse_error = str(exc)
        if (
            has_owner_marker(current)
            and current_semantics is not None
            and current_semantics.get("name") == LEGACY_RESEARCHER_NAME
        ):
            action = "remove"
        else:
            action = "conflict"
    delta = render_removal_delta(target, current) if action == "remove" and current else ""
    return RetiredAgentPlan(
        LEGACY_RESEARCHER_NAME,
        target,
        current,
        action,
        delta,
        current_parse_error,
    )


def build_plan(
    codex_home: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
    _template_paths: Mapping[str, Path] | None = None,
) -> Plan:
    home = resolve_codex_home(codex_home, environ=environ, user_home=user_home)
    if not home.is_dir():
        raise SetupAgentsError("Codex home must already exist and be a directory")
    overrides = dict(_template_paths or {})
    agents = tuple(
        build_agent_plan(home, definition, _template_path=overrides.get(definition.name))
        for definition in AGENT_DEFINITIONS
    )
    retired_agents = (build_retired_agent_plan(home),)
    return Plan(home, agents, retired_agents)


def plan_result(plan: Plan) -> dict[str, object]:
    warnings = [
        f"{agent.target}: {agent.current_parse_error}"
        for agent in plan.agents
        if agent.current_parse_error
    ]
    warnings.extend(
        f"{agent.target}: {agent.current_parse_error}"
        for agent in plan.retired_agents
        if agent.current_parse_error
    )
    actions = {agent.action for agent in plan.agents}
    actions.update(
        agent.action for agent in plan.retired_agents if agent.action != "no-op"
    )
    action = next(iter(actions)) if len(actions) == 1 else "mixed"
    return {
        "status": "planned",
        "transaction": "dry_run",
        "action": action,
        "target_paths": [str(agent.target) for agent in plan.agents],
        "delta": "\n".join(
            agent.delta
            for agent in (*plan.agents, *plan.retired_agents)
            if agent.delta
        ),
        "agents": [
            {
                "name": agent.definition.name,
                "action": agent.action,
                "target_path": str(agent.target),
                "delta": agent.delta,
                "current_parse_error": agent.current_parse_error,
            }
            for agent in plan.agents
        ],
        "retired_agents": [
            {
                "name": agent.name,
                "action": agent.action,
                "target_path": str(agent.target),
                "delta": agent.delta,
                "current_parse_error": agent.current_parse_error,
            }
            for agent in plan.retired_agents
        ],
        "warnings": warnings,
    }


def prepare_temp(
    target: Path,
    data: bytes,
    *,
    validate: bool = True,
    expected_identity: Mapping[str, object] | None = None,
) -> Path:
    descriptor, raw_path = tempfile.mkstemp(prefix=".sacha-agent-", suffix=".tmp", dir=target.parent)
    temp_path = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if validate:
            validate_agent(temp_path.read_bytes(), expected_identity)
        if temp_path.read_bytes() != data:
            raise SetupAgentsError("temporary file content mismatch")
        return temp_path
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def verify_installed(target: Path, expected: bytes, definition: AgentDefinition) -> None:
    actual = target.read_bytes()
    validate_definition(expected, definition)
    validate_definition(actual, definition)
    if actual != expected:
        raise SetupAgentsError("installed content mismatch")


def run_setup(
    *,
    codex_home: str | Path | None = None,
    write: bool = False,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
    _template_paths: Mapping[str, Path] | None = None,
    _test_hooks: Mapping[str, Callable[..., None]] | None = None,
) -> dict[str, object]:
    try:
        plan = build_plan(
            codex_home,
            environ=environ,
            user_home=user_home,
            _template_paths=_template_paths,
        )
    except (OSError, SetupAgentsError) as exc:
        return {"status": "refused", "transaction": "no_write", "errors": [str(exc)]}

    result = plan_result(plan)
    if not write:
        return result
    conflicts = [agent for agent in plan.agents if agent.action == "conflict"]
    retired_conflicts = [
        agent for agent in plan.retired_agents if agent.action == "conflict"
    ]
    if conflicts or retired_conflicts:
        result.update(
            status="refused",
            transaction="no_write",
            errors=[
                "non-Sacha or identity-conflicting Agent file cannot be overwritten or retired"
            ],
        )
        return result
    changed_agents = [
        agent for agent in plan.agents if agent.action in {"create", "update"}
    ]
    retired_agents = [
        agent for agent in plan.retired_agents if agent.action == "remove"
    ]
    if not changed_agents and not retired_agents:
        result.update(status="ok", transaction="no_changes")
        return result

    parent = plan.codex_home / "agents"
    parent_created = False
    temp_paths: dict[Path, Path] = {}
    replaced_agents: list[AgentPlan] = []
    removed_retired_agents: list[RetiredAgentPlan] = []
    hooks = dict(_test_hooks or {})
    try:
        for agent in plan.agents:
            if resolve_target(plan.codex_home, agent.definition.target_relative) != agent.target:
                raise SetupAgentsError(f"Agent target resolution changed before write: {agent.definition.name}")
        for agent in plan.retired_agents:
            if resolve_target(plan.codex_home, LEGACY_RESEARCHER_TARGET_RELATIVE) != agent.target:
                raise SetupAgentsError(f"retired Agent target resolution changed before write: {agent.name}")
        if not parent.exists():
            parent.mkdir()
            parent_created = True
        if hook := hooks.get("before_preimage_check"):
            hook()
        for agent in plan.agents:
            current_now = agent.target.read_bytes() if agent.target.is_file() else None
            if current_now != agent.current:
                raise SetupAgentsError(f"target changed after planning: {agent.definition.name}")
        for agent in plan.retired_agents:
            current_now = agent.target.read_bytes() if agent.target.is_file() else None
            if current_now != agent.current:
                raise SetupAgentsError(f"target changed after planning: {agent.name}")
        for agent in changed_agents:
            temp_paths[agent.target] = prepare_temp(
                agent.target,
                agent.template,
                expected_identity=expected_identity(agent.definition),
            )
        for agent in changed_agents:
            os.replace(temp_paths.pop(agent.target), agent.target)
            replaced_agents.append(agent)
            if hook := hooks.get("after_replace"):
                hook(agent.target)
        for agent in changed_agents:
            verify_installed(agent.target, agent.template, agent.definition)
        for agent in retired_agents:
            current_now = agent.target.read_bytes() if agent.target.is_file() else None
            if current_now != agent.current:
                raise SetupAgentsError(f"retired Agent changed before removal: {agent.name}")
            agent.target.unlink()
            removed_retired_agents.append(agent)
            if hook := hooks.get("after_retire"):
                hook(agent.target)
            if agent.target.exists():
                raise SetupAgentsError(f"retired Agent still exists after removal: {agent.name}")
    except Exception as exc:
        for temp_path in temp_paths.values():
            temp_path.unlink(missing_ok=True)
        if not replaced_agents and not removed_retired_agents:
            if parent_created:
                try:
                    parent.rmdir()
                except OSError:
                    pass
            result.update(status="refused", transaction="no_write", errors=[f"write failed: {type(exc).__name__}: {exc}"])
            return result
        try:
            for agent in reversed(removed_retired_agents):
                if agent.target.exists() or agent.current is None:
                    raise SetupAgentsError(
                        f"retired Agent target changed before rollback: {agent.name}"
                    )
                restore_temp = prepare_temp(agent.target, agent.current, validate=False)
                try:
                    os.replace(restore_temp, agent.target)
                finally:
                    restore_temp.unlink(missing_ok=True)
                if agent.target.read_bytes() != agent.current:
                    raise SetupAgentsError(
                        f"retired Agent rollback verification failed: {agent.name}"
                    )
            for agent in reversed(replaced_agents):
                if agent.target.read_bytes() != agent.template:
                    raise SetupAgentsError(f"generated file changed before rollback: {agent.definition.name}")
                if agent.current is None:
                    agent.target.unlink()
                else:
                    restore_temp = prepare_temp(agent.target, agent.current, validate=False)
                    try:
                        os.replace(restore_temp, agent.target)
                    finally:
                        restore_temp.unlink(missing_ok=True)
                restored = agent.target.read_bytes() if agent.target.is_file() else None
                if restored != agent.current:
                    raise SetupAgentsError(f"rollback verification failed: {agent.definition.name}")
            if parent_created:
                parent.rmdir()
            result.update(status="refused", transaction="rolled_back", errors=[f"post-write verification failed: {type(exc).__name__}: {exc}"])
        except Exception as restore_exc:
            result.update(status="error", transaction="rollback_failed", errors=[str(exc), str(restore_exc)])
        return result

    result.update(
        status="ok",
        transaction="written",
        written_paths=[str(agent.target) for agent in changed_agents],
        retired_paths=[str(agent.target) for agent in retired_agents],
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run_setup(
        codex_home=args.codex_home,
        write=args.write,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] in {"planned", "ok"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
