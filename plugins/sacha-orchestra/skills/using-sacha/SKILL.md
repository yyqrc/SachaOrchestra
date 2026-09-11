---
name: using-sacha
description: Human 明确要求编排、选择接受、直接调用规范 Role，或继续既有目标且有 Sacha 接受线索时必须使用；关键方案待比较冻结，或实际需要完整 Spec、跨上下文交接、正式协调或独立验收时，必须使用本入口判断执行方式。未接受且决定、范围、授权与验收明确、当前上下文可安全完成时不用；只读参考 Spec、多文件或局部澄清本身不触发。
---

# Using Sacha（智能入口）

## 功能

拥有 [Intake Contract](../../core/intake-contract.md) 的默认入口流程：决定保持 Direct，或在 Human 接受后把路由交给 [Workflow Contract](../../core/workflow-contract.md)。

## 输入与首查

1. Human 显式调用本 Skill、明确要求编排、选择接受、直接调用规范 Role，或元数据匹配到入口候选或既有接受线索后，必须读取 Intake Contract，核对目标、Scope、授权、验收和项目规则；新接受与继续任务的恢复均按该合同判断。
2. 对自动匹配的入口候选，只读取所需的最小事实，按 Intake Contract 第 3、4 节核对实际未决方案、规格消费者、交接需求与语义转折；局部澄清和自造 Spec 前提也按该合同判断，reference、日志和进度变化沿用原判断。

## 动作与输出

1. 尚未接受且无入口候选时保持 Direct，复杂、耗时、多文件或多平台本身不改变该判断。诊断、验收转为设计或实施中改变关键方案时，必须在继续形成方案或实施前按 Intake Contract 第 4 节重新判断，不沿用先前 Direct 结论跳过入口。
2. 入口判断为直接处理时，主任务使用当前任务语言继续；形成入口候选、Human 尚未接受或拒绝且选择条件具备时，必须读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，说明进入 Sacha 与直接处理对当前交付的差异、成本和推荐，并询问是否进入 Sacha。推荐与询问按 Intake Contract 第 4 节一起完成；同一入口候选只询问一次。按该合同暂停依赖选择的动作并继续已授权的独立事实调查。
3. Human 对入口行为的反问、调查或纠正按 Human Interaction Contract 解释并更新当前问题；入口候选仍成立且选择条件具备时再询问。
4. Human 明确要求用 Sacha 编排当前目标、选择接受或直接调用规范 Role（canonical Role）时记录接受；继续任务按 Intake Contract 核实既有接受。接受或恢复后按 [Workflow Contract](../../core/workflow-contract.md) 第 2.2 节的正式入口读取当前目标 Skill；传输、恢复、外部状态或当前 Runtime 已暴露的 Sacha 观测能力需要映射时读取目标 Adapter。观测记录失败不改变入口结果。
5. 显式 document-project 由 Intake Contract 直接路由到当前文档目标，不视为接受 Sacha，也不得为满足其前置条件补走生产 Role。
6. 拒绝后保持 Direct；新入口候选重新执行入口判断。

## 停止与禁止边界

- 入口判断只供主任务路由；直接处理时不单独向 Human 报告入口结果，入口候选按 Human Interaction Contract 形成当前选择。不得借独立事实调查绕过入口决定或推迟已具备条件的提问；拆分、派发、实施和验收由下游 Owner 处理。
- 接受后的 Role、Gate、Explore、Manager、迁移与收尾路线由 Workflow Contract 处理。
- Artifact 与 Handoff 沿用[术语合同](../../core/terminology-contract.md)；Goal、写入、安装、Git、发布、远程资源和高影响动作使用各自 Owner 与授权。
