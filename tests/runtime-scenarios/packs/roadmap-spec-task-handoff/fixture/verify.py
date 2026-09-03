from pathlib import Path


ROOT = Path(__file__).resolve().parent
ALLOWED = {
    "AGENTS.md",
    "instructions.md",
    "project-facts.md",
    "roadmap.md",
    "verify.py",
}


def main() -> int:
    files = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
    }
    unexpected = sorted(files - ALLOWED)
    missing = sorted(ALLOWED - files)
    if unexpected:
        print(f"ERROR: unexpected files: {unexpected}")
    if missing:
        print(f"ERROR: missing scenario files: {missing}")
    if unexpected or missing:
        return 1
    print("OK: Roadmap Spec task handoff scenario root remained read-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
