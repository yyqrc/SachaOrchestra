#!/usr/bin/env python3
"""Validate and atomically create or update project documentation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


INTEGRATION_GENERATOR = "<!-- Generator: sacha-orchestra:setup-project -->"
INTEGRATION_SCHEMA_VERSIONS = {3, 4}
INPUT_SCHEMA_VERSION = "1"
DOCUMENT_TYPES = {"change-archive", "system-guide", "project-context", "roadmap"}
TRIGGERS = {"human-request", "goal-closeout"}
POLICIES = {"disabled", "on-request", "required-at-closeout"}
ROOT_KINDS = {"project-relative", "external-absolute"}
WRITE_AUTHORIZATIONS = {"bounded-closeout", "per-write-confirmation"}
TEMPLATE_PATH_KINDS = {"project-relative", "external-absolute"}
CANONICAL_CHANGE_ARCHIVE_PROFILE = "canonical-change-archive-v1"
CANONICAL_CHANGE_ARCHIVE_TEMPLATE = (
    Path(__file__).resolve().parents[1] / "assets" / "change-archive.md"
)
CANONICAL_SYSTEM_GUIDE_PROFILE = "canonical-system-guide-v1"
CANONICAL_SYSTEM_GUIDE_TEMPLATE = (
    Path(__file__).resolve().parents[1] / "assets" / "system-guide.md"
)
CANONICAL_ROADMAP_PROFILE = "canonical-roadmap-v1"
CANONICAL_ROADMAP_TEMPLATE = (
    Path(__file__).resolve().parents[1] / "assets" / "roadmap.md"
)
BUNDLED_GENERATION_POLICY = {
    "minimum_section_count": 0,
    "minimum_word_count": 0,
    "output_gate": (
        "不得残留花括号占位符",
        "不得残留模板生成说明",
        "不得存在无实质正文的标题",
    ),
}
ROADMAP_FILE_NAME = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]{0,63}-roadmap\.md$"
)
ROADMAP_FILE_PATTERN = "<YYYY-MM-DD>-<short-slug>-roadmap.md"
ROADMAP_REQUIRED_HEADINGS = (
    "目标与完成形态",
    "当前状态",
    "路线原则",
    "阶段路线",
    "Spec 映射",
    "决策前沿",
    "Unknown",
    "排除范围",
    "主要项目位置与依据",
)
BUNDLED_REQUIRED_TOPICS = {
    "change-archive": ("背景或触发原因", "目标", "实际结果与范围", "关键约束或根因", "验证结论与未验证边界"),
    "system-guide": ("系统用途与边界", "主数据流或执行流", "权威基准", "当前限制或验证边界"),
    "roadmap": ROADMAP_REQUIRED_HEADINGS,
}
TEMPLATE_PROFILE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
TEMPLATE_VERSION = re.compile(r"^[1-9][0-9]*$")
MAX_TITLE_CHARS = 120
MAX_SECTION_CHARS = 8000
MAX_DOCUMENT_CHARS = 24000
MAX_DOCUMENT_BYTES = 64 * 1024
MAX_CHANGE_ARCHIVE_TEMPLATE_BYTES = 64 * 1024
MAX_CONTEXT_ENTRIES = 32
CONTEXT_FILE_NAME = "CONTEXT.md"
CONTEXT_BEGIN = "<!-- BEGIN SACHA PROJECT CONTEXT: terminology -->"
CONTEXT_END = "<!-- END SACHA PROJECT CONTEXT: terminology -->"
CONTEXT_HEADING = "## 项目术语（Sacha 托管）"
CONTEXT_FIELDS = (
    ("definition", "定义"),
    ("excluded_meanings", "明确排除"),
    ("scope", "适用边界"),
    ("evidence", "依据"),
    ("consumers", "任务外消费者"),
)
SECTIONS = (
    ("conclusion", "结论"),
    ("quick_start", "如何使用 / 最短路径"),
    ("behavior_and_impact", "行为与影响"),
    ("problem_and_cause", "问题与原因"),
    ("solution_and_tradeoffs", "方案与取舍"),
    ("implementation", "实现说明"),
    ("validation_and_limits", "验证与限制"),
    ("ai_handoff", "AI 接力附录"),
)
INTERNAL_REFERENCES = (
    re.compile(r"(?<![A-Za-z0-9_.-])\.codex(?:[\\/]|$)", re.IGNORECASE),
    re.compile(
        r"(?<![A-Za-z0-9_.-])(?:spec|execution-report|review)\.md\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?<![A-Za-z0-9_.-])(?:plugins[\\/])?cache(?:[\\/]|$)",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:source_thread_id|thread_id)\b", re.IGNORECASE),
    re.compile(r"<codex_delegation\b", re.IGNORECASE),
    re.compile(r"\bSO-[A-Z0-9][A-Z0-9-]{5,}\b"),
    re.compile(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
        r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        re.IGNORECASE,
    ),
    re.compile(r"(?:^|[\s`'\"(\[{=:;,])(?:[A-Za-z]:[\\/]|\\\\)", re.IGNORECASE),
)
ROADMAP_FORBIDDEN_REFERENCES = tuple(
    pattern
    for index, pattern in enumerate(INTERNAL_REFERENCES)
    if index not in {1, len(INTERNAL_REFERENCES) - 1}
)


class DocumentError(RuntimeError):
    """A safe refusal that must not create or overwrite a publication document."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\s*\r?\n(.*?)(?=^### |\Z)",
        text,
    )
    if match is None:
        raise DocumentError(f"confirmed Project Integration is missing {heading}")
    return match.group(1).strip()


def _optional_section(text: str, heading: str) -> str | None:
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\s*\r?\n(.*?)(?=^### |\Z)",
        text,
    )
    return None if match is None else match.group(1).strip()


def _field(section: str, label: str) -> str:
    match = re.search(rf"(?m)^- {re.escape(label)} = `([^`\r\n]+)`\r?$", section)
    if match is None:
        raise DocumentError(f"Project documentation field is missing: {label}")
    return match.group(1)


def _compact_root(root: str) -> tuple[str, str]:
    external = bool(
        re.match(r"^(?:[A-Za-z]:[\\/]|\\\\|//|/)", root)
    )
    return (
        ("external-absolute", "non-portable")
        if external
        else ("project-relative", "portable")
    )


def _expected_context_path(text: str) -> str:
    match = re.search(r"(?m)^- Spec：`([^`]+)`\r?$", text)
    if match is None:
        raise DocumentError("Project Integration Spec storage root is missing")
    spec_storage_root = match.group(1).rstrip("/\\")
    parts = tuple(part for part in re.split(r"[/\\]+", spec_storage_root) if part)
    if not parts or parts[-1].casefold() != "plan":
        raise DocumentError("Project Integration Spec storage root must end in plan")
    separator = "\\" if re.match(r"^(?:[A-Za-z]:\\|\\\\)", spec_storage_root) else "/"
    spec_base = re.sub(r"[/\\][^/\\]+$", "", spec_storage_root)
    return f"{spec_base}{separator}{CONTEXT_FILE_NAME}"


def _template_catalog_binding(text: str) -> dict[str, Any] | None:
    catalogs = re.findall(
        r"(?m)^- document-template catalog：path kind = `([^`]+)`；"
        r"path = `([^`]+)`(?:；manifest sha256 = `[^`]+`)?\r?$",
        text,
    )
    if not catalogs:
        return None
    if len(catalogs) != 1:
        raise DocumentError("Project Integration template catalog binding is duplicated")
    path_kind, path = catalogs[0]
    if path_kind not in TEMPLATE_PATH_KINDS:
        raise DocumentError("template catalog path kind is invalid")
    return {
        "path_kind": path_kind,
        "path": path,
    }


def _roadmap_storage_binding(text: str) -> dict[str, str] | None:
    root_matches = re.findall(r"(?m)^- Roadmap：`([^`]+)`\r?$", text)
    file_matches = re.findall(r"(?m)^- Roadmap 文件：`([^`]+)`\r?$", text)
    if not root_matches and not file_matches:
        return None
    if len(root_matches) != 1:
        raise DocumentError("Project Integration Roadmap root is duplicated")
    if len(file_matches) != 1:
        raise DocumentError("Project Integration Roadmap file pattern is missing or duplicated")
    if file_matches[0] != ROADMAP_FILE_PATTERN:
        raise DocumentError("Project Integration Roadmap file pattern is unsupported")
    root = root_matches[0]
    root_kind, portability = _compact_root(root)
    return {
        "root_kind": root_kind,
        "root": root,
        "portability": portability,
        "file_pattern": file_matches[0],
    }


