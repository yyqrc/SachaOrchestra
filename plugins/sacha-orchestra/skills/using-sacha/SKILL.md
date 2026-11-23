---
name: using-sacha
description: >-
  需要澄清需求、探索或比较关键方案才能确定目标、范围、验收或做法时，主动评估是否使用 Sacha。
  用户要求为后续实施或验收准备 Spec、需要跨会话交接、正式协调或独立验收时也使用。
  用户明确选择用 Sacha、调用其正式角色，或继续已有接受线索的任务时，按此入口核实。
  普通查询、定位、只读参考 Spec 和可以局部澄清的任务在当前会话直接处理。
  评估入口不表示用户已经接受 Sacha 或授权实施。
---

# Using Sacha（智能入口）

## 功能

拥有 [Intake Contract](../../core/intake-contract.md) 的默认入口流程：决定保持 Direct，或在 Human 接受后把路由交给 [Workflow Contract](../../core/workflow-contract.md)。

## 输入与首查

1. Human 显式调用本 Skill、明确要求编排、选择接受、直接调用规范 Role，或元数据匹配到入口候选或既有接受线索后，必须读取 Intake Contract，核对目标、Scope、授权、验收和项目规则；新接受与继续任务的恢复均按该合同判断。
2. 自动匹配时，只查够判断入口的事实，再按入口合同第 3、4 节核对需要决定的方案、规格的实际使用方、交接需求和本次请求的变化。局部澄清能补齐的事实按合同直接处理。只有引用、日志或进度变化时沿用原判断。

## 动作与输出

1. 尚未接受且无入口候选时保持 Direct，复杂、耗时、多文件或多平台本身不改变该判断。诊断、验收转为设计或实施中改变关键方案时，必须在继续形成方案或实施前按 Intake Contract 第 4 节重新判断，不沿用先前 Direct 结论跳过入口。
2. 判定直接处理时，用当前任务的语言继续。适合提出 Sacha、用户尚未作出选择且决策条件齐备时，读取 [交互合同](../../core/human-interaction-contract.md)。说明两种做法如何影响当前交付、各自的成本和推荐，按入口合同第 4 节一起提出选择。同一候选只问一次。等待决定时继续不依赖答案且已授权的事实调查。
3. Human 对入口行为的反问、调查或纠正按 Human Interaction Contract 解释并更新当前问题；入口候选仍成立且选择条件具备时再询问。
4. Human 明确要求用 Sacha 编排当前目标、选择接受或直接调用规范 Role（canonical Role）时记录接受；继续任务按 Intake Contract 核实既有接受。接受或恢复后按 [Workflow Contract](../../core/workflow-contract.md) 第 2.2 节的正式入口读取当前目标 Skill；传输、恢复、外部状态或当前 Runtime 已暴露的 Sacha 观测能力需要映射时读取目标 Adapter。观测记录失败不改变入口结果。
5. 显式 document-project 由 Intake Contract 直接路由到当前文档目标，不视为接受 Sacha，也不得为满足其前置条件补走生产 Role。
6. 拒绝后保持 Direct；新入口候选重新执行入口判断。

## 停止与禁止边界

- 入口判断只供主任务路由；直接处理时不单独向 Human 报告入口结果，入口候选按 Human Interaction Contract 形成当前选择。不得借独立事实调查绕过入口决定或推迟已具备条件的提问；拆分、派发、实施和验收由下游 Owner 处理。
- 接受后的 Role、Gate、Explore、Manager、迁移与收尾路线由 Workflow Contract 处理。
- Artifact 与 Handoff 沿用[术语合同](../../core/terminology-contract.md)。写入、安装、Git、发布、远程资源和高影响动作使用各自的负责规则与授权。
