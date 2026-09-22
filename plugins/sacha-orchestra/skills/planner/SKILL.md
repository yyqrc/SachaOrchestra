---
name: planner
description: 显式 Planner，或已接受 Sacha 且 Planner Gate 打开时使用；冻结可执行 Scope/验收。未 Intake 或仅任务大、耗时、多文件时不接管。
---

# Planner（规划）

## 职责

根据已核实事实和 Human 决定完成本次必要设计，按 [Artifact Protocol 的 Spec 标准](../../core/artifact-protocol.md#21-spec-artifact)冻结精确实施规格，并把结果交回[术语合同](../../core/terminology-contract.md)定义的主任务。

设计方案前，从当前请求、已确认决定与项目事实中明确预期改变、必须保留的行为和明确排除的做法，并用这些边界筛选方案、安排实现与验收。不得把必须保留的行为改成可选兼容项，或因实现方便重新引入已排除的做法。边界已明确时直接消费；缺失或冲突会改变方案时，按下文核对事实或调用 Explore，不重复要求 Human 确认既有决定。

提出和讨论方案时，必须按 [Workflow Contract 的运行原则](../../core/workflow-contract.md#2-运行原则)从现有实现及必要差异形成最小方案。必要设计及说明精度必须达到 Artifact Protocol 的 Spec 标准，不能等 Human 再次要求细化；删除已排除或缺少依据的扩展。达到该标准后收口交付，不继续扩展设计。运行时停用与 Editor 工具约束由项目规则和领域技能提供。

验收优先复用现有生产入口、测试和日志；仅为无法覆盖的具体风险补充检查。固定轮数、故障注入和新增测试设施须说明必要性，并计入维护与现场恢复成本。Spec 写清必需结果与检查方法；现场受阻且需要改变验证方案时，由主任务判断并按既有路由调整，不将验证设计留给执行者。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Planner Gate；两者皆无时不接管。
2. 先读项目规则和真实状态。Project Integration 有目标 Skill 的已确认加载条目时，按 [Workflow Contract](../../core/workflow-contract.md) 的技能加载策略决定是否加载；设计和规划需要的只读约束可按 `on-demand` 在写入授权前使用。加载后完整读取正文并另行核对前置、副作用、Role 边界和授权。策略不允许或缺少条目、可见 Skill 时，回退 AGENTS、Domain Skill 或原生路线并保留未验证项，不调用 Setup。
3. 读取已落盘决定、相关项目 `CONTEXT.md` 及 Artifact Protocol 的 Spec 标准，按 Workflow Contract 完成冻结前检查。可直接确认的小事实先自行核对；仍需持续探索、会改变方案的未决事实或 Human 决定时，完整读取并调用 `$sacha-orchestra:explore`。事实与决定足以形成方案后才确定 Spec path 或起草 Spec，不能因省去流程切换而跳过实质决定。
4. Explore 返回后核对原问题、已确认决定、阻塞项、未验证项和关键术语；仍不足时按剩余问题自行核对小事实或继续 Explore。一个有界研究委派 Agent 足够时，由主任务按 Coordination Contract 直接派发，不打开 Manager；Planner 委派 Agent 只返回研究结果或协调请求。

## 动作顺序

1. Spec Artifact 沿用[术语合同](../../core/terminology-contract.md)；当前上下文可恢复时使用内联 Plan，方案需 Human 批准、属于破坏性变更或需要跨上下文恢复时写 Spec Artifact。持久化前读取 [Artifact Protocol](../../core/artifact-protocol.md)。
2. 仅在冻结条件满足且命中持久化条件后，才把完整方案写入 `spec.md` 并回读，再向 Human 交付。
   持久化优先使用已确认的 Spec storage root，其次项目现有约定；两者都没有时使用 `docs/plan`。任务目录内写 `spec.md`，按需将 `decisions.md` 写入同一目录。
3. 起草前按 Artifact Protocol 确定本次能够定义 Spec 事实的具体项目 path/reference 和 Human 项目决定；Handoff、报告和工作流输出仅作索引；按 Artifact Protocol 区分目标产品的规范与当前任务编排信息，前者可以作为项目来源，后者不进入 Spec。
4. 依据上一步确认的项目事实与需求完成必要设计，按 Artifact Protocol 的统一内容格式生成面向目标项目的实施规格；项目已有格式只有在完整承载该格式语义时才沿用。
5. 回读并核对 Spec 中所有保留英文的既有项目标识，以及所有拟新增的实现标识和项目概念名称。既有标识逐个与已确认项目来源精确匹配；项目来源未定义简称或别名时，必须改回完整项目名称。拟新增标识和概念名称逐个核对目标位置、相邻 Owner、直接消费者与项目当前命名习惯，命名依据和含义必须由项目来源或 Human 项目决定支持。
6. 按 Artifact Protocol 区分已有事实与拟议技术决定：事实及既有约束必须回指已确认项目来源或 Human 决定，改写保留原条件与含义；缺少事实依据的断言删除。必要的新设计由 Planner 基于事实和需求确定并写入方案，不伪装为项目现状，不要求 Human 代作可自行确定的技术判断。
7. 将需求边界、必要设计、精确修改说明、理由与验收落入 Spec；修订时原位替换依赖已改变前提的旧方案和验收，引用接手所需的当前执行状态。
8. 交付前依据落盘 Spec、项目规则及明确引用的资料，沿本次修改路径推演实施与验收，按 Artifact Protocol 的统一标准核对：执行者是否仍需补设计、比较方案或猜测意图。遗漏的决定补写，可查事实查明后写回，必要技术选择由 Planner 完成；实质未决项按既有冻结条件处理。存在过渡改动时说明其与最终方案的关系。未达标准时原位修订受影响内容后再交付，不转交 Executor 或依赖 Reviewer 补齐；不另建自包含检查产物、重复检查清单或默认增加独立 Agent。
9. 工作流返回、协调和验证责任由主任务分别按 [Workflow Contract](../../core/workflow-contract.md)、[Coordination Contract](../../core/coordination-contract.md) 与 [Assurance Contract](../../core/assurance-contract.md) 处理，不写回 Spec。主任务能形成至少两个独立调查单元，或出现多个候选、依赖或恢复协调时，调用 Manager 并消费其分解、依赖、串行/派发结论和证据；Planner 委派 Agent 返回协调请求。

## 输出

1. 向 Human 提交此前未确认的实质方案前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，交付已落盘 Spec 的 path、方案摘要和优先检查点。
2. 普通批准与明确迁移批准沿用术语合同，下一 Role 路由按 Workflow Contract 返回主任务。`project-context` 候选及 `decisions.md` path 留给收尾文档写入者。

## 停止与禁止边界

- 缺失决策会实质改变 Scope、架构、验收或高影响授权时，Planner 调用 Explore；Explore 将无法收口的决策作为阻塞项返回后，主任务等待 Human。
- Planner 不实施生产修改；Scope、合同或验收变化由主任务返回 Planner 修订。
