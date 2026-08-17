# Codex Code Mode 只读编排压缩 Spec

> 状态：2026-08-17 Human 已普通批准；当前修订为唯一执行基线
> 原始批准：2026-08-14

本文沿用 [Workflow Contract](../../../plugins/sacha-orchestra/core/workflow-contract.md) 的主任务生命周期，以及 [Codex Runtime Adapter](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md) 的 Runtime 传输边界。Code Mode 只压缩非 Agent 的只读工具调用，不取得流程、Role、Scope、授权、验收或根终态 Owner。

## 已确认事实与修订原因

- Programmatic Tool Calling 只允许应用标记为 `programmatic` caller 可调用的工具进入 `functions.exec` 的 `ALL_TOOLS`；主模型可直接调用工具不表示 JavaScript 可调用。
- 既有 v1 Runtime 曾把 `multi_agent_v1.*` 暴露给 Code Mode，相关批量 Agent 场景与原始证据仍然真实；当前 v2 Runtime 把 `collaboration.*` 保持为 direct-only。
- Human 已决定所有 Agent 生命周期工具退出 Sacha Code Mode：v1/v2 的创建、消息、等待、取消、恢复和关闭只走各自原生协作界面。
- Human 已决定 Code Mode 首版只允许非 Agent 的只读工具，canonical JavaScript 由发布插件内独立 Runtime asset 拥有。
- Human 已决定执行前不满足 Code Mode 条件时不选择该优化路线，主任务继续直接读取；任一嵌套调用已开始或状态未知后不得直接重放。
- 本修订取代旧 Spec 中 Agent 批量派发、Agent 等待和 Agent 清理的现行产品路线；`codex-code-mode-v1-batch` 包保持原文与原始证据，不改写成当前验收或 v1/v2 混合证据。

## 需求不变量

- 主任务继续持有调用决定、结果消费、集成和根终态；Code Mode 只执行调用节点已决定的机械调用。
- Core/Role 继续决定授权、Scope、依赖和验收；Codex Adapter 只决定 Runtime 能力发现、传输选择、参数映射、恢复和证据映射。
- Code Mode 只用于至少两个输入自足、相互独立、无写入副作用，且中途不需要模型解释、授权或风险判断的调用。
- 当前工具已有原生批量入口时直接使用原生入口；不得为包一层脚本增加 Code Mode。
- 压缩目标是减少模型—宿主往返和进入模型上下文的中间结果；底层真实工具调用数与第三方 API 成本不因封装消失。
- Pi、OpenCode、Codex SDK、第二个 CLI/App Server、Hook、MCP、Registry、外部服务和其他 Runtime 不进入本 Scope。

## Owner 与直接消费者

| 内容 | 唯一 Owner | 直接消费者 | 可证伪方式 |
| --- | --- | --- | --- |
| 只读批量 JavaScript、输入/输出 schema、上限和停止分支 | `plugins/sacha-orchestra/adapters/codex/code-mode-batch.js` | Codex Adapter、Runtime 主任务、生产入口测试 | Adapter 内仍复制整段脚本，或测试文件成为 Runtime 模板来源 |
| Code Mode 选择、asset 加载、输入绑定、直接读取路线和恢复 | Codex Adapter | 主任务中的现有调用节点 | 从配置/模型名猜测能力，或目标不在 `ALL_TOOLS` 仍进入脚本 |
| 调用是否只读、是否独立、结果消费者与授权 | 现有 Core/Role 调用节点 | Codex Adapter | asset 重新判断需求、Scope、授权或副作用 |
| 场景输入、负例与独立裁决 | `tests/runtime-scenarios/**` | 场景运行者、独立评估者 | Runtime 读取 `tests/**`，或测试字符串替代真实调用证据 |

Runtime asset 位于发布 root 内并随插件发布；根目录规则、`docs/**` 与 `tests/**` 仍只供开发使用，安装后 Runtime 不读取。

## Scope

