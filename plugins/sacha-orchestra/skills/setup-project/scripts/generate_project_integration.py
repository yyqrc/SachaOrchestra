#!/usr/bin/env python3
"""Deterministically render and safely write Sacha Project Integration files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping


GENERATOR_MARKER = "<!-- Generator: sacha-orchestra:setup-project -->"
SCHEMA_MARKER = "<!-- Schema Version: 3 -->"
LEGACY_IGNORED_RULE_CANDIDATES_MARKER = "Sacha ignored rule candidates"
WORKFLOW_STATE_GENERATOR = "sacha-orchestra:setup-project"
WORKFLOW_STATE_SCHEMA_VERSION = 1
AGENTS_BEGIN = "<!-- BEGIN SACHA ORCHESTRA MANAGED BLOCK -->"
AGENTS_END = "<!-- END SACHA ORCHESTRA MANAGED BLOCK -->"
PROJECT_RULES_BEGIN = "<!-- BEGIN SACHA PROJECT RULES: "
PROJECT_RULES_END = "<!-- END SACHA PROJECT RULES: "
PROJECT_RULES_HASH = "<!-- SOURCE SHA-256: "
PROJECT_RULES_HEADING = "## 领域工程纪律（按 provider 合并，Sacha 托管）"
LEGACY_PROJECT_RULES_HEADING = "## 领域工程纪律（由 provider project-rules 注入，marker 托管）"
CONVENTIONAL_SKILL_ROOTS = (".agents/skills", ".codex/skills", ".claude/skills")
CONVENTIONAL_RULE_NAMES = ("TEAM.md", "PROJECT.md", "EditorTools.md")
LOAD_POLICIES = {"always", "role-entry", "on-demand"}
CAPABILITY_LOAD_POLICIES = {"on-demand", "after-write-authorization", "review-only", "risk-matched"}
PROJECT_SKILL_KINDS = {"inspect", "change", "verify", "build", "operate", "coordinate"}
PROJECT_SKILL_ADMISSIONS = {"schedulable", "support_only", "unavailable"}
PROJECT_SKILL_SIDE_EFFECTS = {
    "read_only",
    "project_generated_state",
    "project_source_write",
    "runtime_state",
    "external_state",
}
DOCUMENTATION_POLICIES = {"disabled", "on-request", "required-at-closeout"}
DOCUMENTATION_ROOT_KINDS = {"project-relative", "external-absolute"}
DOCUMENTATION_WRITE_AUTHORIZATIONS = {"bounded-closeout", "per-write-confirmation"}
SPEC_BASE_KINDS = {"project-relative", "external-absolute"}
DEFAULT_SPEC_BASE_KIND = "project-relative"
DEFAULT_SPEC_BASE = "docs"
SPEC_DIRECTORY_PATTERN = "<YYYY-MM-DD>-<short-slug>/"
SPEC_FILE_NAME = "spec.md"
DECISIONS_FILE_NAME = "decisions.md"
PROJECT_CONTEXT_FILE_NAME = "CONTEXT.md"
SKILL_ROOT_DECISIONS = {"authority", "mirror", "independent", "ignore"}
PI_MODEL_ROUTES = {"standard", "pro", "lite"}
MAX_DISCOVERY_FILES = 256
MAX_DISCOVERY_FILE_BYTES = 256 * 1024
MAX_PROJECT_RULES_BYTES = 128 * 1024
CANONICAL_SKILL = re.compile(r"^[a-z0-9][a-z0-9-]*:[a-z0-9][a-z0-9-]*$")
MACHINE_ABSOLUTE_PATH = re.compile(
    r"(?:^|[\s`'\"(\[{=:;,])(?:[A-Za-z]:[\\/]|\\\\|//|/(?!/)|~[\\/]|file:[/]+)",
    re.IGNORECASE,
)


class SetupError(RuntimeError):
    """A safe refusal that must not write target files."""


@dataclass(frozen=True)
class SetupConfig:
    project_root: Path
    agents_path: str = "AGENTS.md"
    workflow_rule_path: str = "docs/workflow-rule.md"
    spec_base_kind: str | None = None
    spec_base: str | None = None
    human_guide: str | None = None
    documentation_policy: str | None = None
    documentation_root_kind: str | None = None
    documentation_root: str | None = None
    documentation_write_authorization: str | None = None
    rule_paths: tuple[str, ...] = ()
    skill_roots: tuple[str, ...] = ()
    scm_provider: str | None = None
    rule_bindings: tuple[str, ...] = ()
    ignored_rule_candidates: tuple[str, ...] = ()
    skill_root_bindings: tuple[str, ...] = ()
    capability_bindings: tuple[str, ...] = ()
    reconcile_capabilities: bool = False
    pi_model_bindings: tuple[str, ...] = ()
    clear_pi_model_bindings: bool = False
    unavailable_capability_skills: tuple[str, ...] = ()
    assess_project_skills: bool = False
    visible_project_skills: tuple[str, ...] = ()
    project_skill_evidence: tuple[str, ...] = ()
    manage_agents: bool = False
    expected_agents_sha256: str | None = None
    replace_unmanaged_workflow: bool = False
    expected_workflow_sha256: str | None = None
    project_rules_sources: tuple[tuple[str, bytes], ...] = ()
    remove_project_rules_skills: tuple[str, ...] = ()
    replace_legacy_project_rules: bool = False


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _file_state(path: Path) -> tuple[bool, bytes | None, str | None]:
    if not path.exists():
        return False, None, None
    if not path.is_file():
        raise SetupError("target path exists but is not a regular file")
    data = path.read_bytes()
    return True, data, sha256_bytes(data)


def _is_valid_git_marker(path: Path) -> bool:
    try:
        if path.is_dir():
            return (path / "HEAD").is_file() and (
                (path / "objects").is_dir() or (path / "commondir").is_file()
            )
        if not path.is_file() or path.stat().st_size > 4096:
            return False
        text = path.read_text(encoding="utf-8").strip()
        if not text.casefold().startswith("gitdir:"):
            return False
        git_dir = Path(text.split(":", 1)[1].strip())
        if not git_dir.is_absolute():
            git_dir = path.parent / git_dir
        git_dir = git_dir.resolve()
        return git_dir.is_dir() and (git_dir / "HEAD").is_file() and (
            (git_dir / "objects").is_dir() or (git_dir / "commondir").is_file()
        )
    except (OSError, UnicodeError):
        return False


def _discover_git_marker(root: Path) -> Path | None:
    root_marker = root / ".git"
    if _is_valid_git_marker(root_marker):
        return root_marker
    if not root_marker.exists():
        return None
    for parent in root.parents:
        candidate = parent / ".git"
        if _is_valid_git_marker(candidate):
            return candidate
    return None


def _relative_marker_source(root: Path, marker: Path) -> str:
    return Path(os.path.relpath(marker, root)).as_posix()


def _normalize_relative_path(root: Path, raw: str, label: str) -> tuple[Path, str]:
    normalized = raw.replace("\\", "/").strip()
    pure = PurePosixPath(normalized)
    if (
        not normalized
        or pure.is_absolute()
        or re.match(r"^[A-Za-z]:", normalized)
        or normalized.startswith("//")
        or any(token in normalized for token in ("\n", "\r", "`"))
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise SetupError(f"{label} must be a normalized relative path inside project root")
    candidate = (root / Path(*pure.parts)).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise SetupError(f"{label} escapes project root") from exc
    return candidate, pure.as_posix()


def _normalize_hash(value: str | None, label: str) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    if not re.fullmatch(r"[0-9A-F]{64}", normalized):
        raise SetupError(f"{label} must be a 64-character SHA-256")
    return normalized


def _contains_machine_absolute_path(value: str) -> bool:
    return MACHINE_ABSOLUTE_PATH.search(value) is not None


def _normalize_scm_provider(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().casefold()
    if normalized not in {"git", "svn", "none"}:
        raise SetupError("scm_provider must be git, svn or none")
    return normalized


def _normalize_documentation(
    root: Path,
    *,
    policy: str | None,
    root_kind: str | None,
    documentation_root: str | None,
    write_authorization: str | None,
) -> tuple[dict[str, str | None], list[dict[str, str]]]:
    if policy not in DOCUMENTATION_POLICIES:
        raise SetupError(
            "documentation_policy must be disabled, on-request or required-at-closeout"
        )
    if policy == "disabled":
        if any(value is not None for value in (root_kind, documentation_root, write_authorization)):
            raise SetupError("disabled documentation must not define a root or write authorization")
        return {
            "policy": policy,
            "root_kind": None,
            "root": None,
            "portability": "not-applicable",
            "write_authorization": None,
        }, []
    if root_kind not in DOCUMENTATION_ROOT_KINDS:
        raise SetupError(
            "enabled documentation requires root_kind project-relative or external-absolute"
        )
    if write_authorization not in DOCUMENTATION_WRITE_AUTHORIZATIONS:
        raise SetupError(
            "enabled documentation requires write authorization bounded-closeout or per-write-confirmation"
        )
    if documentation_root is None:
        raise SetupError("enabled documentation requires documentation_root")
    location, warnings = _normalize_storage_root(
        root,
        root_kind=root_kind,
        configured_root=documentation_root,
        label="documentation_root",
    )
    return {
        "policy": policy,
        **location,
        "write_authorization": write_authorization,
    }, warnings


def _path_separator(value: str) -> str:
    return "\\" if re.match(r"^(?:[A-Za-z]:\\|\\\\)", value) else "/"


def _path_parts(value: str) -> tuple[str, ...]:
    return tuple(part for part in re.split(r"[/\\]+", value) if part)


def _derive_spec_storage_root(spec_base: str) -> str:
    base = spec_base.rstrip("/\\")
    return f"{base}{_path_separator(base)}plan"


def _spec_base_from_storage_root(spec_storage_root: str) -> str:
    storage_root = spec_storage_root.rstrip("/\\")
    parts = _path_parts(storage_root)
    if not parts or parts[-1].casefold() != "plan":
        raise SetupError("normalized Spec storage root must end in plan")
    return re.sub(r"[/\\][^/\\]+$", "", storage_root)


def _project_context_path(spec_storage: Mapping[str, str]) -> str:
    storage_root = str(spec_storage["root"])
    separator = _path_separator(storage_root)
    spec_base = _spec_base_from_storage_root(storage_root)
    return f"{spec_base}{separator}{PROJECT_CONTEXT_FILE_NAME}"


def _normalize_storage_root(
    root: Path,
    *,
    root_kind: str,
    configured_root: str,
    label: str,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    warnings: list[dict[str, str]] = []
    if root_kind == "project-relative":
        _, normalized_root = _normalize_relative_path(
            root, configured_root, label
        )
        return {
            "root_kind": root_kind,
            "root": normalized_root,
            "portability": "portable",
        }, warnings

    raw_root = configured_root.strip()
    if raw_root != configured_root or any(
        token in raw_root for token in ("\n", "\r", "`")
    ):
        raise SetupError(
            f"external {label} must be single-line without surrounding whitespace"
        )
    external = Path(raw_root)
    if not external.is_absolute():
        raise SetupError(f"external {label} must be an absolute path")
    lexical_external = Path(os.path.abspath(raw_root))
    if lexical_external == Path(lexical_external.anchor):
        raise SetupError(f"external {label} must not be a filesystem or drive root")
    resolved_external = external.resolve(strict=False)
    if resolved_external == Path(resolved_external.anchor):
        raise SetupError(f"external {label} must not resolve to a filesystem or drive root")
    try:
        resolved_external.relative_to(root)
    except ValueError:
        pass
    else:
        raise SetupError(
            f"{label} inside the project must use root_kind project-relative"
        )
    try:
        if not external.is_dir():
            warnings.append({
                "kind": f"{label}_unreachable",
                "path": raw_root,
                "reason": f"external {label} is absent or not a directory",
            })
    except OSError:
        warnings.append({
            "kind": f"{label}_unreachable",
            "path": raw_root,
            "reason": f"external {label} cannot be inspected",
        })
    return {
        "root_kind": root_kind,
        "root": raw_root,
        "portability": "non-portable",
    }, warnings


def _normalize_spec_storage(
    root: Path,
    *,
    root_kind: str | None,
    spec_base: str | None,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    if root_kind not in SPEC_BASE_KINDS:
        raise SetupError(
            "spec_base_kind must be project-relative or external-absolute"
        )
    if spec_base is None:
        raise SetupError("spec_base is required")
    _, base_warnings = _normalize_storage_root(
        root,
        root_kind=root_kind,
        configured_root=spec_base,
        label="spec_base",
    )
    spec_storage_root = _derive_spec_storage_root(spec_base)
    location, storage_warnings = _normalize_storage_root(
        root,
        root_kind=root_kind,
        configured_root=spec_storage_root,
        label="spec_storage_root",
    )
    warnings = base_warnings or storage_warnings
    return {
        **location,
        "directory_pattern": SPEC_DIRECTORY_PATTERN,
        "file_name": SPEC_FILE_NAME,
    }, warnings


def _parse_rule_bindings(root: Path, values: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    parsed: dict[str, dict[str, str]] = {}
    for value in values:
        parts = value.split("::")
        if len(parts) != 3:
            raise SetupError("rule_binding must be <path>::<purpose>::<load-policy>")
        _, path = _normalize_relative_path(root, parts[0], "rule_binding path")
        purpose = parts[1].strip()
        policy = parts[2].strip().casefold()
        if (
            not purpose
            or any(token in purpose for token in ("\n", "\r", "`"))
            or _contains_machine_absolute_path(purpose)
        ):
            raise SetupError("rule_binding purpose must be single-line text without backticks or machine absolute paths")
        if policy not in LOAD_POLICIES:
            raise SetupError("rule_binding load policy must be always, role-entry or on-demand")
        if path in parsed:
            raise SetupError(f"duplicate rule binding: {path}")
        parsed[path] = {"path": path, "purpose": purpose, "load_policy": policy}
    return tuple(parsed[path] for path in sorted(parsed))


def _parse_ignored_paths(root: Path, values: tuple[str, ...], label: str) -> tuple[str, ...]:
    parsed: set[str] = set()
    for value in values:
        _, path = _normalize_relative_path(root, value, label)
        parsed.add(path)
    return tuple(sorted(parsed))


def _parse_skill_root_bindings(root: Path, values: tuple[str, ...]) -> tuple[dict[str, str | None], ...]:
    parsed: dict[str, dict[str, str | None]] = {}
    for value in values:
        parts = value.split("::")
        if len(parts) not in {2, 3}:
            raise SetupError("skill_root_binding must be <path>::<decision>[::<authority-path>]")
        _, path = _normalize_relative_path(root, parts[0], "skill_root_binding path")
        decision = parts[1].strip().casefold()
        if decision not in SKILL_ROOT_DECISIONS:
            raise SetupError("skill root decision must be authority, mirror, independent or ignore")
        authority: str | None = None
        if decision == "mirror":
            if len(parts) != 3:
                raise SetupError("mirror skill root binding requires an authority path")
            _, authority = _normalize_relative_path(root, parts[2], "mirror authority path")
            if authority == path:
                raise SetupError("mirror skill root cannot reference itself")
        elif len(parts) != 2:
            raise SetupError("only mirror skill root binding accepts an authority path")
        if path in parsed:
            raise SetupError(f"duplicate skill root binding: {path}")
        parsed[path] = {"path": path, "decision": decision, "authority": authority}
    return tuple(parsed[path] for path in sorted(parsed))


def _normalize_capability_id(value: str) -> str:
    normalized = value.strip()
    if normalized != value or normalized != normalized.casefold():
        raise SetupError("capability id must already be canonical lowercase without surrounding whitespace")
    if not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", normalized):
        raise SetupError("capability id must use lowercase letters, digits, dots or hyphens")
    return normalized


def _normalize_skill_identity(value: str) -> str:
    normalized = value.strip()
    if normalized != value or normalized != normalized.casefold() or "_" in normalized:
        raise SetupError("canonical Skill must already be lowercase, hyphenated and without surrounding whitespace")
    if not re.fullmatch(r"(?:[a-z0-9][a-z0-9-]*:)?[a-z0-9][a-z0-9-]*", normalized):
        raise SetupError("canonical Skill must be <skill> or <plugin>:<skill>")
    return normalized


def _parse_capability_bindings(values: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    parsed: dict[str, dict[str, str]] = {}
    for value in values:
        parts = value.split("::")
        if len(parts) != 3:
            raise SetupError("capability_binding must be <capability-id>::<canonical-skill>::<load-policy>")
        capability_id = _normalize_capability_id(parts[0])
        skill = _normalize_skill_identity(parts[1])
        policy = parts[2]
        if policy != policy.strip() or policy != policy.casefold():
            raise SetupError("capability load policy must already be canonical lowercase without surrounding whitespace")
        if policy not in CAPABILITY_LOAD_POLICIES:
            raise SetupError("capability load policy must be on-demand, after-write-authorization, review-only or risk-matched")
        if capability_id in parsed:
            raise SetupError(f"duplicate capability binding: {capability_id}")
        parsed[capability_id] = {"id": capability_id, "skill": skill, "load_policy": policy}
    return tuple(parsed[key] for key in sorted(parsed))


def _parse_pi_model_bindings(values: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    parsed: dict[str, dict[str, str]] = {}
    for value in values:
        parts = value.split("::")
        if len(parts) != 2:
            raise SetupError("pi_model_binding must be <route>::<provider/model>")
        route = parts[0]
        model = parts[1]
        if route != route.strip() or route != route.casefold() or route not in PI_MODEL_ROUTES:
            raise SetupError(
                "Pi model route must be standard, pro or lite"
            )
        if (
            model != model.strip()
            or not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", model)
        ):
            raise SetupError(
                "Pi model must be an exact provider/model without whitespace or control characters"
            )
        if route in parsed:
            raise SetupError(f"duplicate Pi model route: {route}")
        parsed[route] = {"route": route, "model": model}
    return tuple(parsed[key] for key in sorted(parsed))


def _normalize_unavailable_skills(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({_normalize_skill_identity(value) for value in values}))


def _normalize_project_skill_names(values: tuple[str, ...]) -> tuple[str, ...]:
    normalized: set[str] = set()
    for value in values:
        skill = _normalize_skill_identity(value)
        if ":" in skill:
            raise SetupError("visible project Skill must be an unprefixed project-level Skill")
        normalized.add(skill)
    return tuple(sorted(normalized))


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SetupError(f"{label} must be a non-empty string")
    return value.strip()


def _canonical_choice(value: object, label: str, choices: set[str]) -> str:
    normalized = _required_text(value, label)
    if normalized != value or normalized != normalized.casefold() or normalized not in choices:
        raise SetupError(f"{label} must be one of: {', '.join(sorted(choices))}")
    return normalized


def _string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list):
        raise SetupError(f"{label} must be a JSON array")
    normalized: list[str] = []
    for index, item in enumerate(value):
        text = _required_text(item, f"{label}[{index}]")
        if text in normalized:
            raise SetupError(f"{label} contains a duplicate value: {text}")
        normalized.append(text)
    return normalized


def _validate_body_evidence(
    text: str,
    relative: str,
    raw_ranges: object,
) -> list[str]:
    ranges = _string_list(raw_ranges, "project Skill unit evidence")
    if not ranges:
        raise SetupError("project Skill unit evidence must cite at least one body line")
    frontmatter = re.match(r"\A---\s*\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if frontmatter is None:
        raise SetupError(f"Skill frontmatter is missing: {relative}")
    frontmatter_end_line = len(frontmatter.group(0).splitlines())
    lines = text.splitlines()
    for raw_range in ranges:
        match = re.fullmatch(r"([1-9][0-9]*)(?:-([1-9][0-9]*))?", raw_range)
        if match is None:
            raise SetupError("project Skill unit evidence must use <line> or <start>-<end>")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start > end or end > len(lines):
            raise SetupError(f"project Skill unit evidence is outside {relative}: {raw_range}")
        if start <= frontmatter_end_line:
            raise SetupError("project Skill capability evidence must cite the Skill body, not frontmatter")
        if not any(lines[index - 1].strip() for index in range(start, end + 1)):
            raise SetupError("project Skill unit evidence cannot cite only blank body lines")
    return ranges


def _assess_project_skills(
    root: Path,
    discovery: Mapping[str, object],
    evidence_values: tuple[str, ...],
    visible_skill_values: tuple[str, ...],
    *,
    require_complete: bool,
) -> dict[str, object]:
    root_decisions = {
        str(item["path"]): str(item["decision"])
        for item in discovery["skill_root_bindings"]
    }
    selected = [
        dict(item)
        for item in discovery["skills"]
        if root_decisions.get(str(item["root"])) in {"authority", "independent"}
    ]
    selected_by_path = {str(item["path"]): item for item in selected}
    selected_by_name: dict[str, list[str]] = {}
    for item in selected:
        selected_by_name.setdefault(str(item["normalized_name"]), []).append(str(item["path"]))

    conflicts: list[str] = []
    for name, paths in sorted(selected_by_name.items()):
        if len(paths) > 1:
            conflicts.append(
                f"project Skill identity is ambiguous across schedulable roots: "
                f"{name} ({', '.join(sorted(paths))})"
            )

    try:
        visible_skills = set(_normalize_project_skill_names(visible_skill_values))
    except SetupError as exc:
        conflicts.append(str(exc))
        visible_skills = set()

    assessments: list[dict[str, object]] = []
    candidates: list[dict[str, object]] = []
    bindings: list[dict[str, str]] = []
    policy_decisions: list[dict[str, str]] = []
    assessed_paths: set[str] = set()
    capability_ids: set[str] = set()
    evidence_paths: set[str] = set()

    for evidence_index, raw_evidence in enumerate(evidence_values):
        local_candidates: list[dict[str, object]] = []
        local_bindings: list[dict[str, str]] = []
        local_policies: list[dict[str, str]] = []
        local_ids: set[str] = set()
        try:
            parsed = json.loads(raw_evidence)
            if not isinstance(parsed, dict):
                raise SetupError("project Skill evidence must be a JSON object")
            evidence_fields = {"skill", "skill_path", "skill_sha256", "units"}
            if set(parsed) != evidence_fields:
                raise SetupError(
                    f"project Skill evidence fields must be exactly: "
                    f"{', '.join(sorted(evidence_fields))}"
                )
            skill = _normalize_skill_identity(
                _required_text(parsed.get("skill"), "project Skill evidence skill")
            )
            if ":" in skill:
                raise SetupError("project Skill evidence skill must be unprefixed")
            skill_path, skill_relative = _normalize_relative_path(
                root,
                _required_text(parsed.get("skill_path"), "project Skill evidence skill_path"),
                "project Skill evidence skill_path",
            )
            if skill_relative in evidence_paths:
                raise SetupError(f"duplicate project Skill evidence: {skill_relative}")
            discovered = selected_by_path.get(skill_relative)
            if discovered is None:
                raise SetupError(
                    "project Skill evidence must target a discovered authority or independent Skill"
                )
            if skill != str(discovered["normalized_name"]):
                raise SetupError("project Skill evidence identity does not match discovered Skill body")
            expected_hash = _normalize_hash(
                _required_text(parsed.get("skill_sha256"), "project Skill evidence skill_sha256"),
                "project Skill evidence skill_sha256",
            )
            text, current_hash = _read_discovery_text(skill_path, skill_relative)
            if expected_hash != current_hash or current_hash != discovered["sha256"]:
                raise SetupError(f"project Skill evidence SHA-256 is stale: {skill_relative}")
            parsed_name, _ = _parse_skill_identity(text, skill_relative)
            if parsed_name.casefold() != skill:
                raise SetupError("project Skill evidence identity changed after discovery")

            units = parsed.get("units")
            if not isinstance(units, list) or not units:
                raise SetupError("project Skill evidence units must be a non-empty JSON array")
            normalized_units: list[dict[str, object]] = []
            for unit_index, raw_unit in enumerate(units):
                if not isinstance(raw_unit, dict):
                    raise SetupError(
                        f"project Skill evidence units[{unit_index}] must be a JSON object"
                    )
                unit_fields = {
                    "goal",
                    "kind",
                    "admission",
                    "side_effect",
                    "evidence",
                    "required_paths",
                    "runtime_prerequisites",
                    "reason",
                    "id",
                    "load_policy",
                }
                unknown_unit_fields = set(raw_unit) - unit_fields
                if unknown_unit_fields:
                    raise SetupError(
                        f"project Skill evidence units[{unit_index}] has unknown fields: "
                        f"{', '.join(sorted(unknown_unit_fields))}"
                    )
                goal = _required_text(
                    raw_unit.get("goal"),
                    f"project Skill evidence units[{unit_index}].goal",
                )
                kind = _canonical_choice(
                    raw_unit.get("kind"),
                    f"project Skill evidence units[{unit_index}].kind",
                    PROJECT_SKILL_KINDS,
                )
                admission = _canonical_choice(
                    raw_unit.get("admission"),
                    f"project Skill evidence units[{unit_index}].admission",
                    PROJECT_SKILL_ADMISSIONS,
                )
                side_effect = _canonical_choice(
                    raw_unit.get("side_effect"),
                    f"project Skill evidence units[{unit_index}].side_effect",
                    PROJECT_SKILL_SIDE_EFFECTS,
                )
                body_evidence = _validate_body_evidence(
                    text,
                    skill_relative,
                    raw_unit.get("evidence"),
                )
                required_paths = _string_list(
                    raw_unit.get("required_paths", []),
                    f"project Skill evidence units[{unit_index}].required_paths",
                )
                normalized_required_paths: list[str] = []
                missing_required_paths: list[str] = []
                for raw_path in required_paths:
                    required_path, required_relative = _normalize_relative_path(
                        root,
                        raw_path,
                        "project Skill required_path",
                    )
                    normalized_required_paths.append(required_relative)
                    if not required_path.exists():
                        missing_required_paths.append(required_relative)
                if admission == "schedulable" and missing_required_paths:
                    raise SetupError(
                        "schedulable project Skill required path is missing: "
                        + ", ".join(missing_required_paths)
                    )
                runtime_prerequisites = _string_list(
                    raw_unit.get("runtime_prerequisites", []),
                    f"project Skill evidence units[{unit_index}].runtime_prerequisites",
                )
                reason = _required_text(
                    raw_unit.get("reason"),
                    f"project Skill evidence units[{unit_index}].reason",
                )
                normalized_unit: dict[str, object] = {
                    "goal": goal,
                    "kind": kind,
                    "admission": admission,
                    "side_effect": side_effect,
                    "evidence": body_evidence,
                    "required_paths": normalized_required_paths,
                    "runtime_prerequisites": runtime_prerequisites,
                    "reason": reason,
                }
                if missing_required_paths:
                    normalized_unit["missing_required_paths"] = missing_required_paths
                if admission == "schedulable":
                    capability_id = _normalize_capability_id(
                        _required_text(
                            raw_unit.get("id"),
                            f"project Skill evidence units[{unit_index}].id",
                        )
                    )
                    if capability_id in capability_ids or capability_id in local_ids:
                        raise SetupError(
                            f"duplicate project capability id in body evidence: {capability_id}"
                        )
                    local_ids.add(capability_id)
                    normalized_unit["id"] = capability_id
                    if skill not in visible_skills:
                        raise SetupError(
                            f"project Skill is not visible in the current Runtime: {skill}"
                        )
                    raw_policy = raw_unit.get("load_policy")
                    if raw_policy is None:
                        local_policies.append({
                            "id": capability_id,
                            "skill": skill,
                            "side_effect": side_effect,
                        })
                    else:
                        policy = _canonical_choice(
                            raw_policy,
                            f"project Skill evidence units[{unit_index}].load_policy",
                            CAPABILITY_LOAD_POLICIES,
                        )
                        normalized_unit["load_policy"] = policy
                        local_bindings.append({
                            "id": capability_id,
                            "skill": skill,
                            "load_policy": policy,
                        })
                    local_candidates.append({
                        "id": capability_id,
                        "skill": skill,
                        "goal": goal,
                        "kind": kind,
                        "side_effect": side_effect,
                        "evidence": body_evidence,
                        "required_paths": normalized_required_paths,
                        "runtime_prerequisites": runtime_prerequisites,
                        "reason": reason,
                        **(
                            {"load_policy": normalized_unit["load_policy"]}
                            if "load_policy" in normalized_unit
                            else {}
                        ),
                    })
                elif "id" in raw_unit or "load_policy" in raw_unit:
                    raise SetupError(
                        "support_only or unavailable project Skill units cannot declare "
                        "a capability id or load_policy"
                    )
                normalized_units.append(normalized_unit)

            evidence_paths.add(skill_relative)
            assessed_paths.add(skill_relative)
            capability_ids.update(local_ids)
            assessments.append({
                "skill": skill,
                "skill_path": skill_relative,
                "skill_sha256": current_hash,
                "units": normalized_units,
            })
            candidates.extend(local_candidates)
            bindings.extend(local_bindings)
            policy_decisions.extend(local_policies)
        except (KeyError, TypeError, ValueError, SetupError) as exc:
            conflicts.append(f"project Skill evidence item {evidence_index}: {exc}")

    unassessed = (
        sorted(set(selected_by_path) - assessed_paths)
        if require_complete or evidence_values
        else []
    )
    return {
        "assessments": sorted(assessments, key=lambda item: str(item["skill_path"])),
        "candidates": sorted(candidates, key=lambda item: str(item["id"])),
        "bindings": tuple(sorted(bindings, key=lambda item: item["id"])),
        "policy_decisions_required": sorted(policy_decisions, key=lambda item: item["id"]),
        "unassessed": unassessed,
        "conflicts": conflicts,
    }


def _read_discovery_text(path: Path, relative: str) -> tuple[str, str]:
    if not path.is_file():
        raise SetupError(f"discovery path is not a regular file: {relative}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SetupError(f"cannot read discovery file {relative}: {type(exc).__name__}") from exc
    if len(data) > MAX_DISCOVERY_FILE_BYTES:
        raise SetupError(f"discovery file exceeds {MAX_DISCOVERY_FILE_BYTES} bytes: {relative}")
    try:
        return data.decode("utf-8-sig"), sha256_bytes(data)
    except UnicodeDecodeError as exc:
        raise SetupError(f"discovery file is not UTF-8: {relative}") from exc


def _relative_existing_path(root: Path, path: Path) -> tuple[Path, str]:
    resolved = path.resolve(strict=False)
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise SetupError("discovery path escapes project root") from exc
    return resolved, relative


def _extract_relative_paths(text: str) -> tuple[str, ...]:
    paths: set[str] = set()
    tokens = re.findall(r"`([^`\r\n]+)`", text)
    tokens.extend(re.findall(r"\[[^\]]+\]\(([^)\s#]+)", text))
    tokens.extend(re.findall(r"\*\*([^*\r\n]+)\*\*", text))
    for raw in tokens:
        normalized = raw.strip().strip("<>").split("#", 1)[0].replace("\\", "/")
        if (
            not normalized
            or "://" in normalized
            or normalized.startswith("#")
            or "<" in normalized
            or ">" in normalized
            or "*" in normalized
        ):
            continue
        paths.add(normalized.rstrip("/"))
    return tuple(sorted(paths))


def _parse_skill_identity(text: str, relative: str) -> tuple[str, str]:
    frontmatter = re.match(r"\A---\s*\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if frontmatter is None:
        raise SetupError(f"Skill frontmatter is missing: {relative}")
    name_match = re.search(
        r"(?m)^name[ \t]*:[ \t]*([^#\r\n]+?)[ \t]*\r?$", frontmatter.group(1)
    )
    if name_match is None:
        raise SetupError(f"Skill name is missing: {relative}")
    name = name_match.group(1).strip().strip("\"'")
    if not name:
        raise SetupError(f"Skill name is empty: {relative}")
    description_match = re.search(
        r"(?m)^description[ \t]*:[ \t]*([^#\r\n]+?)[ \t]*\r?$", frontmatter.group(1)
    )
    description = "" if description_match is None else description_match.group(1).strip().strip("\"'")
    return name, description


def _parse_workflow_state(data: bytes) -> tuple[str, ...]:
    try:
        value = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SetupError("managed workflow state is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise SetupError("managed workflow state must be a JSON object")
    if value.get("generator") != WORKFLOW_STATE_GENERATOR:
        raise SetupError("workflow state generator is missing or unknown")
    if value.get("schemaVersion") != WORKFLOW_STATE_SCHEMA_VERSION:
        raise SetupError("workflow state schema version is unsupported")
    ignored = value.get("ignoredRuleCandidates")
    if not isinstance(ignored, list) or not all(isinstance(item, str) for item in ignored):
        raise SetupError("workflow state ignoredRuleCandidates must be a string list")
    return tuple(ignored)


def _parse_existing_project_values(
    data: bytes,
    workflow_state: bytes | None = None,
) -> dict[str, object]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return {}
    if GENERATOR_MARKER not in text:
        return {}
    if SCHEMA_MARKER not in text:
        raise SetupError("managed workflow rule must use Schema Version 3")

    schema_match = re.search(r"<!-- Schema Version: ([0-9]+) -->", text)
    schema_version = None if schema_match is None else int(schema_match.group(1))

    def backtick_value(label: str) -> str | None:
        match = re.search(rf"(?m)^- {re.escape(label)}：`([^`]+)`", text)
        return None if match is None else match.group(1)

    scm_match = re.search(r"(?m)^- provider = `([^`]+)`\r?$", text)
    scm_provider = None
    if scm_match and scm_match.group(1) in {"git", "svn", "none"}:
        scm_provider = scm_match.group(1)
    if scm_provider is None:
        scm_line = re.search(r"(?m)^- SCM：(.+?)\r?$", text)
        if scm_line:
            scm_sources = re.findall(r"`([^`]+)`", scm_line.group(1))
            if any(PurePosixPath(source.replace("\\", "/")).name == ".git" for source in scm_sources):
                scm_provider = "git"
            elif any(PurePosixPath(source.replace("\\", "/")).name == ".svn" for source in scm_sources):
                scm_provider = "svn"
            elif scm_line.group(1).strip() == "未配置":
                scm_provider = "none"

    rule_bindings = []
    rule_section = re.search(r"(?ms)^### Rule bindings\s*\n(.*?)(?=^### )", text)
    if rule_section:
        for path, purpose, policy in re.findall(
            r"(?m)^- `([^`]+)`：purpose = (.*?)；load policy = `([^`]+)`\r?$",
            rule_section.group(1),
        ):
            rule_bindings.append({"path": path, "purpose": purpose, "load_policy": policy})
        if not rule_bindings:
            for policy, entries in re.findall(
                r"(?m)^- `([^`]+)`：(.+?)\r?$",
                rule_section.group(1),
            ):
                for path, purpose in re.findall(r"`([^`]+)` = ([^；\r\n]+)", entries):
                    rule_bindings.append({
                        "path": path,
                        "purpose": purpose,
                        "load_policy": policy,
                    })
    ignored_rule_candidates = []
    ignored_rule_metadata = re.search(
        rf"(?m)^<!-- {re.escape(LEGACY_IGNORED_RULE_CANDIDATES_MARKER)}: (.+) -->\r?$",
        text,
    )
    if ignored_rule_metadata:
        try:
            parsed_ignored_rules = json.loads(ignored_rule_metadata.group(1))
        except json.JSONDecodeError as exc:
            raise SetupError("managed ignored rule candidate metadata is malformed") from exc
        if not isinstance(parsed_ignored_rules, list) or not all(
            isinstance(item, str) for item in parsed_ignored_rules
        ):
            raise SetupError("managed ignored rule candidate metadata must be a string list")
        ignored_rule_candidates = parsed_ignored_rules
    else:
        ignored_rule_section = re.search(r"(?ms)^### Ignored rule candidates\s*\n(.*?)(?=^### )", text)
        if ignored_rule_section:
            ignored_rule_candidates = re.findall(r"(?m)^- `([^`]+)`\r?$", ignored_rule_section.group(1))
        ignored_rule_line = re.search(
            r"(?m)^- Setup (?:refresh exclusions|忽略)：(.+?)\r?$",
            text,
        )
        if ignored_rule_line and not ignored_rule_candidates:
            ignored_rule_candidates = re.findall(r"`([^`]+)`", ignored_rule_line.group(1))
    if workflow_state is not None:
        ignored_rule_candidates = list(_parse_workflow_state(workflow_state))

    skill_root_bindings = []
    skill_section = re.search(r"(?ms)^### Skill roots\s*\n(.*?)(?=^### )", text)
    if skill_section:
        for path, decision, authority in re.findall(
            r"(?m)^- `([^`]+)`：`([^`]+)`(?:；authority = `([^`]+)`)?\r?$",
            skill_section.group(1),
        ):
            skill_root_bindings.append({
                "path": path,
                "decision": decision,
                "authority": authority or None,
            })

    capability_bindings = []
    capability_dirty = []
    capability_section = re.search(r"(?ms)^### Capability bindings\s*\n(.*?)(?=^### )", text)
    if capability_section:
        for line in capability_section.group(1).splitlines():
            stripped = line.strip()
            if not stripped or stripped == "- 无":
                continue
            grouped = re.fullmatch(r"- `([^`]+)`：(.+)", stripped)
            if grouped:
                pairs = re.findall(r"`([^`]+)` -> `([^`]+)`", grouped.group(2))
                if pairs:
                    capability_bindings.extend({
                        "id": capability_id,
                        "skill": skill,
                        "load_policy": grouped.group(1),
                    } for capability_id, skill in pairs)
                    continue
            match = re.fullmatch(
                r"- `([^`]+)` -> `([^`]+)`；load policy = `([^`]+)`"
                r"(?:；fallback = `discoverable-domain-skill-or-native-role`)?",
                stripped,
            )
            if match is None:
                capability_dirty.append(stripped)
                continue
            capability_bindings.append({
                "id": match.group(1),
                "skill": match.group(2),
                "load_policy": match.group(3),
            })
    pi_model_bindings = []
    pi_model_section = re.search(
        r"(?ms)^### Pi one-shot model routing\s*\n(.*?)(?=^### |^## |\Z)",
        text,
    )
    if pi_model_section:
        for line in pi_model_section.group(1).splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("仅供本项目 Runtime 使用；"):
                continue
            match = re.fullmatch(r"- `([^`]+)` -> `([^`]+)`", stripped)
            if match is None:
                raise SetupError("managed Pi model routing is malformed")
            route, model = match.groups()
            pi_model_bindings.append({"route": route, "model": model})
    documentation: dict[str, str | None] = {}
    documentation_section = re.search(
        r"(?ms)^### Project documentation\s*\n(.*?)(?=^### |^## |\Z)",
        text,
    )
    if documentation_section:
        for key, value in re.findall(
            r"(?m)^- (policy|root kind|root|portability|write authorization) = `([^`]+)`\r?$",
            documentation_section.group(1),
        ):
            documentation[key.replace(" ", "_")] = None if value == "none" else value
    compact_documentation = re.search(
        r"(?m)^- 项目文档：`([^`]+)`"
        r"(?: -> `([^`]+)`；write = `([^`]+)`)?\r?$",
        text,
    )
    if compact_documentation:
        policy, root, authorization = compact_documentation.groups()
        documentation = {
            "policy": policy,
            "root_kind": (
                "external-absolute"
                if root and _contains_machine_absolute_path(root)
                else "project-relative" if root else None
            ),
            "root": root,
            "portability": (
                "non-portable"
                if root and _contains_machine_absolute_path(root)
                else "portable" if root else "not-applicable"
            ),
            "write_authorization": authorization,
        }
    spec_storage: dict[str, str | None] = {}
    compact_spec = re.search(r"(?m)^- Spec：`([^`]+)`\r?$", text)
    if compact_spec:
        root = compact_spec.group(1)
        external = _contains_machine_absolute_path(root)
        spec_storage = {
            "root_kind": "external-absolute" if external else "project-relative",
            "root": root,
            "portability": "non-portable" if external else "portable",
            "directory_pattern": SPEC_DIRECTORY_PATTERN,
            "file_name": SPEC_FILE_NAME,
        }
    return {
        "schema_version": schema_version,
        "agents_path": backtick_value("Project AGENTS"),
        "human_guide": backtick_value("Human Guide"),
        "scm_provider": scm_provider,
        "rule_bindings": tuple(rule_bindings),
        "ignored_rule_candidates": tuple(ignored_rule_candidates),
        "skill_root_bindings": tuple(skill_root_bindings),
        "capability_bindings": tuple(capability_bindings),
        "capability_dirty": tuple(capability_dirty),
        "pi_model_bindings": tuple(pi_model_bindings),
        "documentation": documentation,
        "spec_storage": spec_storage,
    }


def _discover_project_integration(
    root: Path,
    *,
    agents_path: Path,
    agents_rel: str,
    workflow_path: Path,
    workflow_rel: str,
    configured_rule_paths: tuple[str, ...],
    configured_skill_roots: tuple[str, ...],
    human_guide: str | None,
    scm_provider: str | None,
    configured_rule_bindings: tuple[dict[str, str], ...],
    ignored_rule_candidates: tuple[str, ...],
    configured_skill_root_bindings: tuple[dict[str, str | None], ...],
) -> dict[str, object]:
    rule_paths: dict[str, dict[str, object]] = {}
    skill_roots: dict[str, dict[str, object]] = {}
    unresolved: list[dict[str, str]] = []
    conflicts: list[dict[str, object]] = []
    files_seen = 0

    def add_rule(path: Path, *, required: bool, source: str, depth: int) -> None:
        try:
            resolved, relative = _relative_existing_path(root, path)
        except SetupError as exc:
            unresolved.append({"path": "<invalid>", "reason": str(exc)})
            return
        if resolved.is_file():
            entry = rule_paths.setdefault(relative, {"path": resolved, "sources": set(), "depth": depth})
            entry["sources"].add(source)
            entry["depth"] = min(int(entry["depth"]), depth)
        elif resolved.exists():
            unresolved.append({"kind": "rule", "path": relative, "reason": "rule_candidate_not_file"})
        elif required:
            unresolved.append({"kind": "rule", "path": relative, "reason": "configured_rule_missing"})

    def add_skill_root(path: Path, *, required: bool, source: str) -> None:
        try:
            resolved, relative = _relative_existing_path(root, path)
        except SetupError as exc:
            unresolved.append({"path": "<invalid>", "reason": str(exc)})
            return
        if resolved.is_dir():
            entry = skill_roots.setdefault(relative, {"path": resolved, "sources": set()})
            entry["sources"].add(source)
        elif resolved.exists() or required:
            unresolved.append({"kind": "skill_root", "path": relative, "reason": "configured_skill_root_missing_or_not_directory"})

    add_rule(agents_path, required=False, source="configured_project_agents", depth=0)
    add_rule(workflow_path, required=False, source="configured_workflow_rule", depth=0)
    if human_guide:
        human_path, _ = _normalize_relative_path(root, human_guide, "human_guide")
        add_rule(human_path, required=False, source="configured_human_guide", depth=1)
    for name in CONVENTIONAL_RULE_NAMES:
        add_rule(root / name, required=False, source="conventional_rule_name", depth=1)
    for raw in configured_rule_paths:
        try:
            path, _ = _normalize_relative_path(root, raw, "rule_path")
            add_rule(path, required=True, source="explicit_rule_path", depth=1)
        except SetupError as exc:
            unresolved.append({"path": "<invalid>", "reason": str(exc)})
    for raw in configured_skill_roots:
        try:
            path, _ = _normalize_relative_path(root, raw, "skill_root")
            add_skill_root(path, required=True, source="explicit_skill_root")
        except SetupError as exc:
            unresolved.append({"path": "<invalid>", "reason": str(exc)})
    for raw in CONVENTIONAL_SKILL_ROOTS:
        path, _ = _normalize_relative_path(root, raw, "skill_root")
        add_skill_root(path, required=False, source="conventional_skill_root")

    agents_text = ""
    if agents_path.is_file():
        try:
            agents_text, _ = _read_discovery_text(agents_path, agents_rel)
        except SetupError as exc:
            unresolved.append({"path": agents_rel, "reason": str(exc)})
    for raw in _extract_relative_paths(agents_text):
        try:
            referenced, referenced_rel = _normalize_relative_path(root, raw, "Project AGENTS path")
        except SetupError:
            continue
        if referenced_rel.endswith(".md") and referenced.exists():
            add_rule(referenced, required=False, source="project_agents_path", depth=1)
        if referenced.is_dir() and "skills" in PurePosixPath(referenced_rel).parts:
            add_skill_root(referenced, required=False, source="project_agents_path")
        elif referenced_rel.endswith("/SKILL.md") and referenced.is_file():
            add_skill_root(referenced.parent.parent, required=False, source="project_agents_path")

    first_hop_rules = [
        (entry["path"], relative)
        for relative, entry in sorted(rule_paths.items())
        if int(entry["depth"]) == 1 and relative != human_guide
    ]
    for first_path, first_rel in first_hop_rules:
        try:
            first_text, _ = _read_discovery_text(first_path, first_rel)
        except SetupError as exc:
            unresolved.append({"kind": "rule", "path": first_rel, "reason": str(exc)})
            continue
        for raw in _extract_relative_paths(first_text):
            candidates = [first_path.parent / raw, root / raw]
            referenced = next((item for item in candidates if item.exists()), candidates[0])
            try:
                resolved, referenced_rel = _relative_existing_path(root, referenced)
            except SetupError:
                continue
            if referenced_rel == human_guide:
                add_rule(resolved, required=False, source="human_guide_path", depth=2)
            elif referenced_rel.endswith(".md") and resolved.is_file():
                add_rule(resolved, required=False, source=f"second_hop:{first_rel}", depth=2)
            if resolved.is_dir() and "skills" in PurePosixPath(referenced_rel).parts:
                add_skill_root(resolved, required=False, source=f"first_hop:{first_rel}")

    scanned_rules: list[dict[str, str]] = []
    rule_candidates: list[dict[str, object]] = []
    scanned_skills: list[dict[str, str]] = []
    if len(rule_paths) > MAX_DISCOVERY_FILES:
        unresolved.append({
            "kind": "budget",
            "path": agents_rel,
            "reason": f"discovery exceeds {MAX_DISCOVERY_FILES} rule files",
        })
    for relative, entry in sorted(rule_paths.items())[:MAX_DISCOVERY_FILES]:
        path = entry["path"]
        if relative == human_guide:
            rule_candidates.append({
                "path": relative,
                "sources": sorted(entry["sources"]),
                "suggested_purpose": "human guide path",
                "suggested_load_policy": "on-demand",
                "human_guide": True,
                "generated_target": False,
                "sha256": None,
            })
            continue
        try:
            text, digest = _read_discovery_text(path, relative)
            files_seen += 1
            scanned_rules.append({"path": relative, "sha256": digest})
            if relative == agents_rel:
                purpose, policy = "project instructions", "always"
            else:
                purpose, policy = "project rule", "on-demand"
            rule_candidates.append({
                "path": relative,
                "sources": sorted(entry["sources"]),
                "suggested_purpose": purpose,
                "suggested_load_policy": policy,
                "human_guide": relative == human_guide,
                "generated_target": relative == workflow_rel and GENERATOR_MARKER in text,
                "sha256": digest,
            })
        except SetupError as exc:
            unresolved.append({"kind": "rule", "path": relative, "reason": str(exc)})
    for root_rel, root_entry in sorted(skill_roots.items()):
        skill_root = root_entry["path"]
        try:
            child_dirs = sorted(path for path in skill_root.iterdir() if path.is_dir())
        except OSError as exc:
            unresolved.append({"kind": "skill_root", "path": root_rel, "reason": f"skill_root_scan_failed:{type(exc).__name__}"})
            continue
        for child in child_dirs:
            skill_path = child / "SKILL.md"
            if not skill_path.exists():
                continue
            try:
                resolved, relative = _relative_existing_path(root, skill_path)
                files_seen += 1
                if files_seen > MAX_DISCOVERY_FILES:
                    raise SetupError(f"discovery exceeds {MAX_DISCOVERY_FILES} Skill files")
                text, digest = _read_discovery_text(resolved, relative)
                name, _ = _parse_skill_identity(text, relative)
                scanned_skills.append({"root": root_rel, "path": relative, "name": name, "normalized_name": name.casefold(), "sha256": digest})
            except SetupError as exc:
                unresolved.append({"kind": "skill", "path": skill_path.relative_to(root).as_posix(), "reason": str(exc)})
            except OSError as exc:
                unresolved.append({"kind": "skill", "path": skill_path.relative_to(root).as_posix(), "reason": f"skill_scan_failed:{type(exc).__name__}"})

    scm_evidence = []
    git_marker = _discover_git_marker(root)
    if git_marker is not None:
        scm_evidence.append({"provider": "git", "source": _relative_marker_source(root, git_marker)})
    svn_marker = root / ".svn"
    if svn_marker.is_dir():
        scm_evidence.append({"provider": "svn", "source": ".svn"})
    evidence_providers = {item["provider"] for item in scm_evidence}
    selected_provider = scm_provider
    if selected_provider is None and len(evidence_providers) == 1:
        selected_provider = next(iter(evidence_providers))
    if len(evidence_providers) > 1 and selected_provider not in evidence_providers:
        conflicts.append({"kind": "scm", "reason": "multiple_root_providers", "providers": sorted(evidence_providers)})
    elif selected_provider in {"git", "svn"} and selected_provider not in evidence_providers:
        conflicts.append({"kind": "scm", "reason": "selected_provider_has_no_root_evidence", "provider": selected_provider})
    elif selected_provider == "none" and evidence_providers:
        conflicts.append({"kind": "scm", "reason": "none_conflicts_with_root_evidence", "providers": sorted(evidence_providers)})
    elif selected_provider is None:
        unresolved.append({"kind": "scm", "path": ".", "reason": "provider_requires_explicit_none_or_root_evidence"})

    rule_binding_map = {item["path"]: item for item in configured_rule_bindings}
    ignored_rule_set = set(ignored_rule_candidates)
    candidate_paths = {item["path"] for item in rule_candidates}
    if set(rule_binding_map) & ignored_rule_set:
        conflicts.append({"kind": "rule_binding", "reason": "candidate_both_bound_and_ignored", "paths": sorted(set(rule_binding_map) & ignored_rule_set)})
    for path in sorted((set(rule_binding_map) | ignored_rule_set) - candidate_paths):
        unresolved.append({"kind": "rule_binding", "path": path, "reason": "decision_path_not_discovered"})
    default_agents_binding = {"path": agents_rel, "purpose": "project instructions", "load_policy": "always"}
    effective_rule_bindings = {agents_rel: default_agents_binding, **rule_binding_map}
    for item in rule_candidates:
        path = str(item["path"])
        if path == agents_rel or path == workflow_rel or item["human_guide"]:
            continue
        if path not in effective_rule_bindings and path not in ignored_rule_set:
            unresolved.append({"kind": "rule_binding", "path": path, "reason": "rule_candidate_requires_binding_or_ignore"})

    groups: list[dict[str, object]] = []
    by_name: dict[str, list[dict[str, str]]] = {}
    for skill in scanned_skills:
        by_name.setdefault(skill["normalized_name"], []).append(skill)
    for name, members in sorted(by_name.items()):
        hashes = {item["sha256"] for item in members}
        roots = sorted({item["root"] for item in members})
        relation = "single"
        if len(members) > 1 and len(hashes) == 1 and len(roots) > 1:
            relation = "mirror_candidate"
        elif len(members) > 1:
            relation = "content_conflict"
        groups.append({"name": name, "relation": relation, "roots": roots, "members": members})

    root_binding_map = {item["path"]: item for item in configured_skill_root_bindings}
    root_inventories: dict[str, dict[str, str]] = {}
    for skill in scanned_skills:
        inventory = root_inventories.setdefault(skill["root"], {})
        name = skill["normalized_name"]
        if name in inventory:
            conflicts.append({"kind": "skill_content", "name": name, "reason": "duplicate_skill_name_in_root", "roots": [skill["root"]]})
        inventory[name] = skill["sha256"]
    discovered_roots = set(skill_roots)
    for path in sorted(set(root_binding_map) - discovered_roots):
        unresolved.append({"kind": "skill_root_binding", "path": path, "reason": "decision_path_not_discovered"})
    for path in sorted(discovered_roots - set(root_binding_map)):
        unresolved.append({"kind": "skill_root_binding", "path": path, "reason": "skill_root_requires_decision"})
    for path, binding in sorted(root_binding_map.items()):
        if binding["decision"] == "mirror":
            authority = binding["authority"]
            authority_binding = root_binding_map.get(str(authority))
            if authority_binding is None or authority_binding["decision"] != "authority":
                conflicts.append({"kind": "skill_root_binding", "path": path, "reason": "mirror_authority_not_confirmed", "authority": authority})
                continue
            if root_inventories.get(path, {}) != root_inventories.get(str(authority), {}):
                conflicts.append({"kind": "skill_root_binding", "path": path, "reason": "mirror_content_not_identical", "authority": authority})
    for group in groups:
        if group["relation"] != "content_conflict":
            continue
        undecided_roots = [root_path for root_path in group["roots"] if root_path not in root_binding_map]
        mirror_roots = [root_path for root_path in group["roots"] if root_binding_map.get(root_path, {}).get("decision") == "mirror"]
        if undecided_roots or mirror_roots:
            conflicts.append({"kind": "skill_content", "name": group["name"], "reason": "same_name_different_content", "roots": group["roots"]})

    decision_reasons = {
        "provider_requires_explicit_none_or_root_evidence",
        "rule_candidate_requires_binding_or_ignore",
        "skill_root_requires_decision",
    }
    hard_unresolved = [item for item in unresolved if item.get("reason") not in decision_reasons]
    if hard_unresolved:
        status = "incomplete"
    elif unresolved or conflicts:
        status = "needs_decision"
    else:
        status = "complete"
    return {
        "status": status,
        "agents_path": agents_rel,
        "workflow_rule_path": workflow_rel,
        "scm": {"provider": selected_provider, "evidence": scm_evidence},
        "rule_candidates": rule_candidates,
        "rule_bindings": [effective_rule_bindings[path] for path in sorted(effective_rule_bindings)],
        "ignored_rule_candidates": sorted(ignored_rule_set),
        "rule_files": scanned_rules,
        "skill_roots": [{"path": path, "sources": sorted(skill_roots[path]["sources"])} for path in sorted(skill_roots)],
        "skill_groups": groups,
        "skill_root_bindings": [root_binding_map[path] for path in sorted(root_binding_map)],
        "skills": scanned_skills,
        "unresolved": unresolved,
        "conflicts": conflicts,
    }


def _reconcile_capabilities(
    existing: tuple[dict[str, str], ...],
    requested: tuple[dict[str, str], ...],
    *,
    reconcile: bool,
    unavailable_skills: tuple[str, ...],
    dirty_entries: tuple[str, ...],
) -> tuple[tuple[dict[str, str], ...], dict[str, list[dict[str, object]]], bool]:
    existing_map: dict[str, dict[str, str]] = {}
    invalid_existing: list[dict[str, object]] = []
    for item in existing:
        try:
            capability_id = _normalize_capability_id(str(item["id"]))
            skill = _normalize_skill_identity(str(item["skill"]))
            policy = str(item.get("load_policy", "on-demand"))
            if policy != policy.strip() or policy != policy.casefold():
                raise SetupError("existing capability load policy is not canonical")
            if policy not in CAPABILITY_LOAD_POLICIES:
                raise SetupError("invalid existing capability load policy")
            normalized = {"id": capability_id, "skill": skill, "load_policy": policy}
            if capability_id in existing_map:
                invalid_existing.append({"entry": capability_id, "reason": "duplicate_existing_capability"})
            else:
                existing_map[capability_id] = normalized
        except (KeyError, SetupError) as exc:
            invalid_existing.append({"entry": repr(item), "reason": str(exc)})
    invalid_existing.extend({"entry": item, "reason": "unparsed_managed_capability"} for item in dirty_entries)

    requested_map = {item["id"]: dict(item) for item in requested}
    if reconcile:
        desired_map = requested_map
    else:
        desired_map = dict(existing_map)
        desired_map.update(requested_map)

    changes: dict[str, list[dict[str, object]]] = {
        "keep": [],
        "add": [],
        "replace": [],
        "remove": [],
        "warning": [],
    }
    for capability_id in sorted(set(existing_map) | set(desired_map)):
        before = existing_map.get(capability_id)
        after = desired_map.get(capability_id)
        if before is None and after is not None:
            changes["add"].append({"id": capability_id, "after": after})
        elif before is not None and after is None:
            changes["remove"].append({"id": capability_id, "before": before})
        elif before == after:
            changes["keep"].append({"id": capability_id, "value": after})
        else:
            changes["replace"].append({"id": capability_id, "before": before, "after": after})
    for item in invalid_existing:
        target = "remove" if reconcile else "warning"
        changes[target].append(item)
    unavailable = set(unavailable_skills)
    for item in desired_map.values():
        if item["skill"] in unavailable:
            changes["warning"].append({
                "id": item["id"],
                "skill": item["skill"],
                "reason": "unavailable_in_current_context_fallback_retained",
            })
    blocked = bool(invalid_existing) and not reconcile
    return tuple(desired_map[key] for key in sorted(desired_map)), changes, blocked


def render_workflow_rule(
    agents_path: str,
    workflow_rule_path: str,
    spec_storage: Mapping[str, str],
    human_guide: str | None,
    discovery: Mapping[str, object],
    capability_bindings: tuple[dict[str, str], ...],
    pi_model_bindings: tuple[dict[str, str], ...],
    documentation: Mapping[str, str | None],
) -> bytes:
    scm = discovery["scm"]
    evidence = [item["source"] for item in scm["evidence"] if item["provider"] == scm["provider"]]
    scm_evidence = "、".join(f"`{item}`" for item in evidence) or "未配置"
    rule_groups: dict[str, list[str]] = {}
    for item in discovery["rule_bindings"]:
        rule_groups.setdefault(item["load_policy"], []).append(
            f"`{item['path']}` = {item['purpose']}"
        )
    rule_lines = [
        f"- `{policy}`：" + "；".join(entries)
        for policy, entries in rule_groups.items()
    ]
    skill_lines = []
    for item in discovery["skill_root_bindings"]:
        suffix = f"；authority = `{item['authority']}`" if item["decision"] == "mirror" else ""
        skill_lines.append(f"- `{item['path']}`：`{item['decision']}`{suffix}")
    capability_groups: dict[str, list[str]] = {}
    for item in capability_bindings:
        capability_groups.setdefault(item["load_policy"], []).append(
            f"`{item['id']}` -> `{item['skill']}`"
        )
    capability_lines = [
        f"- `{policy}`：" + "；".join(entries)
        for policy, entries in capability_groups.items()
    ]
    unresolved_lines = [
        f"- {item.get('kind', 'unknown')}：`{item.get('path', '.')}`（{item.get('reason', 'unresolved')}）"
        for item in discovery["unresolved"]
    ]
    conflict_lines = [
        f"- {item.get('kind', 'unknown')}：{item.get('reason', 'conflict')}"
        for item in discovery["conflicts"]
    ]
    binding_lines = [
        f"- Project AGENTS：`{agents_path}`",
        f"- SCM：{scm_evidence}",
    ]
    if human_guide:
        binding_lines.append(
            f"- Human Guide：`{human_guide}`（只读引用；setup 不管理正文）"
        )
    ignored_rules = discovery["ignored_rule_candidates"]
    if ignored_rules:
        binding_lines.append(
            f"- Setup 不绑定为项目规则：已分类 {len(ignored_rules)} 项"
        )

    sections = [
        f"{GENERATOR_MARKER}\n{SCHEMA_MARKER}\n# Sacha Orchestra 项目接入",
        "`setup-project` 生成；只记录项目差异。",
        "## 项目绑定\n\n" + "\n".join(binding_lines),
    ]
    if rule_lines:
        sections.append("### Rule bindings\n\n" + "\n".join(rule_lines))
    if skill_lines:
        sections.append("### Skill roots\n\n" + "\n".join(skill_lines))
    if capability_lines:
        sections.append("### Capability bindings\n\n" + "\n".join(capability_lines))
    if pi_model_bindings:
        pi_model_lines = [
            f"- `{item['route']}` -> `{item['model']}`"
            for item in pi_model_bindings
        ]
        sections.append(
            "### Pi one-shot model routing\n\n"
            + "\n".join(pi_model_lines)
            + "\n\n仅供本项目 Runtime 使用；由 `setup-project` 从本机 Pi 可用模型确认，不复制到 plugin 源码。"
        )
    storage_lines = [
        f"- Spec：`{spec_storage['root']}`",
        f"- 任务目录：`{spec_storage['directory_pattern']}`",
        f"- 文件：`{spec_storage['file_name']}`；澄清决定：`{DECISIONS_FILE_NAME}`（按需，与 Spec 同目录）",
    ]
    if documentation["policy"] == "disabled":
        storage_lines.append("- 项目文档：`disabled`")
    else:
        storage_lines.append(
            f"- 项目文档：`{documentation['policy']}` -> `{documentation['root']}`；"
            f"write = `{documentation['write_authorization']}`"
        )
    storage_lines.append(
        f"- 项目 Context：`{_project_context_path(spec_storage)}`"
        "（术语与跨任务约束；setup 只记录 path，不创建正文）"
    )
    sections.append("### Storage\n\n" + "\n".join(storage_lines))
    if unresolved_lines:
        sections.append("### Unresolved\n\n" + "\n".join(unresolved_lines))
    if conflict_lines:
        sections.append("### Conflicts\n\n" + "\n".join(conflict_lines))
    text = "\n\n".join(sections) + "\n"
    return text.encode("utf-8")


def render_workflow_state(discovery: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            {
                "generator": WORKFLOW_STATE_GENERATOR,
                "schemaVersion": WORKFLOW_STATE_SCHEMA_VERSION,
                "ignoredRuleCandidates": discovery["ignored_rule_candidates"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def _normalize_project_rules_skill(value: str) -> str:
    skill = value.strip()
    if not CANONICAL_SKILL.fullmatch(skill):
        raise SetupError("project rules source must use canonical plugin:skill identity")
    return skill


def _normalize_project_rules_content(content: bytes) -> bytes:
    if len(content) > MAX_PROJECT_RULES_BYTES:
        raise SetupError(f"project rules content exceeds {MAX_PROJECT_RULES_BYTES} bytes")
    text = content.decode("utf-8")
    if "\x00" in text:
        raise SetupError("project rules content contains NUL")
    reserved = (
        AGENTS_BEGIN,
        AGENTS_END,
        PROJECT_RULES_BEGIN,
        PROJECT_RULES_END,
        PROJECT_RULES_HASH,
    )
    if any(marker in text for marker in reserved):
        raise SetupError("project rules content contains a reserved managed marker")
    normalized = text.strip("\r\n")
    if not normalized.strip():
        raise SetupError("project rules content must not be empty")
    return normalized.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _extract_project_rules(
    preimage: bytes | None,
    *,
    replace_legacy: bool = False,
) -> dict[str, bytes]:
    if preimage is None:
        return {}
    text = preimage.decode("utf-8")
    begin_count = text.count(AGENTS_BEGIN)
    end_count = text.count(AGENTS_END)
    if begin_count == 0 and end_count == 0:
        return {}
    if begin_count != 1 or end_count != 1:
        raise SetupError("Project AGENTS contains duplicate or broken managed markers")
    start = text.index(AGENTS_BEGIN) + len(AGENTS_BEGIN)
    finish = text.find(AGENTS_END, start)
    if finish < 0:
        raise SetupError("Project AGENTS managed markers are out of order")
    managed = text[start:finish]
    if LEGACY_PROJECT_RULES_HEADING in managed:
        if not replace_legacy:
            raise SetupError(
                "Project AGENTS contains unattributed legacy project rules; "
                "read and reassign them with canonical source plus --replace-legacy-project-rules"
            )
        if PROJECT_RULES_BEGIN in managed or PROJECT_RULES_END in managed:
            raise SetupError("Project AGENTS mixes legacy and canonical project rules")
    rules: dict[str, bytes] = {}
    cursor = 0
    while True:
        begin = managed.find(PROJECT_RULES_BEGIN, cursor)
        if begin < 0:
            break
        header_end = managed.find(" -->", begin)
        if header_end < 0:
            raise SetupError("Project AGENTS contains a broken project rules marker")
        skill = _normalize_project_rules_skill(
            managed[begin + len(PROJECT_RULES_BEGIN):header_end]
        )
        content_start = header_end + len(" -->")
        if managed.startswith("\r\n", content_start):
            content_start += 2
        elif managed.startswith("\n", content_start):
            content_start += 1
        else:
            raise SetupError("Project AGENTS project rules marker must end its line")
        declared_hash = None
        first_line_end = managed.find("\n", content_start)
        if first_line_end >= 0:
            first_line = managed[content_start:first_line_end].rstrip("\r")
            if first_line.startswith(PROJECT_RULES_HASH):
                if not first_line.endswith(" -->"):
                    raise SetupError("Project AGENTS contains a broken project rules source hash")
                declared_hash = _normalize_hash(
                    first_line[len(PROJECT_RULES_HASH):-len(" -->")],
                    "project rules source SHA-256",
                )
                content_start = first_line_end + 1
        if declared_hash is None and not replace_legacy:
            raise SetupError(
                f"Project AGENTS project rules source hash is missing: {skill}; "
                "refresh the canonical asset with --replace-legacy-project-rules"
            )
        end_marker = f"{PROJECT_RULES_END}{skill} -->"
        content_end = managed.find(end_marker, content_start)
        if content_end < 0:
            raise SetupError("Project AGENTS contains an unclosed project rules marker")
        if skill in rules:
            raise SetupError(f"Project AGENTS contains duplicate project rules source: {skill}")
        raw_content = managed[content_start:content_end].rstrip("\r\n").encode("utf-8")
        normalized_content = _normalize_project_rules_content(raw_content)
        if declared_hash is not None and declared_hash != sha256_bytes(normalized_content):
            raise SetupError(f"Project AGENTS project rules source hash is stale: {skill}")
        rules[skill] = normalized_content
        cursor = content_end + len(end_marker)
    if managed.count(PROJECT_RULES_BEGIN) != len(rules) or managed.count(PROJECT_RULES_END) != len(rules):
        raise SetupError("Project AGENTS contains unmatched project rules markers")
    return rules


def _project_rules_replacement_requirements(preimage: bytes | None) -> tuple[bool, tuple[str, ...]]:
    """Return unattributed legacy and per-source hash refresh requirements.

    Call only after ``_extract_project_rules`` has validated the managed block.
    """
    if preimage is None:
        return False, ()
    text = preimage.decode("utf-8")
    if AGENTS_BEGIN not in text:
        return False, ()
    start = text.index(AGENTS_BEGIN) + len(AGENTS_BEGIN)
    finish = text.index(AGENTS_END, start)
    managed = text[start:finish]
    if LEGACY_PROJECT_RULES_HEADING in managed:
        return True, ()
    missing_hashes: list[str] = []
    cursor = 0
    while True:
        begin = managed.find(PROJECT_RULES_BEGIN, cursor)
        if begin < 0:
            break
        header_end = managed.find(" -->", begin)
        skill = _normalize_project_rules_skill(
            managed[begin + len(PROJECT_RULES_BEGIN):header_end]
        )
        content_start = header_end + len(" -->")
        if managed.startswith("\r\n", content_start):
            content_start += 2
        else:
            content_start += 1
        first_line_end = managed.find("\n", content_start)
        first_line = managed[content_start:first_line_end].rstrip("\r")
        if not first_line.startswith(PROJECT_RULES_HASH):
            missing_hashes.append(skill)
        end_marker = f"{PROJECT_RULES_END}{skill} -->"
        cursor = managed.find(end_marker, content_start) + len(end_marker)
    return False, tuple(missing_hashes)


def _reconcile_project_rules(
    existing: Mapping[str, bytes],
    sources: tuple[tuple[str, bytes], ...],
    remove_skills: tuple[str, ...],
) -> tuple[dict[str, bytes], dict[str, list[str]]]:
    planned = dict(existing)
    reconciliation = {"keep": [], "add": [], "update": [], "remove": []}
    removals = {_normalize_project_rules_skill(item) for item in remove_skills}
    source_map: dict[str, bytes] = {}
    for raw_skill, raw_content in sources:
        skill = _normalize_project_rules_skill(raw_skill)
        if skill in source_map:
            raise SetupError(f"duplicate project rules source: {skill}")
        source_map[skill] = _normalize_project_rules_content(raw_content)
    overlap = removals & set(source_map)
    if overlap:
        raise SetupError(f"project rules source cannot be updated and removed together: {sorted(overlap)[0]}")
    for skill in sorted(removals):
        if skill in planned:
            del planned[skill]
            reconciliation["remove"].append(skill)
    for skill, content in sorted(source_map.items()):
        if skill not in planned:
            reconciliation["add"].append(skill)
        elif planned[skill] == content:
            reconciliation["keep"].append(skill)
        else:
            reconciliation["update"].append(skill)
        planned[skill] = content
    reconciliation["keep"].extend(
        skill for skill in sorted(planned)
        if skill not in source_map and skill not in reconciliation["keep"]
    )
    return planned, reconciliation


def render_agents_block(workflow_rule_path: str, project_rules: Mapping[str, bytes] | None = None) -> bytes:
    text = f"""{AGENTS_BEGIN}
