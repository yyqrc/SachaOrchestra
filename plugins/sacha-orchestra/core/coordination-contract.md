# Coordination Contract

> Contract Version: 2
> Status: Normative Core coordination contract

## 1. 范围与 owner

本文是 Manager 控制面、非生产 Role Packet、completion/return、identity/dedup 和 deviation 的唯一权威。Gate/high-level lifecycle 由 [Workflow Contract](workflow-contract.md) 定义；持久 Artifact/Handoff 由 [Artifact Protocol](artifact-protocol.md) 定义。无 delegation、跨 context return 或恢复 consumer 时不加载本文。

Manager 不是生产 Role。生产 Role transition 由 workflow owner 路由；多个 delegated unit、依赖图、跨 context 恢复或并行生命周期由 Manager 管理。当前 owner 可直接使用一个有界 helper 完成职责内的调查、验证或候选 patch，并负责 scope、等待、取消、结果核对与集成；helper 不取得独立 Role verdict。

## 2. Packet 与 single writer

Packet 至少包含 `owner`、`read scope`、`write scope`、`dependencies`、`input`、`expected output`、`verification`、`stop condition`。Research Packet 额外明确 research question 与 expected evidence，默认 read-only。

只读 Packet 可并行。共享工作树中同一文件或可变输出不得并行写；隔离 worktree、patch-only 或候选实现可重叠分析，由 integration owner 串行应用并解决冲突。共享生成物、公共 schema、Git 和整体验证由 integration owner 串行完成。

单个 ready Packet 使用 `C1 Managed Serial`；至少两个独立 ready Packet 且 scope、依赖、授权和 Runtime 允许时使用 `C2 Managed Parallel`。首次 wait/join 前启动至少两个实例为 `parallel_started`；条件受阻为 `parallel_blocked`，条件满足却未启动为 `parallel_dispatch_missed`。不足两个 ready Packet 不伪装成并行。

Packet report 默认 delta-only，保留 outcome、changed files、validation、blockers、risks/unknowns 与 locators；长度预算是可按消费者和风险扩展的提示，不得为满足预算而新建无消费者 Artifact，也不得隐藏失败、未验证、Scope 偏离或授权阻塞。

## 3. Clarify research

Clarify 先使用当前 context 可达事实；一个有界只读 helper 足够时由 Clarify 直接管理。只有多个研究单元、依赖图、正式恢复或并行生命周期需要独立 owner 时打开 Manager Gate，由 Manager 建立 Research Packet。

Research Packet 不授权写入、冻结方案、验收或外部动作。发现需写入、新 Scope/方案或新授权时停止并返回 Planner/Human。Manager 返回 evidence locator；Clarify 只消费事实并继续澄清。

## 4. Completion、return 与 deviation

Owner 保存 objective、Scope、授权和完成条件。每个 delegated unit/Role 对同一 revision 返回一个 terminal completion notice：Task ID、Source、Outcome、Scope、Artifact/Evidence locators、Owner、Next Role、Human Decision Required。更正使用新 revision；长度按消费者自适应，优先 delta 与 locator，不为硬限额丢失决策信息或强制创建 Artifact。

同一 payload 兼作 Packet report/notice 时取更严预算；完整 report/evidence 先落 Artifact，return 保留最高 severity、finding/blocker 数、失败、未验证、授权阻塞和 locator。无上游 owner 的 Human-facing final 不属于 transport。

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
- Identity：Task/Scope/revision/owner/Source/Target/Baseline/Packet 一致；
- Progress：下一 transition 已启动、处于可证明的 Runtime wait/用户 steering，或进入合法根终态。

失败产生 bounded deviation packet，保留 expected/actual、identity、locator、责任层、影响/授权、Human stop gate、repair/re-verification entry、return address 与 dedup key。错误、陈旧或重复 completion 不产生额外 transition/write/terminal；环境不可用先耗尽同 Scope 安全替代。
