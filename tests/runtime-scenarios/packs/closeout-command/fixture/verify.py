from pathlib import Path


root = Path(__file__).resolve().parent
spec = root / "current" / "spec.md"
content = spec.read_text(encoding="utf-8")
errors = []

if "> 状态：已完成" not in content:
    errors.append("current/spec.md status must be completed")
if "只验证当前 Spec 原位完成；正文必须保持不变。" not in content:
    errors.append("Spec body changed")
if not spec.is_file():
    errors.append("current/spec.md must remain in place")
if (root / "docs" / "done").exists():
    errors.append("docs/done must not be created")
if (root / "docs" / "archive").exists():
    errors.append("project documentation must not be created")
if len(list(root.rglob("spec.md"))) != 1:
    errors.append("Spec must not be copied or moved")

if errors:
    raise SystemExit("\n".join(errors))
print("closeout_command_status=pass")
