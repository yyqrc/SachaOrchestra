---
name: planner
description: 显式 Planner，或已接受 Sacha 且 Planner Gate 打开时使用；冻结可执行 Scope/验收。未 Intake 或仅任务大、耗时、多文件时不接管。
---

# Planner（规划）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Planner Gate；两者皆无时不接管。
2. 先读项目规则和真实状态。mapping 可用才调用对应 Skill；缺 Binding/mapping 时用 AGENTS、Domain Skill 或原生路线，不调用 Setup。
3. 只比较会改变实现的方案，分清事实、假设和取舍。缺少会改变方案的 Human 决定时使用 Clarify；一个有界研究 helper 足够时不打开 Manager。
4. 当前 context 可恢复时用 inline plan；只有批准、breaking 或跨 context 恢复需要时写 Spec Artifact。持久化时在已确认的 Spec storage 下创建任务目录并默认写入 `spec.md`；没有 confirmed storage 时使用项目现有约定，不调用 Setup。
5. 给 Executor 明确 Scope、Non-goals、依赖、冻结决定、停止/回退条件和可证伪验收；不要求无消费者的字段、ID 或表格。
6. 需要持久记录或正式恢复时才读取 [Artifact Protocol](../../core/artifact-protocol.md)。完成后返回 workflow owner；Planner 不创建执行实例。

## 暂停与路由

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时等待 Human。
- 已授权且无方案分歧的实施请求直接进入 Executor，不重复请求批准。
- Planner 不实施生产修改；Scope、合同或验收变化回到 Planner 修订。
