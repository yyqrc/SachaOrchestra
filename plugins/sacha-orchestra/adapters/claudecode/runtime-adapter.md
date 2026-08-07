# Claude Code Runtime Adapter

> 实现：Intake Contract 6；Workflow Contract 19；Human Interaction Contract 1；Assurance Contract 2；Coordination Contract 10；Artifact Protocol 6
> 状态：Normative Claude Code mapping

## 1. 边界

本文映射 Claude Code 原生能力。owner reference：

- [Intake Contract](../../core/intake-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

入口、Role、Gate、Artifact、项目知识和发布状态由对应 Core、Skill、Project Integration 与 Evolution 拥有。本 Adapter 消费已确定的动作并映射 Claude Code transport。

## 2. Intake、Role 与 context

| Core 职责 | Claude Code 映射 |
| --- | --- |
| Intake/Route owner | 主对话通过正式 Skill discovery 装载 `using-sacha` |
| Planner | 独立 `Agent` context 装载 Planner 指令 |
| Executor | 明确 owner 的主对话或独立 `Agent` context |
| Reviewer | 未参与方案/实现的独立 `Agent` context |
| Manager | 主对话或控制面 `Agent` 协调独立任务 |
| Workflow owner | 默认是 Human 接受后的主对话；明确会话迁移后转为唯一 target |
| Human 互斥选择 | 使用已验证的原生选择能力；当前 Runtime 无可用映射时使用普通文本提问 |
| Human 进度与结果 | 由当前 workflow owner 在主对话展示 |

Runtime 常驻面只暴露 metadata。入口与 Role 由正式 Skill discovery 加载；当前动作需要 transport、恢复或 Runtime 证据时读取本 Adapter。

独立性由参与历史/input provenance 判断；agent 名称和 Runtime id 只用于调度。canonical entry/Role/Artifact 不可达时报告真实 discovery 缺口。

## 3. Transition、return 与恢复

每次 transition 先核对 Runtime 可用能力：

1. 核对 Task/Scope、Role、Artifact 可达性、provenance、owner 和 return path。
2. 同 context 工作在主对话执行；需要独立 provenance 的正式 Role transition 使用可保留 identity/terminal 的 Agent transport。一个有界 helper 由当前 owner 直接管理。
3. Source payload 由 route intent、Scope/Handoff reference、必要约束与 runtime identity 组成。
4. 独立 Review 使用新 `Agent` context；同 Task/Scope 的 repair、补证据和 re-review 保持原 owner。
5. 当前 transport 不可用时先尝试同 Scope 安全替代；owner/Role/return 仍无法唯一确定才进入 Core 阻塞路线。

### 3.1 完成与等待

前台执行由主对话消费 terminal result；后台执行由 owner 保持 phase，以正式 completion notification 和 identity 消费一次结果。派发后先推进不依赖结果且不冲突的 ready 工作；当前 owner 是 result consumer、下一 transition 依赖结果且没有其他 ready 工作时等待。

Target completion 返回结果/delta、实际验证、阻塞/风险和必要 reference；原生 notification 未携带且消歧必需时补 route identity/revision/dedup。错误、陈旧或重复结果停止当前 transition。

### 3.2 Human 决定与任务迁移

Adapter 消费 Workflow/Coordination 已确认的当前任务执行或用户任务迁移决定。当前任务执行由主对话继续；迁移需要 Human 已明确选择、可验证的等价用户会话 transport、唯一 owner 与单向 handoff，创建或复用 target 后由 Source 交付 reference 并结束。条件不足时保持当前 owner 和原始缺口；用户任务迁移 identity 只属于 target。

### 3.3 Feedback owner transfer

Adapter 消费 Coordination Contract 返回的 Feedback identity、匹配和 owner transfer 判断。唯一匹配或 `no_op` 返回既有用户可见 context reference；需要新目标时创建唯一 context；无法完成等价 owner transfer 时报告真实能力缺口。来源任务交付 reference 后结束。

### 3.4 模型映射

正式跨 context dispatch 先应用 Human 本次或批准 Scope 的精确配置，否则按 Role/risk 选择：

| Target | Model | 条件 |
| --- | --- | --- |
| Planner | `opus` | 需要冻结实质方案 |
| Executor | `opus` | 安全、权限、持久数据、breaking、不可逆外部动作或广泛兼容/发布风险 |
| Executor | `sonnet` | Scope/验收已冻结、实现与验证明确且属于普通风险 |
| Reviewer | `opus` | 独立验收 |
| bounded read-only helper | `haiku` | 自包含调查，只返回事实与 reference |

Planner/Reviewer/Manager Gate 结果来自 Core。普通 Executor 只有输入自包含时使用 `sonnet`。Human/Scope 精确配置不受支持时暂停；自动配置不可用时使用 Runtime default。owner 核对并记录 requested/effective model 与宿主覆盖原因；旧写入者 terminal/cancelled 前不得以其他模型启动同 Scope 写入。Direct/current context 保持当前模型和 route 状态。

Transport/Identity/Progress 失败按 Coordination Contract 生成 deviation；本 Adapter 补充原生结果未携带且恢复必需的 agent/task、前后台模式、notification/return、工具错误和恢复入口。

Human 输出按 Human Interaction Contract 展示。liveness 证据来自当前前台调用或后台 completion/cancel 状态；timeout 只报告当前状态。

搜索、diff、日志和列表默认返回短摘要，缺少决策信息时定向展开。大原文已有消费者时写入 task-local 文件或既有 Artifact，否则保留工具 reference；截断结果保留 Human Interaction Contract 规定的必须披露信息。

## 4. Agent 协调与 Artifact 映射

Manager Gate 开启后，每个 ready 单元使用独立 `Agent` context；`parallel_expected` 成立时在消费 completion 前启动至少两个实例。共享工作树同一文件/输出由 integration owner 串行处理；隔离 patch/候选实现使用并行 `Agent` context。

completion 在 transport 需要时核对 revision/dedup；结果按消费者和风险保留必要 delta，Artifact 只在消费者需要时落盘。真实 Runtime/槽位/依赖/Scope/授权阻塞为 `parallel_blocked`，条件满足却未启动为 `parallel_dispatch_missed`。

Agent context 通过稳定 reference 读取 Scope、Artifact、原始 evidence 和当前 consumer 所需 Handoff 语义。恢复以可用 route identity、Scope、revision 与 Entry Condition 为依据；reference 不可达时停止 transition 并记录唯一入口。

## 5. 发现机制与 Hook 边界

项目规则、`using-sacha`、canonical Role 和 Domain Skill 由当前 Runtime 的正式 discovery/加载机制暴露。discovery 的证据范围为入口可达；lifecycle、并行、恢复与验收使用真实行为证据。

SessionStart Hook 仅在 Human 另行授权且项目正式配置时预加载环境信息；入口接受、授权和 owner 恢复仍由正式 Core/Skill 路线处理。正式 discovery 无法稳定暴露入口时报告该 Runtime 未支持。

Hook 或 workspace 外动作需要精确授权。Runtime 能力不可用时记录原始错误并停止对应 transition；Core 合同保持 Runtime-neutral。