## Sacha Orchestra 接入

- 潜在 Sacha 任务先由 `sacha-orchestra:using-sacha` 感知；本地路线只遵循适用 Project AGENTS。
- Human 接受 Sacha 后才读取 `{workflow_rule_path}` 获取项目绑定；入口、Gate 和 Role 路由仍以 plugin canonical contract 为准。
{AGENTS_END}"""
    body = text.encode("utf-8")
    if project_rules:
        entries: list[str] = []
        for skill, content in sorted(project_rules.items()):
            normalized_skill = _normalize_project_rules_skill(skill)
            rules_text = _normalize_project_rules_content(content).decode("utf-8")
            entries.append(
                f"{PROJECT_RULES_BEGIN}{normalized_skill} -->\n"
                f"{PROJECT_RULES_HASH}{sha256_bytes(rules_text.encode('utf-8'))} -->\n"
                f"{rules_text}\n"
                f"{PROJECT_RULES_END}{normalized_skill} -->"
            )
        insert = ("\n\n" + PROJECT_RULES_HEADING + "\n\n" + "\n\n".join(entries) + "\n").encode("utf-8")
        end = AGENTS_END.encode("utf-8")
        body = body.replace(end, insert + end, 1)
    return body


def _merge_agents(preimage: bytes | None, managed_block: bytes) -> bytes:
    if preimage is None:
        return managed_block + b"\n"
    begin = AGENTS_BEGIN.encode("utf-8")
    end = AGENTS_END.encode("utf-8")
    begin_count = preimage.count(begin)
    end_count = preimage.count(end)
    if begin_count == 0 and end_count == 0:
        separator = b"" if not preimage else (b"\n" if preimage.endswith(b"\n") else b"\n\n")
        return preimage + separator + managed_block + b"\n"
    if begin_count != 1 or end_count != 1:
        raise SetupError("Project AGENTS contains duplicate or broken managed markers")
    start = preimage.find(begin)
    finish = preimage.find(end)
    if start < 0 or finish < start:
        raise SetupError("Project AGENTS managed markers are out of order")
    finish += len(end)
    return preimage[:start] + managed_block + preimage[finish:]


def _base_result(
    workflow_rel: str,
    agents_rel: str,
    manage_agents: bool,
) -> dict[str, object]:
    return {
        "status": "ready",
        "transaction": "dry_run",
        "discovery": {"status": "not_run"},
        "workflow_rule": {"path": workflow_rel, "action": "unknown"},
        "workflow_state": {"path": "<unknown>", "action": "unknown"},
        "agents_block": {"path": agents_rel, "enabled": manage_agents, "action": "disabled"},
        "project_rules_reconciliation": {"keep": [], "add": [], "update": [], "remove": []},
        "project_skill_assessments": [],
        "project_capability_candidates": [],
        "project_policy_decisions_required": [],
        "unassessed_project_skills": [],
        "capability_reconciliation": {
            "keep": [],
            "add": [],
            "replace": [],
            "remove": [],
            "warning": [],
        },
        "changed_files": [],
        "replaced": [],
        "restored": [],
        "restore_failed": [],
        "conflicts": [],
        "warnings": [],
        "recovery_steps": [],
        "cleanup_failed": [],
        "targets": {},
    }


def _target_record(relative: str, existed: bool, pre_hash: str | None, generated: bytes) -> dict[str, object]:
    return {
        "path": relative,
        "existed": existed,
        "preimage_sha256": pre_hash,
        "generated_sha256": sha256_bytes(generated),
        "current_sha256": pre_hash,
    }


def _prepare_temp(target: Path, data: bytes) -> Path:
    descriptor, raw_path = tempfile.mkstemp(prefix=".sacha-setup-", suffix=".tmp", dir=target.parent)
    temp_path = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if sha256_bytes(temp_path.read_bytes()) != sha256_bytes(data):
            raise OSError("temporary file validation failed")
        return temp_path
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _create_parent_dirs(root: Path, parent: Path) -> list[Path]:
    missing: list[Path] = []
    cursor = parent
    while cursor != root and not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    if cursor != root and not cursor.exists():
        raise SetupError("target parent cannot be anchored inside project root")
    created: list[Path] = []
    for path in reversed(missing):
        path.mkdir()
        created.append(path)
    return created


def _cleanup_paths(
    root: Path,
    temp_paths: list[Path],
    created_dirs: list[Path],
) -> list[str]:
    failed: list[str] = []
    for path in temp_paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            failed.append(path.relative_to(root).as_posix())
    for path in reversed(created_dirs):
        try:
            path.rmdir()
        except OSError:
            if path.exists() and not any(path.iterdir()):
                failed.append(path.relative_to(root).as_posix())
    return failed


def run_setup(
    config: SetupConfig,
    *,
    write: bool = False,
    confirmed_planned_delta_sha256: str | None = None,
    _test_hooks: Mapping[str, Callable[..., None]] | None = None,
) -> dict[str, object]:
    """Discover, render, validate and optionally write integration files.

    ``_test_hooks`` is an internal fault-injection seam and is intentionally not
    exposed by the CLI. Supported hooks are ``before_replace``,
    ``after_replace`` and ``before_restore``.
    """

    hooks = dict(_test_hooks or {})
    root = config.project_root.resolve(strict=False)
    if not root.exists() or not root.is_dir():
        return {
            **_base_result("<invalid>", "<invalid>", config.manage_agents),
            "status": "refused",
            "transaction": "no_write",
            "conflicts": ["project root must already exist and be a directory"],
        }

    try:
        workflow_path, workflow_rel = _normalize_relative_path(root, config.workflow_rule_path, "workflow_rule_path")
        workflow_state_path = workflow_path.with_suffix(".state.json")
        workflow_state_rel = workflow_state_path.relative_to(root).as_posix()
        workflow_state_data = (
            workflow_state_path.read_bytes() if workflow_state_path.is_file() else None
        )
        if workflow_state_data is not None:
            _parse_workflow_state(workflow_state_data)
        if workflow_state_data is not None and not workflow_path.is_file():
            raise SetupError("managed workflow state exists without its workflow rule")
        existing_values: dict[str, object] = {}
        if workflow_path.is_file():
            existing_values = _parse_existing_project_values(
                workflow_path.read_bytes(),
                workflow_state_data,
            )
        effective_agents_path = config.agents_path
        if config.agents_path == "AGENTS.md" and existing_values.get("agents_path"):
            effective_agents_path = str(existing_values["agents_path"])
        agents_path, agents_rel = _normalize_relative_path(root, effective_agents_path, "agents_path")
        human_guide = None
        effective_human_guide = config.human_guide or existing_values.get("human_guide")
        if effective_human_guide:
            _, human_guide = _normalize_relative_path(root, str(effective_human_guide), "human_guide")
        if config.documentation_policy is None:
            existing_documentation = existing_values.get("documentation", {})
            documentation_policy = existing_documentation.get("policy")
            documentation_root_kind = existing_documentation.get("root_kind")
            documentation_root = existing_documentation.get("root")
            documentation_write_authorization = existing_documentation.get(
                "write_authorization"
            )
        else:
            documentation_policy = config.documentation_policy
            documentation_root_kind = config.documentation_root_kind
            documentation_root = config.documentation_root
            documentation_write_authorization = config.documentation_write_authorization
        documentation, documentation_warnings = _normalize_documentation(
            root,
            policy=documentation_policy,
            root_kind=documentation_root_kind,
            documentation_root=documentation_root,
            write_authorization=documentation_write_authorization,
        )
        if config.spec_base_kind is None:
            existing_spec_storage = existing_values.get("spec_storage", {})
            if existing_spec_storage:
                spec_base_kind = existing_spec_storage.get("root_kind")
                spec_base = _spec_base_from_storage_root(
                    str(existing_spec_storage.get("root", ""))
                )
                spec_storage_source = "existing-binding"
            elif workflow_path.is_file():
                spec_base_kind = None
                spec_base = None
                spec_storage_source = "missing-existing-binding"
            else:
                spec_base_kind = DEFAULT_SPEC_BASE_KIND
                spec_base = DEFAULT_SPEC_BASE
                spec_storage_source = "default"
        else:
            spec_base_kind = config.spec_base_kind
            spec_base = config.spec_base
            spec_storage_source = "explicit-input"
        spec_storage, spec_warnings = _normalize_spec_storage(
            root,
            root_kind=spec_base_kind,
            spec_base=spec_base,
        )
        expected_agents = _normalize_hash(config.expected_agents_sha256, "expected_agents_sha256")
        expected_workflow = _normalize_hash(config.expected_workflow_sha256, "expected_workflow_sha256")
        confirmed_planned_delta = _normalize_hash(
            confirmed_planned_delta_sha256,
            "confirmed_planned_delta_sha256",
        )
        effective_scm_provider = config.scm_provider
        if effective_scm_provider is None and existing_values.get("scm_provider"):
            effective_scm_provider = str(existing_values["scm_provider"])
        scm_provider = _normalize_scm_provider(effective_scm_provider)
        if config.rule_bindings:
            rule_bindings = _parse_rule_bindings(root, config.rule_bindings)
        else:
            rule_bindings = _parse_rule_bindings(root, tuple(
                f"{item['path']}::{item['purpose']}::{item['load_policy']}"
                for item in existing_values.get("rule_bindings", ())
                if item["path"] != effective_agents_path.replace("\\", "/")
            ))
        effective_ignored_rules = config.ignored_rule_candidates or tuple(
            existing_values.get("ignored_rule_candidates", ())
        )
        ignored_rule_candidates = _parse_ignored_paths(root, tuple(effective_ignored_rules), "ignore_rule_candidate")
        if config.skill_root_bindings:
            skill_root_bindings = _parse_skill_root_bindings(root, config.skill_root_bindings)
        else:
            skill_root_bindings = _parse_skill_root_bindings(root, tuple(
                f"{item['path']}::{item['decision']}" + (f"::{item['authority']}" if item.get("authority") else "")
                for item in existing_values.get("skill_root_bindings", ())
            ))
        capability_bindings = _parse_capability_bindings(config.capability_bindings)
        if config.pi_model_bindings and config.clear_pi_model_bindings:
            raise SetupError(
                "pi_model_bindings and clear_pi_model_bindings are mutually exclusive"
            )
        if config.clear_pi_model_bindings:
            pi_model_bindings: tuple[dict[str, str], ...] = ()
        elif config.pi_model_bindings:
            pi_model_bindings = _parse_pi_model_bindings(config.pi_model_bindings)
        else:
            pi_model_bindings = _parse_pi_model_bindings(tuple(
                f"{item['route']}::{item['model']}"
                for item in existing_values.get("pi_model_bindings", ())
            ))
        unavailable_skills = _normalize_unavailable_skills(config.unavailable_capability_skills)
        existing_capabilities = tuple(existing_values.get("capability_bindings", ()))
        capability_dirty = tuple(str(item) for item in existing_values.get("capability_dirty", ()))
        if workflow_path == agents_path:
            raise SetupError("workflow rule and Project AGENTS must be different files")
    except (OSError, UnicodeError, SetupError) as exc:
        result = _base_result("<invalid>", "<invalid>", config.manage_agents)
        message = str(exc) if isinstance(exc, (SetupError, UnicodeError)) else f"filesystem operation failed: {type(exc).__name__}"
        result.update(status="refused", transaction="no_write", conflicts=[message])
        return result

    result = _base_result(workflow_rel, agents_rel, config.manage_agents)
    discovery = _discover_project_integration(
        root,
        agents_path=agents_path,
        agents_rel=agents_rel,
        workflow_path=workflow_path,
        workflow_rel=workflow_rel,
        configured_rule_paths=config.rule_paths,
        configured_skill_roots=config.skill_roots,
        human_guide=human_guide,
        scm_provider=scm_provider,
        configured_rule_bindings=rule_bindings,
        ignored_rule_candidates=ignored_rule_candidates,
        configured_skill_root_bindings=skill_root_bindings,
    )
    result["discovery"] = discovery
    result["documentation"] = documentation
    result["warnings"].extend(documentation_warnings)
    result["spec_storage"] = spec_storage
    result["pi_model_bindings"] = list(pi_model_bindings)
    result["warnings"].extend(spec_warnings)
    selected_project_roots = {
        str(item["path"])
        for item in discovery["skill_root_bindings"]
        if item["decision"] in {"authority", "independent"}
    }
    assessment = _assess_project_skills(
        root,
        discovery,
        config.project_skill_evidence,
        config.visible_project_skills,
        require_complete=(
            config.assess_project_skills
            or any(
                str(item["root"]) in selected_project_roots
                for item in discovery["skills"]
            )
        ),
    )
    result["project_skill_assessments"] = assessment["assessments"]
    result["project_capability_candidates"] = assessment["candidates"]
    result["project_policy_decisions_required"] = assessment[
        "policy_decisions_required"
    ]
    result["unassessed_project_skills"] = assessment["unassessed"]
    result["conflicts"].extend(assessment["conflicts"])

    requested_capabilities: dict[str, dict[str, str]] = {}
    mapping_conflicts: list[str] = []
    for item in capability_bindings:
        if ":" not in item["skill"]:
            mapping_conflicts.append(
                "unprefixed capability-binding cannot add a project Skill; "
                "use project Skill evidence derived from the full body"
            )
            continue
        requested_capabilities[item["id"]] = dict(item)
    for item in assessment["bindings"]:
        if item["id"] in requested_capabilities:
            mapping_conflicts.append(
                f"capability id is declared by both provider and project Skill evidence: "
                f"{item['id']}"
            )
            continue
        requested_capabilities[item["id"]] = dict(item)
    result["conflicts"].extend(mapping_conflicts)
    effective_capabilities, capability_reconciliation, capability_blocked = _reconcile_capabilities(
        existing_capabilities,
        tuple(requested_capabilities[key] for key in sorted(requested_capabilities)),
        reconcile=config.reconcile_capabilities,
        unavailable_skills=unavailable_skills,
        dirty_entries=capability_dirty,
    )
    admitted_project_bindings = {
        (item["id"], item["skill"])
        for item in assessment["bindings"]
    }
    for item in effective_capabilities:
        if ":" not in item["skill"] and (item["id"], item["skill"]) not in admitted_project_bindings:
            capability_reconciliation["warning"].append({
                "id": item["id"],
                "skill": item["skill"],
                "reason": "existing_project_skill_mapping_not_reverified_from_current_body",
            })
    result["capability_reconciliation"] = capability_reconciliation
    assessment_blocked = bool(
        assessment["conflicts"]
        or assessment["unassessed"]
        or assessment["policy_decisions_required"]
        or mapping_conflicts
    )
    discovery_blocked = discovery["status"] != "complete"
    targets: list[dict[str, object]] = []
    try:
        workflow_existed, workflow_preimage, workflow_hash = _file_state(workflow_path)
        workflow_generated = render_workflow_rule(
            agents_rel,
            workflow_rel,
            spec_storage,
            human_guide,
            discovery,
            effective_capabilities,
            pi_model_bindings,
            documentation,
        )
        workflow_action = "unchanged" if workflow_preimage == workflow_generated else ("update" if workflow_existed else "create")
        result["workflow_rule"] = {
            "path": workflow_rel,
            "action": workflow_action,
            "preimage_sha256": workflow_hash,
            "generated_sha256": sha256_bytes(workflow_generated),
            "planned_content": workflow_generated.decode("utf-8"),
        }
        result["targets"][workflow_rel] = _target_record(workflow_rel, workflow_existed, workflow_hash, workflow_generated)
        if workflow_existed:
            assert workflow_preimage is not None
            has_generator = GENERATOR_MARKER.encode("utf-8") in workflow_preimage
            schema_markers = re.findall(rb"<!-- Schema Version: ([^>]+) -->", workflow_preimage)
            if has_generator and schema_markers == [b"3"]:
                pass
            elif has_generator or schema_markers:
                result["workflow_rule"]["action"] = "refuse"
                raise SetupError("workflow rule has incomplete or unknown generator/schema markers")
            else:
                if not write:
                    workflow_action = "replace_unmanaged_workflow"
                    result["workflow_rule"]["action"] = workflow_action
                elif not config.replace_unmanaged_workflow:
                    result["workflow_rule"]["action"] = "refuse"
                    raise SetupError("existing workflow rule is unmanaged; explicit replacement is required")
                elif expected_workflow is None or expected_workflow != workflow_hash:
                    result["workflow_rule"]["action"] = "refuse"
                    raise SetupError("unmanaged workflow rule expected SHA-256 is missing or stale")
            if write and workflow_preimage != workflow_generated and has_generator:
                if expected_workflow is None or expected_workflow != workflow_hash:
                    result["workflow_rule"]["action"] = "refuse"
                    raise SetupError("managed workflow rule expected SHA-256 is missing or stale")
        if workflow_action != "unchanged":
            targets.append({
                "path": workflow_path,
                "relative": workflow_rel,
                "existed": workflow_existed,
                "preimage": workflow_preimage,
                "pre_hash": workflow_hash,
                "generated": workflow_generated,
                "generated_hash": sha256_bytes(workflow_generated),
            })

        workflow_state_existed, workflow_state_preimage, workflow_state_hash = _file_state(
            workflow_state_path
        )
        workflow_state_generated = render_workflow_state(discovery)
        workflow_state_action = (
            "unchanged"
            if workflow_state_preimage == workflow_state_generated
            else ("update" if workflow_state_existed else "create")
        )
        result["workflow_state"] = {
            "path": workflow_state_rel,
            "action": workflow_state_action,
            "preimage_sha256": workflow_state_hash,
            "generated_sha256": sha256_bytes(workflow_state_generated),
        }
        result["targets"][workflow_state_rel] = _target_record(
            workflow_state_rel,
            workflow_state_existed,
            workflow_state_hash,
            workflow_state_generated,
        )
        if workflow_state_action != "unchanged":
            targets.append({
                "path": workflow_state_path,
                "relative": workflow_state_rel,
                "existed": workflow_state_existed,
                "preimage": workflow_state_preimage,
                "pre_hash": workflow_state_hash,
                "generated": workflow_state_generated,
                "generated_hash": sha256_bytes(workflow_state_generated),
            })

        if config.manage_agents:
            agents_existed, agents_preimage, agents_hash = _file_state(agents_path)
            result["agents_block"] = {
                "path": agents_rel,
                "enabled": True,
                "action": "refuse",
                "preimage_sha256": agents_hash,
                "generated_sha256": None,
            }
            result["targets"][agents_rel] = {
                "path": agents_rel,
                "existed": agents_existed,
                "preimage_sha256": agents_hash,
                "generated_sha256": None,
                "current_sha256": agents_hash,
            }
            if agents_existed and write and expected_agents is None:
                raise SetupError("existing Project AGENTS requires expected SHA-256 for write")
            if expected_agents is not None and expected_agents != agents_hash:
                raise SetupError("Project AGENTS expected SHA-256 is stale")
            existing_project_rules = _extract_project_rules(
                agents_preimage,
                replace_legacy=config.replace_legacy_project_rules,
            )
            legacy_rules, hashless_rules = _project_rules_replacement_requirements(
                agents_preimage
            )
            source_skills = {
                _normalize_project_rules_skill(skill)
                for skill, _ in config.project_rules_sources
            }
            if legacy_rules and not source_skills:
                raise SetupError(
                    "Project AGENTS legacy project rules require at least one canonical "
                    "project rules asset with --replace-legacy-project-rules"
                )
            missing_assets = sorted(set(hashless_rules) - source_skills)
            if missing_assets:
                raise SetupError(
                    "Project AGENTS project rules source hash is missing; provide the "
                    f"canonical asset for: {missing_assets[0]}"
                )
            planned_project_rules, project_rules_reconciliation = _reconcile_project_rules(
                existing_project_rules,
                config.project_rules_sources,
                config.remove_project_rules_skills,
            )
            result["project_rules_reconciliation"] = project_rules_reconciliation
            agents_generated = _merge_agents(
                agents_preimage,
                render_agents_block(workflow_rel, planned_project_rules),
            )
            agents_action = "unchanged" if agents_preimage == agents_generated else ("update" if agents_existed else "create")
            result["agents_block"] = {
                "path": agents_rel,
                "enabled": True,
                "action": agents_action,
                "preimage_sha256": agents_hash,
                "generated_sha256": sha256_bytes(agents_generated),
            }
            result["targets"][agents_rel] = _target_record(agents_rel, agents_existed, agents_hash, agents_generated)
            if agents_action != "unchanged":
                targets.append({
                    "path": agents_path,
                    "relative": agents_rel,
                    "existed": agents_existed,
                    "preimage": agents_preimage,
                    "pre_hash": agents_hash,
                    "generated": agents_generated,
                    "generated_hash": sha256_bytes(agents_generated),
                })
    except (OSError, UnicodeError, SetupError) as exc:
        message = str(exc) if isinstance(exc, (SetupError, UnicodeError)) else f"filesystem operation failed: {type(exc).__name__}"
        result.update(status="refused", transaction="no_write", conflicts=[message])
        return result

    result["changed_files"] = [target["relative"] for target in targets]
    current_configuration = {
        "spec_storage": existing_values.get("spec_storage") or None,
        "documentation": existing_values.get("documentation") or None,
    }
    planned_configuration = {
        "spec_storage": spec_storage,
        "documentation": documentation,
    }
    configuration_sources = {
        "spec_storage": spec_storage_source,
        "documentation": (
            "existing-binding"
            if config.documentation_policy is None
            else "explicit-input"
        ),
    }
    confirmation_payload = {
        "project_root": str(root),
        "current": current_configuration,
        "planned": planned_configuration,
        "sources": configuration_sources,
        "changed_files": result["changed_files"],
        "targets": [
            {
                "path": relative,
                "existed": target["existed"],
                "preimage_sha256": target["preimage_sha256"],
                "generated_sha256": target["generated_sha256"],
            }
            for relative, target in sorted(result["targets"].items())
        ],
        "warnings": result["warnings"],
    }
    planned_delta_sha256 = sha256_bytes(
        json.dumps(
            confirmation_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    result["write_confirmation"] = {
        "required": bool(targets),
        "project_root": str(root),
        "current": current_configuration,
        "planned": planned_configuration,
        "sources": configuration_sources,
        "planned_delta_sha256": planned_delta_sha256,
    }
    if discovery_blocked or capability_blocked or assessment_blocked:
        decision_conflicts: list[str] = list(result["conflicts"])
        if discovery["status"] == "incomplete":
            decision_conflicts.append("Project Binding discovery or decisions are incomplete")
        elif discovery["status"] == "needs_decision":
            decision_conflicts.append("Project Binding discovery requires explicit decisions")
        if discovery["conflicts"]:
            decision_conflicts.append("Project Binding conflicts require explicit resolution")
        if capability_blocked:
            decision_conflicts.append("managed capability data is invalid; explicit reconciliation is required")
        if assessment["unassessed"]:
            decision_conflicts.append(
                "project Skills require full-body assessment before capability reconciliation"
            )
        if assessment["policy_decisions_required"]:
            decision_conflicts.append(
                "project capability candidates require explicit load-policy decisions"
            )
        result.update(status="refused", transaction="no_write", conflicts=decision_conflicts)
        return result
    if not write:
        return result
    if not targets:
        result.update(status="ok", transaction="no_changes")
        return result
    if confirmed_planned_delta != planned_delta_sha256:
        result.update(
            status="refused",
            transaction="no_write",
            conflicts=[
                "write requires the exact confirmed planned delta SHA-256 from the current dry-run"
            ],
        )
        return result

    created_dirs: list[Path] = []
    prepared: dict[str, Path] = {}
    try:
        for target in targets:
            created_dirs.extend(_create_parent_dirs(root, target["path"].parent))
        for target in targets:
            prepared[target["relative"]] = _prepare_temp(target["path"], target["generated"])
        for target in targets:
            existed, _, current_hash = _file_state(target["path"])
            if existed != target["existed"] or current_hash != target["pre_hash"]:
                raise SetupError("target changed after precondition validation")
    except (OSError, SetupError) as exc:
        message = str(exc) if isinstance(exc, SetupError) else f"filesystem operation failed: {type(exc).__name__}"
        result.update(status="refused", transaction="no_write", conflicts=[message])
        result["cleanup_failed"] = _cleanup_paths(root, list(prepared.values()), created_dirs)
        return result

    replaced_targets: list[dict[str, object]] = []
    try:
        for index, target in enumerate(targets):
            hook = hooks.get("before_replace")
            if hook:
                hook(index, target["relative"], dict(prepared))
            existed, _, current_hash = _file_state(target["path"])
            if existed != target["existed"] or current_hash != target["pre_hash"]:
                raise SetupError("target changed immediately before replacement")
            temp_path = prepared[target["relative"]]
            os.replace(temp_path, target["path"])
            prepared.pop(target["relative"], None)
            # Record the replacement before any post-replacement observation.
            # If hashing or an internal seam fails after os.replace, the target
            # must still enter compensation accounting.
            replaced_targets.append(target)
            result["replaced"].append(target["relative"])
            result["targets"][target["relative"]]["current_sha256"] = None
            hook = hooks.get("after_replace")
            if hook:
                hook(index, target["relative"], target["path"])
            if sha256_bytes(target["path"].read_bytes()) != target["generated_hash"]:
                raise OSError("post-replacement hash validation failed")
            result["targets"][target["relative"]]["current_sha256"] = target["generated_hash"]
    except Exception as exc:  # fault injection deliberately exercises this boundary
        result["conflicts"].append(f"replacement failed: {type(exc).__name__}")
        if not replaced_targets:
            result["cleanup_failed"] = _cleanup_paths(root, list(prepared.values()), created_dirs)
            result.update(status="refused", transaction="no_write")
            return result
        for target in reversed(replaced_targets):
            relative = target["relative"]
            try:
                hook = hooks.get("before_restore")
                if hook:
                    hook(relative)
                existed, _, current_hash = _file_state(target["path"])
                if not existed or current_hash != target["generated_hash"]:
                    raise SetupError("current file no longer matches generated hash; refusing to overwrite concurrent change")
                if target["existed"]:
                    restore_temp = _prepare_temp(target["path"], target["preimage"])
                    try:
                        os.replace(restore_temp, target["path"])
                    finally:
                        restore_temp.unlink(missing_ok=True)
                else:
                    target["path"].unlink()
                restored_exists, _, restored_hash = _file_state(target["path"])
                if restored_exists != target["existed"] or restored_hash != target["pre_hash"]:
                    raise OSError("compensating restore validation failed")
                result["restored"].append(relative)
                result["targets"][relative]["current_sha256"] = restored_hash
            except Exception as restore_exc:
                result["restore_failed"].append(relative)
                try:
                    _, _, current_hash = _file_state(target["path"])
                except (OSError, SetupError):
                    current_hash = None
                result["targets"][relative]["current_sha256"] = current_hash
                if target["existed"]:
                    step = (
                        f"从可信备份恢复 `{relative}` 到 preimage SHA-256 {target['pre_hash']}；"
                        f"恢复前核对 current SHA-256 {current_hash or 'ABSENT'}。"
                    )
                else:
                    step = (
                        f"仅当 `{relative}` 的 current SHA-256 仍为 {current_hash or 'ABSENT'} "
                        "且确认无并发改动时删除该本次新建文件。"
                    )
                result["recovery_steps"].append(step)
                result["conflicts"].append(f"restore failed for {relative}: {type(restore_exc).__name__}")

        result["cleanup_failed"] = _cleanup_paths(root, list(prepared.values()), created_dirs)
        if result["restore_failed"]:
            result.update(status="failed", transaction="partial_write")
        else:
            result.update(status="failed", transaction="rolled_back")
        return result

    result["cleanup_failed"] = _cleanup_paths(root, list(prepared.values()), [])
    result.update(status="ok", transaction="committed")
    return result


def _read_project_rules_sources(values: list[str]) -> tuple[tuple[str, bytes], ...]:
    sources: list[tuple[str, bytes]] = []
    for value in values:
        parts = value.split("::", 1)
        if len(parts) != 2:
            raise SetupError("project-rules-file must be <canonical-skill>::<path>")
        skill = _normalize_project_rules_skill(parts[0])
        path = Path(parts[1]).resolve(strict=False)
        if not path.is_file():
            raise SetupError(f"project rules file is not a regular file: {path}")
        skill_name = skill.split(":", 1)[1]
        if (
            path.name != "project-rules.md"
            or path.parent.name != "assets"
            or path.parent.parent.name != skill_name
            or path.parent.parent.parent.name != "skills"
        ):
            raise SetupError(
                "project rules file must be the canonical "
                "skills/<skill>/assets/project-rules.md asset"
            )
        sources.append((skill, path.read_bytes()))
    return tuple(sources)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Sacha Project Integration files safely.")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--agents-path", default="AGENTS.md")
    parser.add_argument("--workflow-rule-path", default="docs/workflow-rule.md")
    parser.add_argument("--spec-base-kind", choices=tuple(sorted(SPEC_BASE_KINDS)))
    parser.add_argument(
        "--spec-base",
        help="Spec base input; setup derives the Spec storage root in its plan child directory",
    )
    parser.add_argument("--human-guide")
    parser.add_argument("--documentation-policy", choices=tuple(sorted(DOCUMENTATION_POLICIES)))
    parser.add_argument("--documentation-root-kind", choices=tuple(sorted(DOCUMENTATION_ROOT_KINDS)))
    parser.add_argument(
        "--documentation-root",
        help="Exact Project Documentation root; setup preserves it without appending directories",
    )
    parser.add_argument(
        "--documentation-write-authorization",
        choices=tuple(sorted(DOCUMENTATION_WRITE_AUTHORIZATIONS)),
    )
    parser.add_argument("--rule-path", action="append", default=[])
    parser.add_argument("--skill-root", action="append", default=[])
    parser.add_argument("--scm-provider", choices=("git", "svn", "none"))
    parser.add_argument("--rule-binding", action="append", default=[])
    parser.add_argument("--ignore-rule-candidate", action="append", default=[])
    parser.add_argument("--skill-root-binding", action="append", default=[])
    parser.add_argument("--capability-binding", action="append", default=[])
    parser.add_argument("--reconcile-capabilities", action="store_true")
    parser.add_argument("--pi-model-binding", action="append", default=[])
    parser.add_argument("--clear-pi-model-bindings", action="store_true")
    parser.add_argument("--unavailable-capability-skill", action="append", default=[])
    parser.add_argument("--assess-project-skills", action="store_true")
    parser.add_argument("--visible-project-skill", action="append", default=[])
    parser.add_argument("--project-skill-evidence", action="append", default=[])
    parser.add_argument("--manage-agents", action="store_true")
    parser.add_argument("--expected-agents-sha256")
    parser.add_argument("--replace-unmanaged-workflow", action="store_true")
    parser.add_argument("--expected-workflow-sha256")
    parser.add_argument("--confirmed-planned-delta-sha256")
    parser.add_argument(
        "--project-rules-file",
        action="append",
        default=[],
        metavar="CANONICAL-SKILL::PATH",
    )
    parser.add_argument("--remove-project-rules-skill", action="append", default=[])
    parser.add_argument("--replace-legacy-project-rules", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    try:
        project_rules_sources = _read_project_rules_sources(args.project_rules_file)
        remove_project_rules_skills = tuple(
            _normalize_project_rules_skill(item)
            for item in args.remove_project_rules_skill
        )
    except (OSError, UnicodeError, SetupError) as exc:
        result = _base_result("<invalid>", args.agents_path, args.manage_agents)
        message = str(exc) if isinstance(exc, (SetupError, UnicodeError)) else f"filesystem operation failed: {type(exc).__name__}"
        result.update(status="refused", transaction="no_write", conflicts=[message])
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    config = SetupConfig(
        project_root=args.project_root,
        agents_path=args.agents_path,
        workflow_rule_path=args.workflow_rule_path,
        spec_base_kind=args.spec_base_kind,
        spec_base=args.spec_base,
        human_guide=args.human_guide,
        documentation_policy=args.documentation_policy,
        documentation_root_kind=args.documentation_root_kind,
        documentation_root=args.documentation_root,
        documentation_write_authorization=args.documentation_write_authorization,
        rule_paths=tuple(args.rule_path),
        skill_roots=tuple(args.skill_root),
        scm_provider=args.scm_provider,
        rule_bindings=tuple(args.rule_binding),
        ignored_rule_candidates=tuple(args.ignore_rule_candidate),
        skill_root_bindings=tuple(args.skill_root_binding),
        capability_bindings=tuple(args.capability_binding),
        reconcile_capabilities=args.reconcile_capabilities,
        pi_model_bindings=tuple(args.pi_model_binding),
        clear_pi_model_bindings=args.clear_pi_model_bindings,
        unavailable_capability_skills=tuple(args.unavailable_capability_skill),
        assess_project_skills=args.assess_project_skills,
        visible_project_skills=tuple(args.visible_project_skill),
        project_skill_evidence=tuple(args.project_skill_evidence),
        manage_agents=args.manage_agents,
        expected_agents_sha256=args.expected_agents_sha256,
        replace_unmanaged_workflow=args.replace_unmanaged_workflow,
        expected_workflow_sha256=args.expected_workflow_sha256,
        project_rules_sources=project_rules_sources,
        remove_project_rules_skills=remove_project_rules_skills,
        replace_legacy_project_rules=args.replace_legacy_project_rules,
    )
    result = run_setup(
        config,
        write=args.write,
        confirmed_planned_delta_sha256=args.confirmed_planned_delta_sha256,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] in {"ready", "ok"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
