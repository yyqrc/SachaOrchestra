---
name: using-sacha
description: Sacha 默认入口。显式 Sacha，或任务确需跨 context owner、冻结 Scope、独立验收/协调时使用；清晰已授权任务直接执行，仅在编排会实质改变执行方式时询问一次。
---

# Using Sacha（智能入口）

## 工作流

1. 核对当前 objective/Scope、适用项目规则和显式接受事实，读取 [Intake Contract](../../core/intake-contract.md)。
2. 目标、授权和验收清晰且当前 context 可安全完成时保持 `L0`，直接执行；文件数、耗时或持续验证不构成 candidate。
3. 只有持久 owner、跨 context 恢复、正式协调或冻结方案会实质改变执行方式时判断 `D0 candidate`/`Planner candidate`；L0 不加载生产 Core、Artifact、Project Integration 或 Role。
4. Candidate 说明新增能力、成本、下游 Gate 与主要影响，只询问一次。显式 using-sacha、明确使用 Sacha 或直接 canonical Role 调用视为已接受。
5. 接受后读取 [Workflow Contract](../../core/workflow-contract.md) 与目标 Role；仅有 discovery、transport、恢复或外部状态 consumer 时读取当前 Runtime Adapter，项目绑定确有消费方时才读取 confirmed Project Integration。root owner 推进到合法终态。
6. 拒绝后保持 L0；只有 objective、Scope、Acceptance、风险、授权或交付模型实质变化才重评估，不持久化拒绝状态。
7. Intake 不创建 Goal、Artifact 或 Handoff，不授权写入、安装、Git、发布、远程资源或高影响动作，也不依赖 Hook。

## 路由

- Scope/Acceptance/owner/路径存在实质不确定性 → Planner；否则接受后 → Executor。
- Reviewer/Manager 只作为 downstream Gate；打开后分别按 Assurance/Coordination Contract 执行。
- Clarify/Setup Project 保持 explicit-only narrow capability；完成后新的开发目标重新 Intake。
