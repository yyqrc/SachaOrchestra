import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "plugins/sacha-orchestra/adapters/codex/scripts/cbc_acp.py"
SPEC = importlib.util.spec_from_file_location("sacha_cbc_acp", SCRIPT)
assert SPEC and SPEC.loader
cbc = importlib.util.module_from_spec(SPEC)
with patch.object(sys, "path", [str(SCRIPT.parent), *sys.path]):
    SPEC.loader.exec_module(cbc)


class CodeBuddyDispatchTests(unittest.TestCase):
    def test_role_model_and_default_effort_must_match_before_sending_prompt(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            role = "sacha-reviewer"
            prompt = cwd / "prompt.txt"
            prompt.write_text("Synthetic review input", encoding="utf-8")
            args = SimpleNamespace(cwd=cwd, agent=role, prompt_file=prompt, resume_result=None,
                                   model=None, timeout=30)
            for current_role, offered_model, error in (
                ("cli", cbc.DEFAULT_MODEL, "did not confirm the selected role"),
                (role, "another-model", "Unavailable ACP config selection"),
                (role, cbc.DEFAULT_MODEL, None),
            ):
                with self.subTest(current_role=current_role, offered_model=offered_model):
                    client = Mock()
                    model = {"id": "model", "type": "select", "currentValue": offered_model,
                             "options": [{"value": offered_model}]}
                    effort = {"id": "thought_level", "type": "select", "currentValue": "low",
                              "options": [{"value": "low"}, {"value": "high"}]}
                    client.request.side_effect = [
                        {"protocolVersion": 1, "agentCapabilities": {"mainAgentSupport": True}},
                        {"agents": [{"name": role}]},
                        {"sessionId": "test-session", "currentAgentName": current_role, "configOptions": [model, effort]},
                        {"configOptions": [model, {**effort, "currentValue": "high"}]},
                    ]
                    report = {"status": "error", "turn_state": "not_sent"}
                    client.report = report
                    with patch.object(cbc, "launcher", return_value=["codebuddy"]), \
                            patch.object(cbc, "AcpClient", return_value=client):
                        if error:
                            with self.assertRaisesRegex(cbc.AcpError, error):
                                cbc.run(args, report)
                            client.prompt.assert_not_called()
                        else:
                            cbc.run(args, report)
                            client.request.assert_called_with("session/set_config_option", sessionId="test-session",
                                                              configId="thought_level", value="high")
                            client.prompt.assert_called_once_with("Synthetic review input", 30)
                            self.assertEqual(report["session"]["confirmed_model"], "claude-opus-5.5")
                    client.close.assert_called_once_with(accept_termination=True)

    def test_continuation_reuses_the_confirmed_nondefault_model_after_forced_shutdown(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp).resolve()
            role = "sacha-reviewer"
            previous_model = "claude-sonnet-5"
            session_id = "test-session"
            session = {"runtime": "cbc-acp", "cwd": str(cwd), "agent": role, "auth": "cached-login",
                       "sessionId": session_id, "confirmed_model": previous_model}
            receipt = cwd / "receipt.json"
            prior = {"status": "completed", "process_exit_code": 1, "forced_shutdown": True, "session": session}
            receipt.write_text(json.dumps(prior), encoding="utf-8")
            args = SimpleNamespace(cwd=cwd, agent=role, prompt_file=None, resume_result=receipt, model=None)
            client = Mock()
            report = {"status": "error", "turn_state": "not_sent"}
            client.report = report
            option = {"id": "model", "type": "select", "currentValue": previous_model,
                      "options": [{"value": previous_model}, {"value": cbc.DEFAULT_MODEL}]}
            client.request.side_effect = [
                {"protocolVersion": 1, "agentCapabilities": {"mainAgentSupport": True, "loadSession": True}},
                {"agents": [{"name": role}]},
                {"sessionId": session_id, "currentAgentName": role, "configOptions": [option]},
            ]
            with patch.object(cbc, "launcher", return_value=["codebuddy"]), \
                    patch.object(cbc, "AcpClient", return_value=client) as start:
                cbc.run(args, report)
                self.assertEqual(start.call_args.args[0][-2:], ["--model", previous_model])
                self.assertEqual((report["session_method"], report["session"]["confirmed_model"]),
                                 ("session/load", previous_model))
                client.request.assert_any_call("session/load", cwd=str(cwd), mcpServers=[], sessionId=session_id)
                self.assertEqual(client.request.call_count, 3)

                receipt.write_text(json.dumps({**prior, "process_exit_code": None}), encoding="utf-8")
                with self.assertRaisesRegex(cbc.AcpError, "matching settled session"):
                    cbc.run(args, report)
                start.assert_called_once()

    def test_staging_directory_reuses_only_the_same_role(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp).resolve()
            cbc.prepare_role(cwd, "sacha-explorer")
            cbc.prepare_role(cwd, "sacha-explorer")
            with self.assertRaisesRegex(cbc.AcpError, "Unexpected CodeBuddy configuration"):
                cbc.prepare_role(cwd, "sacha-reviewer")
