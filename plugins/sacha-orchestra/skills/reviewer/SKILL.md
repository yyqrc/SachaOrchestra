---
name: reviewer
description: 显式 Reviewer，或已接受 Sacha 且 Reviewer Gate 打开/重审时使用；独立核对 Scope、实现与证据。未 Intake、无 Gate 或参与实现者不得独立裁决。
---

# Reviewer（复核）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 的接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Reviewer Gate/Review 请求；两者皆无时不裁决。裁决语义读取 [Assurance Contract](../../core/assurance-contract.md)。
2. 读 Scope、实现和原始证据。mapping policy 允许才用 Skill；缺 Binding、目标 mapping 或可用 Skill 时回退 AGENTS/Domain Skill/原生路线，不调用 Setup。
3. 建立 provenance。参与过当前规划或实现时只能声明同 context 自检，不能声明独立 Review。
4. 复核 Baseline、`acceptance_revision` 与矩阵的 required/attempted ID、状态、计数和 locator；provider 只作证据索引。
5. 检查真实 diff/状态并重跑风险最高且成本合理的验证。自动化无法证明的具体检查给出可执行人工路线；不得把缺证据等同于实现缺陷。
6. 按 Assurance Outcome 裁决并明确实现、构建、运行、人工、环境和最终状态。Baseline 变化停止裁决；evidence-only delta 只复核受影响 check。
7. 需要 Review Artifact 或正式 Handoff 时读取 [Artifact Protocol](../../core/artifact-protocol.md)，然后按当前 Runtime Adapter 返回 workflow owner；Reviewer 不实现 transport 或监控 owner。

## 暂停与路由

- 实现缺陷 → 原 Executor；合同问题 → Planner；缺证据 → 唯一证据 owner。
- 只有批准矩阵明确为 release-blocking 的未完成项阻塞交付。
- 不为使实现通过而改合同，不默认修复，不用 Executor 自报代替独立判断。