def _attach_context_path(
    text: str,
    documentation: dict[str, Any],
) -> dict[str, Any]:
    expected = _expected_context_path(text)
    match = re.search(r"(?m)^- 项目 Context：`([^`]+)`(?:（[^\r\n]*）)?\r?$", text)
    if match is not None and match.group(1) != expected:
        raise DocumentError("Project Context path is inconsistent with Spec base")
    return {
        **documentation,
        "context_path": expected,
        "roadmap_storage": _roadmap_storage_binding(text),
    }


def parse_project_integration(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DocumentError("Project Integration must be UTF-8") from exc
    schema_versions = re.findall(r"<!-- Schema Version: ([0-9]+) -->", text)
    if (
        INTEGRATION_GENERATOR not in text
        or len(schema_versions) != 1
        or int(schema_versions[0]) not in INTEGRATION_SCHEMA_VERSIONS
    ):
        raise DocumentError(
            "Project Integration is not a confirmed managed Schema v3/v4 file"
        )
    unresolved = _optional_section(text, "### Unresolved")
    if unresolved not in {None, "- 无"}:
        raise DocumentError("Project Integration has unresolved decisions")
    conflicts = _optional_section(text, "### Conflicts")
    if conflicts not in {None, "- 无"}:
        raise DocumentError("Project Integration has conflicts")

    compact = re.search(
        r"(?m)^- 项目文档：`([^`]+)`"
        r"(?: -> `([^`]+)`；write = `([^`]+)`)?\r?$",
        text,
    )
    if compact:
        policy, root, authorization = compact.groups()
        if policy == "disabled":
            if _template_catalog_binding(text) is not None:
                raise DocumentError("disabled Project documentation must not bind a template")
            return _attach_context_path(text, {
                "policy": policy,
                "root_kind": None,
                "root": None,
                "portability": "not-applicable",
                "write_authorization": None,
            })
        if root is None or authorization is None:
            raise DocumentError("enabled Project documentation is incomplete")
        root_kind, portability = _compact_root(root)
        result = {
            "policy": policy,
            "root_kind": root_kind,
            "root": root,
            "portability": portability,
            "write_authorization": authorization,
        }
        if policy not in POLICIES or policy == "disabled":
            raise DocumentError("Project documentation policy is invalid")
        if authorization not in WRITE_AUTHORIZATIONS:
            raise DocumentError("Project documentation write authorization is invalid")
        template_catalog = _template_catalog_binding(text)
        if template_catalog is not None:
            result["template_catalog"] = template_catalog
        return _attach_context_path(text, result)

    documentation = _section(text, "### Project documentation")
    document_types = re.search(
        r"(?m)^- document types = `change-archive`、`system-guide`(?:、`project-context`)?\r?$",
        documentation,
    )
    if document_types is None:
        raise DocumentError("Project documentation document types are invalid")
    result: dict[str, str | None] = {
        "policy": _field(documentation, "policy"),
        "root_kind": _field(documentation, "root kind"),
        "root": _field(documentation, "root"),
        "portability": _field(documentation, "portability"),
        "write_authorization": _field(documentation, "write authorization"),
    }
    policy = result["policy"]
    if policy not in POLICIES:
        raise DocumentError("Project documentation policy is invalid")
    if policy == "disabled":
        if any(
            result[key] != expected
            for key, expected in (
                ("root_kind", "none"),
                ("root", "none"),
                ("portability", "not-applicable"),
                ("write_authorization", "none"),
            )
        ):
            raise DocumentError("disabled documentation contains active root or authorization")
        if _template_catalog_binding(text) is not None:
            raise DocumentError("disabled Project documentation must not bind a template")
        return _attach_context_path(text, result)
    if result["root_kind"] not in ROOT_KINDS:
        raise DocumentError("Project Documentation root kind is invalid")
    if result["write_authorization"] not in WRITE_AUTHORIZATIONS:
        raise DocumentError("Project documentation write authorization is invalid")
    if result["root"] in {None, "none"}:
        raise DocumentError("enabled Project Documentation root is missing")
    expected_portability = (
        "portable" if result["root_kind"] == "project-relative" else "non-portable"
    )
    if result["portability"] != expected_portability:
        raise DocumentError("Project documentation portability is inconsistent")
    template_catalog = _template_catalog_binding(text)
    if template_catalog is not None:
        result["template_catalog"] = template_catalog
    return _attach_context_path(text, result)


def _normalized_relative_path(raw: Any, label: str) -> PurePosixPath:
    if not isinstance(raw, str):
        raise DocumentError(f"{label} must be text")
    normalized = raw.replace("\\", "/").strip()
    pure = PurePosixPath(normalized)
    if (
        not normalized
        or pure.is_absolute()
        or re.match(r"^[A-Za-z]:", normalized)
        or normalized.startswith("//")
        or any(part in {"", ".", ".."} for part in pure.parts)
        or any(token in normalized for token in ("\n", "\r", "`"))
    ):
        raise DocumentError(f"{label} must be a normalized relative path")
    return pure


def _resolve_document_root(
    project_root: Path,
    documentation: dict[str, Any],
) -> Path:
    if documentation["policy"] == "disabled":
        raise DocumentError("Project documentation is disabled")
    raw = str(documentation["root"])
    kind = documentation["root_kind"]
    if kind == "project-relative":
        pure = _normalized_relative_path(raw, "Project Documentation root")
        root = (project_root / Path(*pure.parts)).resolve(strict=False)
        try:
            root.relative_to(project_root)
        except ValueError as exc:
            raise DocumentError("Project Documentation root escapes project root") from exc
    elif kind == "external-absolute":
        candidate = Path(raw)
        if not candidate.is_absolute():
            raise DocumentError("external Project Documentation root is not absolute")
        lexical = Path(os.path.abspath(raw))
        resolved = candidate.resolve(strict=False)
        if lexical == Path(lexical.anchor) or resolved == Path(resolved.anchor):
            raise DocumentError("external Project Documentation root must not be a drive or share root")
        try:
            resolved.relative_to(project_root)
        except ValueError:
            pass
        else:
            raise DocumentError(
                "Project Documentation root inside project must be project-relative"
            )
        root = resolved
    else:
        raise DocumentError("Project Documentation root kind is invalid")
    try:
        if not root.is_dir():
            raise DocumentError("Project Documentation root is absent or unreachable")
    except OSError as exc:
        raise DocumentError("Project Documentation root is unreachable") from exc
    return root


def _resolve_roadmap_root(
    project_root: Path,
    documentation: dict[str, Any],
) -> Path:
    storage = documentation.get("roadmap_storage")
    if not isinstance(storage, dict):
        raise DocumentError("Project Integration Roadmap root is missing")
    raw = str(storage.get("root"))
    kind = storage.get("root_kind")
    if kind == "project-relative":
        pure = _normalized_relative_path(raw, "Roadmap root")
        root = (project_root / Path(*pure.parts)).resolve(strict=False)
        try:
            root.relative_to(project_root)
        except ValueError as exc:
            raise DocumentError("Roadmap root escapes project root") from exc
    elif kind == "external-absolute":
        candidate = Path(raw)
        if not candidate.is_absolute():
            raise DocumentError("external Roadmap root is not absolute")
        lexical = Path(os.path.abspath(raw))
        root = candidate.resolve(strict=False)
        if lexical == Path(lexical.anchor) or root == Path(root.anchor):
            raise DocumentError("external Roadmap root must not be a drive or share root")
        try:
            root.relative_to(project_root)
        except ValueError:
            pass
        else:
            raise DocumentError("Roadmap root inside project must be project-relative")
    else:
        raise DocumentError("Roadmap root kind is invalid")
    try:
        if not root.is_dir():
            raise DocumentError("Roadmap root is absent or unreachable")
    except OSError as exc:
        raise DocumentError("Roadmap root is unreachable") from exc
    return root


def _legacy_structured_template(document_type: str) -> dict[str, Any]:
    body = "# {{title}}\n\n" + "\n\n".join(
        f"## {heading}\n\n{{{{{key}}}}}" for key, heading in SECTIONS
    ) + "\n"
    data = body.encode("utf-8")
    return {
        "source": "legacy-structured-default",
        "profile": f"legacy-{document_type}-v1",
        "version": "1",
        "path_kind": "generated",
        "path": "none",
        "sha256": sha256_bytes(data),
        "body": body,
        "fields": tuple(key for key, _ in SECTIONS),
        "headings": tuple(heading for _, heading in SECTIONS),
    }


def _resolve_change_archive_template(
    project_root: Path,
    documentation: dict[str, Any],
) -> dict[str, Any]:
    return _legacy_structured_template("change-archive")


def _resolve_canonical_system_guide_template() -> dict[str, Any]:
    return _legacy_structured_template("system-guide")


def _resolve_bundled_profile_template(document_type: str, profile: str) -> dict[str, Any]:
    if document_type == "change-archive":
        expected_profile, target = (
            CANONICAL_CHANGE_ARCHIVE_PROFILE,
            CANONICAL_CHANGE_ARCHIVE_TEMPLATE,
        )
    elif document_type == "system-guide":
        expected_profile, target = (
            CANONICAL_SYSTEM_GUIDE_PROFILE,
            CANONICAL_SYSTEM_GUIDE_TEMPLATE,
        )
    elif document_type == "roadmap":
        expected_profile, target = (
            CANONICAL_ROADMAP_PROFILE,
            CANONICAL_ROADMAP_TEMPLATE,
        )
    else:
        raise DocumentError("selected template profile has an unsupported document type")
    if profile != expected_profile:
        raise DocumentError("selected template profile requires a bound project catalog")
    try:
        data = target.read_bytes()
        text = data.decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise DocumentError("bundled fallback template is unreachable or not UTF-8") from exc
    if len(data) > MAX_CHANGE_ARCHIVE_TEMPLATE_BYTES:
        raise DocumentError("bundled fallback template exceeds 65536 bytes")
    headings = tuple(re.findall(r"(?m)^(#{1,6}) ([^\r\n]+)\r?$", text))
    if not headings or headings[0][0] != "#":
        raise DocumentError("bundled fallback template must start with a title")
    return {
        "source": "bundled-fallback",
        "profile": expected_profile,
        "version": "1",
        "path_kind": "plugin-bundled",
        "path": str(target),
        "sha256": sha256_bytes(data),
        "text": text,
        "headings": headings,
        "generation_policy": BUNDLED_GENERATION_POLICY,
        "required_topics": BUNDLED_REQUIRED_TOPICS[document_type],
        "optional_sections": (),
    }


def _resolve_catalog_root(
    project_root: Path,
    documentation: dict[str, Any],
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    catalog = documentation.get("template_catalog")
    if not isinstance(catalog, dict):
        raise DocumentError("Project Integration has no bound template catalog")
    raw_path = str(catalog["path"])
    if catalog["path_kind"] == "project-relative":
        pure = _normalized_relative_path(raw_path, "template catalog path")
        root = project_root.joinpath(*pure.parts).resolve(strict=False)
        try:
            root.relative_to(project_root)
        except ValueError as exc:
            raise DocumentError("template catalog path escapes project root") from exc
    elif catalog["path_kind"] == "external-absolute":
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            raise DocumentError("external template catalog path is not absolute")
        root = candidate.resolve(strict=False)
        if root == Path(root.anchor):
            raise DocumentError("external template catalog must not be a filesystem root")
        try:
            root.relative_to(project_root)
        except ValueError:
            pass
        else:
            raise DocumentError("project-local template catalog path must be project-relative")
    else:
        raise DocumentError("template catalog path kind is invalid")
    try:
        if not root.is_dir():
            raise DocumentError("template catalog is absent or not a directory")
        manifest_data = (root / "profiles.json").read_bytes()
    except OSError as exc:
        raise DocumentError("template catalog is unreachable") from exc
    try:
        manifest = json.loads(manifest_data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DocumentError("template catalog manifest must be UTF-8 JSON") from exc
    selection = manifest.get("selection") if isinstance(manifest, dict) else None
    generation_policy = manifest.get("generation_policy") if isinstance(manifest, dict) else None
    manifest_profiles = manifest.get("profiles") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != 1
        or not isinstance(selection, dict)
        or selection.get("strategy") != "manifest-ranked"
        or selection.get("read_templates_before_selection") is not False
        or selection.get("tie_policy") != "ask-human"
        or selection.get("allow_profile_merge") is not False
        or selection.get("allow_ad_hoc_profile", False) is not False
        or not isinstance(generation_policy, dict)
        or generation_policy.get("minimum_section_count") != 0
        or generation_policy.get("minimum_word_count") != 0
        or not isinstance(generation_policy.get("output_gate"), list)
        or not generation_policy.get("output_gate")
        or not isinstance(manifest_profiles, list)
    ):
        raise DocumentError("template catalog selection contract is invalid")
    seen_profiles: set[str] = set()
    for item in manifest_profiles:
        if not isinstance(item, dict):
            raise DocumentError("template catalog profile metadata is invalid")
        profile = item.get("id")
        document_type = item.get("document_type")
        file_name = item.get("template")
        if (
            not all(isinstance(value, str) for value in (profile, document_type, file_name))
            or document_type not in {"change-archive", "system-guide", "roadmap"}
            or TEMPLATE_PROFILE.fullmatch(profile) is None
            or profile in seen_profiles
        ):
            raise DocumentError("template catalog profile metadata is invalid")
        seen_profiles.add(profile)
        version_match = re.search(r"-v([1-9][0-9]*)$", profile)
        if version_match is None:
            raise DocumentError("template catalog profile version is invalid")
        pure = _normalized_relative_path(file_name, "template profile file")
        if pure.suffix.casefold() != ".md":
            raise DocumentError("template profile file must be a relative Markdown file")
    return root, catalog, manifest


def _resolve_profile_template(
    project_root: Path,
    documentation: dict[str, Any],
    *,
    document_type: str,
    profile: str,
) -> dict[str, Any]:
    if "template_catalog" not in documentation:
        return _resolve_bundled_profile_template(document_type, profile)
    root, catalog, manifest = _resolve_catalog_root(project_root, documentation)
    manifest_matches = [item for item in manifest["profiles"] if item.get("id") == profile]
    if len(manifest_matches) != 1:
        raise DocumentError("selected template profile metadata is absent or duplicated")
    manifest_profile = manifest_matches[0]
    if manifest_profile.get("document_type") != document_type:
        raise DocumentError("selected template profile has the wrong document type")
    version_match = re.search(r"-v([1-9][0-9]*)$", profile)
    if version_match is None:
        raise DocumentError("selected template profile version is invalid")
    pure = _normalized_relative_path(manifest_profile.get("template"), "template profile file")
    target = root.joinpath(*pure.parts).resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise DocumentError("template profile file escapes the catalog") from exc
    try:
        if not target.is_file():
            raise DocumentError("selected template profile file is absent")
        data = target.read_bytes()
    except OSError as exc:
        raise DocumentError("selected template profile file is unreachable") from exc
    if len(data) > MAX_CHANGE_ARCHIVE_TEMPLATE_BYTES:
        raise DocumentError("selected template profile exceeds 65536 bytes")
    actual_hash = sha256_bytes(data)
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DocumentError("selected template profile must be UTF-8") from exc
    headings = tuple(re.findall(r"(?m)^(#{1,6}) ([^\r\n]+)\r?$", text))
    if not headings or headings[0][0] != "#":
        raise DocumentError("selected template profile must start with a title")
    return {
        "document_type": document_type,
        "profile": profile,
        "file": pure.as_posix(),
        "version": version_match.group(1),
        "source": "project-catalog",
        "path_kind": catalog["path_kind"],
        "path": str(target),
        "sha256": actual_hash,
        "text": text,
        "headings": headings,
        "generation_policy": manifest["generation_policy"],
        "required_topics": tuple(manifest_profile["required_topics"]),
        "optional_sections": tuple(manifest_profile["optional_sections"]),
    }


def _resolve_context_target(
    project_root: Path,
    documentation: dict[str, str | None],
) -> Path:
    raw = str(documentation["context_path"])
    candidate = Path(raw)
    if candidate.name.casefold() != CONTEXT_FILE_NAME.casefold():
        raise DocumentError("Project Context path must target CONTEXT.md")
    if candidate.is_absolute():
        lexical = Path(os.path.abspath(raw))
        target = candidate.resolve(strict=False)
        if lexical.parent == Path(lexical.anchor) or target.parent == Path(target.anchor):
            raise DocumentError("project context root must not be a drive or share root")
        try:
            target.relative_to(project_root)
        except ValueError:
            pass
        else:
            raise DocumentError("project-local Context path must be project-relative")
    else:
        pure = _normalized_relative_path(raw, "Project Context path")
        target = project_root.joinpath(*pure.parts).resolve(strict=False)
        try:
            target.relative_to(project_root)
        except ValueError as exc:
            raise DocumentError("Project Context path escapes project root") from exc
    spec_base = target.parent
    try:
        if not spec_base.is_dir():
            raise DocumentError("Spec base is absent or unreachable")
    except OSError as exc:
        raise DocumentError("Spec base is unreachable") from exc
    return target


def _public_text(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise DocumentError(f"{label} must be text")
    normalized = value.strip()
    if not normalized:
        raise DocumentError(f"{label} must not be empty")
    if len(normalized) > MAX_SECTION_CHARS:
        raise DocumentError(f"{label} exceeds {MAX_SECTION_CHARS} characters")
    if re.search(r"(?m)^#{1,6}\s", normalized):
        raise DocumentError(f"{label} must not add Markdown headings")
    for pattern in INTERNAL_REFERENCES:
        if pattern.search(normalized):
            raise DocumentError(f"{label} contains an internal or machine-local reference")
    return normalized


def _context_text(value: Any, label: str, *, max_chars: int = 2000) -> str:
    normalized = _public_text(value, label)
    if len(normalized) > max_chars or any(token in normalized for token in ("\n", "\r", "`")):
        raise DocumentError(f"{label} must be one line without backticks and at most {max_chars} characters")
    return normalized


def _parse_context_input(value: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version",
        "document_type",
        "trigger",
        "persistent_product_delta",
        "expected_target_sha256",
        "entries",
    }
    if set(value) != expected:
        raise DocumentError(f"project-context input fields must be exactly {sorted(expected)}")
    if value["schema_version"] != INPUT_SCHEMA_VERSION:
        raise DocumentError(f"document input schema_version must be {INPUT_SCHEMA_VERSION}")
    if value["trigger"] not in TRIGGERS:
        raise DocumentError("trigger must be human-request or goal-closeout")
    if value["persistent_product_delta"] is not True:
        raise DocumentError("project-context requires persistent_product_delta true")
    expected_hash = value["expected_target_sha256"]
    if expected_hash is not None and (
        not isinstance(expected_hash, str)
        or re.fullmatch(r"[0-9A-Fa-f]{64}", expected_hash) is None
    ):
        raise DocumentError("expected_target_sha256 must be null or a 64-character SHA-256")
    entries = value["entries"]
    if not isinstance(entries, list) or not entries or len(entries) > MAX_CONTEXT_ENTRIES:
        raise DocumentError(f"project-context entries must contain 1-{MAX_CONTEXT_ENTRIES} items")
    parsed_entries: list[dict[str, str]] = []
    seen: set[str] = set()
    expected_entry_fields = {"term", *(key for key, _ in CONTEXT_FIELDS)}
    for index, item in enumerate(entries):
        if not isinstance(item, dict) or set(item) != expected_entry_fields:
            raise DocumentError(
                f"entries[{index}] fields must be exactly {sorted(expected_entry_fields)}"
            )
        term = _context_text(item["term"], f"entries[{index}].term", max_chars=120)
        if any(token in term for token in ("#", "<!--", "-->")):
            raise DocumentError(f"entries[{index}].term contains unsafe Markdown syntax")
        identity = term.casefold()
        if identity in seen:
            raise DocumentError(f"duplicate project-context term: {term}")
        seen.add(identity)
        parsed = {"term": term}
        for key, _ in CONTEXT_FIELDS:
            parsed[key] = _context_text(item[key], f"entries[{index}].{key}")
        parsed_entries.append(parsed)
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
        "document_type": "project-context",
        "trigger": value["trigger"],
        "persistent_product_delta": True,
        "expected_target_sha256": None if expected_hash is None else expected_hash.upper(),
        "entries": parsed_entries,
    }


def _parse_roadmap_input(value: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version",
        "document_type",
        "title",
        "trigger",
        "output_path",
        "mode",
        "expected_target_sha256",
        "template_profile",
        "rendered_markdown",
    }
    if set(value) != expected:
        raise DocumentError(f"roadmap input fields must be exactly {sorted(expected)}")
    if value["schema_version"] != INPUT_SCHEMA_VERSION:
        raise DocumentError(f"roadmap input schema_version must be {INPUT_SCHEMA_VERSION}")
    if value["document_type"] != "roadmap":
        raise DocumentError("roadmap input document_type must be roadmap")
    if value["trigger"] != "human-request":
        raise DocumentError("roadmap requires a Human request")
    title = value["title"]
    if (
        not isinstance(title, str)
        or not title.strip()
        or len(title.strip()) > MAX_TITLE_CHARS
        or any(token in title for token in ("\n", "\r", "#", "`"))
    ):
        raise DocumentError("roadmap title is empty, unsafe or too long")
    output = _normalized_relative_path(value["output_path"], "roadmap output_path")
    if len(output.parts) != 1 or ROADMAP_FILE_NAME.fullmatch(output.name) is None:
        raise DocumentError(
            "roadmap output_path must be <YYYY-MM-DD>-<short-slug>-roadmap.md"
        )
    mode = value["mode"]
    if mode not in {"create", "update"}:
        raise DocumentError("roadmap mode must be create or update")
    expected_hash = value["expected_target_sha256"]
    if expected_hash is not None and (
        not isinstance(expected_hash, str)
        or re.fullmatch(r"[0-9A-Fa-f]{64}", expected_hash) is None
    ):
        raise DocumentError(
            "roadmap expected_target_sha256 must be null or a 64-character SHA-256"
        )
    if mode == "create" and expected_hash is not None:
        raise DocumentError("roadmap create must not provide expected_target_sha256")
    if mode == "update" and expected_hash is None:
        raise DocumentError("roadmap update requires expected_target_sha256")
    profile = value["template_profile"]
    if not isinstance(profile, str) or TEMPLATE_PROFILE.fullmatch(profile) is None:
        raise DocumentError("roadmap template_profile is invalid")
    rendered = value["rendered_markdown"]
    if not isinstance(rendered, str) or not rendered.strip():
        raise DocumentError("roadmap rendered_markdown must not be empty")
    if len(rendered) > MAX_DOCUMENT_CHARS:
        raise DocumentError(f"roadmap content exceeds {MAX_DOCUMENT_CHARS} characters")
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
        "document_type": "roadmap",
        "title": title.strip(),
        "trigger": "human-request",
        "output_path": output.as_posix(),
        "mode": mode,
        "expected_target_sha256": (
            None if expected_hash is None else expected_hash.upper()
        ),
        "template_profile": profile,
        "rendered_markdown": rendered.strip() + "\n",
    }


def parse_document_input(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DocumentError("document input root must be an object")
    if value.get("document_type") == "roadmap":
        return _parse_roadmap_input(value)
    if value.get("document_type") == "project-context":
        return _parse_context_input(value)
    if "template_profile" in value or "rendered_markdown" in value:
        profile_input = {
            "schema_version",
            "document_type",
            "title",
            "trigger",
            "persistent_product_delta",
            "template_profile",
            "rendered_markdown",
        }
        explicit_target = "target_path" in value
        expected_profile_input = profile_input | (
            {
                "target_path",
                "mode",
                "expected_target_sha256",
                "template_catalog_path",
            }
            if explicit_target
            else {"output_path"}
        )
        if set(value) != expected_profile_input:
            raise DocumentError(
                f"profile document input fields must be exactly {sorted(expected_profile_input)}"
            )
        if value.get("document_type") not in {"change-archive", "system-guide"}:
            raise DocumentError("template profiles only support change-archive or system-guide")
        profile = value.get("template_profile")
        if not isinstance(profile, str) or TEMPLATE_PROFILE.fullmatch(profile) is None:
            raise DocumentError("template_profile is invalid")
        rendered = value.get("rendered_markdown")
        if not isinstance(rendered, str) or not rendered.strip():
            raise DocumentError("rendered_markdown must not be empty")
        if len(rendered) > MAX_DOCUMENT_CHARS:
            raise DocumentError(f"document content exceeds {MAX_DOCUMENT_CHARS} characters")
        common = dict(value)
        common.pop("template_profile")
        common.pop("rendered_markdown")
        if explicit_target:
            if value.get("trigger") != "human-request":
                raise DocumentError("explicit target requires a Human request")
            target = _normalized_relative_path(value["target_path"], "target_path")
            if target.suffix.casefold() != ".md":
                raise DocumentError("target_path must end in .md")
            mode = value.get("mode")
            if mode not in {"create", "update"}:
                raise DocumentError("explicit target mode must be create or update")
            expected_hash = value.get("expected_target_sha256")
            if expected_hash is not None and (
                not isinstance(expected_hash, str)
                or re.fullmatch(r"[0-9A-Fa-f]{64}", expected_hash) is None
            ):
                raise DocumentError(
                    "explicit target expected_target_sha256 must be null or a 64-character SHA-256"
                )
            if mode == "create" and expected_hash is not None:
                raise DocumentError("explicit target create must not provide expected_target_sha256")
            if mode == "update" and expected_hash is None:
                raise DocumentError("explicit target update requires expected_target_sha256")
            catalog = value.get("template_catalog_path")
            if catalog is not None:
                catalog = _normalized_relative_path(
                    catalog,
                    "template_catalog_path",
                ).as_posix()
            for key in (
                "target_path",
                "mode",
                "expected_target_sha256",
                "template_catalog_path",
            ):
                common.pop(key)
            common["output_path"] = target.as_posix()
        common["sections"] = {key: value for key, value in SECTIONS}
        parsed = parse_document_input(common)
        parsed.pop("sections")
        if explicit_target:
            parsed.pop("output_path")
            parsed.update(
                target_path=target.as_posix(),
                mode=mode,
                expected_target_sha256=(
                    None if expected_hash is None else expected_hash.upper()
                ),
                template_catalog_path=catalog,
            )
        parsed["template_profile"] = profile
        parsed["rendered_markdown"] = rendered.strip() + "\n"
        return parsed
    expected = {
        "schema_version",
        "document_type",
        "title",
        "trigger",
        "persistent_product_delta",
        "output_path",
        "sections",
    }
    if set(value) != expected:
        raise DocumentError(f"document input fields must be exactly {sorted(expected)}")
    if value["schema_version"] != INPUT_SCHEMA_VERSION:
        raise DocumentError(f"document input schema_version must be {INPUT_SCHEMA_VERSION}")
    if value["document_type"] not in DOCUMENT_TYPES:
        raise DocumentError("document_type must be change-archive, system-guide or project-context")
    if value["trigger"] not in TRIGGERS:
        raise DocumentError("trigger must be human-request or goal-closeout")
    if not isinstance(value["persistent_product_delta"], bool):
        raise DocumentError("persistent_product_delta must be boolean")

    title = value["title"]
    if (
        not isinstance(title, str)
        or not title.strip()
        or len(title.strip()) > MAX_TITLE_CHARS
        or any(token in title for token in ("\n", "\r", "#", "`"))
    ):
        raise DocumentError("title is empty, unsafe or too long")
    title = title.strip()
    for pattern in INTERNAL_REFERENCES:
        if pattern.search(title):
            raise DocumentError("title contains an internal or machine-local reference")

    output = _normalized_relative_path(value["output_path"], "output_path")
    if output.suffix.casefold() != ".md":
        raise DocumentError("output_path must end in .md")
    sections = value["sections"]
    if not isinstance(sections, dict) or set(sections) != {key for key, _ in SECTIONS}:
        raise DocumentError("canonical document sections must contain the canonical semantic fields")
    parsed_sections = {
        key: _public_text(sections[key], f"sections.{key}") for key, _ in SECTIONS
    }
    total = len(title) + sum(len(item) for item in parsed_sections.values())
    if total > MAX_DOCUMENT_CHARS:
        raise DocumentError(f"document content exceeds {MAX_DOCUMENT_CHARS} characters")
    return {
        "schema_version": INPUT_SCHEMA_VERSION,
        "document_type": value["document_type"],
        "title": title,
        "trigger": value["trigger"],
        "persistent_product_delta": value["persistent_product_delta"],
        "output_path": output.as_posix(),
        "sections": parsed_sections,
    }


def _authorize(
    documentation: dict[str, str | None],
    document: dict[str, Any],
    *,
    per_write_confirmed: bool,
) -> None:
    policy = documentation["policy"]
    if policy == "disabled":
        raise DocumentError("Project documentation policy is disabled")
    trigger = document["trigger"]
    if policy == "on-request" and trigger != "human-request":
        raise DocumentError("on-request policy requires a Human request")
    if trigger == "goal-closeout" and (
        policy != "required-at-closeout" or not document["persistent_product_delta"]
    ):
        raise DocumentError(
            "goal-closeout requires required-at-closeout policy and persistent product delta"
        )
    authorization = documentation["write_authorization"]
    bounded_closeout = (
        authorization == "bounded-closeout"
        and policy == "required-at-closeout"
        and trigger == "goal-closeout"
        and document["persistent_product_delta"]
    )
    if not bounded_closeout and not per_write_confirmed:
        raise DocumentError("this document requires explicit per-write confirmation")


def render_document(
    document: dict[str, Any],
    *,
    document_template: dict[str, Any] | None = None,
) -> bytes:
    if document["document_type"] in {"change-archive", "system-guide"}:
        if document_template is None:
            raise DocumentError(f"{document['document_type']} rendering requires a resolved template")
        required_fields = set(document_template["fields"])
        if set(document["sections"]) != required_fields:
            raise DocumentError(
                f"{document['document_type']} input fields do not match the resolved template contract"
            )
        text = str(document_template["body"])
        replacements = {"title": document["title"], **document["sections"]}
        for key, value in replacements.items():
            text = text.replace(f"{{{{{key}}}}}", value)
        if "{{" in text or "}}" in text:
            raise DocumentError(f"{document['document_type']} template contains unresolved placeholders")
        return text.encode("utf-8")
    raise DocumentError("unsupported publication document type")


def render_profile_document(
    document: dict[str, Any],
    template: dict[str, Any],
) -> bytes:
    text = str(document["rendered_markdown"])
    forbidden_references = (
        ROADMAP_FORBIDDEN_REFERENCES
        if document["document_type"] == "roadmap"
        else INTERNAL_REFERENCES
    )
    for pattern in forbidden_references:
        if pattern.search(text):
            raise DocumentError("rendered_markdown contains an internal or machine-local reference")
    generated_headings = tuple(re.findall(r"(?m)^(#{1,6}) ([^\r\n]+)\r?$", text))
    if (
        not generated_headings
        or generated_headings[0][0] != "#"
        or generated_headings[0][1] != document["title"]
    ):
        raise DocumentError("rendered_markdown title must equal title")
    if "<!--" in text or "-->" in text or "生成说明" in text:
        raise DocumentError("rendered_markdown still contains template-author instructions")
    placeholders = set(re.findall(r"\{[^{}\r\n]+\}", template["text"]))
    unresolved = sorted(placeholder for placeholder in placeholders if placeholder in text)
    if unresolved:
        raise DocumentError("rendered_markdown still contains template placeholders")
    heading_matches = list(re.finditer(r"(?m)^(#{1,6}) [^\r\n]+\r?$", text))
    for index, match in enumerate(heading_matches):
        level = len(match.group(1))
        section_end = len(text)
        for following in heading_matches[index + 1:]:
            if len(following.group(1)) <= level:
                section_end = following.start()
                break
        section_body = text[match.end():section_end]
        substantive = re.sub(r"(?m)^\s*(?:---+|\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?)\s*$", "", section_body)
        substantive = re.sub(r"(?m)^#{1,6} [^\r\n]+$", "", substantive).strip()
        if not substantive:
            raise DocumentError("rendered_markdown contains a heading without substantive content")
    data = text.encode("utf-8")
    if len(data) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"generated document exceeds {MAX_DOCUMENT_BYTES} bytes")
    return data


def render_roadmap_document(document: dict[str, Any]) -> bytes:
    text = str(document["rendered_markdown"])
    for pattern in ROADMAP_FORBIDDEN_REFERENCES:
        if pattern.search(text):
            raise DocumentError("roadmap contains a Sacha-internal reference")
    title_match = re.match(r"\A# ([^\r\n]+)\r?\n", text)
    if (
        title_match is None
        or title_match.group(1) != document["title"]
        or len(re.findall(r"(?m)^# ", text)) != 1
    ):
        raise DocumentError("roadmap must have exactly one title matching title")
    if "<!--" in text or "-->" in text or "{{" in text or "}}" in text:
        raise DocumentError("roadmap contains comments or unresolved placeholders")
    headings = re.findall(r"(?m)^## ([^\r\n]+)\r?$", text)
    positions: list[int] = []
    for heading in ROADMAP_REQUIRED_HEADINGS:
        if headings.count(heading) != 1:
            raise DocumentError(f"roadmap required heading is missing or duplicated: {heading}")
        positions.append(headings.index(heading))
    if positions != sorted(positions):
        raise DocumentError("roadmap required headings are out of order")
    heading_matches = list(re.finditer(r"(?m)^## ([^\r\n]+)\r?$", text))
    for index, match in enumerate(heading_matches):
        section_end = (
            heading_matches[index + 1].start()
            if index + 1 < len(heading_matches)
            else len(text)
        )
        if not text[match.end() : section_end].strip():
            raise DocumentError(
                f"roadmap heading has no substantive content: {match.group(1)}"
            )
    data = text.encode("utf-8")
    if len(data) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"roadmap exceeds {MAX_DOCUMENT_BYTES} bytes")
    return data


