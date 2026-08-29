#!/usr/bin/env python3
"""Resolve provider/Skill queries and propose Skill-level loading entries."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_LOAD_POLICIES = {"on-demand", "change-authorized", "review-only", "risk-matched"}
PROVIDER_CATALOG_SCHEMA_VERSIONS = {"2", "3"}
PROVIDER_SIDE_EFFECTS = {"read_only", "project_generated_state"}
CAPABILITY_ID_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*")
PLUGIN_NAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*")
CANONICAL_SKILL_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*:[a-z0-9][a-z0-9-]*")


class CatalogError(RuntimeError):
    """The explicit catalog cannot be consumed safely."""


def _normalized(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(token for token in re.split(r"[^a-z0-9]+", value.casefold()) if token)


def _strings(value: Any, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise CatalogError(f"{label} must be an array of non-empty strings")
    return tuple(item.strip() for item in value)


def _score(query: str, candidate: dict[str, Any]) -> tuple[int, str]:
    query_folded = query.casefold().strip()
    query_normalized = _normalized(query)
    canonical = str(candidate["canonical"])
    name = str(candidate["name"])
    exact_values = {canonical.casefold(), name.casefold()}
    if query_folded in exact_values:
        return 100, "canonical_or_name_exact"
    if query_normalized and query_normalized in {_normalized(canonical), _normalized(name)}:
        return 95, "case_separator_normalized_exact"
    aliases = tuple(candidate.get("aliases", ()))
    if query_folded in {alias.casefold() for alias in aliases}:
        return 90, "declared_alias_exact"
    if query_normalized and query_normalized in {_normalized(alias) for alias in aliases}:
        return 85, "declared_alias_normalized"
    keywords = tuple(candidate.get("keywords", ()))
    if query_folded in {keyword.casefold() for keyword in keywords}:
        return 90, "declared_keyword_exact"
    if query_normalized and query_normalized in {_normalized(keyword) for keyword in keywords}:
        return 85, "declared_keyword_normalized"
    candidate_tokens = set(_tokens(" ".join((canonical, name, *aliases, *keywords))))
    query_tokens = set(_tokens(query))
    if query_tokens and query_tokens.issubset(candidate_tokens):
        return 75, "token_match"
    if query_normalized and any(
        query_normalized in _normalized(value) or _normalized(value) in query_normalized
        for value in (canonical, name, *aliases, *keywords)
        if _normalized(value)
    ):
        return 65, "prefix_suffix_or_substring"
    description = str(candidate.get("description", ""))
    if query_tokens and query_tokens.issubset(set(_tokens(description))):
        return 50, "description_candidate"
    return 0, "no_match"


def _canonical_skill(value: Any, label: str) -> str:
    if not isinstance(value, str) or CANONICAL_SKILL_PATTERN.fullmatch(value) is None:
        raise CatalogError(f"{label} must be a canonical <plugin>:<skill> identity")
    return value


def validate_provider_catalog(
    value: Any,
    *,
    expected_provider: str,
    visible_skills: tuple[str, ...],
) -> tuple[dict[str, str], ...]:
    """Validate a provider catalog and normalize it to Skill-level entries."""
    if PLUGIN_NAME_PATTERN.fullmatch(expected_provider) is None:
        raise CatalogError("context provider must be a canonical lowercase plugin identity")
    if not isinstance(value, dict):
        raise CatalogError("provider catalog root must be an object")
    expected_root_keys = {"schema_version", "provider", "capabilities"}
    if set(value) != expected_root_keys:
        raise CatalogError(
            f"provider catalog fields must be exactly {sorted(expected_root_keys)}"
        )
    schema_version = value.get("schema_version")
    if schema_version not in PROVIDER_CATALOG_SCHEMA_VERSIONS:
        raise CatalogError(
            "provider catalog schema_version must be '2' or '3'"
        )
    if value.get("provider") != expected_provider:
        raise CatalogError("provider catalog identity must match the context provider")

    visible = {
        _canonical_skill(skill, "visible_skills item")
        for skill in visible_skills
    }
    capabilities = value.get("capabilities")
    if not isinstance(capabilities, list):
        raise CatalogError("provider catalog capabilities must be an array")
    parsed: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_skills: set[str] = set()
    expected_capability_keys = (
        {"id", "skill", "side_effect"}
        if schema_version == "2"
        else {"skill", "side_effect"}
    )
    for index, item in enumerate(capabilities):
        label = f"provider catalog capabilities[{index}]"
        if not isinstance(item, dict):
            raise CatalogError(f"{label} must be an object")
        if set(item) != expected_capability_keys:
            raise CatalogError(
                f"{label} fields must be exactly {sorted(expected_capability_keys)}"
            )
        if schema_version == "2":
            capability_id = item.get("id")
            if (
                not isinstance(capability_id, str)
                or CAPABILITY_ID_PATTERN.fullmatch(capability_id) is None
            ):
                raise CatalogError(
                    f"{label}.id must use canonical lowercase letters, digits, dots or hyphens"
                )
            if capability_id in seen_ids:
                raise CatalogError(f"duplicate provider capability id: {capability_id}")
            seen_ids.add(capability_id)
        skill = _canonical_skill(item.get("skill"), f"{label}.skill")
        if not skill.startswith(f"{expected_provider}:"):
            raise CatalogError(f"{label}.skill must belong to the context provider")
        if skill not in visible:
            raise CatalogError(f"{label}.skill is not visible in the current context: {skill}")
        if skill in seen_skills:
            raise CatalogError(f"duplicate provider Skill: {skill}")
        seen_skills.add(skill)
        side_effect = item.get("side_effect")
        if side_effect not in PROVIDER_SIDE_EFFECTS:
            raise CatalogError(
                f"{label}.side_effect must be one of {sorted(PROVIDER_SIDE_EFFECTS)}"
            )
        parsed.append({
            "skill": skill,
            "side_effect": side_effect,
        })
    return tuple(parsed)


def _capabilities(value: Any, label: str) -> tuple[dict[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise CatalogError(f"{label} must be an array")
    parsed: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise CatalogError(f"{label}[{index}] must be an object")
        skill = item.get("skill")
        if not isinstance(skill, str) or not skill.strip():
            raise CatalogError(f"{label}[{index}].skill must be a non-empty string")
        entry = {"skill": skill.strip()}
        side_effect = item.get("side_effect")
        if side_effect is not None:
            if side_effect not in PROVIDER_SIDE_EFFECTS:
                raise CatalogError(
                    f"{label}[{index}].side_effect must be one of {sorted(PROVIDER_SIDE_EFFECTS)}"
                )
            entry["side_effect"] = side_effect
        parsed.append(entry)
    return tuple(parsed)


def _candidates(catalog: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    candidates: list[dict[str, Any]] = []
    for kind, key in (("provider", "providers"), ("skill", "skills")):
        values = catalog.get(key, [])
        if not isinstance(values, list):
            raise CatalogError(f"{key} must be an array")
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                raise CatalogError(f"{key}[{index}] must be an object")
            canonical = item.get("canonical") or item.get("name")
            name = item.get("name")
            if not isinstance(canonical, str) or not canonical.strip():
                raise CatalogError(f"{key}[{index}].canonical must be a non-empty string")
            if not isinstance(name, str) or not name.strip():
                raise CatalogError(f"{key}[{index}].name must be a non-empty string")
            description = item.get("description", "")
            if not isinstance(description, str):
                raise CatalogError(f"{key}[{index}].description must be a string")
            if "catalog" in item:
                if kind != "provider":
                    raise CatalogError("只有 Provider 备选项可以声明 provider catalog")
                if "capabilities" in item:
                    raise CatalogError(
                        f"{key}[{index}] must not combine catalog and capabilities"
                    )
                visible_skills = _strings(
                    item.get("visible_skills"),
                    f"{key}[{index}].visible_skills",
                )
                capabilities = validate_provider_catalog(
                    item["catalog"],
                    expected_provider=canonical.strip(),
                    visible_skills=visible_skills,
                )
            else:
                capabilities = _capabilities(
                    item.get("capabilities"),
                    f"{key}[{index}].capabilities",
                )
            candidates.append({
                "kind": kind,
                "canonical": canonical.strip(),
                "name": name.strip(),
                "description": description.strip(),
                "aliases": _strings(item.get("aliases"), f"{key}[{index}].aliases"),
                "keywords": _strings(item.get("keywords"), f"{key}[{index}].keywords"),
                "capabilities": capabilities,
            })
    return tuple(candidates)


def resolve_project_root(
    *,
    explicit_override: str | None = None,
    active_workspace_roots: tuple[str, ...] = (),
    binding_roots: tuple[str, ...] = (),
    scm_roots: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Resolve the first non-empty verified project-root source without guessing."""
    stages = (
        ("explicit_override", () if explicit_override is None else (explicit_override,)),
        ("active_workspace_root", active_workspace_roots),
        ("project_agents_or_binding", binding_roots),
        ("scm_root", scm_roots),
    )
    for source, values in stages:
        unique: dict[str, str] = {}
        for value in values:
            candidate = value.strip()
            if not candidate:
                raise CatalogError(f"{source} roots must be non-empty strings")
            unique.setdefault(candidate.replace("\\", "/").rstrip("/").casefold(), candidate)
        candidates = [unique[key] for key in sorted(unique)]
        if not candidates:
            continue
        if len(candidates) == 1:
            return {"status": "resolved", "source": source, "project_root": candidates[0], "candidates": candidates}
        return {"status": "needs_decision", "source": source, "project_root": None, "candidates": candidates}
    return {"status": "needs_decision", "source": None, "project_root": None, "candidates": []}