1. 新增 `plugins/sacha-orchestra/adapters/codex/code-mode-batch.js` 作为 canonical Runtime asset。
2. Codex Adapter 删除内嵌 JavaScript、Agent Code Mode 批量派发与 Agent Code Mode 清理，只保留 asset 选择、输入绑定、结果/恢复和证据映射。
3. Code Mode 候选调用只允许非 Agent 的只读工具；Agent 工具、文件/配置写入、消息发送和外部资源动作不得进入 `CODE_MODE_CALLS`。
4. 新增独立的只读 Code Mode Runtime 场景；现有 v1 Agent 场景原样保留，并从“当前基线包”移到最短的“已取代证据”入口。
5. 用真实 Runtime 记录验证实际 asset、`ALL_TOOLS` 解析、并发调用、逐项结果、输出上限和零重放；不以源码字符串或执行者自报证明行为。

预计修改位置不是硬性 allowlist；同 Scope 漏改可由 Executor 补齐，但不得扩大到 Core、Manager Skill、其他 Runtime、安装、配置或宿主实现。

## Non-goals

- 不通过 Code Mode 创建、继续、等待、取消、恢复或关闭 Agent。
- 不执行任何本地或外部写入，不处理审批敏感动作。
- 不新增第二套 Agent Loop、流程节点、Gate、状态、Artifact、Registry 或跨轮持久工作流。
- 不让 asset 选择 Role、模型、路由、依赖、Scope、授权、重试或 Human 决定。
- 不为所有工具建立静态 allowlist；调用节点负责只把已确认的只读调用交给 Adapter。
- 不修改 Codex/ChatGPT backend、OpenCodex、用户配置或 `allowed_callers`。

## 传输选择

主任务按以下顺序选择一次，后续不在两条路线间反复切换：

1. 调用数少于两个、存在依赖/中途语义判断、任一调用非只读，或结果无需代码缩减：使用直接调用。
2. 当前工具原生支持同一目标集合的批量输入：使用原生批量入口。
3. Runtime asset 可达，且每个目标 `normalized_name` 在当前 `ALL_TOOLS` 中恰有一个可调用入口：读取 asset、绑定完整输入并使用 Code Mode。
4. 任一前置不满足：记录 `code_mode_not_selected` 的具体原因，使用直接读取；这发生在任何嵌套调用前，不属于失败恢复或重试。

## Runtime asset 合同

调用方只绑定：

- `CODE_MODE_CALLS`：非空数组；每项包含稳定 `unit_id`、当前 `ALL_TOOLS` 中的 `normalized_name`、完整 `args`、显式 `result_fields` 和 `reference_fields`。
- `CODE_MODE_OUTPUT_LIMIT`：正整数，限制最终编码结果。

asset 必须：

1. 使用机器 `schema_version: 1`，不使用会与协作界面混淆的 `batch-v1/v2` 文本身份。
2. 在创建 Promise 前拒绝空调用、重复/非法 `unit_id`、非法投影、非法上限、工具零匹配/多匹配/不可调用，以及装不下最小未知结果包络的上限。
3. 每个输入恰好调用一次，使用 `await Promise.allSettled`，按输入顺序和 `unit_id` 返回逐项成功字段、错误与必要 reference。
4. 不自动重试、不补写参数、不扩大投影；字段冲突或需要语义解释时返回模型。
5. 最终结果依次尝试完整结果、保留 reference 的有界省略、最小 `outcome_unknown`；任何发送结果不得突破 `CODE_MODE_OUTPUT_LIMIT`。
6. 所有分支必须被 `await`；未等待 Promise 不得作为后台运行、等待或恢复机制。

## 失败与恢复

- 输入校验、上限预检或工具解析在 Promise 创建前失败：没有嵌套调用；主任务可沿用同 Scope 的直接读取路线。
- `Promise.allSettled` 中单项拒绝：保留其他逐项结果，不重放任何已调用项；主任务决定是否还需要新的语义判断。
- 外层调用返回不完整、最终状态未知或任一调用可能已开始：保留原始 call/reference，停止受影响批次，不直接重放。
- Runtime 明确证明全部嵌套调用未开始时，主任务可重新评估直接读取；不得把“不确定”解释为“未开始”。

## 实施顺序

