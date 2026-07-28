---
name: planner
description: 显式 Planner，或已接受 Sacha 且 Planner Gate 打开时使用；冻结可执行 Scope/验收。未 Intake 或仅任务大、耗时、多文件时不接管。
---

# Planner（规划）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 核对 Planner Gate、目标、授权、owner、约束与验证面；两者皆无时不规划。
2. 独立评估三个 Gate。目标或验收仍模糊时使用 `sacha-orchestra:clarify`；Clarify 需要隔离研究时按 [Coordination Contract](../../core/coordination-contract.md) 交给 Manager，路径唯一时不重复澄清或制造 Plan。
3. mapping policy 允许才用 Skill；缺 Binding、目标 mapping 或可用 Skill 时回退 AGENTS/Domain Skill/原生路线，不调用 Setup。
4. 只比较实质不同方案，区分已验证事实、假设、取舍和冻结理由。
5. 选择最低 Planning 强度。Inline Plan 足够时不创建文件；只有批准、恢复、跨 context 或 breaking contract 确实需要时才创建持久 Spec。创建时优先消费 confirmed Project Integration 的 Plan storage；未配置则按 Project AGENTS/现有项目约定，不调用 Setup。
6. 使 Executor 无需重设计：定义 Scope、Non-goals、依赖、边界、暂停/回退和可证伪验收；稳定 ID 绑定预期、失败路线与 locator。
7. 需要持久 Artifact 或正式 Handoff 时读取 [Artifact Protocol](../../core/artifact-protocol.md)。正式 Handoff 保留九个核心字段；确有消费者时附 namespaced `Extensions`。
8. Plan 完成后按当前 Runtime Adapter 返回 workflow owner，由 owner 进入唯一 Executor 路线；Planner 不创建执行实例。

## 暂停与路由

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时等待 Human。
- 已授权且无方案分歧的实施请求直接进入 Executor，不重复请求批准。
- Planner 不实施生产修改；Scope、合同或验收变化回到 Planner 修订。
