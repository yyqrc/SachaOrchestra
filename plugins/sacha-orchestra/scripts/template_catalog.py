"""Shared validation for published document template catalogs."""
from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

MAX_CHANGE_ARCHIVE_TEMPLATE_BYTES = 64 * 1024
CHANGE_ARCHIVE_TEMPLATE_PROFILE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
DOCUMENT_TEMPLATE_TYPES = {"change-archive", "system-guide", "roadmap"}


class TemplateCatalogError(ValueError):
    pass


def load_template_catalog(catalog_root: Path) -> tuple[dict[str, Any], bytes, dict[str, Path]]:
    """Read the manifest once; inspect unselected templates only as files."""
    try:
        return _load_template_catalog(catalog_root)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise TemplateCatalogError(str(exc)) from exc


def _load_template_catalog(catalog_root: Path) -> tuple[dict[str, Any], bytes, dict[str, Path]]:
    if not catalog_root.is_absolute():
        raise TemplateCatalogError("template catalog root must be absolute")
    catalog_root = catalog_root.resolve(strict=False)
    try:
        if not catalog_root.is_dir():
            raise TemplateCatalogError("documentation template catalog path is absent or not a directory")
        manifest = catalog_root / "profiles.json"
        if not manifest.is_file():
            raise TemplateCatalogError("documentation template catalog requires profiles.json")
        manifest_data = manifest.read_bytes()
        if len(manifest_data) > MAX_CHANGE_ARCHIVE_TEMPLATE_BYTES:
            raise TemplateCatalogError("documentation template catalog manifest exceeds 65536 bytes")
        manifest_value = json.loads(manifest_data.decode("utf-8-sig"))
    except OSError as exc:
        raise TemplateCatalogError("documentation template catalog is unreachable") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TemplateCatalogError("documentation template catalog manifest must be UTF-8 JSON") from exc

    if not isinstance(manifest_value, dict) or manifest_value.get("schema_version") != 1:
        raise TemplateCatalogError("documentation template catalog schema_version must be 1")
    selection = manifest_value.get("selection")
    if not isinstance(selection, dict) or (
        selection.get("strategy") != "manifest-ranked"
        or selection.get("read_templates_before_selection") is not False
        or selection.get("tie_policy") != "ask-human"
        or selection.get("allow_profile_merge") is not False
        or selection.get("allow_ad_hoc_profile", False) is not False
    ):
        raise TemplateCatalogError("documentation template catalog selection contract is invalid")
    manifest_profiles = manifest_value.get("profiles")
    if not isinstance(manifest_profiles, list) or not manifest_profiles:
        raise TemplateCatalogError("documentation template catalog contains no profiles")
    generation_policy = manifest_value.get("generation_policy")
    required_generation_fields = {
        "minimum_section_count",
        "minimum_word_count",
        "structure_rule",
        "required_topics_rule",
        "optional_sections_rule",
        "section_admission_test",
        "section_admission_rule",
        "compression_rule",
        "navigation_rule",
        "revision_history_rule",
        "output_gate",
    }
    if not isinstance(generation_policy, dict) or not required_generation_fields.issubset(
        generation_policy
    ):
        raise TemplateCatalogError("documentation template catalog generation_policy is invalid")
    if generation_policy["minimum_section_count"] != 0 or generation_policy["minimum_word_count"] != 0:
        raise TemplateCatalogError("documentation template catalog must not impose section or word quotas")
    for label in (
        "structure_rule",
        "required_topics_rule",
        "optional_sections_rule",
        "section_admission_rule",
        "compression_rule",
        "navigation_rule",
        "revision_history_rule",
    ):
        if not isinstance(generation_policy[label], str) or not generation_policy[label].strip():
            raise TemplateCatalogError(f"documentation template catalog generation_policy.{label} is invalid")
    for label in ("section_admission_test", "output_gate"):
        if (
            not isinstance(generation_policy[label], list)
            or not generation_policy[label]
            or any(not isinstance(value, str) or not value.strip() for value in generation_policy[label])
        ):
            raise TemplateCatalogError(f"documentation template catalog generation_policy.{label} is invalid")

    paths: dict[str, Path] = {}
    seen: set[str] = set()
    required_profile_fields = {
        "id",
        "document_type",
        "primary_purpose",
        "primary_question",
        "choose_when",
        "avoid_when",
        "required_topics",
        "optional_sections",
        "template",
    }
    for item in manifest_profiles:
        if not isinstance(item, dict) or not required_profile_fields.issubset(item):
            raise TemplateCatalogError("documentation template profile fields are invalid")
        profile = item["id"]
        document_type = item["document_type"]
        file_name = item["template"]
        if not isinstance(profile, str) or CHANGE_ARCHIVE_TEMPLATE_PROFILE.fullmatch(profile) is None:
            raise TemplateCatalogError("documentation template profile id is invalid")
        if not isinstance(document_type, str) or document_type not in DOCUMENT_TEMPLATE_TYPES:
            raise TemplateCatalogError("documentation template document_type is invalid")
        if profile in seen:
            raise TemplateCatalogError("documentation template catalog contains duplicate profiles")
        seen.add(profile)
        for label in ("primary_purpose", "primary_question"):
            if not isinstance(item[label], str) or not item[label].strip():
                raise TemplateCatalogError(f"documentation template profile {label} is invalid")
        for label in ("choose_when", "avoid_when"):
            if (
                not isinstance(item[label], list)
                or not item[label]
                or any(not isinstance(value, str) or not value.strip() for value in item[label])
            ):
                raise TemplateCatalogError(f"documentation template profile {label} is invalid")
        for label in ("required_topics", "optional_sections"):
            if (
                not isinstance(item[label], list)
                or not item[label]
                or any(not isinstance(value, str) or not value.strip() for value in item[label])
            ):
                raise TemplateCatalogError(f"documentation template profile {label} is invalid")
        version_match = re.search(r"-v([1-9][0-9]*)$", profile)
        if version_match is None:
            raise TemplateCatalogError("documentation template profile must end with -v<positive integer>")
        if not isinstance(file_name, str):
            raise TemplateCatalogError("documentation template profile template is invalid")
        relative = PurePosixPath(file_name.replace("\\", "/"))
        if (
            not file_name or relative.is_absolute()
            or re.match(r"^[A-Za-z]:", file_name) is not None
            or any(part in {"", ".", ".."} for part in file_name.replace("\\", "/").split("/"))
            or any(part in {"", ".", ".."} for part in relative.parts)
            or relative.suffix.casefold() != ".md"
        ):
            raise TemplateCatalogError("documentation template catalog file must be a relative Markdown file")
        template_target = catalog_root.joinpath(*relative.parts).resolve(strict=False)
        try:
            template_target.relative_to(catalog_root)
        except ValueError as exc:
            raise TemplateCatalogError("documentation template catalog file escapes the catalog") from exc
        if not template_target.is_file():
            raise TemplateCatalogError("documentation template catalog references an absent file")
        if template_target.stat().st_size > MAX_CHANGE_ARCHIVE_TEMPLATE_BYTES:
            raise TemplateCatalogError("documentation template exceeds 65536 bytes")
        paths[profile] = template_target
    return manifest_value, manifest_data, paths
