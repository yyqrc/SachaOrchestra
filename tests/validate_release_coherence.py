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
INTAKE = PLUGIN / "core" / "intake-contract.md"
CORE = PLUGIN / "core" / "workflow-contract.md"
ASSURANCE = PLUGIN / "core" / "assurance-contract.md"
COORDINATION = PLUGIN / "core" / "coordination-contract.md"
ARTIFACT = PLUGIN / "core" / "artifact-protocol.md"
CODEX_ADAPTER = PLUGIN / "adapters" / "codex" / "runtime-adapter.md"
CLAUDE_ADAPTER = PLUGIN / "adapters" / "claudecode" / "runtime-adapter.md"
CLAUDE_ONCE = PLUGIN / "scripts" / "claude_once.ps1"
SETUP_GENERATOR = PLUGIN / "skills" / "setup-project" / "scripts" / "generate_project_integration.py"
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
EXPLICIT_ONLY_SKILLS = {"clarify", "setup-project"}
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

    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    version = args.version
    tag = f"v{version}"
    manifest = json.loads(text(MANIFEST))
    claude_manifest = json.loads(text(CLAUDE_MANIFEST))
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
        intake_version is not None and intake_version.group(1) == "3",
        "Intake Contract schema is not current",
    )
    check(
        core_version is not None and core_version.group(1) == "9",
        "Workflow Contract schema is not current",
    )
    check(
        assurance_version is not None and assurance_version.group(1) == "1",
        "Assurance Contract schema is not current",
    )
    check(
        coordination_version is not None and coordination_version.group(1) == "3",
        "Coordination Contract schema is not current",
    )
    check(
        artifact_version is not None and artifact_version.group(1) == "3",
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
    check(len(re.findall(r"(?m)^> 当前 release：", evolution)) == 1, "Evolution must have exactly one current release")
    check(len(re.findall(r"(?m)^> 当前 source candidate：", evolution)) == 1, "Evolution must have exactly one current source candidate")
    current_mainlines = re.findall(r"(?m)^> 当前主线：(.+)$", evolution)
    check(len(current_mainlines) == 1, "Evolution must have exactly one current mainline authority")
    check("source candidate" not in codex_adapter and "source candidate" not in claude_adapter, "Adapter still owns candidate state")
    check("../codex/runtime-adapter.md" not in claude_adapter, "Claude Code Adapter references Codex Adapter")
    check("../claudecode/runtime-adapter.md" not in codex_adapter, "Codex Adapter references Claude Code Adapter")
    codex_model_contract = (
        "`gpt-5.6-sol` / `xhigh`",
        "`gpt-5.6-sol` / `high`",
        "`gpt-5.6-sol` / `medium`",
        "`gpt-5.6-terra` / `xhigh`",
        "`gpt-5.6-terra` / `high`",
        "`fork_turns=none`、`model` 和 `reasoning_effort`",
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
    check(CLAUDE_ONCE.is_file(), "Claude CLI one-shot helper is missing")
    if CLAUDE_ONCE.is_file():
        claude_once = text(CLAUDE_ONCE)
        check(
            all(
                marker in claude_once
                for marker in (
                    "'-p'",
                    "'--safe-mode'",
                    "'--no-session-persistence'",
                    "'--permission-mode', 'dontAsk'",
                    "'--output-format', 'json'",
                    "'--tools', 'Read,Edit,Write'",
                    '"Read($permissionPath)"',
                    '"Edit($permissionPath)"',
                    "scope_violations",
                    "ignored_scope_violations",
                    "git_metadata_changed",
                    "head_before",
                    "head_after",
                    "capabilities_verified",
                )
            ),
            "Claude CLI one-shot helper containment/transport markers are incomplete",
        )
        check(
            "--dangerously-skip-permissions" not in claude_once,
            "Claude CLI one-shot helper bypasses permissions",
        )
        check(
            "AllowedBash" not in claude_once
            and "@('Read', 'Glob', 'Grep', 'Edit', 'Write')" not in claude_once,
            "Claude CLI one-shot helper exposes broad or subprocess tools",
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
    feedback_routing_contract = (
        "只有唯一完整匹配才复用",
        "新 context 不扩权",
        "消费一次 terminal result",
    )
    check(
        all(marker in skill_documents_by_name["feedback"] for marker in feedback_routing_contract),
        "Feedback repair-target isolation contract is incomplete",
    )
    codex_feedback_routing_contract = (
        "唯一匹配才复用",
        "新 task 不扩权",
        "Source 只 join 一次",
    )
    check(
        all(marker in codex_adapter for marker in codex_feedback_routing_contract),
        "Codex Feedback repair-task routing contract is incomplete",
    )
    intake_reassessment_contract = (
        "初次判断及 Direct 执行期间",
        "关键 Human 澄清",
        "先冻结/持久化可执行 Spec",
        "难回退跨 owner 决策",
        "只有复杂、耗时、多文件或多平台仍保持 L0",
        "实质变化形成新 candidate 时可再推荐一次",
    )
    check(
        all(marker in intake for marker in intake_reassessment_contract),
        "Intake task-evolution reassessment contract is incomplete",
    )
    using_sacha_reassessment_contract = (
        "Direct 执行期间",
        "关键 Human 澄清",
        "先冻结/持久化 Spec",
        "跨 context owner/恢复",
        "正式协调/独立验收",
        "难回退的跨 owner 决策",
        "复杂调试、耗时、文件多、多平台或持续验证本身仍保持 Direct",
    )
    check(
        all(
            marker in skill_documents_by_name["using-sacha"]
            for marker in using_sacha_reassessment_contract
        ),
        "using-sacha task-evolution procedure is incomplete",
    )
    planner_reassessment_contract = (
        "实施前需关键 Human 澄清",
        "需冻结/持久化 Spec",
        "难回退跨 owner 决策",
        "复杂、文件多、耗时、多平台、无分歧修改",
        "Direct 或 active workflow",
    )
    check(
        all(marker in core for marker in planner_reassessment_contract),
        "Planner Gate task-evolution alignment is incomplete",
    )
    setup_confirmation_contract = (
        "等待 Human 明确确认",
        "历史 Binding 不是本轮写入授权",
        "`planned_delta_sha256`",
        "`--confirmed-planned-delta-sha256`",
    )
    check(
        all(
            marker in skill_documents_by_name["setup-project"]
            for marker in setup_confirmation_contract
        ),
        "Setup Project configuration-confirmation contract is incomplete",
    )
    setup_confirmation_generator = (
        '"write_confirmation"',
        '"planned_delta_sha256"',
        "--confirmed-planned-delta-sha256",
        "confirmed_planned_delta != planned_delta_sha256",
    )
    check(
        all(marker in setup_generator for marker in setup_confirmation_generator),
        "Setup Project write-confirmation guard is incomplete",
    )
    runtime_model_markers = ("gpt-5.6-sol", "gpt-5.6-terra", "reasoning_effort", "`opus`", "`sonnet`", "`haiku`")
    check(
        all(marker not in content for marker in runtime_model_markers for content in (intake, core, assurance, coordination, artifact, *role_skill_documents.values())),
        "Runtime model policy leaks into Core or Role Skills",
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
            assurance,
            coordination,
            artifact,
            *(
                content
                for path, content in role_skill_documents.items()
                if "project-documentation" not in path
            ),
        )) <= 24000,
        "Workflow Core and Skill documents exceed the active text budget",
    )
    check(
        len(skill_documents_by_name.get("project-documentation", "")) <= 1200,
        "Project Documentation exceeds its on-demand text budget",
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
        lines = content.splitlines()
        check(
            len(lines) <= 30 and len(content) <= 1600,
            f"Skill exceeds the bounded procedure surface: {path}",
        )
        check(max((len(line) for line in lines), default=0) <= 220, f"Role Skill contains an oversized compound line: {path}")
        links = set(re.findall(r"\]\(([^)]+)\)", content))
        allowed_links = {
            "../../core/intake-contract.md",
            "../../core/workflow-contract.md",
            "../../core/assurance-contract.md",
            "../../core/coordination-contract.md",
            "../../core/artifact-protocol.md",
            "scripts/resolve_capability_queries.py",
            "scripts/generate_project_integration.py",
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
                "../../scripts/claude_once.ps1",
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
        len(agents.splitlines()) <= 120 and len(agents) <= 7000,
        "Project AGENTS exceeds the resident Sacha development context budget",
    )
    check(
        "docs/history/" not in agents
        and "docs/plans/" not in agents
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
        check(f"> 当前 source candidate：`{version}`" in evolution, "Evolution candidate does not match --version")
    else:
        check(f"> 当前 release：`{version}`" in evolution, "Evolution release does not match --version")
        check("> 当前 source candidate：无" in evolution, "Released state still has a source candidate")
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
