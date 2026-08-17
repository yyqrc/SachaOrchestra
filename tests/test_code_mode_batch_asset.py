import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "plugins" / "sacha-orchestra" / "adapters" / "codex" / "code-mode-batch.js"
NODE = shutil.which("node")

NODE_WRAPPER = r"""
const fs = require("fs");

(async () => {
  const config = JSON.parse(fs.readFileSync(0, "utf8"));
  const asset = fs.readFileSync(process.argv[1], "utf8");
  globalThis.CODE_MODE_CALLS = config.calls;
  globalThis.CODE_MODE_OUTPUT_LIMIT = config.outputLimit;

  const callLog = [];
  const tools = {};
  for (const [name, behavior] of Object.entries(config.tools)) {
    tools[name] = async (args) => {
      callLog.push({ name, args });
      if (Object.prototype.hasOwnProperty.call(behavior, "reject")) {
        throw new Error(behavior.reject);
      }
      return behavior.value;
    };
  }

  const outputs = [];
  const text = (value) => outputs.push(String(value));
  let thrown = null;
  try {
    const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
    await new AsyncFunction("ALL_TOOLS", "tools", "text", asset)(
      config.allTools,
      tools,
      text,
    );
  } catch (error) {
    thrown = String(error);
  }
  process.stdout.write(JSON.stringify({ thrown, callLog, outputs }));
})().catch((error) => {
  process.stderr.write(String(error));
  process.exitCode = 2;
});
"""


def call(unit_id, name, *, result_fields=None, reference_fields=None):
    return {
        "unit_id": unit_id,
        "normalized_name": name,
        "args": {"source": unit_id},
        "result_fields": ["count", "sum"] if result_fields is None else result_fields,
        "reference_fields": ["reference"] if reference_fields is None else reference_fields,
    }


@unittest.skipUnless(NODE, "node is required to execute the Runtime asset")
class CodeModeBatchAssetTests(unittest.TestCase):
    def run_asset(self, calls, tools, *, output_limit=12000, all_tools=None):
        if all_tools is None:
            all_tools = [{"name": name} for name in tools]
        completed = subprocess.run(
            [NODE, "-e", NODE_WRAPPER, str(ASSET)],
            input=json.dumps(
                {
                    "calls": calls,
                    "tools": tools,
                    "allTools": all_tools,
                    "outputLimit": output_limit,
                }
            ),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_two_successful_calls_are_settled_once(self):
        result = self.run_asset(
            [call("alpha", "read_alpha"), call("beta", "read_beta")],
            {
                "read_alpha": {"value": {"count": 3, "sum": 12, "reference": "alpha.json"}},
                "read_beta": {"value": {"count": 3, "sum": 18, "reference": "beta.json"}},
            },
        )

        self.assertIsNone(result["thrown"])
        self.assertEqual([entry["name"] for entry in result["callLog"]], ["read_alpha", "read_beta"])
        payload = json.loads(result["outputs"][0])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["status"], "settled")
        self.assertEqual(payload["results"][0]["value"], {"count": 3, "sum": 12})
        self.assertEqual(payload["results"][1]["references"], {"reference": "beta.json"})

    def test_duplicate_unit_is_rejected_before_calls(self):
        result = self.run_asset(
            [call("same", "read_alpha"), call("same", "read_beta")],
            {
                "read_alpha": {"value": {}},
                "read_beta": {"value": {}},
            },
        )

        self.assertIn("code_mode_unit_id_duplicate:same", result["thrown"])
        self.assertEqual(result["callLog"], [])

    def test_invalid_projection_is_rejected_before_calls(self):
        invalid = call("alpha", "read_alpha")
        del invalid["result_fields"]
        result = self.run_asset(
            [invalid, call("beta", "read_beta")],
            {
                "read_alpha": {"value": {}},
                "read_beta": {"value": {}},
            },
        )

        self.assertIn("code_mode_projection_fields_invalid:alpha:result_fields", result["thrown"])
        self.assertEqual(result["callLog"], [])

    def test_small_output_limit_is_rejected_before_calls(self):
        result = self.run_asset(
            [call("alpha", "read_alpha"), call("beta", "read_beta")],
            {
                "read_alpha": {"value": {}},
                "read_beta": {"value": {}},
            },
            output_limit=1,
        )

        self.assertIn("code_mode_output_limit_too_small", result["thrown"])
        self.assertEqual(result["callLog"], [])

    def test_tool_resolution_is_rejected_before_calls(self):
        result = self.run_asset(
            [call("alpha", "read_alpha"), call("beta", "read_beta")],
            {
                "read_alpha": {"value": {}},
                "read_beta": {"value": {}},
            },
            all_tools=[{"name": "read_alpha"}],
        )

        self.assertIn("code_mode_tool_resolution_failed:beta:read_beta:0", result["thrown"])
        self.assertEqual(result["callLog"], [])

    def test_ambiguous_tool_resolution_is_rejected_before_calls(self):
        result = self.run_asset(
            [call("alpha", "read_alpha"), call("beta", "read_beta")],
            {
                "read_alpha": {"value": {}},
                "read_beta": {"value": {}},
            },
            all_tools=[
                {"name": "read_alpha"},
                {"name": "read_alpha"},
                {"name": "read_beta"},
            ],
        )

        self.assertIn("code_mode_tool_resolution_failed:alpha:read_alpha:2", result["thrown"])
        self.assertEqual(result["callLog"], [])

    def test_one_rejection_does_not_hide_other_result(self):
        result = self.run_asset(
            [call("alpha", "read_alpha"), call("beta", "read_beta")],
            {
                "read_alpha": {"value": {"count": 3, "sum": 12, "reference": "alpha.json"}},
                "read_beta": {"reject": "controlled_failure"},
            },
        )

        self.assertIsNone(result["thrown"])
        self.assertEqual(len(result["callLog"]), 2)
        payload = json.loads(result["outputs"][0])
        self.assertEqual(payload["results"][0]["status"], "fulfilled")
        self.assertEqual(payload["results"][1]["status"], "rejected")
        self.assertIn("controlled_failure", payload["results"][1]["error"])

    def test_large_values_are_omitted_before_references(self):
        result = self.run_asset(
            [call("alpha", "read_alpha"), call("beta", "read_beta")],
            {
                "read_alpha": {
                    "value": {"count": 3, "sum": "x" * 1000, "reference": "alpha.json"}
                },
                "read_beta": {
                    "value": {"count": 3, "sum": "y" * 1000, "reference": "beta.json"}
                },
            },
            output_limit=320,
        )

        self.assertIsNone(result["thrown"])
        payload = json.loads(result["outputs"][0])
        self.assertEqual(payload["status"], "output_limit_exceeded")
        self.assertTrue(all(entry["value_omitted"] for entry in payload["results"]))
        self.assertEqual(payload["results"][0]["references"], {"reference": "alpha.json"})

    def test_large_references_fall_back_to_outcome_unknown(self):
        result = self.run_asset(
            [call("alpha", "read_alpha"), call("beta", "read_beta")],
            {
                "read_alpha": {
                    "value": {"count": 3, "sum": "x" * 1000, "reference": "a" * 1000}
                },
                "read_beta": {
                    "value": {"count": 3, "sum": "y" * 1000, "reference": "b" * 1000}
                },
            },
            output_limit=220,
        )

        self.assertIsNone(result["thrown"])
        payload = json.loads(result["outputs"][0])
        self.assertEqual(payload["status"], "outcome_unknown")
        self.assertEqual([entry["unit_id"] for entry in payload["units"]], ["alpha", "beta"])


if __name__ == "__main__":
    unittest.main()