def resolve_queries(
    catalog: dict[str, Any],
    queries: tuple[str, ...],
    *,
    load_policies: dict[str, str] | None = None,
) -> dict[str, Any]:
    candidates = _candidates(catalog)
    results: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    proposed: dict[str, dict[str, str]] = {}
    policy_required: dict[str, dict[str, str]] = {}
    warnings: list[str] = []
    descriptions = {
        str(candidate["canonical"]): str(candidate.get("description", ""))
        for candidate in candidates
        if candidate["kind"] == "skill"
    }
    for raw_query in queries:
        query = raw_query.strip()
        if not query:
            raise CatalogError("queries must be non-empty strings")
        ranked = []
        for candidate in candidates:
            score, reason = _score(query, candidate)
            if score:
                ranked.append({
                    "kind": candidate["kind"],
                    "canonical": candidate["canonical"],
                    "name": candidate["name"],
                    "score": score,
                    "reason": reason,
                    "capabilities": list(candidate["capabilities"]),
                })
        ranked.sort(key=lambda item: (-item["score"], item["kind"], item["canonical"]))
        top_score = ranked[0]["score"] if ranked else 0
        top = [item for item in ranked if item["score"] == top_score]
        resolution = "zero_match" if not ranked else ("resolved" if len(top) == 1 and top_score >= 85 else "ambiguous")
        selected_item = top[0] if resolution == "resolved" else None
        if selected_item:
            selected.append({key: selected_item[key] for key in ("kind", "canonical", "name", "reason")})
            if selected_item["kind"] == "provider" and not selected_item["capabilities"]:
                warnings.append(f"provider_capabilities_missing:{selected_item['canonical']}")
            for capability in selected_item["capabilities"]:
                skill = capability["skill"]
                load_policy = (load_policies or {}).get(skill)
                proposed[skill] = {"skill": skill}
                if load_policy is None:
                    policy_required[skill] = {
                        "skill": skill,
                        **(
                            {"description": descriptions[skill]}
                            if descriptions.get(skill)
                            else {}
                        ),
                        **(
                            {"side_effect": capability["side_effect"]}
                            if "side_effect" in capability
                            else {}
                        ),
                    }
                elif load_policy not in SKILL_LOAD_POLICIES:
                    raise CatalogError(
                        f"load policy for {skill} must be one of "
                        f"{sorted(SKILL_LOAD_POLICIES)}"
                    )
        results.append({"query": query, "resolution": resolution, "candidates": ranked})
    unknown_policy_skills = sorted(set(load_policies or {}) - set(proposed))
    if unknown_policy_skills:
        raise CatalogError(
            f"load policy has no selected Skill: {', '.join(unknown_policy_skills)}"
        )
    status = "resolved" if all(item["resolution"] == "resolved" for item in results) and not any(
        warning.startswith("provider_conflict:") for warning in warnings
    ) and not policy_required else "needs_decision"
    return {
        "status": status,
        "queries": results,
        "selected": selected,
        "proposed_skill_loadings": [
            {
                "skill": skill,
                "load_policy": (load_policies or {})[skill],
            }
            for skill in sorted(proposed)
            if skill in (load_policies or {})
        ],
        "skill_policy_decisions_required": [
            policy_required[skill]
            for skill in sorted(policy_required)
        ],
        "warnings": sorted(set(warnings)),
    }


def _load_policy_args(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        parts = value.split("::")
        if len(parts) != 2 or not all(part.strip() for part in parts):
            raise CatalogError("load policy must be <canonical-skill>::<policy>")
        skill, policy = (part.strip() for part in parts)
        if skill in parsed:
            raise CatalogError(f"duplicate load policy: {skill}")
        parsed[skill] = policy
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve setup-project provider and Skill queries.")
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--load-policy", action="append", default=[])
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        data = json.loads(args.catalog.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise CatalogError("catalog root must be an object")
        result = resolve_queries(
            data,
            tuple(args.query),
            load_policies=_load_policy_args(args.load_policy),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, CatalogError) as exc:
        result = {"status": "refused", "error": str(exc)}
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "resolved" else 2


if __name__ == "__main__":
    raise SystemExit(main())
