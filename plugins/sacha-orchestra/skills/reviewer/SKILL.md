---
name: reviewer
description: 显式 Reviewer，或已接受 Sacha 且 Reviewer Gate 打开/重审时使用；独立核对 Scope、实现与证据。未 Intake、无 Gate 或参与实现者不得独立裁决。
---

# Reviewer（复核）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Reviewer Gate。
   裁决读取 [Assurance Contract](../../core/assurance-contract.md)。
2. 读 Scope、真实实现和原始证据。mapping 可用才调用对应 Skill；缺失时用 AGENTS、Domain Skill 或原生路线。
3. 核对 provenance；参与当前规划或实现时只能声明自检。
4. 建立当前 Baseline，重跑最可能改变 verdict 的验证；自动化无法证明的检查给出具体人工路线。
5. 按 Assurance 的矩阵、Outcome、re-review 和 owner route 裁决；re-review 只返回受影响检查与下一路由。
6. 需要持久 Review 或正式恢复时才读取 [Artifact Protocol](../../core/artifact-protocol.md)，然后按 Adapter 返回 workflow owner。

## 边界

- 不重定义 Outcome、阻塞边界或返回 owner；不为通过而修改合同或默认修复。
