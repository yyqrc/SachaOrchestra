---
name: using-sacha
description: Human 明确要求编排、选择接受或直接调用规范 Role 时使用；目标或下一步仍有影响实施路线的关键方案待比较冻结，或用户要求、实际后续消费者需要完整 Spec、跨上下文交接、正式协调或独立验收时主动判断入口。关键决定、范围、授权与验收明确且当前上下文可安全完成时不用；多文件、跨插件、行为修改或局部澄清本身不触发。
---

# Using Sacha（智能入口）

## 功能

拥有 [Intake Contract](../../core/intake-contract.md) 的默认入口流程：决定保持 Direct，或在 Human 接受后把路由交给 [Workflow Contract](../../core/workflow-contract.md)。

## 输入与首查

1. Human 显式调用本 Skill、明确要求编排、选择接受、直接调用规范 Role，或元数据匹配到入口候选后，读取 Intake Contract，核对目标、Scope、授权、验收和项目规则；是否接受只使用该合同的判断。
2. 对自动匹配的入口候选，只读取所需的最小事实，按 Intake Contract 第 3、4 节核对实际未决方案、规格消费者、交接需求与语义转折；局部澄清和自造 Spec 前提也按该合同判断，reference、日志和进度变化沿用原判断。

## 动作与输出

1. 复杂、耗时、多文件、多平台或持续验证保持 Direct；执行方式会改变时才建议 Sacha。
2. 入口判断为直接处理时，主任务使用当前任务语言继续；形成入口候选且 Human 尚未接受或拒绝时，读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，说明收益、成本和推荐，并询问是否进入 Sacha。推荐与询问按 Intake Contract 第 4 节一起完成；同一入口候选只询问一次。按该合同暂停依赖选择的动作并继续已授权的独立事实调查。
3. Human 对入口行为的反问、调查或纠正按 Human Interaction Contract 解释并更新当前问题；入口候选仍成立且选择条件具备时再询问。
4. Human 明确要求用 Sacha 编排当前目标、选择接受或直接调用规范 Role（canonical Role）时记录接受。接受后按 [Workflow Contract](../../core/workflow-contract.md) 第 2.2 节的正式入口读取目标 Skill；传输、恢复、外部状态或当前 Runtime 已暴露的 Sacha 观测能力需要映射时读取目标 Adapter。观测记录失败不改变入口结果。
5. 显式 document-project 由 Intake Contract 直接路由到当前文档目标，不视为接受 Sacha，也不得为满足其前置条件补走生产 Role。
6. 拒绝后保持 Direct；新入口候选重新执行入口判断。

## 停止与禁止边界

- 入口判断只供主任务路由；直接处理时不单独向 Human 报告入口结果，入口候选按 Human Interaction Contract 形成当前选择。不得借独立事实调查绕过入口决定或推迟已具备条件的提问；拆分、派发、实施和验收由下游 Owner 处理。
- 接受后的 Role、Gate、Explore、Manager、迁移与收尾路线由 Workflow Contract 处理。
- Artifact 与 Handoff 沿用[术语合同](../../core/terminology-contract.md)；Goal、写入、安装、Git、发布、远程资源和高影响动作使用各自 Owner 与授权。
