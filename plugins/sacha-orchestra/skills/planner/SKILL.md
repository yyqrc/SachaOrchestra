---
name: planner
description: 显式 Planner，或已接受 Sacha 且 Planner Gate 打开时使用；冻结可执行 Scope/验收。未 Intake 或仅任务大、耗时、多文件时不接管。
---

# Planner（规划）

## 职责

把已核实事实和 Human 决定冻结成可执行 Scope、约束与验收，并把结果交回[术语合同](../../core/terminology-contract.md)定义的主任务。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Planner Gate；两者皆无时不接管。
2. 先读项目规则和真实状态。映射可用时才调用对应 Skill；缺少 Binding/映射时用 AGENTS、Domain Skill 或原生路线，不调用 Setup。
3. 读取已落盘决定和相关项目 `CONTEXT.md`，按 Workflow Contract 判断目标结果、Scope/Non-goals、验收和会改变方案的 Human 决定是否满足冻结条件。存在未收口项时必须调用 `$sacha-orchestra:clarify`；Clarify 返回且冻结条件满足前不得进入 Spec 持久化。代码、项目规则或 Skill 可确认的事实先自行调查。
4. Clarify 返回后核对原问题、已确认决定、阻塞项、未验证项和关键术语；仍不足以冻结 Spec 时继续 Clarify。一个有界研究委派 Agent 足够时，由主任务按 Coordination Contract 直接派发，不打开 Manager；Planner 委派 Agent 只返回研究结果或协调请求。

## 动作顺序

1. Spec Artifact 沿用[术语合同](../../core/terminology-contract.md)；当前上下文可恢复时使用内联 Plan，方案需 Human 批准、属于破坏性变更或需要跨上下文恢复时写 Spec Artifact。持久化前读取 [Artifact Protocol](../../core/artifact-protocol.md)。
2. 仅在冻结条件满足且命中持久化条件后，才把完整方案写入 `spec.md` 并回读，再向 Human 交付。
   持久化优先使用已确认的 Spec storage root，其次项目现有约定；两者都没有时使用 `docs/plan`。任务目录内写 `spec.md`，按需将 `decisions.md` 写入同一目录。
3. Spec 细化到 Executor 可直接实施；每步说明目标 path、预期改动、约束与不变量、依赖与顺序、检查与证据，以及返回 Planner 的条件。
4. 给 Executor 明确 Scope、Non-goals、依赖、冻结决定、停止/回退条件和 A/B/C 验收路线。主任务出现多个候选单元、依赖或恢复协调时，按 [Coordination Contract](../../core/coordination-contract.md) 调用 Manager 并消费其分解、依赖、串行/派发结论和证据；Planner 委派 Agent 返回协调请求。

## 输出

1. 向 Human 提交此前未确认的实质方案前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，交付已落盘 Spec 的 path、方案摘要和优先检查点。
2. 普通批准与明确迁移批准沿用术语合同，下一 Role 路由按 Workflow Contract 返回主任务。`project-context` 候选及 `decisions.md` path 留给收尾文档写入者。

## 停止与禁止边界

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时等待 Human。
- Planner 不实施生产修改；Scope、合同或验收变化由主任务返回 Planner 修订。
