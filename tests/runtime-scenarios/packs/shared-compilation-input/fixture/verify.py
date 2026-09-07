import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
inputs = {name: (root / name).read_bytes() for name in ("a.py", "b.py")}
result = {"inputs": {name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()}}
try:
    values = []
    for name, data in inputs.items():
        namespace = {}
        exec(compile(data, name, "exec"), namespace)
        values.append(namespace["value"]())
    result.update(actual=sum(values), expected=7, passed=sum(values) == 7)
except Exception as error:
    result.update(passed=False, error=f"{type(error).__name__}: {error}")
with (root / "verification-events.jsonl").open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(result, ensure_ascii=False) + "\n")
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(0 if result["passed"] else 1)
