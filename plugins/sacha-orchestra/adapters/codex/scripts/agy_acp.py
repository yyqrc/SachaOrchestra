"""Run one read-only Antigravity ACP session operation from Codex."""

from __future__ import annotations

import argparse
import json
import math
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path


ROLES = ("sacha-explorer", "sacha-reviewer")
RUNTIME = "agy-acp"
API_KEY_AUTH = "gemini-api-key"
CACHED_LOGIN = "cached-login"
CONNECTION_OWNER = "sacha-orchestra/setup-agents"
REQUEST_TIMEOUT = 30
CANCEL_GRACE = 5
STDERR_LIMIT = 4096


class AcpError(RuntimeError):
    pass


class RemoteError(AcpError):
    def __init__(self, request: str, error: dict):
        super().__init__(f"{request}: {error.get('message', 'ACP error')}")
        self.code = error.get("code")


class AcpClient:
    def __init__(self, argv: list[str], cwd: Path, env: dict[str, str], report: dict):
        self.process = subprocess.Popen(
            argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8",
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            start_new_session=os.name != "nt",
        )
        self.report = report
        self.report["process_id"] = self.process.pid
        self.inbox = queue.Queue()
        self.outbox = queue.Queue()
        self.request_id = 0
        self.session_id = None
        self.prompting = False
        self.cancel_reason = None
        self.cancel_deadline = math.inf
        self.chunks: list[str] = []
        self.stderr_tail = b""
        self.stderr_reader = threading.Thread(target=self.read_stderr, daemon=True)
        self.stderr_reader.start()
        threading.Thread(target=self.read_messages, daemon=True).start()
        threading.Thread(target=self.write_messages, daemon=True).start()

    def read_stderr(self):
        with self.process.stderr as stream:
            while chunk := stream.buffer.read1(1024):
                self.stderr_tail = (self.stderr_tail + chunk)[-STDERR_LIMIT:]

    def read_messages(self):
        try:
            with self.process.stdout as stream:
                for line in stream:
                    self.inbox.put(json.loads(line))
        except (ValueError, OSError) as exc:
            self.inbox.put(AcpError(f"Invalid ACP stdout: {type(exc).__name__}"))
        finally:
            self.inbox.put(None)

    def send(self, **message):
        self.outbox.put({"jsonrpc": "2.0", **message})

    def write_messages(self):
        try:
            with self.process.stdin as stream:
                while (message := self.outbox.get()) is not None:
                    stream.write(json.dumps(message) + "\n")
                    stream.flush()
        except OSError as exc:
            self.inbox.put(AcpError(f"ACP stdin failed: {type(exc).__name__}"))

    def send_request(self, method: str, params: dict) -> int:
        self.request_id += 1
        self.send(id=self.request_id, method=method, params=params)
        return self.request_id

    def request(self, method: str, **params) -> dict:
        request_id = self.send_request(method, params)
        return self.receive(request_id, method, REQUEST_TIMEOUT)

    def receive(self, request_id: int, method: str, timeout: float) -> dict:
        deadline = time.monotonic() + timeout
        while True:
            remaining = min(deadline, self.cancel_deadline) - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"Timed out waiting for {method}")
            try:
                # A short bounded wait lets Ctrl+C interrupt promptly on Windows.
                message = self.inbox.get(timeout=min(remaining, 0.2))
            except queue.Empty:
                continue
            if message is None:
                raise AcpError(f"ACP process closed stdout before replying to {method}")
            if isinstance(message, Exception):
                raise message
            if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                raise AcpError("Invalid ACP message")
            if "method" in message:
                self.handle_message(message)
            elif message.get("id") == request_id:
                if isinstance(message.get("error"), dict):
                    raise RemoteError(method, message["error"])
                if not isinstance(message.get("result"), dict):
                    raise AcpError(f"Missing result for {method}")
                return message["result"]
            else:
                raise AcpError(f"Unexpected ACP response ID while waiting for {method}")

    def handle_message(self, message: dict):
        method = message["method"]
        params = message.get("params") or {}
        same_session = self.session_id is not None and params.get("sessionId") == self.session_id
        if "id" in message:
            request_id = message["id"]
            if method == "session/request_permission" and same_session and self.prompting:
                tool = params.get("toolCall") or {}
                evidence = {key: tool[key] for key in ("toolCallId", "title", "kind") if key in tool}
                reject = next((option["optionId"] for option in params.get("options", ())
                               if option.get("kind") == "reject_once"), None)
                if reject and not self.cancel_reason:
                    outcome = {"outcome": "selected", "optionId": reject}
                else:
                    self.cancel("permission")
                    outcome = {"outcome": "cancelled"}
                self.report["requests"].append({"method": method, "toolCall": evidence, **outcome})
                self.send(id=request_id, result={"outcome": outcome})
            else:
                record = {"method": method, "outcome": "unsupported"}
                if same_session and isinstance(params.get("message"), str):
                    record["message"] = params["message"]
                self.report["requests"].append(record)
                self.send(id=request_id, error={"code": -32601, "message": "Client method unavailable"})
            return
        if method != "session/update" or not same_session or not self.prompting:
            return
        update = params.get("update") or {}
        kind = update.get("sessionUpdate")
        if kind == "agent_message_chunk":
            content = update.get("content") or {}
            if content.get("type") == "text" and isinstance(content.get("text"), str):
                self.chunks.append(content["text"])
        elif kind == "config_option_update":
            self.report["config_options"] = update.get("configOptions", [])
        elif kind in {"tool_call", "tool_call_update"}:
            keys = ("sessionUpdate", "toolCallId", "title", "kind", "status", "locations")
            self.report["tool_updates"].append({key: update[key] for key in keys if key in update})

    def cancel(self, reason: str):
        if self.cancel_reason is None:
            self.cancel_reason = reason
            self.cancel_deadline = time.monotonic() + CANCEL_GRACE
            self.report["cancel_requested"] = reason
            self.send(method="session/cancel", params={"sessionId": self.session_id})

    def prompt(self, text: str, timeout: float):
        self.prompting = True
        self.report["turn_state"] = "unknown"
        try:
            request_id = self.send_request("session/prompt", {
                "sessionId": self.session_id,
                "prompt": [{"type": "text", "text": text}],
            })
            try:
                result = self.receive(request_id, "session/prompt", timeout)
            except (TimeoutError, KeyboardInterrupt) as exc:
                self.cancel("timeout" if isinstance(exc, TimeoutError) else "interrupt")
                result = self.receive(request_id, "session/prompt", CANCEL_GRACE)
            reason = result.get("stopReason")
            if not isinstance(reason, str):
                raise AcpError("session/prompt has no protocol stop reason")
            self.report.update(turn_state="terminal", stop_reason=reason)
        except RemoteError:
            self.report["turn_state"] = "terminal_error"
            raise
        finally:
            self.prompting = False
            self.report["text"] = "".join(self.chunks)

        self.report["status"] = (
            "completed" if reason == "end_turn" and self.report["text"].strip()
            and not self.cancel_reason else "incomplete"
        )

    def close(self, *, accept_termination=False):
        self.outbox.put(None)
        try:
            self.process.wait(timeout=CANCEL_GRACE)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            self.report["forced_shutdown"] = True
            self.process.kill()
            self.process.wait(timeout=CANCEL_GRACE)
            if isinstance(exc, KeyboardInterrupt):
                raise
        finally:
            exit_code = self.process.poll()
            self.report["process_exit_code"] = exit_code
            terminated_after_close = accept_termination and self.report.get("forced_shutdown") and exit_code is not None
            if exit_code != 0 and not terminated_after_close and self.report["status"] in {
                "initialized", "session_ready", "completed"
            }:
                self.report.update(status="incomplete", error="ACP process did not exit cleanly")
            if exit_code != 0 or self.report["status"] == "error":
                self.stderr_reader.join(timeout=0.2)
                diagnostic = self.stderr_tail.decode("utf-8", errors="replace").strip()
                if diagnostic:
                    self.report["stderr"] = diagnostic


