# 任务：验证只读 Code Mode Runtime asset

你会收到一个隔离 root，以及当前源码 Codex Runtime Adapter 和 `code-mode-batch.js` 的明确 path。读取 root 内的 `probe.json`、Adapter 与 asset；不得读取源任务包 path 或 `oracle.md`。当前 `functions.exec`、`get_goal` 或 `exec_command` 不可达，或任一目标在 `ALL_TOOLS` 中不是唯一 callable 时停止并报告 `blocked`，不得从配置或历史任务猜测。

先分别使用一个单调用 `functions.exec` 执行 `get_goal({})`，以及使用另一个单调用 `functions.exec` 执行 `exec_command`；后者的完整参数固定为 `cmd="Get-Location"`、`workdir=<隔离 root>`、`shell="powershell"`、`login=false`，不得添加其他命令。记录两个外层调用和消费者所需字段，作为逐次基线。随后计算 asset 的 SHA-256，并在一个 `functions.exec` 中先设置：

- `globalThis.CODE_MODE_CALLS`：`goal_snapshot` 调用 `get_goal` 并投影 `goal`、`remainingTokens`、`completionBudgetReport`；`cwd_snapshot` 调用 `exec_command`，完整参数与基线相同，并投影 `exit_code`、`output`、`wall_time_seconds`；两项的 `reference_fields` 都是 `[]`。
- `globalThis.CODE_MODE_OUTPUT_LIMIT`：使用 `probe.json` 的 `output_limit`。

两个输入绑定后必须原样附加 asset 全文并执行，不得改写 asset 控制流、schema 或结果。保留外层程序原文、两个嵌套调用及 caller 关系、asset 原始输出和最终解析结果。程序中不得调用任何 Agent、写入、消息发送或外部资源工具；不得重试任一调用。

只在隔离 root 写入 `result.json`。结构包含 `asset_path`、`asset_sha256`、`baseline`、`code_mode`、`retry_count`、`agent_tool_call_count`、`human_prompt_count` 和 `evidence_layers`；其中 baseline 保存两个工具名、`outer_call_count=2`、直接 goal 值、cwd 的 `exit_code` 与 `output`，Code Mode 保存 `outer_call_count=1`、`nested_call_count=2` 和解析后的 asset payload。然后运行 `python -B verify.py`，报告退出码、文件 delta、输入哈希、未验证边界以及逐次与 Code Mode 的模型工具往返差异。

授权只覆盖读取明确提供的入口和隔离 root、两个直接只读基线调用、一个只读 `functions.exec`、写入 `result.json` 和执行 verifier；不得修改输入、SachaOrchestra 源码、Git、安装、配置或外部状态，不得创建 Agent。
