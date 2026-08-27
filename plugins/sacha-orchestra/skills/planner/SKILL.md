---
name: planner
description: 显式 Planner，或已接受 Sacha 且 Planner Gate 打开时使用；冻结可执行 Scope/验收。未 Intake 或仅任务大、耗时、多文件时不接管。
---

# Planner（规划）

## 职责

把已核实事实和 Human 决定冻结成可执行 Scope、约束与验收，并把结果交回[术语合同](../../core/terminology-contract.md)定义的主任务。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Planner Gate；两者皆无时不接管。
2. 先读项目规则和真实状态。已确认的 Binding 可用时按 [Workflow Contract](../../core/workflow-contract.md) 的能力加载策略决定是否加载对应 Skill；加载后完整读取正文并另行核对前置、副作用、Role 边界和授权。策略不允许或缺少 Binding、映射、可见 Skill 时，回退 AGENTS、Domain Skill 或原生路线并保留未验证项，不调用 Setup。
3. 读取已落盘决定和相关项目 `CONTEXT.md`，按 Workflow Contract 完成冻结前检查。目标结果、Scope/Non-goals、验收或会改变方案的 Human 决定存在未收口项时，必须完整读取并调用 `$sacha-orchestra:explore`；Explore 返回且冻结条件满足后，才继续读取 Artifact Protocol、确定 Spec path 或起草 Spec。代码、项目规则或 Skill 可确认的事实先自行调查。
4. Explore 返回后核对原问题、已确认决定、阻塞项、未验证项和关键术语；仍不足以冻结 Spec 时继续 Explore。一个有界研究委派 Agent 足够时，由主任务按 Coordination Contract 直接派发，不打开 Manager；Planner 委派 Agent 只返回研究结果或协调请求。

## 动作顺序

1. Spec Artifact 沿用[术语合同](../../core/terminology-contract.md)；当前上下文可恢复时使用内联 Plan，方案需 Human 批准、属于破坏性变更或需要跨上下文恢复时写 Spec Artifact。持久化前读取 [Artifact Protocol](../../core/artifact-protocol.md)。
2. 仅在冻结条件满足且命中持久化条件后，才把完整方案写入 `spec.md` 并回读，再向 Human 交付。
   持久化优先使用已确认的 Spec storage root，其次项目现有约定；两者都没有时使用 `docs/plan`。任务目录内写 `spec.md`，按需将 `decisions.md` 写入同一目录。
3. 起草前按 Artifact Protocol 确定本次能够定义 Spec 事实的具体项目 path/reference 和 Human 项目决定；Handoff、报告、工作流输出、运行时传输及 Sacha 规则只用于各自消费者，不进入起草来源。
4. 只使用上一步确认的项目来源，按 Artifact Protocol 的唯一内容格式生成面向目标项目的实施规格；项目已有格式只有在完整承载该格式语义时才沿用。
5. 第一遍回读枚举 Spec 中所有保留英文的既有项目标识，以及所有拟新增的实现标识和项目概念名称。既有标识逐个与已确认项目来源精确匹配；项目来源未定义简称或别名时，必须改回完整项目名称。拟新增标识和概念名称逐个核对目标位置、相邻 Owner、直接消费者与项目当前命名习惯，命名依据和含义必须由项目来源或 Human 项目决定支持。
6. 第二遍回读逐项核对影响实施或验收的陈述是否由已确认项目来源或 Human 项目决定支持；改写必须保留来源中的主体、条件、动作、规范强度、边界与例外，不得增加来源没有的概括性标签。无法回指的内容必须删除，不得通过翻译、改写、概括或同义替换保留。
7. 第三遍回读只提供项目规则、项目事实和 Spec，核对不了解 Sacha 的 Executor 与 Reviewer 能否直接实施与评审。
8. 向 Human 交付前必须完成格式、来源和项目语境核对；任一项不满足时由当前 Planner 原位修订并重新执行三遍回读。全部满足前不得交付 Spec、请求批准、进入 Executor 或依赖 Reviewer 发现问题。
9. 工作流返回、协调和验证责任由主任务分别按 [Workflow Contract](../../core/workflow-contract.md)、[Coordination Contract](../../core/coordination-contract.md) 与 [Assurance Contract](../../core/assurance-contract.md) 处理，不写回 Spec。主任务出现多个候选单元、依赖或恢复协调时，调用 Manager 并消费 Coordination Contract 的分解、依赖、串行/派发结论和证据；Planner 委派 Agent 返回协调请求。

## 输出

1. 向 Human 提交此前未确认的实质方案前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，交付已落盘 Spec 的 path、方案摘要和优先检查点。
2. 普通批准与明确迁移批准沿用术语合同，下一 Role 路由按 Workflow Contract 返回主任务。`project-context` 候选及 `decisions.md` path 留给收尾文档写入者。

## 停止与禁止边界

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时，Planner 调用 Explore；Explore 将无法收口的决策作为阻塞项返回后，主任务等待 Human。
- Planner 不实施生产修改；Scope、合同或验收变化由主任务返回 Planner 修订。
