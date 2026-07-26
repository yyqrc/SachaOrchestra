"""Check the minimal metadata contract for a Sacha Orchestra source release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CORE = PLUGIN / "core" / "workflow-contract.md"
ARTIFACT = PLUGIN / "core" / "artifact-protocol.md"
CODEX_ADAPTER = PLUGIN / "adapters" / "codex" / "runtime-adapter.md"
CLAUDE_ADAPTER = PLUGIN / "adapters" / "claudecode" / "runtime-adapter.md"
SETUP_GENERATOR = PLUGIN / "skills" / "setup-project" / "scripts" / "generate_project_integration.py"
EVOLUTION = ROOT / "docs" / "architecture" / "evolution.md"
ROOT_README = ROOT / "README.md"
PLUGIN_README = PLUGIN / "README.md"
AGENTS = ROOT / "AGENTS.md"
SKILL_ROOTS = tuple(sorted((PLUGIN / "skills").iterdir()))
ROLE_SKILLS = tuple(path / "SKILL.md" for path in SKILL_ROOTS)
SKILL_METADATA = tuple(path / "agents" / "openai.yaml" for path in SKILL_ROOTS)
EXPLICIT_ONLY_SKILLS = {"clarify", "setup-project"}
RUNTIME_API_MARKERS = (
    "create_thread",
    "wait_threads",
    "send_message_to_thread",
    "spawn_agent",
    "wait_agent",
    "send_message",
    "followup_task",
    "interrupt_agent",
    "<codex_",
    "Goal-first",
    "G1 Goal-only",
    "G2 Spec-only",
    "G3 Spec + Goal",
    "model + thinking",
    "terminal callback",
    "joined wait",
    "create/reuse",
    "docs/CONTEXT.md",
    "docs/adr/",
    "cgame-unity",
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, check=False, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--phase", choices=("candidate", "release"), required=True)
    args = parser.parse_args()

    checks = 0
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(message)

    version = args.version
    tag = f"v{version}"
    manifest = json.loads(text(MANIFEST))
    claude_manifest = json.loads(text(CLAUDE_MANIFEST))
    core = text(CORE)
    artifact = text(ARTIFACT)
    codex_adapter = text(CODEX_ADAPTER)
    claude_adapter = text(CLAUDE_ADAPTER)
    setup_generator = text(SETUP_GENERATOR)
    evolution = text(EVOLUTION)
    root_readme = text(ROOT_README)
    plugin_readme = text(PLUGIN_README)
    agents = text(AGENTS)
    formal_documents = {
        str(path.relative_to(ROOT)): text(path)
        for path in (CORE, ARTIFACT, CODEX_ADAPTER, CLAUDE_ADAPTER, *ROLE_SKILLS)
    }
    role_skill_documents = {
        str(path.relative_to(ROOT)): text(path)
        for path in ROLE_SKILLS
    }
    skill_metadata_documents = {
        path.parent.parent.name: text(path)
        for path in SKILL_METADATA
    }
    adapters = {
        "Codex": codex_adapter,
        "Claude Code": claude_adapter,
    }

    check(
        manifest.get("version") == version and claude_manifest.get("version") == version,
        "Deployment manifest versions do not match --version",
    )
    core_version = re.search(r"(?m)^> Contract Version: ([0-9]+)$", core)
    artifact_version = re.search(r"(?m)^> Contract Version: ([0-9]+)", artifact)
    check(core_version is not None, "Workflow Contract version is missing")
    check(artifact_version is not None, "Artifact Protocol version is missing")
    expected_mapping = (
        f"> Implements: Workflow Contract {core_version.group(1)}；"
        f"Artifact Protocol {artifact_version.group(1)}"
        if core_version and artifact_version
        else ""
    )
    check(expected_mapping in codex_adapter, "Codex Adapter contract mapping is stale")
    check(expected_mapping in claude_adapter, "Claude Code Adapter contract mapping is stale")
    check("Product Version:" not in core and "Product Version:" not in artifact, "Core contracts still own product release history")
    check("Adapter Version:" not in codex_adapter and "Adapter Version:" not in claude_adapter, "Runtime Adapters still own product release history")
    check(len(re.findall(r"(?m)^> 当前 release：", evolution)) == 1, "Evolution must have exactly one current release")
    check(len(re.findall(r"(?m)^> 当前 source candidate：", evolution)) == 1, "Evolution must have exactly one current source candidate")
    check("source candidate" not in codex_adapter and "source candidate" not in claude_adapter, "Adapter still owns candidate state")
    check("../codex/runtime-adapter.md" not in claude_adapter, "Claude Code Adapter references Codex Adapter")
    check("../claudecode/runtime-adapter.md" not in codex_adapter, "Codex Adapter references Claude Code Adapter")
    check(len(codex_adapter.splitlines()) <= 200, "Codex Adapter exceeds the bounded mapping surface")
    check(len(claude_adapter.splitlines()) <= 200, "Claude Code Adapter exceeds the bounded mapping surface")
    check(len(core.splitlines()) <= 220, "Workflow Contract exceeds the bounded Core surface")
    check(len(artifact.splitlines()) <= 90, "Artifact Protocol exceeds the bounded Core surface")
    check(
        sum(len(content) for content in (core, artifact, *role_skill_documents.values())) <= 18000,
        "Formal Core and Skill documents exceed the total text budget",
    )
    for path, content in role_skill_documents.items():
        lines = content.splitlines()
        check(len(lines) <= 35, f"Role Skill exceeds the bounded procedure surface: {path}")
        check(max((len(line) for line in lines), default=0) <= 220, f"Role Skill contains an oversized compound line: {path}")
        links = set(re.findall(r"\]\(([^)]+)\)", content))
        allowed_links = {
            "../../core/workflow-contract.md",
            "../../core/artifact-protocol.md",
            "scripts/resolve_capability_queries.py",
            "scripts/generate_project_integration.py",
        }
        check(links <= allowed_links, f"Role Skill adds a non-canonical documentation dependency: {path}")
    metadata_failures: list[str] = []
    for skill_root, skill_path, metadata_path in zip(SKILL_ROOTS, ROLE_SKILLS, SKILL_METADATA):
        skill = text(skill_path)
        metadata = text(metadata_path)
        name_match = re.search(r"(?m)^name: ([a-z0-9-]+)$", skill)
        skill_name = name_match.group(1) if name_match else ""
        short_match = re.search(r'(?m)^  short_description: "([^"]+)"$', metadata)
        prompt_match = re.search(r'(?m)^  default_prompt: "([^"]+)"$', metadata)
        if skill_name != skill_root.name:
            metadata_failures.append(f"{skill_root.name}: name")
        if short_match is None:
            metadata_failures.append(f"{skill_root.name}: short_description missing")
        elif not 25 <= len(short_match.group(1)) <= 64:
            metadata_failures.append(f"{skill_root.name}: short_description length")
        if prompt_match is None:
            metadata_failures.append(f"{skill_root.name}: default_prompt missing")
        elif f"$sacha-orchestra:{skill_name}" not in prompt_match.group(1):
            metadata_failures.append(f"{skill_root.name}: canonical invocation")
        implicit_disabled = re.search(r"(?m)^  allow_implicit_invocation: false$", metadata) is not None
        if implicit_disabled != (skill_name in EXPLICIT_ONLY_SKILLS):
            metadata_failures.append(f"{skill_root.name}: implicit policy")
    check(
        not metadata_failures,
        "Skill metadata coherence failed: " + ", ".join(metadata_failures),
    )
    allowed_adapter_links = {
        "../../core/workflow-contract.md",
        "../../core/artifact-protocol.md",
    }
    for runtime, adapter in adapters.items():
        adapter_links = set(re.findall(r"\]\(([^)]+)\)", adapter))
        check(
            adapter_links <= allowed_adapter_links,
            f"{runtime} Adapter depends on a document outside Core/Artifact Protocol",
        )
    check(
        all(re.search(r"\b0\.1\.\d+\b", content) is None for content in formal_documents.values()),
        "Formal plugin document still contains product release history",
    )
    forbidden_compatibility = (
        "source_thread_id",
        "observed_outcome",
        "spec-author",
        "Schema v1",
        "Schema v2",
        "Legacy alias",
        "legacy fallback",
        "旧四档",
        "兼容提示",
        "Migration note",
        "待验证项",
    )
    for marker in forbidden_compatibility:
        check(
            all(marker not in content for content in formal_documents.values()),
            f"Formal plugin document still contains compatibility/history marker: {marker}",
        )
    for marker in RUNTIME_API_MARKERS:
        check(
            all(marker not in content for content in role_skill_documents.values()),
            f"Role Skill leaks Runtime API detail: {marker}",
        )
    metadata_runtime_leaks = [
        f"{skill}: {marker}"
        for skill, content in skill_metadata_documents.items()
        for marker in RUNTIME_API_MARKERS
        if marker in content
    ]
    check(
        not metadata_runtime_leaks,
        "Skill metadata leaks Runtime API detail: " + ", ".join(metadata_runtime_leaks),
    )
    for marker in ("K0 Current Context", "F0 In-scope Correction", "S0 No Setup", "## 7. Conformance"):
        check(marker not in core, f"Workflow Contract still owns a single-Skill taxonomy or duplicate checklist: {marker}")
    retired_generator_markers = (
        "Goal-first",
        "G1 Goal-only",
        "G2 Spec-only",
        "G3 Spec + Goal",
        "## 简明操作模板",
        "`L0 Local Direct`",
        "`D0 Sacha Direct`",
        "Planner/Reviewer Gate",
    )
    emitted_retired_markers = [marker for marker in retired_generator_markers if marker in setup_generator]
    check(
        not emitted_retired_markers,
        "Generated Project Integration still emits retired concepts: " + ", ".join(emitted_retired_markers),
    )
    check("docs/architecture/evolution.md" in root_readme, "Root README does not link release authority")
    check("../../docs/architecture/evolution.md" in plugin_readme, "Plugin README does not link release authority")
    check("docs/architecture/evolution.md" in agents, "AGENTS does not link release authority")
    check("当前 Git release、源码与 manifest：" not in root_readme, "Root README still duplicates current release state")
    check("是当前 Git release" not in plugin_readme, "Plugin README still duplicates current release state")
    check(len(root_readme.splitlines()) <= 60, "Root README exceeds the bounded entrypoint surface")
    check(len(plugin_readme.splitlines()) <= 40, "Plugin README exceeds the bounded entrypoint surface")
    check(
        len(re.findall(r"\b0\.1\.\d+\b", root_readme)) <= 1,
        "Root README still contains a version-by-version chronology",
    )
    check(
        re.search(r"\b0\.1\.\d+\b", plugin_readme) is None,
        "Plugin README still contains product version history",
    )
    duplicated_readme_markers = (
        "`L0 Local Direct`",
        "`D0 Sacha Direct`",
        "`V0`",
        "九字段 Handoff Envelope",
        "## Artifact 与 Handoff 行为",
        "## 迁移说明",
    )
    duplicated_readme_surfaces = [marker for marker in duplicated_readme_markers if marker in plugin_readme]
    check(
        not duplicated_readme_surfaces,
        "Plugin README still duplicates formal contract surfaces: " + ", ".join(duplicated_readme_surfaces),
    )

    if args.phase == "candidate":
        check(f"> 当前 source candidate：`{version}`" in evolution, "Evolution candidate does not match --version")
    else:
        check(f"> 当前 release：`{version}`" in evolution, "Evolution release does not match --version")
        check("> 当前 source candidate：无" in evolution, "Released state still has a source candidate")
        tag_ref = git("rev-parse", "--verify", f"refs/tags/{tag}")
        check(tag_ref.returncode == 0, "Annotated release tag is missing")
        tag_commit = git("rev-parse", f"{tag}^{{}}")
        head_commit = git("rev-parse", "HEAD")
        check(tag_commit.returncode == 0 and tag_commit.stdout.strip() == head_commit.stdout.strip(), "Release tag does not resolve to HEAD")

    print(f"release_coherence_checks={checks}")
    print(f"release_coherence_failures={len(failures)}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