def available_values(option: dict) -> set[str]:
    values = set()
    for item in option.get("options") or ():
        if "value" in item:
            values.add(item["value"])
        else:
            values.update(child["value"] for child in item.get("options", ()))
    return values


def configure(client: AcpClient, requested: list[str]):
    selections = {}
    for selection in requested:
        config_id, _, value = selection.partition("=")
        option = next((item for item in client.report["config_options"]
                       if item.get("id") == config_id and item.get("type") == "select"), None)
        if option is None or value not in available_values(option):
            raise AcpError(f"Unavailable ACP config selection: {selection}")
        category = option.get("category") or config_id
        if category not in {"model", "thought_level"} and (category, value) != ("mode", "plan"):
            raise AcpError(f"Read-only ACP does not permit config selection: {selection}")
        selections[config_id] = value
        if option.get("currentValue") == value:
            continue
        result = client.request("session/set_config_option", sessionId=client.session_id,
                                configId=config_id, value=value)
        client.report["config_options"] = result.get("configOptions", [])
        if not any(item.get("id") == config_id and item.get("currentValue") == value
                   for item in client.report["config_options"]):
            raise AcpError(f"ACP did not confirm config selection: {selection}")
    actual = {item.get("id"): item.get("currentValue") for item in client.report["config_options"]}
    if any(actual.get(config_id) != value for config_id, value in selections.items()):
        raise AcpError("Dependent ACP options changed an explicit selection")


