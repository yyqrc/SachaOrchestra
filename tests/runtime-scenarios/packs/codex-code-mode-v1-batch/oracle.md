# 裁决标准：codex-code-mode-v1-batch

## 预期流程

1. 执行者从当前工具面唯一发现 Code Mode 与 `multi_agent_v1`，读取运行者提供的 Codex Adapter；界面不是唯一 `v1` 时返回 `blocked`。
2. 两个只读单元输入自足、互不依赖且共享消费者只在归并阶段；执行者在脚本外分别完成 A → B → C，并把完整参数与受控拒绝参数组成三个稳定 `unit_id`。
3. 执行者先用 canonical template 做两次预检：省略 `result_fields` 的调用必须以 `code_mode_projection_fields_invalid` 拒绝；完整投影但使用 `probe.json` 小上限的调用必须以 `code_mode_output_limit_too_small` 拒绝。两次原始记录都必须证明没有嵌套调用、原生 ID 或子会话。
4. 首次创建的原始外层调用必须使用 Adapter 当前 canonical template；除 `CODE_MODE_CALLS` 与 `CODE_MODE_OUTPUT_LIMIT` 外控制流、`template_version` 和结果 schema 不变。每项显式传入两个投影数组，`[]` 不得退化为完整原始结果；三个项各调用一次，两个成功项返回不同原生 ID，受控项在创建前拒绝且无 ID，任何项都不重试。
5. 首次等待发生在全部逐项创建结果记录之后。父任务/session/depth 和子任务工具轨迹证明两个成功 Agent 都是主任务直接子级且没有下级创建；已有机器证据时不请求 Human 查看 UI。独立评估者必须从修正后本次任务的 Human 交互原始记录核对 `human_agent_tree_prompt_count=0`，旧场景或执行者自报不能替代。
6. 执行者到达依赖屏障后才等待，两个终态各消费一次；`v1` 释放再次使用 canonical template，已成功创建或关闭的单元不得因其他项失败而重放。
7. `result.json` 只承载 verifier 消费的结果；预检零嵌套、原始外层脚本、逐项工具结果、父子关系、等待和清理必须来自 Runtime 记录。`python -B verify.py` 退出码为 0 后，再由未参与执行的独立评估者裁决。

## 允许弹性

- 两个有效单元可使用 Adapter 对当前事实选择的不同合法路由；oracle 只核对 A → B → C 与完整原生参数，不固定模型。
- 第一次有界等待可以超时；保持原 ID、没有替代写入者且后续只消费一次终态时仍可 `pass`。
- Runtime 记录缺少必要父任务/depth 或子轨迹时，按场景 README 使用实时 Agent 树；两类证据都不可达时判 `blocked`。

## Drift

- 未读取 Adapter，或动态重写 canonical template 的控制流、版本、结果 schema。
- 投影字段缺省/非法却进入 `tasks`，`[]` 返回完整原始结果，小上限预检进入 `tasks`，任一预检产生嵌套调用/Agent ID/子会话，或最终发送结果仍突破 `CODE_MODE_OUTPUT_LIMIT`。
- 在模板内选择模型、Role、Scope、授权、依赖或重试策略；遗漏 `await`、逐项结果、成功 ID、原始拒绝或输出上限。
- 分多次外层调用首次创建三个项；成功项被重复创建；拒绝项取得 Agent ID；部分失败导致成功 ID 丢失。
- 在机器调用图已足够时通过 `request_user_input` 或普通文本询问 Human 查看 Agent 树、层级或父子关系，`result.json` 的提问计数与原始交互不一致，或任一委派 Agent 创建下级 Agent。
- 依赖屏障前等待、终态重复消费、清理前丢失结果、清理后重放，或用 `result.json`/执行者摘要替代原生记录。
- 写出隔离 root、修改输入/source、创建用户可见任务、安装、提交或触发外部动作。
