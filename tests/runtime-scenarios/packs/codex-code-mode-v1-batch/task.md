# 任务：验证 Codex Code Mode 批量传输

你会收到一个隔离 root，以及当前源码 Codex Runtime Adapter 的明确 reference。读取 root 内的 `probe.json`、`alpha.json`、`beta.json` 和 Adapter；当前协作界面不是唯一 `v1` 时停止并报告 `blocked`，不得猜测或切换界面。

使用 Adapter 的 canonical Code Mode template，在一次外层调用中提交三个完整调用项：两个只读委派单元分别读取 `alpha.json`、`beta.json` 并返回 `count` 与 `sum`；第三项使用 `probe.json` 给出的不存在 Agent 类型形成创建前受控拒绝。每项必须显式传入 `result_fields` 和 `reference_fields` 字符串数组，`[]` 表示不返回该类字段；两个有效单元的模型与参数必须在进入模板前按 Adapter 完成路由，模板不得选择或改写参数。

先执行两次无嵌套调用的前置校验：第一次使用一个完整有效的只读委派参数但省略 `result_fields`，必须以 `code_mode_projection_fields_invalid` 在创建 `tasks` 前拒绝；第二次使用同一模板和完整投影字段，把 `CODE_MODE_OUTPUT_LIMIT` 绑定为 `probe.json` 的 `small_output_limit`，必须以 `code_mode_output_limit_too_small` 在创建 `tasks` 前拒绝。两次均不得产生原生 Agent ID、子会话或嵌套工具调用；随后再执行上述三项正式批量调用，这不是创建重试。

在首次等待前保留两个成功原生 ID 和受控拒绝原文。父任务/session/depth 与子任务工具轨迹能够证明单层派发时直接使用机器证据，不向 Human 询问 Agent 树。到达真实依赖屏障后才等待两个成功单元，逐项只消费一次终态，并使用同一 canonical template 释放已消费的 `v1` Agent；不得重试任一创建项。

只在隔离 root 写入 `result.json`，结构包含 `template_version`、`collaboration_interface`、`projection_preflight`、`small_limit_preflight`、三个 `batch_results`、`human_agent_tree_prompt_count` 和 `retry_count`。`human_agent_tree_prompt_count` 只统计要求 Human 查看 Agent 树、层级或父子关系的 `request_user_input`/普通文本提问，本场景必须为 `0`；两个预检项必须分别记录 `status`、空 `agent_id` 和原始 `error`；两个成功项必须记录 `unit_id`、`spawn_status`、`agent_id`、`terminal_status` 与 `summary`；拒绝项必须记录 `unit_id`、`spawn_status`、空 `agent_id` 和原始 `error`。然后运行 `python -B verify.py`，报告两次预检外层调用及零嵌套证据、正式外层调用、显式投影、原生派发/返回、机器调用图、Human 交互原始记录、等待/清理、文件 delta、verifier 退出状态和未验证项；`result.json` 的计数不能替代原始交互记录。

授权只覆盖读取明确提供的入口和隔离 root、写入 `result.json`、执行 verifier；不得修改输入、SachaOrchestra 源码、Git 状态、安装、配置或外部资源，不得创建用户可见任务或让委派 Agent 再派发。