def load_resume_session(path: Path | None, identity: dict, *, accept_termination=False):
    if path is None:
        return None
    previous = json.loads(path.read_text(encoding="utf-8-sig"))
    session = previous.get("session", {})
    forced = previous.get("forced_shutdown")
    exit_code = previous.get("process_exit_code")
    exited = isinstance(exit_code, int) and (accept_termination if forced else exit_code == 0)
    if (
        previous.get("status") not in {"session_ready", "completed"}
        or not exited
        or any(session.get(key) != value for key, value in identity.items())
        or not isinstance(session.get("sessionId"), str)
        or not session["sessionId"]
    ):
        raise AcpError("Continuation requires a matching settled session result")
    return session


def open_session(client: AcpClient, identity: dict, capabilities: dict, *, previous_session=None, new_meta=None):
    params = {"cwd": identity["cwd"], "mcpServers": []}
    method = "session/new"
    if previous_session is not None:
        client.session_id = previous_session["sessionId"]
        client.report["session"] = previous_session
        params["sessionId"] = client.session_id
        if (capabilities.get("sessionCapabilities") or {}).get("resume") is not None:
            method = "session/resume"
        elif capabilities.get("loadSession") is True:
            method = "session/load"
        else:
            raise AcpError("ACP server did not negotiate session resume or load")
    elif new_meta:
        params["_meta"] = new_meta
    client.report["session_method"] = method
    opened = client.request(method, **params)
    if method == "session/new":
        client.session_id = opened.get("sessionId")
    elif opened.get("sessionId", client.session_id) != client.session_id:
        raise AcpError("ACP returned a different session ID on continuation")
    if not isinstance(client.session_id, str) or not client.session_id:
        raise AcpError("ACP did not return a session ID")
    client.report["session"] = {**identity, "sessionId": client.session_id}
    client.report["config_options"] = opened.get("configOptions") or []
    return opened


def connection_path() -> Path:
    return Path.home() / ".gemini" / "config" / "sacha-acp.json"