def parse_roadmap_document(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentError("roadmap must be UTF-8") from exc
    title_match = re.match(r"\A# ([^\r\n]+)\r?\n", text)
    if title_match is None:
        raise DocumentError("roadmap title is missing")
    document = {
        "title": title_match.group(1),
        "rendered_markdown": text,
    }
    generated = render_roadmap_document(document)
    if generated != data:
        raise DocumentError("roadmap normalization changed generated bytes")
    return {
        "title": title_match.group(1),
        "sections": re.findall(r"(?m)^## ([^\r\n]+)\r?$", text),
    }


def parse_generated_document(
    data: bytes,
    *,
    expected_headings: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    if len(data) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"generated document exceeds {MAX_DOCUMENT_BYTES} bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentError("generated document must be UTF-8") from exc
    title_match = re.match(r"\A# ([^\r\n]+)\r?\n", text)
    if title_match is None or len(re.findall(r"(?m)^# ", text)) != 1:
        raise DocumentError("generated document must have exactly one title")
    headings = re.findall(r"(?m)^## ([^\r\n]+)\r?$", text)
    required_headings = (
        tuple(heading for _, heading in SECTIONS)
        if expected_headings is None
        else expected_headings
    )
    if tuple(headings) != required_headings:
        raise DocumentError("generated document headings are missing, duplicated or out of order")
    sections: dict[str, str] = {}
    section_pairs = (
        SECTIONS
        if expected_headings is None
        else tuple((heading, heading) for heading in expected_headings)
    )
    for key, heading in section_pairs:
        match = re.search(
            rf"(?ms)^## {re.escape(heading)}\s*\r?\n(.*?)(?=^## |\Z)",
            text,
        )
        if match is None:
            raise DocumentError(f"generated document section is missing: {heading}")
        sections[key] = _public_text(match.group(1), f"generated.{key}")
    return {"title": title_match.group(1), "sections": sections}


def _render_context_entry(entry: dict[str, str]) -> str:
    lines = [f"### {entry['term']}"]
    lines.extend(f"- {label}：{entry[key]}" for key, label in CONTEXT_FIELDS)
    return "\n".join(lines)


def _render_context_block(entries: dict[str, dict[str, str]]) -> str:
    bodies = [
        _render_context_entry(entries[key])
        for key in sorted(entries, key=lambda item: (item.casefold(), item))
    ]
    return f"{CONTEXT_BEGIN}\n{CONTEXT_HEADING}\n\n" + "\n\n".join(bodies) + f"\n{CONTEXT_END}"


def _parse_context_document(data: bytes) -> tuple[str, dict[str, dict[str, str]], tuple[int, int] | None]:
    if len(data) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"project context exceeds {MAX_DOCUMENT_BYTES} bytes")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DocumentError("project context must be UTF-8") from exc
    begin_count = text.count(CONTEXT_BEGIN)
    end_count = text.count(CONTEXT_END)
    if begin_count == 0 and end_count == 0:
        return text, {}, None
    if begin_count != 1 or end_count != 1:
        raise DocumentError("project context contains duplicate or broken managed markers")
    start = text.find(CONTEXT_BEGIN)
    finish = text.find(CONTEXT_END, start)
    if finish < start:
        raise DocumentError("project context managed markers are out of order")
    finish += len(CONTEXT_END)
    block = text[start:finish]
    normalized_block = block.replace("\r\n", "\n")
    prefix = f"{CONTEXT_BEGIN}\n{CONTEXT_HEADING}\n\n"
    suffix = f"\n{CONTEXT_END}"
    if not normalized_block.startswith(prefix) or not normalized_block.endswith(suffix):
        raise DocumentError("project context managed block structure is invalid")
    body = normalized_block[len(prefix) : -len(suffix)]
    chunks = re.split(r"\n\n(?=### )", body) if body else []
    entries: dict[str, dict[str, str]] = {}
    for chunk in chunks:
        lines = chunk.splitlines()
        if not lines or not lines[0].startswith("### "):
            raise DocumentError("project context term heading is invalid")
        term = _context_text(lines[0][4:], "existing term", max_chars=120)
        if len(lines) != 1 + len(CONTEXT_FIELDS):
            raise DocumentError(f"project context term structure is invalid: {term}")
        entry = {"term": term}
        for line, (key, label) in zip(lines[1:], CONTEXT_FIELDS):
            marker = f"- {label}："
            if not line.startswith(marker):
                raise DocumentError(f"project context field is invalid: {term}/{label}")
            entry[key] = _context_text(line[len(marker) :], f"existing.{term}.{key}")
        identity = term.casefold()
        if identity in entries:
            raise DocumentError(f"duplicate project-context term: {term}")
        entries[identity] = entry
    return text, entries, (start, finish)


def _merge_context_document(
    original: bytes | None,
    incoming: list[dict[str, str]],
) -> tuple[bytes, list[str]]:
    if original is None:
        text, entries, span = "# 项目上下文\n", {}, None
    else:
        text, entries, span = _parse_context_document(original)
    changed_existing: list[str] = []
    for entry in incoming:
        identity = entry["term"].casefold()
        if identity in entries and entries[identity] != entry:
            changed_existing.append(entries[identity]["term"])
        entries[identity] = entry
    block = _render_context_block(entries)
    newline = "\r\n" if original is not None and b"\r\n" in original else "\n"
    if newline != "\n":
        block = block.replace("\n", newline)
    if span is None:
        separator = newline if text.endswith(("\n", "\r")) else newline * 2
        merged = text + separator + block + newline
    else:
        merged = text[: span[0]] + block + text[span[1] :]
        if not merged.endswith("\n"):
            merged += "\n"
    generated = merged.encode("utf-8")
    if original is not None and original.startswith(b"\xef\xbb\xbf"):
        generated = b"\xef\xbb\xbf" + generated
    if len(generated) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"project context exceeds {MAX_DOCUMENT_BYTES} bytes")
    _parse_context_document(generated)
    return generated, changed_existing


