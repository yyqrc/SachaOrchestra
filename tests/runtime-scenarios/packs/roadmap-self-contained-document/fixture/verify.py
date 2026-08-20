from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
STATIC_FILES = {
    "AGENTS.md",
    "instructions.md",
    "project-facts.md",
    "verify.py",
    "docs/workflow-rule.md",
    "docs/archive/.gitkeep",
    "docs/plan/2026-08-10-depth-fetch-baseline/spec.md",
    "docs/roadmap/.gitkeep",
    "templates/profiles.json",
    "templates/roadmap-project-roadmap-v1.md",
}


def main() -> int:
    files = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
    }
    roadmap_files = sorted(
        path for path in files if path.startswith("docs/roadmap/") and path != "docs/roadmap/.gitkeep"
    )
    errors = []
    if len(roadmap_files) != 1:
        errors.append(f"expected one Roadmap file, got {roadmap_files}")
    elif re.fullmatch(
        r"docs/roadmap/[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]{0,63}-roadmap\.md",
        roadmap_files[0],
    ) is None:
        errors.append(f"invalid Roadmap path: {roadmap_files[0]}")
    unexpected = sorted(files - STATIC_FILES - set(roadmap_files))
    missing = sorted(STATIC_FILES - files)
    if unexpected:
        errors.append(f"unexpected files: {unexpected}")
    if missing:
        errors.append(f"missing files: {missing}")
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors))
        return 1
    print(f"OK: Roadmap created at {roadmap_files[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