def run(args, report: dict, env: dict[str, str]):
    executable = args.agy
    auth_method = None
    if not args.probe:
        config = connection_path()
        try:
            if config.resolve(strict=True) != config.parent.resolve() / config.name:
                raise AcpError("Managed Antigravity connection must not redirect")
            saved = json.loads(config.read_text(encoding="utf-8"))
        except FileNotFoundError:
            report.update(status="not_configured", error="Antigravity setup has not been saved")
            return
        if (not isinstance(saved, dict) or set(saved) != {"managed_by", "executable", "auth"}
                or saved["managed_by"] != CONNECTION_OWNER):
            raise AcpError("Invalid managed Antigravity connection")
        executable = Path(saved["executable"])
        auth_method = saved["auth"]
        if auth_method is None:
            report.update(status="not_configured", error="Antigravity has no enabled authentication method")
            return

    cwd = args.cwd.resolve(strict=True)
    if not cwd.is_dir():
        raise AcpError("ACP working directory must be a directory")
    executable = executable.expanduser()
    if not executable.is_absolute():
        raise AcpError("Use the verified official agy executable's absolute path")
    path = executable.resolve(strict=True)
    if not args.probe and path != executable:
        raise AcpError("The saved Antigravity CLI now redirects; check the installation in setup-agents")
    if not path.is_file() or (os.name == "nt" and path.suffix.lower() != ".exe"):
        raise AcpError("Use the verified official agy executable")
    prompt = None
    if args.prompt_file:
        prompt = args.prompt_file.read_text(encoding="utf-8-sig")
        if not prompt.strip():
            raise AcpError("Prompt file is empty")
    if args.probe or auth_method == CACHED_LOGIN:
        env.pop("GEMINI_API_KEY", None)
    elif auth_method == API_KEY_AUTH:
        if not env.get("GEMINI_API_KEY"):
            raise AcpError("The saved API key method requires GEMINI_API_KEY in the local environment")
    else:
        raise AcpError("Unsupported saved Antigravity authentication method")

    identity = {"runtime": RUNTIME, "cwd": str(cwd), "agent": args.agent, "auth": auth_method}
    previous = load_resume_session(args.resume_result, identity)
    report["invocation"] = {**identity, "executable": str(path)}
    argv = [str(path), "acp", "--disable-telemetry"]
    if not args.probe:
        argv.extend(["--agent", args.agent, "--sandbox"])
    client = AcpClient(argv, cwd, env, report)
    try:
        hello = client.request("initialize", protocolVersion=1, clientCapabilities={})
        capabilities = hello.get("agentCapabilities") or {}
        report["initialize"] = hello
        if hello.get("protocolVersion") != 1:
            raise AcpError("The server did not negotiate ACP v1")
        if args.probe:
            report["status"] = "initialized"
            return
        if auth_method == API_KEY_AUTH:
            if not any(method.get("id") == API_KEY_AUTH and method.get("type", "agent") == "agent"
                       for method in (hello.get("authMethods") or ())):
                raise AcpError("ACP server did not advertise the approved API key method")
            client.request("authenticate", methodId=API_KEY_AUTH)
        open_session(client, identity, capabilities, previous_session=previous)
        configure(client, args.set_config)
        if prompt is None:
            report["status"] = "session_ready"
        else:
            client.prompt(prompt, args.timeout)
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agy", type=Path, help="Explicit official executable path for --probe")
    parser.add_argument("--cwd", type=Path, required=True)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--probe", action="store_true", help="Only negotiate ACP, without a session")
    operation.add_argument("--agent", choices=ROLES)
    parser.add_argument("--prompt-file", type=Path)
    parser.add_argument("--resume-result", type=Path)
    parser.add_argument("--set-config", action="append", default=[], metavar="ID=VALUE")
    parser.add_argument("--timeout", type=float, default=300, help="Prompt timeout in seconds")
    args = parser.parse_args()
    if args.probe and (args.prompt_file or args.resume_result or args.set_config):
        parser.error("--probe does not accept session options")
    if args.probe and args.agy is None:
        parser.error("--probe requires the path to the official executable via --agy")
    if not args.probe and args.agy is not None:
        parser.error("--agy is only supported with --probe; session calls use the saved setup")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")

    result = {"status": "error", "turn_state": "not_sent", "requests": [], "tool_updates": []}
    try:
        run(args, result, dict(os.environ))
    except (AcpError, OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired) as exc:
        result.update(status="error", error=str(exc))
        if isinstance(exc, RemoteError):
            result["error_code"] = exc.code
    except KeyboardInterrupt:
        result.update(status="incomplete", error="Interrupted")
    output = json.dumps(result, ensure_ascii=False, indent=2)
    # Redact an echo only for a session launched with the API key method.
    if result.get("invocation", {}).get("auth") == API_KEY_AUTH:
        if key := os.environ.get("GEMINI_API_KEY"):
            output = output.replace(json.dumps(key, ensure_ascii=False)[1:-1], "[REDACTED]")
    print(output)
    if result["status"] == "not_configured":
        return 3
    return 0 if result["status"] in {"initialized", "session_ready", "completed"} else 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