def _target_path(root: Path, output_path: str) -> Path:
    pure = _normalized_relative_path(output_path, "output_path")
    target = root.joinpath(*pure.parts)
    parent = target.parent.resolve(strict=False)
    try:
        parent.relative_to(root)
    except ValueError as exc:
        raise DocumentError("output parent escapes Project Documentation root") from exc
    if not parent.is_dir():
        raise DocumentError("output parent directory does not exist")
    if target.exists():
        raise DocumentError("output target already exists; overwrite is forbidden")
    return target


def _explicit_target_path(project_root: Path, target_path: str) -> Path:
    pure = _normalized_relative_path(target_path, "target_path")
    if pure.suffix.casefold() != ".md":
        raise DocumentError("target_path must end in .md")
    target = project_root.joinpath(*pure.parts)
    parent = target.parent.resolve(strict=False)
    try:
        parent.relative_to(project_root)
    except ValueError as exc:
        raise DocumentError("explicit target parent escapes project root") from exc
    if not parent.is_dir():
        raise DocumentError("explicit target parent directory does not exist")
    if target.is_symlink():
        raise DocumentError("explicit target must not be a symbolic link")
    if target.exists():
        resolved = target.resolve(strict=False)
        try:
            resolved.relative_to(project_root)
        except ValueError as exc:
            raise DocumentError("explicit target escapes project root") from exc
    return target


