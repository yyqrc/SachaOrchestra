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
AGENTS_BEGIN = "<!-- BEGIN SACHA ORCHESTRA MANAGED BLOCK -->"
AGENTS_END = "<!-- END SACHA ORCHESTRA MANAGED BLOCK -->"
CONVENTIONAL_SKILL_ROOTS = (".agents/skills", ".codex/skills", ".claude/skills")
CONVENTIONAL_RULE_NAMES = ("TEAM.md", "PROJECT.md", "EditorTools.md")
LOAD_POLICIES = {"always", "role-entry", "on-demand"}
CAPABILITY_LOAD_POLICIES = {"on-demand", "after-write-authorization", "review-only", "risk-matched"}
SKILL_ROOT_DECISIONS = {"authority", "mirror", "independent", "ignore"}
MAX_DISCOVERY_FILES = 256
MAX_DISCOVERY_FILE_BYTES = 256 * 1024
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
    artifact_root: str = "docs/plans/<YYYY-MM-DD>-<short-slug>/"
    human_guide: str | None = None
    rule_paths: tuple[str, ...] = ()
    skill_roots: tuple[str, ...] = ()
    scm_provider: str | None = None
    rule_bindings: tuple[str, ...] = ()
    ignored_rule_candidates: tuple[str, ...] = ()
    skill_root_bindings: tuple[str, ...] = ()
    capability_bindings: tuple[str, ...] = ()
    reconcile_capabilities: bool = False
    unavailable_capability_skills: tuple[str, ...] = ()
    manage_agents: bool = False
    expected_agents_sha256: str | None = None
    replace_unmanaged_workflow: bool = False
    expected_workflow_sha256: str | None = None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _file_state(path: Path) -> tuple[bool, bytes | None, str | None]:
    if not path.exists():
        return False, None, None
    if not path.is_file():
        raise SetupError("target path exists but is not a regular file")
    data = path.read_bytes()
    return True, data, sha256_bytes(data)


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


def _normalize_pattern(raw: str, label: str) -> str:
    normalized = raw.replace("\\", "/").strip()
    trailing_slash = normalized.endswith("/")
    pure = PurePosixPath(normalized)
    if (
        not normalized
        or pure.is_absolute()
        or re.match(r"^[A-Za-z]:", normalized)
        or normalized.startswith("//")
        or any(part in {"", ".", ".."} for part in pure.parts)
        or "\n" in normalized
        or "\r" in normalized
    ):
        raise SetupError(f"{label} must be a normalized relative project pattern")
    result = pure.as_posix()
    return result + "/" if trailing_slash and not result.endswith("/") else result


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
        if len(parts) not in {2, 3}:
            raise SetupError("capability_binding must be <capability-id>::<canonical-skill>[::<load-policy>]")
        capability_id = _normalize_capability_id(parts[0])
        skill = _normalize_skill_identity(parts[1])
        policy = "on-demand" if len(parts) == 2 else parts[2]
        if policy != policy.strip() or policy != policy.casefold():
            raise SetupError("capability load policy must already be canonical lowercase without surrounding whitespace")
        if policy not in CAPABILITY_LOAD_POLICIES:
            raise SetupError("capability load policy must be on-demand, after-write-authorization, review-only or risk-matched")
        if capability_id in parsed:
            raise SetupError(f"duplicate capability binding: {capability_id}")
        parsed[capability_id] = {"id": capability_id, "skill": skill, "load_policy": policy}
    return tuple(parsed[key] for key in sorted(parsed))


def _normalize_unavailable_skills(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted({_normalize_skill_identity(value) for value in values}))


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


def _extract_relative_references(text: str) -> tuple[str, ...]:
    references: set[str] = set()
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
        references.add(normalized.rstrip("/"))
    return tuple(sorted(references))


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


