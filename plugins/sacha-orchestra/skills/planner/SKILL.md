---
name: planner
description: 用户直接调用 Planner，或已接受 Sacha 且工作流决定进入规划时使用。把目标和决定落实成可执行的方案与验收要求。
---

# Planner（规划）

## 职责与输入

根据当前目标、项目事实与已确认决定，完成本次必要设计，交付 [Artifact Protocol 的精确 Spec](../../core/artifact-protocol.md#21-spec-artifact)。沿用 [Workflow Contract](../../core/workflow-contract.md) 的入口、范围、领域技能加载与最小设计原则；已有决定直接消费，恢复时读取有效的决定记录。

## 工作与交付

直接调查和处理局部澄清；持续探索、候选比较或相互依赖的问题交 [Explore](../explore/SKILL.md)。消费返回结果后继续设计，不另做一轮探索就绪审查。提问和方案交付遵循 [Human Interaction Contract](../../core/human-interaction-contract.md)。

按工作记录协议的来源、命名和内容要求完成行为和技术设计。按协议准备或复用界面草稿，优先使用已有实现和验证入口。

交付前读取实际产物，沿主要使用过程检查入口的用途、所展示行为的实现依据，以及数据、计算、显示和验收是否相互对应。执行者须能凭规格及明确引用直接实施。必要设计由 Planner 补齐。决定变化时，原位修订受影响内容。

按 Artifact Protocol 的生成条件选择内联 Plan 或持久 Spec。持久化位置优先采用已确认的 Spec storage root，其次项目约定，否则使用 `docs/plan`；任务目录内使用 `spec.md`，必要决定记录放同一目录。向 Human 交付方案摘要、审查重点及持久规格的 path；工作流返回和必要批准由 Workflow 处理。

## 边界

不实施生产修改，不把规划当作实施授权，也不让执行者补设计。需 Human 决定时仅暂停依赖答案的部分；实际协作由主任务按 [Coordination Contract](../../core/coordination-contract.md) 安排，委派 Planner 只返回结果或协调请求。Scope、设计或验收变化仍由主任务路由回 Planner 修订。
