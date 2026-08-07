---
name: using-sacha
description: Sacha 默认入口。显式使用，或任务演变会改变执行方式时重评估；仅复杂、耗时或多文件仍保持 Direct。
---

# Using Sacha（智能入口）

## 功能

拥有 [Intake Contract](../../core/intake-contract.md) 的默认入口 procedure：决定保持 Direct，或在 Human 接受后把路由交给 [Workflow Contract](../../core/workflow-contract.md)。

## 输入与首查

1. 读取 Intake Contract，核对目标、Scope、授权、验收和项目规则。
2. 初次判断及 Direct 执行期间检查语义转折。目标、Scope、验收、风险、授权或交付模型的实质变化形成新 candidate；reference、日志和进度变化沿用原判断。

## 动作与输出

1. 复杂、耗时、多文件、多平台或持续验证保持 Direct；执行方式会改变时才建议 Sacha。
2. 需要 Human 选择时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，说明收益、成本和推荐；同一 candidate 只询问一次。
3. 显式 using-sacha、明确使用 Sacha 或直接调用 canonical Role 视为接受。接受后读取 Workflow Contract 与目标 Role；transport、恢复或外部状态需要映射时读取目标 Adapter。
4. 拒绝后保持 Direct；新 candidate 重新执行入口判断。

## 停止与禁止边界

- 本 Skill 的产出是 Direct 或 Sacha 入口结果；拆分、派发、实施和验收由 downstream owner 处理。
- 接受后的 Role、Gate、Clarify、Manager、迁移与收尾路线由 Workflow Contract 处理。
- Goal、Artifact、Handoff、写入、安装、Git、发布、远程资源和高影响动作使用各自 owner 与授权。
