"""Dispatch a read-only Sacha role through the local CodeBuddy Code CLI."""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from agy_acp import ROLES, AcpClient, AcpError, RemoteError, configure, load_resume_session, open_session


TOOLS = "Read,Glob,Grep"
DEFAULT_MODEL = "claude-opus-5.5"
TEMPLATES = Path(__file__).resolve().parents[3] / "skills/setup-agents/assets/agy"


def launcher():
    if not (command := shutil.which("codebuddy")):
        raise FileNotFoundError("CodeBuddy Code CLI was not found on PATH")
    path = Path(command).resolve(strict=True)
    if os.name != "nt" or path.suffix.lower() == ".exe":
        return [str(path)]
    # Bypass the Windows npm shim so the managed process is the ACP server.
    entry = path.parent / "node_modules/@tencent-ai/codebuddy-code/bin/codebuddy"
    if path.suffix.lower() == ".cmd" and entry.is_file() and (node := shutil.which("node")):
        return [node, str(entry)]
    raise AcpError("Use the native CodeBuddy executable or the CodeBuddy npm installation with Node.js on PATH")


def prepare_role(cwd: Path, role: str):
    if not cwd.is_dir() or any((parent / ".git").exists() for parent in (cwd, *cwd.parents)):
        raise AcpError("Use a staging directory outside the repository containing only approved material")
    frontmatter, _, body = (TEMPLATES / role / "agent.md").read_text(encoding="utf-8").partition("\n---\n")
    description = next(line for line in frontmatter.splitlines() if line.startswith("description: "))
    content = f"---\nname: {role}\n{description}\nmainAgent: true\ntools: [{TOOLS}]\n---\n{body}"
    config = cwd / ".codebuddy"
    agents = config / "agents"
    for directory, expected in ((config, "agents"), (agents, f"{role}.md")):
        directory.mkdir(exist_ok=True)
        if directory.resolve() != directory or any(path.name != expected for path in directory.iterdir()):
            raise AcpError(f"Unexpected CodeBuddy configuration in staging directory: {directory}")
    target = agents / f"{role}.md"
    if target.resolve() != target:
        raise AcpError("CodeBuddy role file must not redirect")
    try:
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    except FileExistsError:
        if target.read_text(encoding="utf-8") != content:
            raise AcpError("Staging directory contains a different CodeBuddy role definition") from None


def run(args, report):
    argv = launcher()
    cwd = args.cwd.resolve(strict=True)
    prompt = args.prompt_file.read_text(encoding="utf-8-sig") if args.prompt_file else None
    if prompt is not None and not prompt.strip():
        raise AcpError("Prompt file is empty")
    identity = {"runtime": "cbc-acp", "cwd": str(cwd), "agent": args.agent, "auth": "cached-login"}
    previous = load_resume_session(args.resume_result, identity, accept_termination=True)
    model = args.model
    if model is None:
        model = DEFAULT_MODEL if previous is None else previous.get("confirmed_model")
        if not isinstance(model, str) or not model.strip():
            raise AcpError("Continuation result does not identify the confirmed CodeBuddy model")
    prepare_role(cwd, args.agent)
    env = dict(os.environ, DISABLE_AUTOUPDATER="1", CODEBUDDY_DISABLE_PARENT_MEMORY="1",
               CODEBUDDY_DISABLE_AUTO_MEMORY="1", CODEBUDDY_CODE_DISABLE_AUTO_MEMORY="1")
    for key in ("CODEBUDDY_API_KEY", "CODEBUDDY_AUTH_TOKEN"):
        env.pop(key, None)
    report["invocation"] = {**identity, "launcher": argv, "model": model}
    client = AcpClient([*argv, "--acp", "--setting-sources", "project", "--strict-mcp-config",
                        "--permission-mode", "dontAsk", "--tools", TOOLS, "--allowedTools", "Read(./**)",
                        "--agent", args.agent, "--model", model], cwd, env, report)
    try:
        hello = client.request("initialize", protocolVersion=1,
                               clientCapabilities={"_meta": {"codebuddy.ai": {"mainAgentSupport": True}}})
        capabilities = hello.get("agentCapabilities") or {}
        report["initialize"] = hello
        if hello.get("protocolVersion") != 1 or capabilities.get("mainAgentSupport") is not True:
            raise AcpError("CodeBuddy did not negotiate ACP v1 with main Agent support")
        catalog = client.request("_codebuddy.ai/getAgents")
        if not any(item.get("name") == args.agent for item in catalog.get("agents", [])):
            raise AcpError(f"CodeBuddy did not discover the staged role: {args.agent}")
        opened = open_session(client, identity, capabilities, previous_session=previous,
                              new_meta={"codebuddy.ai/agent": args.agent})
        report["session"]["confirmed_agent"] = opened.get("currentAgentName")
        if report["session"]["confirmed_agent"] != args.agent:
            raise AcpError(f"CodeBuddy did not confirm the selected role: {args.agent}")
        configure(client, [f"model={model}"])
        report["session"]["confirmed_model"] = model
        if prompt is None:
            report["status"] = "session_ready"
        else:
            client.prompt(prompt, args.timeout)
    finally:
        # CodeBuddy may stay alive after stdin closes, even after end_turn.
        client.close(accept_termination=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", type=Path, required=True, help="Staging directory with approved material")
    parser.add_argument("--agent", choices=ROLES, required=True)
    parser.add_argument("--prompt-file", type=Path)
    parser.add_argument("--resume-result", type=Path)
    parser.add_argument("--model", help=f"Exact CodeBuddy model ID (new sessions default to {DEFAULT_MODEL})")
    parser.add_argument("--timeout", type=float, default=300, help="Prompt timeout in seconds")
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")

    report = {"status": "error", "turn_state": "not_sent", "requests": [], "tool_updates": []}
    try:
        run(args, report)
    except (AcpError, OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired) as exc:
        report.update(status="error", error=str(exc))
        if isinstance(exc, RemoteError):
            report["error_code"] = exc.code
    except KeyboardInterrupt:
        report.update(status="incomplete", error="Interrupted")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"session_ready", "completed"} else 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