def _parse_existing_project_values(data: bytes) -> dict[str, object]:
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

    rule_bindings = []
    rule_section = re.search(r"(?ms)^### Rule bindings\s*\n(.*?)(?=^### )", text)
    if rule_section:
        for path, purpose, policy in re.findall(
            r"(?m)^- `([^`]+)`：purpose = (.*?)；load policy = `([^`]+)`\r?$",
            rule_section.group(1),
        ):
            rule_bindings.append({"path": path, "purpose": purpose, "load_policy": policy})
    ignored_rule_candidates = []
    ignored_rule_section = re.search(r"(?ms)^### Ignored rule candidates\s*\n(.*?)(?=^### )", text)
    if ignored_rule_section:
        ignored_rule_candidates = re.findall(r"(?m)^- `([^`]+)`\r?$", ignored_rule_section.group(1))

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
            match = re.fullmatch(
                r"- `([^`]+)` -> `([^`]+)`；load policy = `([^`]+)`；fallback = `discoverable-domain-skill-or-native-role`",
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
    return {
        "schema_version": schema_version,
        "agents_path": backtick_value("Project AGENTS"),
        "artifact_root": backtick_value("Artifact 根模式"),
        "human_guide": backtick_value("Human Guide"),
        "scm_provider": scm_provider,
        "rule_bindings": tuple(rule_bindings),
        "ignored_rule_candidates": tuple(ignored_rule_candidates),
        "skill_root_bindings": tuple(skill_root_bindings),
        "capability_bindings": tuple(capability_bindings),
        "capability_dirty": tuple(capability_dirty),
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
    for raw in _extract_relative_references(agents_text):
        try:
            referenced, referenced_rel = _normalize_relative_path(root, raw, "Project AGENTS reference")
        except SetupError:
            continue
        if referenced_rel.endswith(".md") and referenced.exists():
            add_rule(referenced, required=False, source="project_agents_reference", depth=1)
        if referenced.is_dir() and "skills" in PurePosixPath(referenced_rel).parts:
            add_skill_root(referenced, required=False, source="project_agents_reference")
        elif referenced_rel.endswith("/SKILL.md") and referenced.is_file():
            add_skill_root(referenced.parent.parent, required=False, source="project_agents_reference")

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
        for raw in _extract_relative_references(first_text):
            candidates = [first_path.parent / raw, root / raw]
            referenced = next((item for item in candidates if item.exists()), candidates[0])
            try:
                resolved, referenced_rel = _relative_existing_path(root, referenced)
            except SetupError:
                continue
            if referenced_rel == human_guide:
                add_rule(resolved, required=False, source="human_guide_reference", depth=2)
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
                "suggested_purpose": "human guide reference",
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
    for provider, marker in (("git", ".git"), ("svn", ".svn")):
        marker_path = root / marker
        if (provider == "git" and marker_path.exists()) or (provider == "svn" and marker_path.is_dir()):
            scm_evidence.append({"provider": provider, "source": marker})
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
    artifact_root: str,
    human_guide: str | None,
    discovery: Mapping[str, object],
    capability_bindings: tuple[dict[str, str], ...],
) -> bytes:
    guide = (
        f"`{human_guide}`（只读引用；setup 不管理正文）"
        if human_guide
        else "未配置"
    )
    scm = discovery["scm"]
    scm_provider = scm["provider"] or "未决"
    evidence = [item["source"] for item in scm["evidence"] if item["provider"] == scm["provider"]]
    scm_evidence = "、".join(f"`{item}`" for item in evidence) or "无"
    rule_lines = [
        f"- `{item['path']}`：purpose = {item['purpose']}；load policy = `{item['load_policy']}`"
        for item in discovery["rule_bindings"]
    ] or ["- 无"]
    ignored_rule_lines = [
        f"- `{item}`" for item in discovery["ignored_rule_candidates"]
    ] or ["- 无"]
    skill_lines = []
    for item in discovery["skill_root_bindings"]:
        suffix = f"；authority = `{item['authority']}`" if item["decision"] == "mirror" else ""
        skill_lines.append(f"- `{item['path']}`：`{item['decision']}`{suffix}")
    if not skill_lines:
        skill_lines.append("- 无")
    capability_lines = [
        f"- `{item['id']}` -> `{item['skill']}`；load policy = `{item['load_policy']}`；fallback = `discoverable-domain-skill-or-native-role`"
        for item in capability_bindings
    ] or ["- 无"]
    unresolved_lines = [
        f"- {item.get('kind', 'unknown')}：`{item.get('path', '.')}`（{item.get('reason', 'unresolved')}）"
        for item in discovery["unresolved"]
    ]
    conflict_lines = [
        f"- {item.get('kind', 'unknown')}：{item.get('reason', 'conflict')}"
        for item in discovery["conflicts"]
    ]
    if not unresolved_lines:
        unresolved_lines.append("- 无")
    if not conflict_lines:
        conflict_lines.append("- 无")
    text = f"""{GENERATOR_MARKER}
{SCHEMA_MARKER}
# Sacha Orchestra 项目接入

本文件由 `sacha-orchestra:setup-project` 幂等管理。项目接入值可刷新；通用合同只引用 canonical 权威，不在此复制。

## 项目值

- Project AGENTS：`{agents_path}`
- Workflow rule：`{workflow_rule_path}`
- Artifact 根模式：`{artifact_root}`
- Human Guide：{guide}

## 项目绑定

### SCM

- provider = `{scm_provider}`
- evidence source = {scm_evidence}

### Rule bindings

{chr(10).join(rule_lines)}

### Ignored rule candidates

{chr(10).join(ignored_rule_lines)}

### Skill roots

{chr(10).join(skill_lines)}

### Capability bindings

{chr(10).join(capability_lines)}

### Unresolved

{chr(10).join(unresolved_lines)}

### Conflicts

{chr(10).join(conflict_lines)}

### Fallback

- Binding、provider 或能力未配置时，回退到 Project AGENTS、可发现的 Domain Skill 和当前 Role 原生流程；不得阻断合法的 Direct 或 Executor-only 路线。
- 已配置 capability mapping 时只把 canonical Skill 关系作为按需定位输入；若同一 Skill 已被当前 context 选中则复用并去重，仍须读取对应 Domain Skill 正文。

## Canonical locators

- Skills：`sacha-orchestra:planner`、`sacha-orchestra:executor`、`sacha-orchestra:reviewer`、`sacha-orchestra:manager`、`sacha-orchestra:feedback`、`sacha-orchestra:clarify`
- Workflow Core：plugin `core/workflow-contract.md`
- Artifact Protocol：plugin `core/artifact-protocol.md`
- Codex Runtime Adapter：plugin `adapters/codex/runtime-adapter.md`

项目命令、领域知识、证据等级和验证规则仍由 Project AGENTS 或 Domain Skill 所有。
"""
    return text.encode("utf-8")


def render_agents_block(workflow_rule_path: str) -> bytes:
    text = f"""{AGENTS_BEGIN}
## Sacha Orchestra 接入

- 普通局部任务不因 plugin 存在而强制进入 Sacha；直接遵循本 Project AGENTS。
- Sacha 入口事实成立后读取 `{workflow_rule_path}` 获取项目绑定；入口、Gate 和 Role 路由仍以 plugin canonical contract 为准。
{AGENTS_END}"""
    return text.encode("utf-8")


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
        "agents_block": {"path": agents_rel, "enabled": manage_agents, "action": "disabled"},
        "changed_files": [],
        "replaced": [],
        "restored": [],
        "restore_failed": [],
        "conflicts": [],
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
        existing_values: dict[str, object] = {}
        if workflow_path.is_file():
            existing_values = _parse_existing_project_values(workflow_path.read_bytes())
        effective_agents_path = config.agents_path
        if config.agents_path == "AGENTS.md" and existing_values.get("agents_path"):
            effective_agents_path = str(existing_values["agents_path"])
        agents_path, agents_rel = _normalize_relative_path(root, effective_agents_path, "agents_path")
        effective_artifact_root = config.artifact_root
        if config.artifact_root == "docs/plans/<YYYY-MM-DD>-<short-slug>/" and existing_values.get("artifact_root"):
            effective_artifact_root = str(existing_values["artifact_root"])
        artifact_root = _normalize_pattern(effective_artifact_root, "artifact_root")
        human_guide = None
        effective_human_guide = config.human_guide or existing_values.get("human_guide")
        if effective_human_guide:
            _, human_guide = _normalize_relative_path(root, str(effective_human_guide), "human_guide")
        expected_agents = _normalize_hash(config.expected_agents_sha256, "expected_agents_sha256")
        expected_workflow = _normalize_hash(config.expected_workflow_sha256, "expected_workflow_sha256")
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
        unavailable_skills = _normalize_unavailable_skills(config.unavailable_capability_skills)
        existing_capabilities = tuple(existing_values.get("capability_bindings", ()))
        capability_dirty = tuple(str(item) for item in existing_values.get("capability_dirty", ()))
        effective_capabilities, capability_reconciliation, capability_blocked = _reconcile_capabilities(
            existing_capabilities,
            capability_bindings,
            reconcile=config.reconcile_capabilities,
            unavailable_skills=unavailable_skills,
            dirty_entries=capability_dirty,
        )
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
    result["capability_reconciliation"] = capability_reconciliation
    discovery_blocked = discovery["status"] != "complete"
    targets: list[dict[str, object]] = []
    try:
        workflow_existed, workflow_preimage, workflow_hash = _file_state(workflow_path)
        workflow_generated = render_workflow_rule(
            agents_rel, workflow_rel, artifact_root, human_guide, discovery, effective_capabilities
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
            agents_generated = _merge_agents(agents_preimage, render_agents_block(workflow_rel))
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
    if discovery_blocked or capability_blocked:
        decision_conflicts: list[str] = []
        if discovery["status"] == "incomplete":
            decision_conflicts.append("Project Binding discovery or decisions are incomplete")
        if discovery["conflicts"]:
            decision_conflicts.append("Project Binding conflicts require explicit resolution")
        if capability_blocked:
            decision_conflicts.append("managed capability data is invalid; explicit reconciliation is required")
        result.update(status="refused", transaction="no_write", conflicts=decision_conflicts)
        return result
    if not write:
        return result
    if not targets:
        result.update(status="ok", transaction="no_changes")
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Sacha Project Integration files safely.")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--agents-path", default="AGENTS.md")
    parser.add_argument("--workflow-rule-path", default="docs/workflow-rule.md")
    parser.add_argument("--artifact-root", default="docs/plans/<YYYY-MM-DD>-<short-slug>/")
    parser.add_argument("--human-guide")
    parser.add_argument("--rule-path", action="append", default=[])
    parser.add_argument("--skill-root", action="append", default=[])
    parser.add_argument("--scm-provider", choices=("git", "svn", "none"))
    parser.add_argument("--rule-binding", action="append", default=[])
    parser.add_argument("--ignore-rule-candidate", action="append", default=[])
    parser.add_argument("--skill-root-binding", action="append", default=[])
    parser.add_argument("--capability-binding", action="append", default=[])
    parser.add_argument("--reconcile-capabilities", action="store_true")
    parser.add_argument("--unavailable-capability-skill", action="append", default=[])
    parser.add_argument("--manage-agents", action="store_true")
    parser.add_argument("--expected-agents-sha256")
    parser.add_argument("--replace-unmanaged-workflow", action="store_true")
    parser.add_argument("--expected-workflow-sha256")
    parser.add_argument("--write", action="store_true")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    config = SetupConfig(
        project_root=args.project_root,
        agents_path=args.agents_path,
        workflow_rule_path=args.workflow_rule_path,
        artifact_root=args.artifact_root,
        human_guide=args.human_guide,
        rule_paths=tuple(args.rule_path),
        skill_roots=tuple(args.skill_root),
        scm_provider=args.scm_provider,
        rule_bindings=tuple(args.rule_binding),
        ignored_rule_candidates=tuple(args.ignore_rule_candidate),
        skill_root_bindings=tuple(args.skill_root_binding),
        capability_bindings=tuple(args.capability_binding),
        reconcile_capabilities=args.reconcile_capabilities,
        unavailable_capability_skills=tuple(args.unavailable_capability_skill),
        manage_agents=args.manage_agents,
        expected_agents_sha256=args.expected_agents_sha256,
        replace_unmanaged_workflow=args.replace_unmanaged_workflow,
        expected_workflow_sha256=args.expected_workflow_sha256,
    )
    result = run_setup(config, write=args.write)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] in {"ready", "ok"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
