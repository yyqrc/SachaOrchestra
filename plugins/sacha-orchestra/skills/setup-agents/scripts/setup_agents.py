"""Safely plan and install Sacha-owned Codex custom Agents."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping


OWNER_MARKER = "# managed-by: sacha-orchestra/setup-agents"
TARGET_RELATIVE = Path("agents") / "sacha-luna-worker.toml"
DEFAULT_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "sacha-luna-worker.toml"
XHIGH_TARGET_RELATIVE = Path("agents") / "sacha-luna-worker-xhigh.toml"
XHIGH_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "sacha-luna-worker-xhigh.toml"
IDENTITY_FIELDS = ("name", "model", "model_reasoning_effort")
REQUIRED_FIELDS = (*IDENTITY_FIELDS, "description", "developer_instructions")


class SetupAgentsError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    target_relative: Path
    template_path: Path
    reasoning_effort: str


AGENT_DEFINITIONS = (
    AgentDefinition("sacha_luna_worker", TARGET_RELATIVE, DEFAULT_TEMPLATE, "max"),
    AgentDefinition("sacha_luna_worker_xhigh", XHIGH_TARGET_RELATIVE, XHIGH_TEMPLATE, "xhigh"),
)


@dataclass(frozen=True)
class AgentPlan:
    definition: AgentDefinition
    target: Path
    template: bytes
    current: bytes | None
    action: str
    delta: str
    planned_delta_sha256: str
    current_parse_error: str | None


@dataclass(frozen=True)
class Plan:
    codex_home: Path
    agents: tuple[AgentPlan, ...]
    planned_delta_sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def resolve_target(codex_home: Path, target_relative: Path = TARGET_RELATIVE) -> Path:
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
    missing = [field for field in REQUIRED_FIELDS if not isinstance(parsed.get(field), str)]
    if missing:
        raise SetupAgentsError("missing string fields: " + ", ".join(missing))
    mismatched = [
        key for key, value in (expected_identity or {}).items() if parsed.get(key) != value
    ]
    if mismatched:
        raise SetupAgentsError("unexpected Agent identity: " + ", ".join(mismatched))
    return parsed


def has_owner_marker(data: bytes) -> bool:
    try:
        return OWNER_MARKER in data.decode("utf-8").splitlines()
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
    expected_identity = {
        "name": definition.name,
        "model_reasoning_effort": definition.reasoning_effort,
    }
    template_semantics = validate_agent(template, expected_identity)

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
    confirmation_payload = {
        "target_path": str(target),
        "action": action,
        "current_sha256": sha256_bytes(current) if current is not None else None,
        "generated_sha256": sha256_bytes(template),
        "delta": delta,
        "current_parse_error": current_parse_error,
        "owned_update": action == "update",
    }
    return AgentPlan(
        definition,
        target,
        template,
        current,
        action,
        delta,
        sha256_bytes(
            json.dumps(
                confirmation_payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ),
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
    confirmation_payload = [
        {
            "name": agent.definition.name,
            "target_path": str(agent.target),
            "action": agent.action,
            "current_sha256": sha256_bytes(agent.current) if agent.current is not None else None,
            "generated_sha256": sha256_bytes(agent.template),
            "delta": agent.delta,
            "current_parse_error": agent.current_parse_error,
            "owned_update": agent.action == "update",
        }
        for agent in agents
    ]
    planned_hash = sha256_bytes(
        json.dumps(
            confirmation_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    return Plan(home, agents, planned_hash)


def plan_result(plan: Plan) -> dict[str, object]:
    warnings = [
        f"{agent.target}: {agent.current_parse_error}"
        for agent in plan.agents
        if agent.current_parse_error
    ]
    actions = {agent.action for agent in plan.agents}
    action = next(iter(actions)) if len(actions) == 1 else "mixed"
    return {
        "status": "planned",
        "transaction": "dry_run",
        "action": action,
        "target_paths": [str(agent.target) for agent in plan.agents],
        "planned_delta_sha256": plan.planned_delta_sha256,
        "delta": "\n".join(agent.delta for agent in plan.agents if agent.delta),
        "agents": [
            {
                "name": agent.definition.name,
                "action": agent.action,
                "target_path": str(agent.target),
                "current_sha256": sha256_bytes(agent.current) if agent.current is not None else None,
                "generated_sha256": sha256_bytes(agent.template),
                "delta": agent.delta,
                "current_parse_error": agent.current_parse_error,
            }
            for agent in plan.agents
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
        if sha256_bytes(temp_path.read_bytes()) != sha256_bytes(data):
            raise SetupAgentsError("temporary file hash mismatch")
        return temp_path
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def verify_installed(target: Path, expected: bytes) -> None:
    actual = target.read_bytes()
    expected_parsed = validate_agent(expected)
    validate_agent(actual, {key: expected_parsed[key] for key in IDENTITY_FIELDS})
    if actual != expected or sha256_bytes(actual) != sha256_bytes(expected):
        raise SetupAgentsError("installed content/hash mismatch")


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
    changed_agents = [agent for agent in plan.agents if agent.action != "no-op"]
    if not changed_agents:
        result.update(status="ok", transaction="no_changes")
        return result
    if any(agent.action == "conflict" for agent in changed_agents):
        result.update(status="refused", transaction="no_write", errors=["non-Sacha or identity-conflicting Agent file cannot be overwritten"])
        return result

    parent = plan.codex_home / "agents"
    parent_created = False
    temp_paths: dict[Path, Path] = {}
    replaced_agents: list[AgentPlan] = []
    hooks = dict(_test_hooks or {})
    try:
        for agent in plan.agents:
            if resolve_target(plan.codex_home, agent.definition.target_relative) != agent.target:
                raise SetupAgentsError(f"Agent target resolution changed before write: {agent.definition.name}")
        if not parent.exists():
            parent.mkdir()
            parent_created = True
        if hook := hooks.get("before_preimage_check"):
            hook()
        for agent in plan.agents:
            current_now = agent.target.read_bytes() if agent.target.is_file() else None
            if current_now != agent.current:
                raise SetupAgentsError(f"target changed after planning: {agent.definition.name}")
        for agent in changed_agents:
            template_parsed = validate_agent(agent.template)
            temp_paths[agent.target] = prepare_temp(
                agent.target,
                agent.template,
                expected_identity={key: template_parsed[key] for key in IDENTITY_FIELDS},
            )
        for agent in changed_agents:
            os.replace(temp_paths.pop(agent.target), agent.target)
            replaced_agents.append(agent)
            if hook := hooks.get("after_replace"):
                hook(agent.target)
        for agent in changed_agents:
            verify_installed(agent.target, agent.template)
    except Exception as exc:
        for temp_path in temp_paths.values():
            temp_path.unlink(missing_ok=True)
        if not replaced_agents:
            if parent_created:
                try:
                    parent.rmdir()
                except OSError:
                    pass
            result.update(status="refused", transaction="no_write", errors=[f"write failed: {type(exc).__name__}: {exc}"])
            return result
        try:
            for agent in reversed(replaced_agents):
                if sha256_bytes(agent.target.read_bytes()) != sha256_bytes(agent.template):
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
        installed_sha256={
            agent.definition.name: sha256_bytes(agent.target.read_bytes())
            for agent in changed_agents
        },
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
