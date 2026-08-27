---
name: using-sacha
description: Sacha 默认入口。主任务收到当前可执行目标后必须先判断 Direct 或建议进入 Sacha；查询或诊断转为方案、修改或持久化时必须重新判断。
---

# Using Sacha（智能入口）

## 功能

拥有 [Intake Contract](../../core/intake-contract.md) 的默认入口流程：决定保持 Direct，或在 Human 接受后把路由交给 [Workflow Contract](../../core/workflow-contract.md)。

## 输入与首查

1. 主任务收到当前可执行目标后，必须先读取 Intake Contract，核对目标、Scope、授权、验收和项目规则，完成入口判断，再继续调查、形成方案或实施。
2. 同一目标从查询或诊断转为方案、修改或持久化时，必须在继续前重新判断。目标、Scope、验收、风险、授权或交付模型的实质变化形成新入口候选；reference、日志和进度变化沿用原判断。

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
