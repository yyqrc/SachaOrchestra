# Claude Code Runtime Adapter

> Implements: Workflow Contract 4；Artifact Protocol 1
> Status: Normative Claude Code mapping

## 1. Responsibility boundary

本文只把 Sacha Orchestra Core 映射到 Claude Code 原生能力。稳定协作语义来自：

- [Workflow Contract](../../core/workflow-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

本 Adapter 不定义 Role、Gate、生命周期、Artifact、Handoff、项目命令、证据等级或发布流程。Project rules 和 Domain Skills 拥有项目知识；Skill/agent definition 拥有 Role-local procedure；Evolution 拥有版本与验证状态。

## 2. Role、owner 与 context

| Core responsibility | Claude Code mapping |
| --- | --- |
| Planner | 独立 `Agent` context 装载 Planner 指令，只接收目标、可读事实与必要约束 |
| Executor | 一个明确 owner 的主对话或独立 `Agent` context 执行批准 Scope |
| Reviewer | 未参与当前方案或实现的独立 `Agent` context 装载 Reviewer 指令 |
| Manager | 主对话或明确控制面的 `Agent` context 协调已批准 Work Packet |
| Workflow owner | 接收用户 objective 的主对话；持有当前 phase 并持续推进到 Core 根终态 |

独立性由输入与参与历史的 provenance 判断，不由 agent 名称或标识符判断。Runtime agent/task id 只用于当前调度，不写入 Core Artifact 或九字段 Handoff。

正式 Role dispatch 只有在目标 context 能直接到达 canonical Role 指令和批准 Artifact 时才允许执行；不可达时记录真实缺口，不用临时提示模拟缺失的 Role contract。

## 3. Formal Role transition

### 3.1 Dispatch

每次 transition：

1. 根据 Task ID、Scope Reference、目标 Role、Artifact 可达性、provenance 和 owner 核对目标 context。
2. Source 只传 route intent、批准 Scope/Handoff locator、必要约束和 runtime-only identity；不复制长报告或隐藏会话历史。
3. 需要独立 provenance 时创建新的 `Agent` context；同一 Task ID/Scope 的 repair、补证据和 re-review 保持原 owner 连续性。
4. 无法唯一确定 owner、目标 Role 或 return path 时进入 Core 对应阻塞路线。

### 3.2 Completion consumption

Claude Code 暴露前台或后台执行时，均须满足 Core 的 Transport、Identity 和 Progress：

- 前台执行：主对话在当前调用完成时消费 terminal result，验证 identity 后立即执行唯一下一 transition。
- 后台执行：workflow owner 保持当前 phase，以 Runtime completion notification 和 agent/task identity 消费一次 terminal result；不得把通知留给 Human 触发，也不得因后台启动成功提前结束流程。

Target completion 包含 Core completion notice、Task ID、Scope Reference、Handoff locator/revision、Source/Target Role、Outcome 和 dedup key。错误、陈旧或重复结果不产生额外 dispatch、写入或 terminal transition。

### 3.3 Model configuration

`Agent` 使用 Runtime 实际暴露的模型参数。只有 Human 当前明确指定，或批准 Scope 原样保存了 Human 的精确配置时才传覆盖值；否则省略覆盖并使用 Runtime 默认配置。工具不支持显式配置时报告真实错误，不自行替换或降级。

### 3.4 Progress and failure

前台调用由当前调用生命周期提供 liveness；后台调用由 completion notification、Runtime 状态和取消能力提供 liveness。具体窗口由当前 Runtime 能力与项目规则限定，但任何 timeout 都不能替代 terminal result、取消确认或 Core 完成证据。

Transport、Identity 或 Progress 失败时，按 Core schema 生成 runtime deviation packet。Claude Code 只补充真实 agent/task identity、前台/后台模式、notification/return 状态、工具错误和可执行 repair/re-verification entry。

## 4. Manager and parallel mapping

Manager Gate 由 Core 或批准 Scope 决定。Gate 开启后：

1. 每个 ready Work Packet 使用一个独立 `Agent` context。
2. `parallel_expected` 成立时，在消费任何 completion 前启动至少两个实例。
3. 只读 Packet 可并行；写入 Packet 只有 exact write scope 静态不重叠时并行。
4. completion 由 workflow owner/Manager 按 Packet revision 和 dedup key 聚合；共享生成物、Git 动作和整体验证由单一 integration owner 串行完成。
5. Runtime、槽位、依赖、Scope 或授权阻塞记录为 `parallel_blocked`；条件满足却未启动记录为 `parallel_dispatch_missed`。

## 5. Artifact reachability and recovery

Agent context 通过文件系统或 Runtime 提供的稳定 locator 读取批准 Scope、必要 Artifact、原始 evidence locators 和完整九字段 Handoff。恢复先核对 Task ID、Scope Reference、Handoff revision 和 Entry Condition，不从主对话隐藏历史猜测。

Artifact、canonical Role 指令或 return identity 不可达时停止对应 transition，记录影响和唯一恢复入口。

## 6. Project rules and discovery

项目规则、canonical Role 指令和 Domain Skills 必须通过当前 Claude Code context 的正式 discovery/加载机制可达。SessionStart hook 只在 Human 明确授权且项目正式配置时作为加载机制；Adapter 不把 hook 当作默认前提，也不定义项目专属注入内容。

发现成功只证明入口可达；真实 Role lifecycle、并行、恢复和验收仍须由对应 Runtime 行为证据证明。

## 7. Authorization and failure handling

- 安装、hook、Git、push、发布或其他 workspace 外动作必须有 Human 对精确动作的明确授权。
- `Agent`、模型参数、completion notification、取消或 discovery 能力不可用时记录真实错误，不静默换成不完整路线。
- Core 与本 Adapter 冲突时停止相关写入；Adapter 不修改 Core 迁就平台限制。
