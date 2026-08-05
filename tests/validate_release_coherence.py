"""Check the minimal metadata contract for a Sacha Orchestra source release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sacha-orchestra"
MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
INTAKE = PLUGIN / "core" / "intake-contract.md"
CORE = PLUGIN / "core" / "workflow-contract.md"
ASSURANCE = PLUGIN / "core" / "assurance-contract.md"
COORDINATION = PLUGIN / "core" / "coordination-contract.md"
ARTIFACT = PLUGIN / "core" / "artifact-protocol.md"
CODEX_ADAPTER = PLUGIN / "adapters" / "codex" / "runtime-adapter.md"
CLAUDE_ADAPTER = PLUGIN / "adapters" / "claudecode" / "runtime-adapter.md"
PI_ONCE = PLUGIN / "scripts" / "pi_once.ps1"
PI_GUARD = PLUGIN / "scripts" / "pi_guard.mjs"
SETUP_GENERATOR = PLUGIN / "skills" / "setup-project" / "scripts" / "generate_project_integration.py"
PI_MODEL_INSPECTOR = PLUGIN / "skills" / "setup-project" / "scripts" / "inspect_pi_models.ps1"
SETUP_AGENTS = PLUGIN / "skills" / "setup-agents"
SETUP_AGENTS_SCRIPT = SETUP_AGENTS / "scripts" / "setup_agents.py"
LUNA_WORKER_TEMPLATES = {
    SETUP_AGENTS / "assets" / "sacha-luna-worker.toml": ("sacha_luna_worker", "max"),
    SETUP_AGENTS / "assets" / "sacha-luna-worker-xhigh.toml": ("sacha_luna_worker_xhigh", "xhigh"),
}
SETUP_AGENTS_TEST = ROOT / "tests" / "test_setup_agents.py"
PROJECT_DOCUMENTATION = PLUGIN / "skills" / "project-documentation"
DOCUMENTATION_GENERATOR = (
    PROJECT_DOCUMENTATION / "scripts" / "generate_project_document.py"
)
DOCUMENTATION_TEMPLATES = (
    PROJECT_DOCUMENTATION / "assets" / "change-archive.md",
    PROJECT_DOCUMENTATION / "assets" / "system-guide.md",
)
CAPABILITY_PROVIDER_GUIDE = ROOT / "docs" / "integrations" / "capability-provider-guide.md"
EVOLUTION = ROOT / "docs" / "architecture" / "evolution.md"
ROOT_README = ROOT / "README.md"
PLUGIN_README = PLUGIN / "README.md"
AGENTS = ROOT / "AGENTS.md"
SKILL_ROOTS = tuple(sorted((PLUGIN / "skills").iterdir()))
ROLE_SKILLS = tuple(path / "SKILL.md" for path in SKILL_ROOTS)
SKILL_METADATA = tuple(path / "agents" / "openai.yaml" for path in SKILL_ROOTS)
EXPLICIT_ONLY_SKILLS = {"clarify", "setup-project", "setup-agents"}
INTAKE_GATED_SKILLS = {"planner", "executor", "reviewer", "manager"}
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

    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    version = args.version
    tag = f"v{version}"
    manifest = json.loads(text(MANIFEST))
    claude_manifest = json.loads(text(CLAUDE_MANIFEST))
    marketplace = json.loads(text(MARKETPLACE))
    intake = text(INTAKE)
    core = text(CORE)
    assurance = text(ASSURANCE)
    coordination = text(COORDINATION)
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
        for path in (INTAKE, CORE, ASSURANCE, COORDINATION, ARTIFACT, CODEX_ADAPTER, CLAUDE_ADAPTER, *ROLE_SKILLS)
    }
    role_skill_documents = {
        str(path.relative_to(ROOT)): text(path)
        for path in ROLE_SKILLS
    }
    skill_documents_by_name = {
        path.parent.name: text(path)
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
    marketplace_plugins = marketplace.get("plugins", [])
    check(
        marketplace.get("name") == "sacha"
        and marketplace.get("interface", {}).get("displayName") == "Sacha"
        and len(marketplace_plugins) == 1
        and marketplace_plugins[0].get("name") == "sacha-orchestra"
        and marketplace_plugins[0].get("source") == {
            "source": "local",
            "path": "./plugins/sacha-orchestra",
        },
        "Marketplace identity or local plugin source is not the released sacha configuration",
    )
    intake_version = re.search(r"(?m)^> Contract Version: ([0-9]+)$", intake)
    core_version = re.search(r"(?m)^> Contract Version: ([0-9]+)$", core)
    assurance_version = re.search(r"(?m)^> Contract Version: ([0-9]+)$", assurance)
    coordination_version = re.search(r"(?m)^> Contract Version: ([0-9]+)$", coordination)
    artifact_version = re.search(r"(?m)^> Contract Version: ([0-9]+)", artifact)
    check(intake_version is not None, "Intake Contract version is missing")
    check(core_version is not None, "Workflow Contract version is missing")
    check(assurance_version is not None, "Assurance Contract version is missing")
    check(coordination_version is not None, "Coordination Contract version is missing")
    check(artifact_version is not None, "Artifact Protocol version is missing")
    check(
        intake_version is not None and intake_version.group(1) == "4",
        "Intake Contract schema is not current",
    )
    check(
        core_version is not None and core_version.group(1) == "11",
        "Workflow Contract schema is not current",
    )
    check(
        assurance_version is not None and assurance_version.group(1) == "2",
        "Assurance Contract schema is not current",
    )
    check(
        coordination_version is not None and coordination_version.group(1) == "4",
        "Coordination Contract schema is not current",
    )
    check(
        artifact_version is not None and artifact_version.group(1) == "5",
        "Artifact Protocol schema changed",
    )
    expected_mapping = (
        f"> Implements: Intake Contract {intake_version.group(1)}；"
        f"Workflow Contract {core_version.group(1)}；"
        f"Assurance Contract {assurance_version.group(1)}；"
        f"Coordination Contract {coordination_version.group(1)}；"
        f"Artifact Protocol {artifact_version.group(1)}"
        if intake_version and core_version and assurance_version and coordination_version and artifact_version
        else ""
    )
    check(expected_mapping in codex_adapter, "Codex Adapter contract mapping is stale")
    check(expected_mapping in claude_adapter, "Claude Code Adapter contract mapping is stale")
    check(
        all("Product Version:" not in content for content in (intake, core, assurance, coordination, artifact)),
        "Core contracts still own product release history",
    )
    check("Adapter Version:" not in codex_adapter and "Adapter Version:" not in claude_adapter, "Runtime Adapters still own product release history")
    current_releases = re.findall(r"(?m)^> 当前 release：(\S+)", evolution)
    current_candidates = re.findall(r"(?m)^> 当前 source candidate：(\S+)", evolution)
    check(len(current_releases) == 1, "Evolution must have exactly one current release")
    check(len(current_candidates) == 1, "Evolution must have exactly one current source candidate")
    current_mainlines = re.findall(r"(?m)^> 当前主线：(.+)$", evolution)
    check(len(current_mainlines) == 1, "Evolution must have exactly one current mainline authority")
    check("source candidate" not in codex_adapter and "source candidate" not in claude_adapter, "Adapter still owns candidate state")
    check("../codex/runtime-adapter.md" not in claude_adapter, "Claude Code Adapter references Codex Adapter")
    check("../claudecode/runtime-adapter.md" not in codex_adapter, "Codex Adapter references Claude Code Adapter")
    codex_model_contract = (
        "`agent_type=sacha_luna_worker`",
        "`agent_type=sacha_luna_worker_xhigh`",
        "`gpt-5.6-sol` / `xhigh`",
        "`gpt-5.6-sol` / `high`",
        "`gpt-5.6-sol` / `medium`",
        "`gpt-5.6-terra` / `xhigh`",
        "`gpt-5.6-terra` / `high`",
        "`fork_turns=none`",
        "requested/effective",
        "Direct/current context",
    )
    claude_model_contract = (
        "| Planner | `opus` |",
        "| Executor | `opus` |",
        "| Executor | `sonnet` |",
        "| Reviewer | `opus` |",
        "| bounded read-only helper | `haiku` |",
        "requested/effective",
        "Direct/current context",
    )
    check(all(marker in codex_adapter for marker in codex_model_contract), "Codex role-aware model routing contract is incomplete")
    check(all(marker in claude_adapter for marker in claude_model_contract), "Claude Code role-aware model routing contract is incomplete")
    check("gpt-5.6-" not in claude_adapter, "Claude Code Adapter leaks Codex model configuration")
    pi_model_contract = (
        "| `pro` |",
        "| `standard` |",
        "| `lite` |",
        "`pi --list-models`",
        "Pi Runtime default",
    )
    check(all(marker in codex_adapter for marker in pi_model_contract), "Pi one-shot model routing contract is incomplete")
    check(PI_ONCE.is_file(), "Pi one-shot helper is missing")
    check(PI_GUARD.is_file(), "Pi one-shot path guard is missing")
    check(PI_MODEL_INSPECTOR.is_file(), "Setup Pi model inspector is missing")
    check(SETUP_AGENTS_SCRIPT.is_file(), "Setup Agents production script is missing")
    check(all(path.is_file() for path in LUNA_WORKER_TEMPLATES), "Luna worker templates are missing")
    check(SETUP_AGENTS_TEST.is_file(), "Setup Agents behavior tests are missing")
    check("setup-agents" not in skill_documents_by_name["setup-project"], "Setup Project owns user-level Agent setup")
    parsed_luna_templates = []
    for template_path, (expected_name, expected_effort) in LUNA_WORKER_TEMPLATES.items():
        if not template_path.is_file():
            continue
        template_text = text(template_path)
        try:
            template = tomllib.loads(template_text)
        except tomllib.TOMLDecodeError:
            template = {}
        parsed_luna_templates.append(template)
        check(template_text.startswith("# managed-by: sacha-orchestra/setup-agents\n"), f"Luna worker template owner marker is missing: {template_path.name}")
        check(
            template.get("name") == expected_name
            and isinstance(template.get("model"), str)
            and template.get("model_reasoning_effort") == expected_effort,
            f"Luna worker template identity is invalid: {template_path.name}",
        )
    check(
        len(parsed_luna_templates) == 2
        and len({template.get("model") for template in parsed_luna_templates}) == 1,
        "Luna worker templates do not share one model tier",
    )
    check(not (PLUGIN / "scripts" / "claude_once.ps1").exists(), "Retired Claude CLI one-shot helper still exists")
    if PI_ONCE.is_file():
        pi_once = text(PI_ONCE)
        check(
            all(
                marker in pi_once
                for marker in (
                    "'-p'",
                    "'--no-session'",
                    "'--mode', 'json'",
                    "'--no-extensions'",
                    "'--extension', $guardPath",
                    "'--no-skills'",
                    "'--no-prompt-templates'",
                    "'--no-context-files'",
                    "'--no-approve'",
                    "'--tools', 'read,edit,write,sacha_result'",
                    "SACHA_PI_READ_PATHS_JSON",
                    "SACHA_PI_WRITE_PATHS_JSON",
                    "structured_result_received",
                    "agent_settled",
                    "scope_violations",
                    "ignored_scope_violations",
                    "git_metadata_changed",
                    "head_before",
                    "head_after",
                    "capabilities_verified",
                    "requested_model",
                    "effective_model",
                    "IsNullOrWhiteSpace($Model)",
                )
            ),
            "Pi one-shot helper containment/transport markers are incomplete",
        )
        tool_allowlist = re.search(r"'--tools', '([^']+)'", pi_once)
        check(
            tool_allowlist is not None
            and all(tool not in tool_allowlist.group(1).split(",") for tool in ("bash", "grep", "find", "ls")),
            "Pi one-shot helper exposes subprocess or broad discovery tools",
        )
    if PI_GUARD.is_file():
        pi_guard = text(PI_GUARD)
        check(
            all(
                marker in pi_guard
                for marker in (
                    'PATH_TOOLS = new Set(["read", "edit", "write"])',
                    'WRITE_TOOLS = new Set(["edit", "write"])',
                    'pi.on("tool_call"',
                    "assertNoReparseAncestor",
                    "nlink > 1",
                    'first === ".git" || first === ".temp"',
                    'name: "sacha_result"',
                    "terminate: true",
                )
            ),
            "Pi one-shot pre-tool guard is incomplete",
        )
    fixed_dispatch_markers = (
        "Packet 至少包含",
        "C1 Managed Serial",
        "C2 Managed Parallel",
        "空核心字段写",
    )
    check(
        all(marker not in coordination + artifact for marker in fixed_dispatch_markers),
        "Current contracts still require retired fixed dispatch formatting",
    )
    setup_confirmation_tokens = (
        "`planned_delta_sha256`",
        "`--confirmed-planned-delta-sha256`",
        "`--list-models`",
        "`--pi-model-binding <route>::<provider/model>`",
        "`--clear-pi-model-bindings`",
        "scripts/inspect_pi_models.ps1",
        "`glm-5.2 | kimi k3 | deepseek | gpt-5.6 luna`",
    )
    check(
        all(
            marker in skill_documents_by_name["setup-project"]
            for marker in setup_confirmation_tokens
        ),
        "Setup Project does not expose its stable configuration entrypoints",
    )
    setup_confirmation_generator = (
        '"write_confirmation"',
        '"planned_delta_sha256"',
        "--confirmed-planned-delta-sha256",
        "confirmed_planned_delta != planned_delta_sha256",
        "--pi-model-binding",
        "--clear-pi-model-bindings",
        "PI_MODEL_ROUTES",
    )
    check(
        all(marker in setup_generator for marker in setup_confirmation_generator),
        "Setup Project write-confirmation guard is incomplete",
    )
    if PI_MODEL_INSPECTOR.is_file():
        pi_model_inspector = text(PI_MODEL_INSPECTOR)
        check(
            all(
                marker in pi_model_inspector
                for marker in (
                    "--list-models",
                    "project_config",
                    "glm-5.2",
                    "kimi k3",
                    "deepseek",
                    "gpt-5.6 luna",
                    "selected_model",
                    "candidates",
                )
            ),
            "Setup Pi model inspection and configuration priority are incomplete",
        )
    runtime_model_markers = ("gpt-5.6-sol", "gpt-5.6-terra", "sacha_luna_worker", "reasoning_effort", "`opus`", "`sonnet`", "`haiku`")
    check(
        all(marker not in content for marker in runtime_model_markers for content in (intake, core, assurance, coordination, artifact, *role_skill_documents.values())),
        "Runtime model policy leaks into Core or Role Skills",
    )
    private_pi_markers = (
        "tencent" + "-intranet",
        "glm-" + "5.2-ioa",
        "kimi-" + "k3-ioa",
        "deepseek-" + "v4-pro-ioa",
        "gpt-" + "5.6-luna",
    )
    source_documents = tuple(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.casefold() in {".md", ".json", ".yaml", ".yml", ".py", ".ps1", ".mjs"}
        and ".git" not in path.parts
        and ".temp" not in path.parts
        and path not in LUNA_WORKER_TEMPLATES
    )
    private_pi_leaks = [
        f"{path.relative_to(ROOT)}:{marker}"
        for path in source_documents
        for marker in private_pi_markers
        if marker in text(path)
    ]
    check(
        not private_pi_leaks,
        "Private Pi provider/model identifiers leak into repository source: "
        + ", ".join(private_pi_leaks),
    )
    check(
        len(intake.splitlines()) <= 80 and len(intake) <= 3200,
        "Intake Contract exceeds the bounded Core surface",
    )
    check(
        len(core.splitlines()) <= 80 and len(core) <= 4000,
        "Workflow Kernel exceeds the bounded Core surface",
    )
    check(
        len(assurance.splitlines()) <= 50 and len(assurance) <= 2000,
        "Assurance Contract exceeds the bounded Core surface",
    )
    check(
        len(coordination.splitlines()) <= 80 and len(coordination) <= 4000,
        "Coordination Contract exceeds the bounded Core surface",
    )
    check(
        len(artifact.splitlines()) <= 90 and len(artifact) <= 3200,
        "Artifact Protocol exceeds the bounded Core surface",
    )
    check(
        len(codex_adapter.splitlines()) <= 140 and len(codex_adapter) <= 7200,
        "Codex Adapter exceeds the bounded mapping surface",
    )
    check(
        len(claude_adapter.splitlines()) <= 110 and len(claude_adapter) <= 5000,
        "Claude Code Adapter exceeds the bounded mapping surface",
    )
    check(
        sum(len(content) for content in (
            intake,
            core,
            skill_documents_by_name["using-sacha"],
            skill_documents_by_name["executor"],
        )) <= 9000,
        "Direct Executor active surface exceeds the progressive-loading budget",
    )
    for path, content in role_skill_documents.items():
        links = set(re.findall(r"\]\(([^)]+)\)", content))
        allowed_links = {
            "../../core/intake-contract.md",
            "../../core/workflow-contract.md",
            "../../core/assurance-contract.md",
            "../../core/coordination-contract.md",
            "../../core/artifact-protocol.md",
            "scripts/resolve_capability_queries.py",
            "scripts/generate_project_integration.py",
            "scripts/inspect_pi_models.ps1",
            "scripts/setup_agents.py",
            "assets/sacha-luna-worker.toml",
            "assets/sacha-luna-worker-xhigh.toml",
        }
        check(links <= allowed_links, f"Role Skill adds a non-canonical documentation dependency: {path}")
    discovery_descriptions = [
        match.group(1)
        for content in role_skill_documents.values()
        if (match := re.search(r"(?m)^description: (.+)$", content)) is not None
    ]
    check(
        len(discovery_descriptions) == len(role_skill_documents)
        and sum(map(len, discovery_descriptions)) <= 800
        and max(map(len, discovery_descriptions), default=0) <= 140,
        "Skill discovery descriptions exceed the resident context budget",
    )
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
    check((PLUGIN / "skills" / "using-sacha").is_dir(), "using-sacha Skill is missing")
    check(
        DOCUMENTATION_GENERATOR.is_file(),
        "Project Documentation executable generator is missing",
    )
    if DOCUMENTATION_GENERATOR.is_file():
        try:
            compile(
                text(DOCUMENTATION_GENERATOR),
                str(DOCUMENTATION_GENERATOR),
                "exec",
            )
        except SyntaxError as exc:
            check(False, f"Project Documentation generator syntax is invalid: {exc}")
    for template in DOCUMENTATION_TEMPLATES:
        check(template.is_file(), f"Project Documentation template is missing: {template.name}")
    default_prompt = manifest.get("interface", {}).get("defaultPrompt", [])
    check(
        isinstance(default_prompt, list)
        and any(
            isinstance(prompt, str) and "$sacha-orchestra:using-sacha" in prompt
            for prompt in default_prompt
        ),
        "Plugin default prompt does not use using-sacha",
    )
    for skill_name in INTAKE_GATED_SKILLS:
        skill_path = PLUGIN / "skills" / skill_name / "SKILL.md"
        check(
            "../../core/intake-contract.md" in text(skill_path),
            f"Production/control Skill does not consume Intake Contract: {skill_name}",
        )
    allowed_adapter_links = {
        "../../core/intake-contract.md",
        "../../core/workflow-contract.md",
        "../../core/assurance-contract.md",
        "../../core/coordination-contract.md",
        "../../core/artifact-protocol.md",
    }
    for runtime, adapter in adapters.items():
        adapter_links = set(re.findall(r"\]\(([^)]+)\)", adapter))
        runtime_allowed_links = set(allowed_adapter_links)
        if runtime == "Codex":
            runtime_allowed_links.update({
                "../../scripts/pi_once.ps1",
            })
        check(
            adapter_links <= runtime_allowed_links,
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
    check(
        "core/intake-contract.md" in root_readme and "core/intake-contract.md" in plugin_readme,
        "README entrypoints do not link Intake Contract",
    )
    check(
        "flowchart TD" in plugin_readme and "using-sacha" in plugin_readme,
        "Plugin README does not expose the using-sacha architecture overview",
    )
    check(
        "docs/history/" not in agents
        and "docs/plans/" not in agents
        and "docs/plan/" not in agents
        and re.search(r"\b0\.\d+\.\d+\b", agents) is None,
        "Project AGENTS still contains release chronology or per-plan routing",
    )
    check(
        not (PLUGIN / "hooks").exists() and "hooks" not in manifest,
        "Plugin adds a Hook surface",
    )
    markdown_documents = (
        INTAKE,
        CORE,
        ASSURANCE,
        COORDINATION,
        ARTIFACT,
        CODEX_ADAPTER,
        CAPABILITY_PROVIDER_GUIDE,
        CLAUDE_ADAPTER,
        PLUGIN_README,
        ROOT_README,
        AGENTS,
        *ROLE_SKILLS,
    )
    for document in markdown_documents:
        for link in re.findall(r"\]\(([^)]+)\)", text(document)):
            if link.startswith(("http://", "https://", "#")):
                continue
            target = (document.parent / link.split("#", 1)[0]).resolve()
            check(target.exists(), f"Broken Markdown link in {document.relative_to(ROOT)}: {link}")
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
        check(current_candidates == [f"`{version}`"], "Evolution candidate does not match --version")
    else:
        check(current_releases == [f"`{version}`"], "Evolution release does not match --version")
        check(current_candidates == ["无"], "Released state still has a source candidate")
        tag_ref = git("rev-parse", "--verify", f"refs/tags/{tag}")
        check(tag_ref.returncode == 0, "Annotated release tag is missing")
        tag_commit = git("rev-parse", f"{tag}^{{}}")
        head_commit = git("rev-parse", "HEAD")
        check(tag_commit.returncode == 0 and tag_commit.stdout.strip() == head_commit.stdout.strip(), "Release tag does not resolve to HEAD")

    print(f"release_coherence_status={'pass' if not failures else 'fail'}")
    print(f"release_coherence_failures={len(failures)}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
