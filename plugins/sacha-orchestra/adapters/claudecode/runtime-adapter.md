# Claude Code Runtime Adapter（运行时适配器）

> 实现：Intake Contract 6；Workflow Contract 19；Human Interaction Contract 1；Assurance Contract 2；Coordination Contract 10；Artifact Protocol 6
> 状态：规范性 Claude Code 传输映射

## 1. 边界

本文映射 Claude Code 原生能力。Owner 依据：

- [Intake Contract](../../core/intake-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

入口、Role、Gate、Artifact、项目知识和发布状态由对应 Core、Skill、Project Integration 与 Evolution 拥有。本 Adapter 消费已确定的动作并映射 Claude Code 传输。

## 2. Intake、Role 与上下文

| Core 职责 | Claude Code 映射 |
| --- | --- |
| Intake/路由 Owner | 主对话通过正式 Skill 发现机制装载 `using-sacha` |
| Planner | 独立 `Agent` 上下文装载 Planner 指令 |
| Executor | 明确 Owner 的主对话或独立 `Agent` 上下文 |
| Reviewer | 未参与方案/实现的独立 `Agent` 上下文 |
| Manager | 主对话或控制面 `Agent` 协调独立任务 |
| 工作流 Owner | 默认是 Human 接受后的主对话；明确会话迁移后转为唯一目标 |
| Human 互斥选择 | 使用已验证的原生选择能力；当前 Runtime 无可用映射时使用普通文本提问 |
| Human 进度与结果 | 由当前工作流 Owner 在主对话展示 |

Runtime 常驻面只暴露元数据。入口与 Role 由正式 Skill 发现机制加载；当前动作需要传输、恢复或 Runtime 证据时读取本 Adapter。

独立性由参与历史/输入来源判断；Agent 名称和 Runtime 标识只用于调度。规范入口/Role/Artifact 不可达时报告真实发现缺口。

## 3. 转换、返回与恢复

每次转换先核对 Runtime 可用能力：

1. 核对 Task/Scope、Role、Artifact 可达性、来源、Owner 和返回路径。
2. 同一上下文的工作在主对话执行；需要独立来源的正式 Role 转换使用可保留标识/终态的 Agent 传输。有界辅助 Agent 由当前 Owner 直接管理。
3. Source 负载由路由意图、Scope/Handoff reference、必要约束与 Runtime 标识组成。
4. 独立 Review 使用新 `Agent` 上下文；同一 Task/Scope 的返修、补证据和重新 Review 保持原 Owner。
5. 当前传输不可用时先尝试同一 Scope 的安全替代；Owner/Role/返回仍无法唯一确定时才进入 Core 阻塞路线。

### 3.1 完成与等待

前台执行由主对话消费终态结果；后台执行由 Owner 保持阶段，以正式完成通知和标识消费一次结果。派发后先推进不依赖结果且不冲突的就绪工作；当前 Owner 是结果消费者、下一转换依赖结果且没有其他就绪工作时等待。

目标完成时返回结果/变更、实际验证、阻塞/风险和必要 reference；原生通知未携带且消歧必需时补路由标识/revision/dedup。错误、陈旧或重复结果停止当前转换。

### 3.2 Human 决定与任务迁移

Adapter 消费 Workflow/Coordination 已确认的当前任务执行或用户任务迁移决定。当前任务执行由主对话继续；迁移需要 Human 已明确选择、可验证的等价用户会话传输、唯一 Owner 与单向 Handoff，创建或复用目标后由 Source 交付 reference 并结束。条件不足时保持当前 Owner 和原始缺口；用户任务迁移标识只属于目标任务。

### 3.3 Feedback Owner 转移

Adapter 消费 Coordination Contract 返回的 Feedback 标识、匹配和 Owner 转移判断。唯一匹配或 `no_op` 返回既有用户可见上下文 reference；需要新目标时创建唯一上下文；无法完成等价 Owner 转移时报告真实能力缺口。来源任务交付 reference 后结束。

### 3.4 模型映射

正式跨上下文派发先应用 Human 本次或批准 Scope 的精确配置，否则按 Role/风险选择：

| 目标 | 模型 | 条件 |
| --- | --- | --- |
| Planner | `opus` | 需要冻结实质方案 |
| Executor | `opus` | 安全、权限、持久数据、破坏性变更、不可逆外部动作或广泛兼容/发布风险 |
| Executor | `sonnet` | Scope/验收已冻结、实现与验证明确且属于普通风险 |
| Reviewer | `opus` | 独立验收 |
| 有界只读辅助 Agent | `haiku` | 自包含调查，只返回事实与 reference |

Planner/Reviewer/Manager Gate 结果来自 Core。普通 Executor 只有输入自包含时使用 `sonnet`。Human/Scope 精确配置不受支持时暂停；自动配置不可用时使用 Runtime 默认值。Owner 核对并记录请求/实际模型与宿主覆盖原因；旧写入者进入 `terminal/cancelled` 前不得以其他模型启动同一 Scope 写入。Direct/当前上下文保持当前模型和路由状态。

传输/标识/进度失败按 Coordination Contract 生成偏差；本 Adapter 补充原生结果未携带且恢复必需的 Agent/任务、前后台模式、通知/返回、工具错误和恢复入口。

Human 输出按 Human Interaction Contract 展示。存活状态证据来自当前前台调用或后台完成/取消状态；超时只报告当前状态。

搜索、diff、日志和列表默认返回短摘要，缺少决策信息时定向展开。大原文已有消费者时写入任务局部文件或既有 Artifact，否则保留工具 reference；截断结果保留 Human Interaction Contract 规定的必须披露信息。

## 4. Agent 协调与 Artifact 映射

Manager Gate 开启后，每个就绪单元使用独立 `Agent` 上下文；`parallel_expected` 成立时在消费完成结果前启动至少两个实例。共享工作树的同一文件/输出由集成 Owner 串行处理；隔离补丁/候选实现使用并行 `Agent` 上下文。

完成结果在传输需要时核对 revision/dedup；结果按消费者和风险保留必要变更，Artifact 只在消费者需要时落盘。真实 Runtime/槽位/依赖/Scope/授权阻塞为 `parallel_blocked`，条件满足却未启动为 `parallel_dispatch_missed`。

Agent 上下文通过稳定 reference 读取 Scope、Artifact、原始证据和当前消费者所需 Handoff 语义。恢复以可用路由标识、Scope、revision 与 Entry Condition 为依据；reference 不可达时停止转换并记录唯一入口。

## 5. 发现机制与 Hook 边界

项目规则、`using-sacha`、规范 Role 和 Domain Skill 由当前 Runtime 的正式发现/加载机制暴露。发现证据只覆盖入口可达；生命周期、并行、恢复与验收使用真实行为证据。

SessionStart Hook 仅在 Human 另行授权且项目正式配置时预加载环境信息；入口接受、授权和 Owner 恢复仍由正式 Core/Skill 路线处理。正式发现机制无法稳定暴露入口时报告该 Runtime 未支持。

Hook 或工作区外动作需要精确授权。Runtime 能力不可用时记录原始错误并停止对应转换；Core 合同不依赖 Runtime。