### P0：恢复当前边界

1. 保存 Adapter、Spec、场景 README 与 v1 包的有界基线。
2. 删除 Adapter 当前 Agent Code Mode C.3、Agent close/wait Code Mode 描述和内嵌模板；不修改原生 v1/v2 协作映射。
3. v1 Agent 场景文件保持字节不变，只在 README 中移动其当前/历史身份。

### P1：Runtime asset

1. 从当前已验证模板提取与 Agent 无关的通用控制流到 `code-mode-batch.js`。
2. 将模板身份改为机器 `schema_version`，保持投影、最小包络预检、逐项 settled 和最终长度不变量。
3. 用隔离 fixture 覆盖正例、重复单元、非法投影、小上限、零/多匹配、单项拒绝和最终省略分支。

### P2：Adapter 消费

1. Adapter 只保留适用条件、原生批量优先、asset path、两个输入绑定、结果消费和停止/恢复边界。
2. Adapter 明确排除全部 Agent 工具和写入工具，不复制 asset 控制流或测试字段。
3. Manager/Core/Role Skill 不变；调用节点继续提供已决定且只读的完整参数。

### P3：Runtime 场景

1. 新增不涉及 Agent 的场景包，选择至少两个无原生共同批量入口的真实只读工具调用。
2. 使用一个外层 `functions.exec` 调用执行 asset，保存实际程序、嵌套 caller 关系、逐项结果与最终输出。
3. 对照逐次直接调用基线，证明模型工具往返减少，底层调用无遗漏/重复，结果与证据未丢失。
4. 未安装时只记 `source-scenario/current Runtime`；安装后 fresh Runtime 需要另行授权。

## 验收

### A 类：Agent 执行并判断

- `A-CM-01`：Runtime asset 是 canonical JavaScript 唯一 Owner；Adapter、Spec 和测试均不复制其完整控制流。
- `A-CM-02`：Adapter 的 Code Mode 路线不包含 `spawn_agent`、Agent 消息、Agent wait/interrupt/resume/close 或任何写入调用；原生 v1/v2 协作映射仍完整。
- `A-CM-03`：原生批量入口存在时不运行 asset；Code Mode 前置不足时直接读取且没有嵌套调用。
- `A-CM-04`：至少两个真实只读调用由一个外层 Code Mode 程序执行，逐项结果正确，外层模型工具往返少于逐次基线。
- `A-CM-05`：非法输入与小上限在 Promise 前拒绝；单项拒绝不掩盖其他结果；任何已开始/未知批次都不直接重放。
- `A-CM-06`：最终输出不突破上限，必要 reference 保留；原始程序、嵌套 caller、逐项结果和 Human 交互记录可达。
- `A-CM-07`：`codex-code-mode-v1-batch` 六个文件内容保持不变，并只作为已取代的 v1 Agent Code Mode 历史证据。
- `A-CM-08`：受影响 Scope 的 Owner、链接、生产入口测试和 `cprobe` 完整，`whitespace.errors=0`。

### B 类：Human 提供前置，Agent 执行并判断

- `B-CM-01`：Human 另行授权安装/刷新后，才从安装后的全新任务验证 asset 发现、读取和真实行为。

### C 类：Human 观察或判断

- `C-CM-01`：Human 只判断减少的模型往返是否值得新增 Runtime asset；工具结果正确性与调用关系由机器证据判断。

## 返回 Planner 条件

- 需要把 Agent 生命周期、写入、审批敏感动作或跨 Runtime 工具纳入 Code Mode。
- 安装后的 Runtime 无法读取独立 asset，必须改变发布结构或新增宿主能力。
- `ALL_TOOLS` 缺少足够的真实只读候选，无法证明收益；此时以 `no_op` 关闭，不预建通用机制。
- 需要新增 allowlist、Registry、Hook、MCP、外部服务、持久状态或改变 Core/Role/授权/验收。

## 授权边界

Human 已确认 Clarify 决定并普通批准本 Spec，授权当前 Executor 在本 Scope 内实施与执行本地最窄验证；不包含安装、配置修改、提交、push、tag 或发布。
