#!/usr/bin/env python3
"""Resolve loose provider/Skill queries against an explicit context catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


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


def _capabilities(value: Any, label: str) -> tuple[dict[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise CatalogError(f"{label} must be an array")
    parsed: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise CatalogError(f"{label}[{index}] must be an object")
        capability_id = item.get("id")
        skill = item.get("skill")
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise CatalogError(f"{label}[{index}].id must be a non-empty string")
        if not isinstance(skill, str) or not skill.strip():
            raise CatalogError(f"{label}[{index}].skill must be a non-empty string")
        parsed.append({"id": capability_id.strip(), "skill": skill.strip()})
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
            candidates.append({
                "kind": kind,
                "canonical": canonical.strip(),
                "name": name.strip(),
                "description": description.strip(),
                "aliases": _strings(item.get("aliases"), f"{key}[{index}].aliases"),
                "keywords": _strings(item.get("keywords"), f"{key}[{index}].keywords"),
                "capabilities": _capabilities(item.get("capabilities"), f"{key}[{index}].capabilities"),
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


def resolve_queries(catalog: dict[str, Any], queries: tuple[str, ...]) -> dict[str, Any]:
    candidates = _candidates(catalog)
    results: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    proposed: dict[str, str] = {}
    warnings: list[str] = []
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
                existing = proposed.get(capability["id"])
                if existing is not None and existing != capability["skill"]:
                    warnings.append(f"capability_conflict:{capability['id']}:{existing}:{capability['skill']}")
                else:
                    proposed[capability["id"]] = capability["skill"]
        results.append({"query": query, "resolution": resolution, "candidates": ranked})
    status = "resolved" if all(item["resolution"] == "resolved" for item in results) and not any(
        warning.startswith("capability_conflict:") for warning in warnings
    ) else "needs_decision"
    return {
        "status": status,
        "queries": results,
        "selected": selected,
        "proposed_capability_bindings": [
            {"id": capability_id, "skill": proposed[capability_id]}
            for capability_id in sorted(proposed)
        ],
        "warnings": sorted(set(warnings)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve loose setup-project provider and Skill queries.")
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--query", action="append", default=[])
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        data = json.loads(args.catalog.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise CatalogError("catalog root must be an object")
        result = resolve_queries(data, tuple(args.query))
    except (OSError, UnicodeError, json.JSONDecodeError, CatalogError) as exc:
        result = {"status": "refused", "error": str(exc)}
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "resolved" else 2


if __name__ == "__main__":
    raise SystemExit(main())