def _publication_preimage(
    target: Path,
    *,
    mode: str,
    expected_sha256: str | None,
) -> bytes | None:
    if mode == "create":
        if target.exists():
            raise DocumentError("explicit target create target already exists")
        return None
    if not target.is_file():
        raise DocumentError("explicit target update target is absent or not a file")
    original = target.read_bytes()
    if sha256_bytes(original) != expected_sha256:
        raise DocumentError("explicit target preimage SHA-256 changed")
    return original


def _match_publication_format(generated: bytes, original: bytes | None) -> bytes:
    if original is None:
        return generated
    formatted = generated
    body = original[3:] if original.startswith(b"\xef\xbb\xbf") else original
    if b"\r\n" in body and b"\n" not in body.replace(b"\r\n", b""):
        formatted = formatted.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    if original.startswith(b"\xef\xbb\xbf"):
        formatted = b"\xef\xbb\xbf" + formatted
    if len(formatted) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"generated document exceeds {MAX_DOCUMENT_BYTES} bytes")
    return formatted


def _explicit_template_documentation(document: dict[str, Any]) -> dict[str, Any]:
    catalog = document.get("template_catalog_path")
    if catalog is None:
        return {}
    return {
        "template_catalog": {
            "path_kind": "project-relative",
            "path": catalog,
        }
    }


