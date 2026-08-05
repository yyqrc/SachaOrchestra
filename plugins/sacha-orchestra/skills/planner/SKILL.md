---
name: planner
description: 显式 Planner，或已接受 Sacha 且 Planner Gate 打开时使用；冻结可执行 Scope/验收。未 Intake 或仅任务大、耗时、多文件时不接管。
---

# Planner（规划）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Planner Gate；两者皆无时不接管。
2. 先读项目规则和真实状态。mapping 可用才调用对应 Skill；缺 Binding/mapping 时用 AGENTS、Domain Skill 或原生路线，不调用 Setup。
3. 形成 Spec 前检查目标、Scope/Non-goals、验收和 Human 决定；先查代码/规则/Skill并读取决定记录和相关项目 `CONTEXT.md`。未收口时显式调用 `$sacha-orchestra:clarify`，一个研究 helper 足够时不启用 Manager。
   Clarify 返回本身不等于澄清完成：核对原问题、恢复 frontier、阻塞项和术语；仍有重要分支或新证据推翻定义时继续 Clarify，不凭 Role 自报进入 Executor。
4. 当前 context 可恢复时用 inline plan；只有方案需 Human 批准、breaking 或跨 context 恢复需要时写 Spec Artifact。
   持久化优先使用 confirmed Spec storage，其次项目现有约定；两者都没有时使用集合根 `docs/plan`。任务目录内写 `spec.md`，按需 `decisions.md` 同目录；不为此调用 Setup。
5. Spec 使 Executor 无需重新设计，但不逐行代写。每步说明位置、改动、约束/不变量、依赖/顺序、检查/证据和返回规划条件；只剩局部代码表达时停止细化。
6. 给 Executor 明确 Scope、Non-goals、依赖、冻结决定、停止/回退条件，以及 A/B/C 验收路线；不要求无消费者的字段、ID 或表格。
7. Human 未确认的实质方案须交付拟执行 Spec，并在回复中说明 Review Focus；它不是固定章节。多项建议按 Workflow Contract 编号收口，不遗漏或新增方案。
8. 仅为持久记录/恢复读取 [Artifact Protocol](../../core/artifact-protocol.md)。把 context 候选和 `decisions.md` locator 交 closeout writer，不纳入 Spec 权威。批准且无未决方案、额外授权或阻塞条件时，立即返回 owner 进入 Executor。

## 暂停与路由

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时等待 Human。
- 已授权且无方案分歧的实施请求，以及 Human 对拟执行 Spec 的清晰批准，直接进入 Executor，不重复请求批准或开始确认。
- Planner 不实施生产修改；Scope、合同或验收变化回到 Planner 修订。
