"""Validate machine-readable release identity and executable entrypoints.

Markdown contracts, README text, Skill prose, and Runtime behavior are outside
this validator. They require owner review and scenario/runtime evidence.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
AGENT_PLUGIN_MANIFEST = PLUGIN / "plugin.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CURSOR_MARKETPLACE = ROOT / ".cursor-plugin" / "marketplace.json"

SETUP_PROJECT_SCRIPT = (
    PLUGIN / "skills" / "setup-project" / "scripts" / "generate_project_integration.py"
)
SETUP_AGENTS_SCRIPT = (
    PLUGIN / "skills" / "setup-agents" / "scripts" / "setup_agents.py"
)
DOCUMENTATION_SCRIPT = (
    PLUGIN / "skills" / "document-project" / "scripts" / "generate_project_document.py"
)

REQUIRED_ENTRYPOINTS = (
    PLUGIN / "scripts" / "pi_once.ps1",
    PLUGIN / "scripts" / "pi_guard.mjs",
    PLUGIN / "skills" / "setup-project" / "scripts" / "inspect_pi_models.ps1",
    SETUP_PROJECT_SCRIPT,
    SETUP_AGENTS_SCRIPT,
    DOCUMENTATION_SCRIPT,
    PLUGIN / "skills" / "document-project" / "assets" / "change-archive.md",
    PLUGIN / "skills" / "document-project" / "assets" / "system-guide.md",
)

def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--phase", choices=("candidate", "release"), required=True)
    args = parser.parse_args()

    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    version = args.version
    manifest = load_json(MANIFEST)
    claude_manifest = load_json(CLAUDE_MANIFEST)
    agent_plugin_manifest = load_json(AGENT_PLUGIN_MANIFEST)
    marketplace = load_json(MARKETPLACE)
    cursor_marketplace = load_json(CURSOR_MARKETPLACE)

    check(
        isinstance(manifest, dict)
        and isinstance(claude_manifest, dict)
        and isinstance(agent_plugin_manifest, dict)
        and manifest.get("version") == version
        and claude_manifest.get("version") == version
        and agent_plugin_manifest.get("version") == version,
        "Deployment manifest versions do not match --version",
    )
    check(
        isinstance(agent_plugin_manifest, dict)
        and agent_plugin_manifest.get("$schema")
        == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        and agent_plugin_manifest.get("name") == "sacha-orchestra",
        "Agent Plugins manifest identity or schema is invalid",
    )

    marketplace_plugins = marketplace.get("plugins", []) if isinstance(marketplace, dict) else []
    check(
        isinstance(marketplace, dict)
        and marketplace.get("name") == "sacha"
        and marketplace.get("interface", {}).get("displayName") == "Sacha"
        and len(marketplace_plugins) == 1
        and marketplace_plugins[0].get("name") == "sacha-orchestra"
        and marketplace_plugins[0].get("source")
        == {"source": "local", "path": "./plugins/sacha-orchestra"},
        "Marketplace identity or local plugin source is invalid",
    )
    cursor_plugins = (
        cursor_marketplace.get("plugins", [])
        if isinstance(cursor_marketplace, dict)
        else []
    )
    check(
        isinstance(cursor_marketplace, dict)
        and cursor_marketplace.get("name") == "sacha"
        and cursor_marketplace.get("metadata", {}).get("version") == version
        and len(cursor_plugins) == 1
        and cursor_plugins[0].get("name") == "sacha-orchestra"
        and cursor_plugins[0].get("source") == "plugins/sacha-orchestra"
        and cursor_plugins[0].get("version") == version,
        "Cursor marketplace identity, version, or plugin source is invalid",
    )

    for entrypoint in REQUIRED_ENTRYPOINTS:
        check(
            entrypoint.is_file(),
            f"Required production entrypoint is missing: {entrypoint.relative_to(ROOT)}",
        )

    for script in (SETUP_PROJECT_SCRIPT, SETUP_AGENTS_SCRIPT, DOCUMENTATION_SCRIPT):
        if not script.is_file():
            continue
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as exc:
            failures.append(f"Python entrypoint syntax is invalid: {script.name}: {exc}")

    manifest_has_hooks = any(
        isinstance(candidate, dict) and "hooks" in candidate
        for candidate in (manifest, claude_manifest, agent_plugin_manifest)
    )
    check(
        not manifest_has_hooks and not (PLUGIN / "hooks").exists(),
        "Plugin adds an unapproved Hook surface",
    )
    if args.phase == "release":
        tag = f"v{version}"
        tag_type = git("cat-file", "-t", f"refs/tags/{tag}")
        check(
            tag_type.returncode == 0 and tag_type.stdout.strip() == "tag",
            "Annotated release tag is missing",
        )
        tag_commit = git("rev-parse", f"{tag}^{{}}")
        head_commit = git("rev-parse", "HEAD")
        check(
            tag_commit.returncode == 0
            and head_commit.returncode == 0
            and tag_commit.stdout.strip() == head_commit.stdout.strip(),
            "Release tag does not resolve to HEAD",
        )

    print(f"release_coherence_status={'pass' if not failures else 'fail'}")
    print(f"release_coherence_failures={len(failures)}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