def _roadmap_target_path(root: Path, output_path: str) -> Path:
    pure = _normalized_relative_path(output_path, "roadmap output_path")
    if len(pure.parts) != 1 or ROADMAP_FILE_NAME.fullmatch(pure.name) is None:
        raise DocumentError(
            "roadmap output_path must be <YYYY-MM-DD>-<short-slug>-roadmap.md"
        )
    return root / pure.name


def _roadmap_preimage(
    target: Path,
    *,
    mode: str,
    expected_sha256: str | None,
) -> bytes | None:
    if mode == "create":
        if target.exists():
            raise DocumentError("roadmap create target already exists")
        return None
    if not target.is_file():
        raise DocumentError("roadmap update target is absent or not a file")
    original = target.read_bytes()
    actual = sha256_bytes(original)
    if expected_sha256 != actual:
        raise DocumentError("roadmap preimage SHA-256 changed")
    return original


def _commit_roadmap_update(
    target: Path,
    generated: bytes,
    original: bytes | None,
) -> None:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".sacha-roadmap-",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(generated)
            handle.flush()
            os.fsync(handle.fileno())
        if original is None:
            os.link(temp_path, target)
        else:
            if not target.is_file() or target.read_bytes() != original:
                raise DocumentError("roadmap changed before atomic replace")
            os.replace(temp_path, target)
            temp_path = None
    except FileExistsError as exc:
        raise DocumentError("roadmap appeared during atomic create") from exc
    except OSError as exc:
        raise DocumentError(f"atomic roadmap write failed: {type(exc).__name__}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _commit_publication_update(
    target: Path,
    generated: bytes,
    original: bytes | None,
) -> None:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".sacha-document-",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(generated)
            handle.flush()
            os.fsync(handle.fileno())
        if original is None:
            os.link(temp_path, target)
        else:
            if not target.is_file() or target.read_bytes() != original:
                raise DocumentError("explicit target changed before atomic replace")
            os.replace(temp_path, target)
            temp_path = None
    except FileExistsError as exc:
        raise DocumentError("explicit target appeared during atomic create") from exc
    except OSError as exc:
        raise DocumentError(f"atomic explicit target write failed: {type(exc).__name__}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _context_preimage(target: Path, expected_sha256: str | None) -> bytes | None:
    if target.exists():
        if not target.is_file():
            raise DocumentError("project context target is not a file")
        original = target.read_bytes()
        actual = sha256_bytes(original)
        if expected_sha256 is None:
            raise DocumentError("existing project context requires expected_target_sha256")
        if actual != expected_sha256:
            raise DocumentError("project context preimage SHA-256 changed")
        return original
    if expected_sha256 is not None:
        raise DocumentError("project context target is absent but expected_target_sha256 was provided")
    return None


def _commit_context_update(target: Path, generated: bytes, original: bytes | None) -> None:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".sacha-context-",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(generated)
            handle.flush()
            os.fsync(handle.fileno())
        if original is None:
            os.link(temp_path, target)
        else:
            if not target.is_file() or target.read_bytes() != original:
                raise DocumentError("project context changed before atomic replace")
            os.replace(temp_path, target)
            temp_path = None
    except FileExistsError as exc:
        raise DocumentError("project context appeared during atomic create") from exc
    except OSError as exc:
        raise DocumentError(f"atomic project context write failed: {type(exc).__name__}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _restore_context(target: Path, original: bytes | None, generated_hash: str) -> bool:
    try:
        if original is None:
            if target.is_file() and sha256_bytes(target.read_bytes()) == generated_hash:
                target.unlink()
            return not target.exists()
        restore_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=".sacha-context-restore-",
                suffix=".tmp",
                dir=target.parent,
                delete=False,
            ) as handle:
                restore_path = Path(handle.name)
                handle.write(original)
                handle.flush()
                os.fsync(handle.fileno())
            if (
                not target.is_file()
                or sha256_bytes(target.read_bytes()) != generated_hash
            ):
                return False
            os.replace(restore_path, target)
            restore_path = None
        finally:
            if restore_path is not None:
                restore_path.unlink(missing_ok=True)
        return target.read_bytes() == original
    except OSError:
        return False


def generate_project_document(
    *,
    project_root: Path,
    workflow_rule_path: str,
    document_input: Any,
    write: bool = False,
    per_write_confirmed: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "refused",
        "transaction": "no_write",
        "document_type": None,
        "target": None,
        "sha256": None,
        "conflicts": [],
    }
    write_started = False
    try:
        project = project_root.resolve(strict=False)
        if not project.is_dir():
            raise DocumentError("project root must exist and be a directory")
        document = parse_document_input(document_input)
        explicit_target = "target_path" in document
        workflow: Path | None = None
        workflow_hash: str | None = None
        if explicit_target:
            documentation = _explicit_template_documentation(document)
        else:
            pure_rule = _normalized_relative_path(workflow_rule_path, "workflow_rule_path")
            workflow = project.joinpath(*pure_rule.parts).resolve(strict=False)
            try:
                workflow.relative_to(project)
            except ValueError as exc:
                raise DocumentError("workflow rule escapes project root") from exc
            workflow_data = workflow.read_bytes()
            workflow_hash = sha256_bytes(workflow_data)
            documentation = parse_project_integration(workflow_data)
        if document["document_type"] == "roadmap":
            if write and not per_write_confirmed:
                raise DocumentError("roadmap write requires explicit per-write confirmation")
            root = _resolve_roadmap_root(project, documentation)
            target = _roadmap_target_path(root, document["output_path"])
            original = _roadmap_preimage(
                target,
                mode=document["mode"],
                expected_sha256=document["expected_target_sha256"],
            )
            document_template = _resolve_profile_template(
                project,
                documentation,
                document_type="roadmap",
                profile=document["template_profile"],
            )
            generated = render_profile_document(document, document_template)
            if generated != render_roadmap_document(document):
                raise DocumentError("roadmap profile rendering changed Roadmap semantics")
            parsed = parse_roadmap_document(generated)
            generated_hash = sha256_bytes(generated)
            original_hash = None if original is None else sha256_bytes(original)
            result.update(
                status="ready",
                transaction="dry_run",
                document_type="roadmap",
                target=str(target),
                sha256=generated_hash,
                preimage_sha256=original_hash,
                mode=document["mode"],
                parsed=parsed,
                template={
                    key: document_template[key]
                    for key in (
                        "source",
                        "profile",
                        "version",
                        "path_kind",
                        "path",
                    )
                },
            )
            result["template"]["required_topics"] = list(
                document_template["required_topics"]
            )
            if not write:
                return result
            write_started = True
            if sha256_bytes(workflow.read_bytes()) != workflow_hash:
                raise DocumentError("Project Integration changed after validation")
            current_root = _resolve_roadmap_root(project, documentation)
            current_target = _roadmap_target_path(
                current_root,
                document["output_path"],
            )
            current = _roadmap_preimage(
                current_target,
                mode=document["mode"],
                expected_sha256=document["expected_target_sha256"],
            )
            if current != original:
                raise DocumentError("roadmap changed after validation")
            current_template = _resolve_profile_template(
                project,
                documentation,
                document_type="roadmap",
                profile=document["template_profile"],
            )
            if current_template["sha256"] != document_template["sha256"]:
                raise DocumentError("roadmap template changed after validation")
            if current == generated:
                result.update(status="ok", transaction="no_changes")
                return result
            _commit_roadmap_update(current_target, generated, current)
            try:
                written = current_target.read_bytes()
                if sha256_bytes(written) != generated_hash:
                    raise DocumentError("post-write roadmap SHA-256 validation failed")
                parse_roadmap_document(written)
            except (OSError, DocumentError) as exc:
                restored = _restore_context(current_target, current, generated_hash)
                result.update(
                    status="failed",
                    transaction="rolled_back" if restored else "partial_write",
                )
                result["conflicts"].append(str(exc))
                return result
            result.update(status="ok", transaction="committed")
            return result
        if not explicit_target:
            _authorize(
                documentation,
                document,
                per_write_confirmed=per_write_confirmed,
            )
        if document["document_type"] == "project-context":
            target = _resolve_context_target(project, documentation)
            original = _context_preimage(target, document["expected_target_sha256"])
            generated, changed_existing = _merge_context_document(
                original,
                document["entries"],
            )
            if changed_existing and not per_write_confirmed:
                raise DocumentError(
                    "updating an existing project context definition requires explicit per-write confirmation"
                )
            generated_hash = sha256_bytes(generated)
            original_hash = None if original is None else sha256_bytes(original)
            _, parsed_entries, _ = _parse_context_document(generated)
            result.update(
                status="ready",
                transaction="dry_run",
                document_type="project-context",
                target=str(target),
                sha256=generated_hash,
                preimage_sha256=original_hash,
                changed_existing_terms=changed_existing,
                parsed={"terms": [entry["term"] for entry in parsed_entries.values()]},
            )
            if not write:
                return result
            write_started = True
            if sha256_bytes(workflow.read_bytes()) != workflow_hash:
                raise DocumentError("Project Integration changed after validation")
            target = _resolve_context_target(project, documentation)
            current = _context_preimage(target, document["expected_target_sha256"])
            if current != original:
                raise DocumentError("project context changed after validation")
            generated, changed_existing = _merge_context_document(
                current,
                document["entries"],
            )
            if changed_existing and not per_write_confirmed:
                raise DocumentError(
                    "updating an existing project context definition requires explicit per-write confirmation"
                )
            if current == generated:
                result.update(status="ok", transaction="no_changes")
                return result
            generated_hash = sha256_bytes(generated)
            _commit_context_update(target, generated, current)
            try:
                written = target.read_bytes()
                if sha256_bytes(written) != generated_hash:
                    raise DocumentError("post-write project context SHA-256 validation failed")
                _parse_context_document(written)
            except (OSError, DocumentError) as exc:
                restored = _restore_context(target, current, generated_hash)
                result.update(
                    status="failed",
                    transaction="rolled_back" if restored else "partial_write",
                )
                result["conflicts"].append(str(exc))
                return result
            result.update(status="ok", transaction="committed")
            return result
        if explicit_target:
            target = _explicit_target_path(project, document["target_path"])
            original = _publication_preimage(
                target,
                mode=document["mode"],
                expected_sha256=document["expected_target_sha256"],
            )
        else:
            root = _resolve_document_root(project, documentation)
            target = _target_path(root, document["output_path"])
            original = None
        if "template_profile" in document:
            document_template = _resolve_profile_template(
                project,
                documentation,
                document_type=document["document_type"],
                profile=document["template_profile"],
            )
            generated = render_profile_document(document, document_template)
            parsed_title = document["title"]
            parsed_sections = [heading for level, heading in document_template["headings"] if level == "##"]
        else:
            document_template = (
                _resolve_change_archive_template(project, documentation)
                if document["document_type"] == "change-archive"
                else _resolve_canonical_system_guide_template()
            )
            generated = render_document(
                document,
                document_template=document_template,
            )
            parsed = parse_generated_document(
                generated,
                expected_headings=document_template["headings"],
            )
            parsed_title = parsed["title"]
            parsed_sections = list(parsed["sections"])
        if explicit_target:
            generated = _match_publication_format(generated, original)
        generated_hash = sha256_bytes(generated)
        result.update(
            status="ready",
            transaction="dry_run",
            document_type=document["document_type"],
            target=str(target),
            sha256=generated_hash,
            parsed={"title": parsed_title, "sections": parsed_sections},
            template={
                key: document_template[key]
                for key in (
                    "source",
                    "profile",
                    "version",
                    "path_kind",
                    "path",
                )
            },
        )
        if explicit_target:
            result.update(
                mode=document["mode"],
                preimage_sha256=(
                    None if original is None else sha256_bytes(original)
                ),
            )
        if "required_topics" in document_template:
            result["template"]["required_topics"] = list(document_template["required_topics"])
        if not write:
            return result
        write_started = True
        if not explicit_target:
            assert workflow is not None and workflow_hash is not None
            if sha256_bytes(workflow.read_bytes()) != workflow_hash:
                raise DocumentError("Project Integration changed after validation")
        current_template = (
            _resolve_profile_template(
                project,
                documentation,
                document_type=document["document_type"],
                profile=document["template_profile"],
            )
            if "template_profile" in document
            else (
                _resolve_change_archive_template(project, documentation)
                if document["document_type"] == "change-archive"
                else _resolve_canonical_system_guide_template()
            )
        )
        if current_template["sha256"] != document_template["sha256"]:
            raise DocumentError(f"{document['document_type']} template changed after validation")
        if explicit_target:
            target = _explicit_target_path(project, document["target_path"])
            current = _publication_preimage(
                target,
                mode=document["mode"],
                expected_sha256=document["expected_target_sha256"],
            )
            if current != original:
                raise DocumentError("explicit target changed after validation")
            if current == generated:
                result.update(status="ok", transaction="no_changes")
                return result
            _commit_publication_update(target, generated, current)
            try:
                written = target.read_bytes()
                if written != generated:
                    raise DocumentError("post-write explicit target validation failed")
            except (OSError, DocumentError) as exc:
                restored = _restore_context(target, current, generated_hash)
                result.update(
                    status="failed",
                    transaction="rolled_back" if restored else "partial_write",
                )
                result["conflicts"].append(str(exc))
                return result
            result.update(status="ok", transaction="committed")
            return result

        root = _resolve_document_root(project, documentation)
        target = _target_path(root, document["output_path"])

        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=".sacha-document-",
                suffix=".tmp",
                dir=target.parent,
                delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                handle.write(generated)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temp_path, target)
        except FileExistsError as exc:
            raise DocumentError("output target already exists; overwrite is forbidden") from exc
        except OSError as exc:
            raise DocumentError(f"atomic new-file creation failed: {type(exc).__name__}") from exc
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass

        try:
            written = target.read_bytes()
            if sha256_bytes(written) != generated_hash:
                raise DocumentError("post-write SHA-256 validation failed")
            if "template_profile" in document:
                if written != render_profile_document(document, document_template):
                    raise DocumentError("post-write profile document validation failed")
            else:
                parse_generated_document(
                    written,
                    expected_headings=document_template["headings"],
                )
        except (OSError, DocumentError) as exc:
            try:
                if target.is_file() and sha256_bytes(target.read_bytes()) == generated_hash:
                    target.unlink()
                    result.update(status="failed", transaction="rolled_back")
                else:
                    result.update(status="failed", transaction="partial_write")
            except OSError:
                result.update(status="failed", transaction="partial_write")
            result["conflicts"].append(str(exc))
            return result
        result.update(status="ok", transaction="committed")
        return result
    except (OSError, UnicodeError, json.JSONDecodeError, DocumentError) as exc:
        if write_started:
            result.update(status="failed", transaction="no_write")
        result["conflicts"].append(
            str(exc)
            if isinstance(exc, (DocumentError, UnicodeError, json.JSONDecodeError))
            else f"filesystem operation failed: {type(exc).__name__}"
        )
        return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and safely create or update project documentation."
    )
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--workflow-rule-path", default="docs/workflow-rule.md")
    parser.add_argument("--input-json", required=True, type=Path)
    parser.add_argument("--per-write-confirmed", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    try:
        document_input = json.loads(args.input_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result = {
            "status": "refused",
            "transaction": "no_write",
            "conflicts": [f"cannot read document input: {type(exc).__name__}"],
        }
    else:
        result = generate_project_document(
            project_root=args.project_root,
            workflow_rule_path=args.workflow_rule_path,
            document_input=document_input,
            write=args.write,
            per_write_confirmed=args.per_write_confirmed,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] in {"ready", "ok"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
