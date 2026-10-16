"""Replay this bounded merge-review input without changing Git state."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    output = args.output.resolve()
    if output.exists():
        parser.error("output already exists; choose a fresh isolated directory")
    fixture = source / "fixture"
    provenance = json.loads((fixture / "provenance.json").read_text(encoding="utf-8"))
    for relative, expected in provenance["sha256"].items():
        actual = hashlib.sha256((fixture / relative).read_bytes()).hexdigest()
        if actual != expected:
            parser.error(f"fixture hash mismatch: {relative}")
    output.mkdir(parents=True)
    shutil.copytree(fixture, output / "input")
    shutil.copyfile(source / "task.md", output / "instructions.md")
    comparisons = output / "comparisons"
    comparisons.mkdir()
    records = []
    for name in ("workflow.md", "artifacts.md"):
        for left, right in (("base", "main"), ("base", "incoming"),
                            ("main", "result"), ("incoming", "result")):
            records.append((f"{name}.{left}-{right}", [
                "git", "diff", "--no-index", "--no-ext-diff", "--",
                f"input/{left}/{name}", f"input/{right}/{name}",
            ], {0, 1}))
        records.append((f"{name}.automatic-merge", [
            "git", "merge-file", "--diff3", "-p", "--",
            f"input/main/{name}", f"input/base/{name}",
            f"input/incoming/{name}",
        ], set(range(128))))
    results = []
    for label, command, accepted in records:
        completed = subprocess.run(command, cwd=output, capture_output=True)
        stdout = comparisons / f"{label}.stdout"
        stderr = comparisons / f"{label}.stderr"
        stdout.write_bytes(completed.stdout)
        stderr.write_bytes(completed.stderr)
        results.append({"command": command, "exit_code": completed.returncode,
                        "stdout": str(stdout.relative_to(output)),
                        "stderr": str(stderr.relative_to(output))})
        if completed.returncode not in accepted:
            (comparisons / "commands.json").write_text(
                json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            raise SystemExit(f"comparison failed: {label}; raw results retained")
    (comparisons / "commands.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "commands": len(results),
                      "semantic_verdict": "not_evaluated"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
