---
name: planner
description: 显式 Planner，或已接受 Sacha 且 Planner Gate 打开时使用；冻结可执行 Scope/验收。未 Intake 或仅任务大、耗时、多文件时不接管。
---

# Planner（规划）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Planner Gate；两者皆无时不接管。
2. 先读项目规则和真实状态。mapping 可用才调用对应 Skill；缺 Binding/mapping 时用 AGENTS、Domain Skill 或原生路线，不调用 Setup。
3. 形成 Spec 前检查目标结果、Scope/Non-goals、验收和会改变方案的 Human 决定。任一未收口时必须显式调用 `$sacha-orchestra:clarify`；可从代码、项目规则或 Skill 查明的事实先自行调查，全部明确时跳过。先读取已落盘决定和相关项目 `CONTEXT.md`，一个有界研究 helper 足够时不打开 Manager。Clarify 返回本身不等于澄清完成：Planner 核对原问题仍被覆盖、可恢复 frontier 没有尚未询问的重要分支、阻塞项已确认/暂缓/授权取舍，且关键术语沿用已确认含义；否则继续 Clarify，新证据推翻定义时也返回 Clarify，不能凭 Role 自报生成 Spec 或进入 Executor。
4. 当前 context 可恢复时用 inline plan；只有方案需 Human 批准、breaking 或跨 context 恢复需要时写 Spec Artifact。命中持久化条件后，先把完整方案写入 `spec.md` 并回读，再向 Human 交付摘要、path 和优先检查点；对话中的完整或简化 Spec 都不能替代落盘文件。
   持久化优先使用 confirmed Spec storage root，其次项目现有约定；两者都没有时使用 `docs/plan`。任务目录内写 `spec.md`，按需 `decisions.md` 同目录；不为此调用 Setup。
5. Spec 详细到 Executor 不需重新设计，但不替 Executor 逐行写代码。实施越依赖顺序、owner、数据边界和领域约束，步骤越接近可直接执行；只剩局部代码表达时停止细化。每步用自然中文说明目标位置、预期改动、约束与不变量、依赖与顺序、检查与证据，以及需要返回规划的条件。
6. 给 Executor 明确 Scope、Non-goals、依赖、冻结决定、停止/回退条件，以及 A/B/C 验收路线；不要求无消费者的字段、ID 或表格。
7. 形成 Human 此前未确认的实质方案时，把已落盘的拟执行 Spec 交给 Human，并在回复中直接说明 path、方案摘要和优先阅读哪些改动敏感部分；无需在对话中重抄全文。Review Focus 不是 Spec 固定章节。多问题或多项建议按 Workflow Contract 在回复末尾编号收口，不能遗漏正文建议或增加未论证方案。
8. 需要持久记录或正式恢复时才读取 [Artifact Protocol](../../core/artifact-protocol.md)。把当前任务 project-context 候选及 `decisions.md` path 保留给 closeout Documentation writer，候选不进入 Spec 执行权威。批准后若无未决方案、额外授权或阻塞性 Entry Condition，返回 workflow owner 并立即进入 Executor，不再等待第二次开始确认；Planner 不自行实施生产修改。

## 暂停与路由

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时等待 Human。
- 已授权且无方案分歧的实施请求，以及 Human 对拟执行 Spec 的清晰批准，直接进入 Executor，不重复请求批准或开始确认。
- Planner 不实施生产修改；Scope、合同或验收变化回到 Planner 修订。
