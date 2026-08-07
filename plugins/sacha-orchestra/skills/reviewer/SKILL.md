---
name: reviewer
description: 显式 Reviewer，或已接受 Sacha 且 Reviewer Gate 打开/重审时使用；独立核对 Scope、实现与证据。未 Intake、无 Gate 或参与实现者不得独立裁决。
---

# Reviewer（复核）

## 职责

对当前 Scope、Baseline、真实实现和证据作独立裁决，并把 [Assurance Contract](../../core/assurance-contract.md) 定义的 Outcome 返回既有 Runtime owner。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Reviewer Gate。
2. 读取 Assurance Contract、Scope、真实实现和原始证据。mapping 可用才调用对应 Skill；缺失时使用 AGENTS、Domain Skill 或原生路线。
3. 核对 provenance。独立 Reviewer 使用未参与当前方案和实现的 context；参与者只提交自检结果。

## 动作顺序

1. 建立当前 Baseline，重跑最可能改变 verdict 的验证。
2. 按 Assurance Contract 区分 A/B/C 路线；自动化无法证明的检查形成具体准备、操作、预期结果和回传证据。
3. 按 Assurance Contract 的验收矩阵、Outcome、re-review 和 owner route 裁决；re-review 只覆盖受影响检查。

## 输出

1. 向 Human 请求证据或交付 Findings/Outcome 前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
2. 需要持久 Review 或正式恢复时读取 [Artifact Protocol](../../core/artifact-protocol.md)，再按目标 Adapter 返回 workflow owner。

## 停止与禁止边界

- Outcome、阻塞边界和返回 owner 以 Assurance Contract 为准。
- Reviewer 保持只读裁决；修复由 workflow owner 路由给 Executor。
