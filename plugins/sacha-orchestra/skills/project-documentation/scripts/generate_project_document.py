#!/usr/bin/env python3
"""Validate, render and atomically create one project publication document."""

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
INTEGRATION_SCHEMA = "<!-- Schema Version: 3 -->"
INPUT_SCHEMA_VERSION = "1"
DOCUMENT_TYPES = {"change-archive", "system-guide"}
TRIGGERS = {"human-request", "goal-closeout"}
POLICIES = {"disabled", "on-request", "required-at-closeout"}
ROOT_KINDS = {"project-relative", "external-absolute"}
WRITE_AUTHORIZATIONS = {"bounded-closeout", "per-write-confirmation"}
MAX_TITLE_CHARS = 120
MAX_SECTION_CHARS = 8000
MAX_DOCUMENT_CHARS = 24000
MAX_DOCUMENT_BYTES = 64 * 1024
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
INTERNAL_LOCATORS = (
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


def _field(section: str, label: str) -> str:
    match = re.search(rf"(?m)^- {re.escape(label)} = `([^`\r\n]+)`\r?$", section)
    if match is None:
        raise DocumentError(f"Project documentation field is missing: {label}")
    return match.group(1)


def parse_project_integration(data: bytes) -> dict[str, str | None]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DocumentError("Project Integration must be UTF-8") from exc
    if INTEGRATION_GENERATOR not in text or INTEGRATION_SCHEMA not in text:
        raise DocumentError("Project Integration is not a confirmed managed Schema v3 file")
    if _section(text, "### Unresolved") != "- 无":
        raise DocumentError("Project Integration has unresolved decisions")
    if _section(text, "### Conflicts") != "- 无":
        raise DocumentError("Project Integration has conflicts")

    documentation = _section(text, "### Project documentation")
    document_types = re.search(
        r"(?m)^- document types = `change-archive`、`system-guide`\r?$",
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
        return result
    if result["root_kind"] not in ROOT_KINDS:
        raise DocumentError("Project documentation root kind is invalid")
    if result["write_authorization"] not in WRITE_AUTHORIZATIONS:
        raise DocumentError("Project documentation write authorization is invalid")
    if result["root"] in {None, "none"}:
        raise DocumentError("enabled documentation root is missing")
    expected_portability = (
        "portable" if result["root_kind"] == "project-relative" else "non-portable"
    )
    if result["portability"] != expected_portability:
        raise DocumentError("Project documentation portability is inconsistent")
    return result


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
    documentation: dict[str, str | None],
) -> Path:
    if documentation["policy"] == "disabled":
        raise DocumentError("Project documentation is disabled")
    raw = str(documentation["root"])
    kind = documentation["root_kind"]
    if kind == "project-relative":
        pure = _normalized_relative_path(raw, "documentation root")
        root = (project_root / Path(*pure.parts)).resolve(strict=False)
        try:
            root.relative_to(project_root)
        except ValueError as exc:
            raise DocumentError("documentation root escapes project root") from exc
    elif kind == "external-absolute":
        candidate = Path(raw)
        if not candidate.is_absolute():
            raise DocumentError("external documentation root is not absolute")
        lexical = Path(os.path.abspath(raw))
        resolved = candidate.resolve(strict=False)
        if lexical == Path(lexical.anchor) or resolved == Path(resolved.anchor):
            raise DocumentError("external documentation root must not be a drive or share root")
        try:
            resolved.relative_to(project_root)
        except ValueError:
            pass
        else:
            raise DocumentError(
                "documentation root inside project must be project-relative"
            )
        root = resolved
    else:
        raise DocumentError("Project documentation root kind is invalid")
    try:
        if not root.is_dir():
            raise DocumentError("documentation root is absent or unreachable")
    except OSError as exc:
        raise DocumentError("documentation root is unreachable") from exc
    return root


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
    for pattern in INTERNAL_LOCATORS:
        if pattern.search(normalized):
            raise DocumentError(f"{label} contains an internal or machine-local locator")
    return normalized


def parse_document_input(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DocumentError("document input root must be an object")
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
        raise DocumentError("document_type must be change-archive or system-guide")
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
    for pattern in INTERNAL_LOCATORS:
        if pattern.search(title):
            raise DocumentError("title contains an internal or machine-local locator")

    output = _normalized_relative_path(value["output_path"], "output_path")
    if output.suffix.casefold() != ".md":
        raise DocumentError("output_path must end in .md")
    sections = value["sections"]
    if not isinstance(sections, dict) or set(sections) != {key for key, _ in SECTIONS}:
        raise DocumentError("sections must contain the exact publication section keys")
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


def render_document(document: dict[str, Any]) -> bytes:
    blocks = [f"# {document['title']}"]
    for key, heading in SECTIONS:
        blocks.append(f"## {heading}\n\n{document['sections'][key]}")
    return ("\n\n".join(blocks) + "\n").encode("utf-8")


def parse_generated_document(data: bytes) -> dict[str, Any]:
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
    expected_headings = [heading for _, heading in SECTIONS]
    if headings != expected_headings:
        raise DocumentError("generated document headings are missing, duplicated or out of order")
    sections: dict[str, str] = {}
    for key, heading in SECTIONS:
        match = re.search(
            rf"(?ms)^## {re.escape(heading)}\s*\r?\n(.*?)(?=^## |\Z)",
            text,
        )
        if match is None:
            raise DocumentError(f"generated document section is missing: {heading}")
        sections[key] = _public_text(match.group(1), f"generated.{key}")
    return {"title": title_match.group(1), "sections": sections}


def _target_path(root: Path, output_path: str) -> Path:
    pure = _normalized_relative_path(output_path, "output_path")
    target = root.joinpath(*pure.parts)
    parent = target.parent.resolve(strict=False)
    try:
        parent.relative_to(root)
    except ValueError as exc:
        raise DocumentError("output parent escapes documentation root") from exc
    if not parent.is_dir():
        raise DocumentError("output parent directory does not exist")
    if target.exists():
        raise DocumentError("output target already exists; overwrite is forbidden")
    return target


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
        pure_rule = _normalized_relative_path(workflow_rule_path, "workflow_rule_path")
        workflow = project.joinpath(*pure_rule.parts).resolve(strict=False)
        try:
            workflow.relative_to(project)
        except ValueError as exc:
            raise DocumentError("workflow rule escapes project root") from exc
        workflow_data = workflow.read_bytes()
        workflow_hash = sha256_bytes(workflow_data)
        documentation = parse_project_integration(workflow_data)
        document = parse_document_input(document_input)
        _authorize(
            documentation,
            document,
            per_write_confirmed=per_write_confirmed,
        )
        root = _resolve_document_root(project, documentation)
        target = _target_path(root, document["output_path"])
        generated = render_document(document)
        parsed = parse_generated_document(generated)
        generated_hash = sha256_bytes(generated)
        result.update(
            status="ready",
            transaction="dry_run",
            document_type=document["document_type"],
            target=str(target),
            sha256=generated_hash,
            parsed={"title": parsed["title"], "sections": list(parsed["sections"])},
        )
        if not write:
            return result
        write_started = True
        if sha256_bytes(workflow.read_bytes()) != workflow_hash:
            raise DocumentError("Project Integration changed after validation")
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
            parse_generated_document(written)
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
        description="Validate and create one self-contained project publication document."
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
