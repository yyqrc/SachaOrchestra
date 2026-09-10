import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def run(mode, source, output):
    return subprocess.run(
        [sys.executable, str(ROOT / "pipeline.py"), mode, str(source), str(output)],
        capture_output=True, text=True, encoding="utf-8", timeout=20,
    )


def main():
    with tempfile.TemporaryDirectory(dir=ROOT) as scratch:
        scratch = Path(scratch)
        for mode, expected in (("receipts", {"A": 15, "B": 7}),
                               ("shipments", {"A": 3, "B": -1})):
            output = scratch / (mode + ".json")
            result = run(mode, ROOT / (mode + ".json"), output)
            assert result.returncode == 0, (mode, result.stdout, result.stderr)
            assert json.loads(output.read_text(encoding="utf-8")) == expected, mode
            source = scratch / (mode + "-invalid.json")
            original = json.loads((ROOT / (mode + ".json")).read_text(encoding="utf-8"))
            for bad in (True, -1, 1.5):
                original["rows"][0]["quantity"] = bad
                source.write_text(json.dumps(original), encoding="utf-8")
                rejected = scratch / (mode + "-rejected.json")
                result = run(mode, source, rejected)
                assert result.returncode != 0, (mode, bad, "invalid quantity accepted")
                assert not rejected.exists(), (mode, bad, "invalid input wrote output")
        print("PASS: receipts, shipments, invalid quantities and output protection")


if __name__ == "__main__":
    main()
