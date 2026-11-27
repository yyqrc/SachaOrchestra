from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/sacha-orchestra/adapters/codex/scripts/agy_acp.py"
SPEC = importlib.util.spec_from_file_location("sacha_agy_acp", SCRIPT)
assert SPEC and SPEC.loader
acp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acp)


def fake_agent():
    def send(**value):
        print(json.dumps({"jsonrpc": "2.0", **value}), flush=True)

    def receive():
        return json.loads(input())

    def consume_permission(session):
        send(id="permission", method="session/request_permission", params={
            "sessionId": session, "toolCall": {"title": "Write file", "kind": "edit"},
            "options": [
                {"kind": "allow_once", "optionId": "allow"},
                {"kind": "reject_once", "optionId": "reject"},
            ],
        })
        assert receive()["result"]["outcome"] == {"outcome": "selected", "optionId": "reject"}
        send(id="file", method="fs/write_text_file", params={
            "sessionId": session, "path": str(Path.cwd() / "unapproved"), "content": "bad",
        })
        assert receive()["error"]["code"] == -32601

    if os.environ.get("SACHA_TEST_FAIL_START"):
        warning = "noise" * 5000 + "启动失败 " + os.environ["GEMINI_API_KEY"]
        sys.stderr.buffer.write(warning.encode("utf-8"))
        raise SystemExit(7)

    assert sys.argv[2:4] == ["acp", "--disable-telemetry"]
    if "--agent" in sys.argv:
        assert "--sandbox" in sys.argv
    else:
        assert "GEMINI_API_KEY" not in os.environ
    assert "--dangerously-skip-permissions" not in sys.argv
    cached_login = os.environ.get("SACHA_TEST_CACHED_LOGIN")
    if cached_login:
        assert "GEMINI_API_KEY" not in os.environ
    auth = False
    model = {
        "id": "model", "type": "select", "currentValue": "gemini-default",
        "options": [{"value": "gemini-default"}, {"value": "gemini-test"}],
    }
    session = None
    while line := sys.stdin.readline():
        request = json.loads(line)
        method, params = request["method"], request["params"]
        result = {}
        if method == "initialize":
            assert params["clientCapabilities"] == {}
            capabilities = ({"loadSession": True} if os.environ.get("SACHA_TEST_LOAD") else
                            {"sessionCapabilities": {"resume": {}}})
            result = {
                "protocolVersion": 1, "agentCapabilities": capabilities,
                "authMethods": [{"id": "gemini-api-key"}, {"id": "oauth-personal"}],
            }
        elif method == "authenticate":
            assert cached_login is None
            assert params == {"methodId": "gemini-api-key"}
            auth = True
        elif method in {"session/new", "session/resume", "session/load"}:
            assert "--agent" in sys.argv
            assert params["cwd"] == str(Path.cwd().resolve()) and params["mcpServers"] == []
            if cached_login == "expired":
                send(id=request["id"], error={"code": -32000, "message": "Authentication required"})
                continue
            assert auth or cached_login == "active"
            session = params.get("sessionId") or uuid.uuid4().hex
            state = Path(session + ".fake-session")
            if method == "session/new":
                state.write_text("", encoding="utf-8")
            else:
                assert state.is_file()
                if method == "session/load":
                    send(method="session/update", params={
                        "sessionId": session, "update": {
                            "sessionUpdate": "agent_message_chunk",
                            "content": {"type": "text", "text": "replayed"},
                        },
                    })
            result = {"sessionId": session, "configOptions": [model]}
        elif method == "session/set_config_option":
            assert params["sessionId"] == session
            model["currentValue"] = params["value"]
            result = {"configOptions": [model]}
        elif method == "session/prompt":
            assert params["sessionId"] == session
            text = params["prompt"][0]["text"]
            if text == "wait":
                assert receive() == {
                    "jsonrpc": "2.0", "method": "session/cancel", "params": {"sessionId": session},
                }
                send(id=request["id"], result={"stopReason": "cancelled"})
                continue
            if text == "disconnect":
                return
            if text == "quota":
                send(id=request["id"], error={"code": 429, "message": "test quota exhausted"})
                continue
            if text == "permission":
                consume_permission(session)
            previous = state.read_text(encoding="utf-8")
            if text.startswith("remember "):
                state.write_text(previous + text.removeprefix("remember "), encoding="utf-8")
            send(method="session/update", params={
                "sessionId": session, "update": {
                    "sessionUpdate": "agent_message_chunk",
                    "content": {"type": "text", "text": previous or text},
                },
            })
            result = {"stopReason": "end_turn"}
        else:
            raise AssertionError(method)
        send(id=request["id"], result=result)
        if method == "session/new" and os.environ.get("SACHA_TEST_STALLED_STDIN"):
            # Keep stdin open, but stop reading so a large prompt fills the pipe.
            time.sleep(60)
        if method == "session/prompt" and params["prompt"][0]["text"] == "hang_after_result":
            time.sleep(60)


class AcpClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.popen = subprocess.Popen
        self.connection = self.root / "sacha-acp.json"
        self.saved = {
            "managed_by": "sacha-orchestra/setup-agents",
            "executable": str(Path(sys.executable).resolve()),
            "auth": "gemini-api-key",
        }
        self.connection.write_text(json.dumps(self.saved), encoding="utf-8")

    def invoke(self, text=None, previous=None, extra=(), probe=False, load=False):
        args = [str(SCRIPT), "--cwd", str(self.root)]
        if probe:
            args.extend(["--agy", sys.executable, "--probe"])
        else:
            args.extend(["--agent", "sacha-explorer"])
        if text is not None:
            prompt = self.root / "prompt.txt"
            prompt.write_text(text, encoding="utf-8")
            args.extend(["--prompt-file", str(prompt)])
        if previous is not None:
            receipt = self.root / "receipt.json"
            receipt.write_text(json.dumps(previous), encoding="utf-8")
            args.extend(["--resume-result", str(receipt)])
        args.extend(extra)

        def start_fake(argv, **kwargs):
            return self.popen([sys.executable, "-B", __file__, "--fake-agent", *argv[1:]], **kwargs)

        key = "fixture-key-only-no-service"
        env = {"GEMINI_API_KEY": key, "SACHA_TEST_LOAD": "1" if load else ""}
        out = io.StringIO()
        with patch.dict(os.environ, env), patch.object(sys, "argv", args), \
                patch.object(acp, "connection_path", return_value=self.connection), \
                patch.object(acp.subprocess, "Popen", side_effect=start_fake) as started, \
                contextlib.redirect_stdout(out):
            code = acp.main()
        self.process_starts = started.call_count
        self.raw_result = out.getvalue()
        self.assertNotIn(key, self.raw_result)
        return code, json.loads(self.raw_result)

    def test_probe_and_three_turns_across_processes_with_isolation(self):
        code, probe = self.invoke(probe=True)
        self.assertEqual((0, "initialized", "not_sent", 0),
                         (code, probe["status"], probe["turn_state"], probe["process_exit_code"]))
        self.assertNotIn("session", probe)
        code, first = self.invoke("remember alpha", extra=("--set-config", "model=gemini-test"))
        self.assertEqual((0, "gemini-test"), (code, first["config_options"][0]["currentValue"]))
        code, second = self.invoke("remember beta", first)
        self.assertEqual((0, "session/resume", "alpha"), (code, second["session_method"], second["text"]))
        code, third = self.invoke("recall", second, load=True)
        self.assertEqual((0, "session/load", "alphabeta"),
                         (code, third["session_method"], third["text"]))
        self.assertEqual(first["session"], third["session"])
        code, separate = self.invoke("recall")
        self.assertEqual((0, "recall"), (code, separate["text"]))
        self.assertNotEqual(first["session"], separate["session"])
        first["session"]["agent"] = "sacha-reviewer"
        code, mismatch = self.invoke("recall", first)
        self.assertEqual((2, "not_sent"), (code, mismatch["turn_state"]))

    def test_permissions_and_cancel_leave_no_side_effect(self):
        code, denied = self.invoke("permission")
        self.assertEqual(0, code)
        self.assertEqual(["selected", "unsupported"], [request["outcome"] for request in denied["requests"]])
        self.assertFalse((self.root / "unapproved").exists())
        code, cancelled = self.invoke("wait", extra=("--timeout", "0.25"))
        self.assertEqual((2, "timeout", "terminal", "cancelled", 0),
                         (code, cancelled["cancel_requested"], cancelled["turn_state"],
                          cancelled["stop_reason"], cancelled["process_exit_code"]))

    def test_remote_error_and_unknown_turn_have_distinct_evidence(self):
        code, quota = self.invoke("quota")
        self.assertEqual((2, "terminal_error", 429, 0),
                         (code, quota["turn_state"], quota["error_code"], quota["process_exit_code"]))
        code, unknown = self.invoke("disconnect")
        self.assertEqual((2, "unknown", 0), (code, unknown["turn_state"], unknown["process_exit_code"]))
        self.assertNotIn("stop_reason", unknown)
        code, refused = self.invoke("recall", unknown)
        self.assertEqual((2, "not_sent"), (code, refused["turn_state"]))

    def test_startup_failure_keeps_a_bounded_and_readable_diagnostic(self):
        with patch.dict(os.environ, {"SACHA_TEST_FAIL_START": "1"}):
            code, failed = self.invoke("fixture prompt")
        self.assertEqual((2, "not_sent", 7), (code, failed["turn_state"], failed["process_exit_code"]))
        self.assertLessEqual(len(failed["stderr"].encode("utf-8")), acp.STDERR_LIMIT)
        self.assertTrue(failed["stderr"].endswith("启动失败 [REDACTED]"))
        self.assertIn("启动失败", self.raw_result)

    def test_timeout_when_the_prompt_cannot_be_written_to_the_pipe(self):
        with patch.dict(os.environ, {"SACHA_TEST_STALLED_STDIN": "1"}), \
                patch.object(acp, "CANCEL_GRACE", 0.25):
            code, stalled = self.invoke("x" * 250_000, extra=("--timeout", "0.25"))
        self.assertEqual((2, "timeout", "unknown"),
                         (code, stalled["cancel_requested"], stalled["turn_state"]))
        self.assertTrue(stalled["forced_shutdown"])
        self.assertIsNotNone(stalled["process_exit_code"])
        self.assertNotEqual(0, stalled["process_exit_code"])

    def test_forced_shutdown_does_not_create_a_continuable_result(self):
        with patch.object(acp, "CANCEL_GRACE", 0.25):
            code, stalled = self.invoke("hang_after_result")
        self.assertEqual((2, "incomplete", "end_turn", True),
                         (code, stalled["status"], stalled["stop_reason"], stalled["forced_shutdown"]))
        code, resumed = self.invoke("recall", stalled)
        self.assertEqual((2, "not_sent"), (code, resumed["turn_state"]))

    def test_refuses_to_resolve_executable_from_project_directory(self):
        code, refused = self.invoke(probe=True, extra=("--agy", "agy.exe"))
        self.assertEqual((2, "not_sent"), (code, refused["turn_state"]))
        self.assertNotIn("process_id", refused)

    def test_saved_setup_drives_dispatch_without_a_separate_process(self):
        self.connection.unlink()
        code, result = self.invoke("fixture prompt")
        self.assertEqual((3, "not_configured", 0), (code, result["status"], self.process_starts))
        disabled = {**self.saved, "auth": None}
        self.connection.write_text(json.dumps(disabled), encoding="utf-8")
        code, result = self.invoke("fixture prompt")
        self.assertEqual((3, "not_configured", 0), (code, result["status"], self.process_starts))
        self.connection.write_text(json.dumps(self.saved), encoding="utf-8")
        code, result = self.invoke("fixture prompt")
        self.assertEqual((0, "completed", 1), (code, result["status"], self.process_starts))
        self.assertEqual("fixture prompt", result["text"])

    def test_session_cannot_override_the_saved_executable(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            self.invoke("fixture prompt", extra=("--agy", sys.executable))
        self.assertEqual(2, raised.exception.code)

    def test_cached_login_opens_session_and_returns_expiration_without_switching_auth(self):
        self.saved["auth"] = "cached-login"
        self.connection.write_text(json.dumps(self.saved), encoding="utf-8")
        with patch.dict(os.environ, {"SACHA_TEST_CACHED_LOGIN": "active"}):
            code, result = self.invoke("fixture prompt")
        self.assertEqual((0, "completed", "cached-login", 1), (
            code, result["status"], result["session"]["auth"], self.process_starts,
        ))
        with patch.dict(os.environ, {"SACHA_TEST_CACHED_LOGIN": "expired"}):
            code, result = self.invoke("fixture prompt")
        self.assertEqual((2, -32000, "not_sent", 1), (
            code, result["error_code"], result["turn_state"], self.process_starts,
        ))

    def test_saved_setup_does_not_follow_redirects(self):
        resolve = Path.resolve
        for redirected in (self.connection, Path(self.saved["executable"])):
            def resolve_path(path, *args, **kwargs):
                if path == redirected:
                    return self.root / "redirected"
                return resolve(path, *args, **kwargs)

            with self.subTest(redirected=redirected.name), patch.object(Path, "resolve", resolve_path):
                code, result = self.invoke("fixture prompt")
                self.assertEqual((2, "not_sent", 0), (code, result["turn_state"], self.process_starts))
                self.assertIn("redirect", result["error"])


if __name__ == "__main__":
    if sys.argv[1:2] == ["--fake-agent"]:
        fake_agent()
    else:
        unittest.main()
