#!/usr/bin/env python3
"""Build an in-place completion plan for one current Spec."""

from __future__ import annotations

import argparse
import json
import re
import stat
from pathlib import Path
from typing import Any, Sequence


STATUS_RE = re.compile(
    r"^(?P<prefix>\s*(?:>\s*|-\s*)?状态\s*[：:]\s*)(?P<value>.*?)(?P<ending>\r?\n)?$"
)
ENGLISH_APPROVED_RE = re.compile(r"^approved(?:$|[\s,，;；:：])", re.IGNORECASE)


class CloseoutError(RuntimeError):
    """A fail-closed closeout error."""


def _result(**values: Any) -> dict[str, Any]:
    return {"schema_version": 1, **values}


def _decode(data: bytes) -> tuple[str, bytes]:
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    try:
        return data[len(bom) :].decode("utf-8"), bom
    except UnicodeDecodeError as exc:
        raise CloseoutError("spec.md must be valid UTF-8") from exc


def _replace_status(data: bytes) -> tuple[bytes, str, int, str, str]:
    text, bom = _decode(data)
    lines = text.splitlines(keepends=True)
    candidates: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(lines[:12]):
        if index > 0 and line.startswith("## "):
            break
        match = STATUS_RE.match(line)
        if match is not None:
            candidates.append((index, match))
    if len(candidates) != 1:
        raise CloseoutError("spec.md must contain exactly one header status line")

    index, match = candidates[0]
    status_line = lines[index]
    previous = match.group("value").strip()
    if previous == "已完成":
        current_line = status_line.removesuffix("\r\n").removesuffix("\n")
        return data, previous, index + 1, current_line, current_line
    if "已批准" not in previous and ENGLISH_APPROVED_RE.match(previous) is None:
        raise CloseoutError("spec.md must be approved before completion")
    ending = match.group("ending") or ""
    before_line = status_line.removesuffix("\r\n").removesuffix("\n")
    after_line = f"{match.group('prefix')}已完成"
    lines[index] = f"{after_line}{ending}"
    return (
        bom + "".join(lines).encode("utf-8"),
        previous,
        index + 1,
        before_line,
        after_line,
    )


def complete_spec(
    *,
    spec_paths: Sequence[Path],
    goal_status: str,
    required_checks_satisfied: bool,
    context_writable: bool,
) -> dict[str, Any]:
    try:
        if len(spec_paths) != 1:
            raise CloseoutError("exactly one current Spec path is required")
        if goal_status != "goal_complete":
            raise CloseoutError("Spec completion requires goal_complete")
        if not required_checks_satisfied:
            raise CloseoutError("required verification and Review must be satisfied")
        if not context_writable:
            raise CloseoutError("current context is read-only")

        path = Path(spec_paths[0])
        if path.name.lower() != "spec.md":
            raise CloseoutError("current Spec path must name spec.md")
        if path.is_symlink() or not path.is_file():
            raise CloseoutError("current Spec path must be one reachable regular file")
        mode = path.stat().st_mode
        if not mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
            raise CloseoutError("spec.md is read-only")

        before = path.read_bytes()
        after, previous_status, line_number, before_line, after_line = _replace_status(before)
        if after == before:
            return _result(
                status="no_op",
                transaction="no_changes",
                target=str(path.resolve()),
                previous_status=previous_status,
                new_status="已完成",
            )

        return _result(
            status="ready",
            transaction="dry_run",
            target=str(path.resolve()),
            previous_status=previous_status,
            new_status="已完成",
            edit={
                "line_number": line_number,
                "before": before_line,
                "after": after_line,
            },
        )
    except CloseoutError as exc:
        return _result(status="refused", transaction="no_write", conflicts=[str(exc)])
    except OSError as exc:
        return _result(status="failed", transaction="no_write", conflicts=[str(exc)])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-path", action="append", default=[])
    parser.add_argument("--goal-status", required=True)
    parser.add_argument("--required-checks-satisfied", action="store_true")
    parser.add_argument("--context-writable", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = complete_spec(
        spec_paths=[Path(value) for value in args.spec_path],
        goal_status=args.goal_status,
        required_checks_satisfied=args.required_checks_satisfied,
        context_writable=args.context_writable,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"ready", "ok", "no_op"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
