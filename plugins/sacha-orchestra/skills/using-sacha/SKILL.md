---
name: using-sacha
description: Human 明确使用 Sacha，或已有事实表明关键 Human 决定、持久化实施规格、跨上下文恢复、正式协调或独立验收会改变执行方式时使用；目标、范围、授权与验收清晰且当前上下文可安全完成时不用。
---

# Using Sacha（智能入口）

## 功能

拥有 [Intake Contract](../../core/intake-contract.md) 的默认入口流程：决定保持 Direct，或在 Human 接受后把路由交给 [Workflow Contract](../../core/workflow-contract.md)。

## 输入与首查

1. Human 显式使用 Sacha，或元数据匹配到入口候选后，读取 Intake Contract，核对目标、Scope、授权、验收和项目规则。
2. 对自动匹配的入口候选，核对当前目标及语义转折是否确实形成入口候选，并判断 Planner Gate 事实是否成立。目标、Scope、验收、风险、授权或交付模型的实质变化可以形成新候选；reference、日志和进度变化沿用原判断。

## 动作与输出

1. 复杂、耗时、多文件、多平台或持续验证保持 Direct；执行方式会改变时才建议 Sacha。
2. 入口判断为直接处理时，主任务使用当前任务语言继续；形成入口候选并需要 Human 选择时，读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，说明收益、成本和推荐；同一入口候选只询问一次。
3. Human 对入口行为的反问、调查或纠正按 Human Interaction Contract 解释并更新当前问题；入口候选仍成立且选择条件具备时再询问。
4. Human 明确使用 Sacha、选择接受或直接调用规范 Role（canonical Role）时记录接受。接受后读取 Workflow Contract 与目标 Role；传输、恢复、外部状态或当前 Runtime 已暴露的 Sacha 观测能力需要映射时读取目标 Adapter。观测记录失败不改变入口结果。
5. 显式 document-project 由 Intake Contract 直接路由到当前文档目标，不视为接受 Sacha，也不得为满足其前置条件补走生产 Role。
6. 拒绝后保持 Direct；新入口候选重新执行入口判断。

## 停止与禁止边界

- 入口判断只供主任务路由；直接处理时不单独向 Human 报告入口结果，入口候选按 Human Interaction Contract 形成当前选择。拆分、派发、实施和验收由下游 Owner 处理。
- 接受后的 Role、Gate、Explore、Manager、迁移与收尾路线由 Workflow Contract 处理。
- Artifact 与 Handoff 沿用[术语合同](../../core/terminology-contract.md)；Goal、写入、安装、Git、发布、远程资源和高影响动作使用各自 Owner 与授权。
