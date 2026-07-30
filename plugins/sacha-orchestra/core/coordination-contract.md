# Coordination Contract

> Contract Version: 3
> Status: Normative Core coordination contract

## 1. 范围与 owner

本文只定义 Manager 控制面、delegation、completion/return、identity/dedup 和 deviation。Gate/lifecycle 见 [Workflow Contract](workflow-contract.md)，持久记录见 [Artifact Protocol](artifact-protocol.md)。无 delegation、跨 context return 或恢复 consumer 时不加载。

Manager 不是生产 Role。生产 Role transition 由 workflow owner 路由；多个 delegated unit、依赖图、跨 context 恢复或并行生命周期由 Manager 管理。当前 owner 可直接使用一个有界 helper 完成职责内的调查、验证或候选 patch，并负责 scope、等待、取消、结果核对与集成；helper 不取得独立 Role verdict。

## 2. 派发与 single writer

Packet 只是派发消息的内部叫法，不是文件、对象或固定 schema。消息只需让 Target 明确目标、允许范围、完成检查和停止条件；依赖或并发存在时再补隔离边界。单个 helper 直接使用 prompt/message，Runtime 已携带的 identity 不重复。研究任务另给问题和预期证据，默认 read-only。

只读任务可并行。共享工作树中同一文件或可变输出不得并行写；隔离 worktree、patch-only 或候选实现可重叠分析，由 integration owner 串行应用。共享生成物、公共 schema、Git 和整体验证保持串行。

单个 ready 单元串行处理。至少两个独立 ready 单元且 Scope、依赖、授权和 Runtime 允许时，首次 wait/join 前启动至少两个实例；记录 `parallel_started`、`parallel_blocked` 或 `parallel_dispatch_missed`。不足两个 ready 单元不伪装成并行。

返回只写结果/delta、实际验证、阻塞/风险和必要 locator。按消费者与风险增减，不为格式新建 Artifact，也不隐藏失败、未验证、Scope 偏离或授权阻塞。

## 3. Clarify research

Clarify 先使用当前 context 可达事实；一个有界只读 helper 足够时直接管理。只有多个研究单元、依赖图、正式恢复或并行生命周期需要独立 owner 时打开 Manager Gate。

研究任务不授权写入、冻结方案、验收或外部动作。发现需写入、新 Scope/方案或新授权时停止并返回 Planner/Human。Manager 返回 evidence locator；Clarify 只消费事实。

## 4. Completion、return 与 deviation

Owner 保存 objective、Scope、授权和完成条件。每个 delegated unit/Role 对同一 revision 只返回一次结果、实际验证、阻塞/风险和必要 locator；原生 transport 无法消歧时才补 Task/Scope revision、Source/Target、owner 或 dedup。更正使用新 revision。

显式 Feedback 的窄授权包含只读取证和完成 repair route。当 repair workspace、Scope、objective、owner 唯一且 transport 可用时，Source 必须复用唯一匹配的 owner context，或在无匹配时创建恰好一个 owner context并消费 terminal；不能以调查报告或再次询问同一目标的创建授权结束。Source 的只读 investigation helper 不取得 repair owner、Role 或 identity，不能充当 repair target。Target 独立核对实施与外部副作用授权。

同一 payload 兼作 report/completion 时不重复内容；完整 report/evidence 仅在有消费者时落 Artifact。面向 Human 的 final 不是 transport，不展示内部字段表。

根终态及结果：

- `goal_complete`：objective、Scope 和 required verification 已满足；
- `goal_partial`：已授权子集完成，剩余部分明确未完成且当前 objective 不再继续；
- `goal_cancelled`：Human 或上游 owner 明确取消；
- `goal_superseded`：objective 被新目标替代；
- `human_decision_required`：继续需要实质方案、Scope/验收变化、新高影响授权、不可消歧 owner 或 Human/外部恢复；
- `completion_return_blocked`：安全 return transport 与替代路径均不可用；
- `external_failure`：外部系统已终止且同 Scope 安全恢复路径耗尽。

无改动但目标已满足时使用 `goal_complete` 并标记 `no_op`。`goal_partial`、`goal_cancelled`、`goal_superseded` 和 `external_failure` 必须保留已完成范围、未完成原因、证据与恢复条件。

每个 transition 检查：

- Transport：terminal 被消费且 return 一次；
- Identity：核对当前 transport/consumer 实际需要的 Task/Scope revision、owner、Source/Target、Baseline；原生 join 已唯一绑定的标识不重复编码；
- Progress：下一 transition 已启动、处于可证明的 Runtime wait/用户 steering，或进入合法根终态。

失败产生 bounded deviation，保留 expected/actual/impact、证据、恢复或停止条件，以及 transport 无法提供的必要 identity/dedup。错误、陈旧或重复 completion 不产生额外 transition/write/terminal；环境不可用先耗尽同 Scope 安全替代。
