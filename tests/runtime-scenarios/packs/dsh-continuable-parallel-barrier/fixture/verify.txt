from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

expected_accounts = [
    {"id": 1, "owner": "alice", "enabled": True},
    {"id": 2, "owner": "bob", "enabled": False},
    {"id": 3, "owner": "carol", "enabled": True},
]
expected_routes = [
    {"path": "/api/admin", "methods": ["DELETE", "POST"]},
    {"path": "/api/users", "methods": ["GET", "POST"]},
    {"path": "/health", "methods": ["GET"]},
]

accounts = json.loads((ROOT / "output" / "accounts.json").read_text(encoding="utf-8"))
routes = json.loads((ROOT / "output" / "routes.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "output" / "manifest.json").read_text(encoding="utf-8"))

assert accounts == expected_accounts, accounts
assert routes == expected_routes, routes
assert manifest == {"accounts": len(expected_accounts), "routes": len(expected_routes)}, manifest
print("verification=pass accounts=3 routes=3")
