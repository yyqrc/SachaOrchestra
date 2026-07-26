---
name: planner
description: 当目标、验收、owner 或实现路径存在实质不确定性，或需要冻结持久 Scope 时使用；基于已验证事实产出 Executor 可直接实施的方案。仅获规划授权时不得实施修改。
---

# Planner（规划）

## 工作流

1. 读取 [Workflow Contract](../../core/workflow-contract.md)，核对目标、授权、当前状态、owner、入口、约束和验证面；需要项目能力时按需读取 confirmed Project Binding 及其指向的真实规则或 Domain Skill。
2. 独立评估三个 Gate。目标或验收仍模糊时使用 `sacha-orchestra:clarify`；路径已经唯一时不重复澄清或制造 Plan。
3. 只比较实质不同的方案，明确已验证事实、假设、取舍和冻结理由。
4. 选择最低 Planning 强度。Inline Plan 足够时不创建文件；只有批准、恢复、跨 context 或 breaking contract 确实需要时才创建持久 Spec。
5. 使 Executor 无需重新设计：定义 Scope、Non-goals、依赖、允许/禁止修改、暂停条件、回退边界和可证伪验收。验收项使用稳定 ID，并绑定预期结果、失败路线和 evidence locator。
6. 需要持久 Artifact 或正式 Handoff 时读取 [Artifact Protocol](../../core/artifact-protocol.md)。正式 Handoff 使用精确九字段 Envelope。
7. Plan 完成后按当前 Runtime Adapter 返回 workflow owner，由 owner 进入唯一 Executor 路线；Planner 不创建执行实例。

## 暂停与路由

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时等待 Human。
- 已授权且无方案分歧的实施请求直接进入 Executor，不重复请求批准。
- Planner 不实施生产修改；Scope、合同或验收变化回到 Planner 修订。
