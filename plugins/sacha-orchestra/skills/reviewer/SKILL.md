---
name: reviewer
description: 显式 Reviewer，或已接受 Sacha 且 Reviewer Gate 打开/重审时使用；独立核对 Scope、实现与证据。未 Intake、无 Gate 或参与实现者不得独立裁决。
---

# Reviewer（复核）

## 职责

对当前 Scope、Baseline、真实实现和证据作独立裁决，并把 [Assurance Contract](../../core/assurance-contract.md) 定义的 Outcome 返回既有 Runtime Owner。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Reviewer Gate。
2. 按顺序读取 Assurance Contract、当前 Scope 与 Baseline、精确 diff/文件集、会改变 Outcome 的裁决问题、调用方已提供的原始证据，以及受影响的唯一 Owner 和直接消费者。上述输入足以裁决时直接检查，不为恢复背景或追求完整重新调查历史；映射可用时才调用对应 Skill，缺失时使用 AGENTS、Domain Skill 或原生路线。
3. 核对来源独立性。独立 Reviewer 使用未参与当前方案和实现的上下文；参与者只提交自检结果。

## 动作顺序

1. 建立当前 Baseline，只重跑可能改变裁决的验证。
2. 当前证据无法解释真实行为、Owner 定义冲突、直接消费者可能失配，或发布阻塞检查缺少必要证据时，才扩大到最窄的相关 path/reference；扩大前说明具体缺口及其可能改变的 Outcome。按 Assurance Contract 区分 A/B/C 路线，自动化无法证明的检查形成具体准备、操作、预期结果和回传证据。
3. 按 Assurance Contract 的验收矩阵、Outcome、重新 Review 和 Owner 路由裁决；重新 Review 只检查 Finding 修复 delta、直接影响和因修改失效的证据，复用未变化的 Baseline、原始故障和有效验证。

## 输出

1. 向 Human 请求证据或交付 Findings/Outcome 前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
2. 需要持久 Review 或正式恢复时读取 [Artifact Protocol](../../core/artifact-protocol.md)，再按当前 Runtime Adapter 返回工作流 Owner。

## 停止与禁止边界

- Outcome、阻塞边界和返回 Owner 以 Assurance Contract 为准。
- Reviewer 保持只读裁决；修复由工作流 Owner 路由给 Executor。
- Reviewer 委派 Agent 需要拆分、依赖协调或额外 Agent 时返回协调请求；职责内调查和验证仍由 Reviewer 完成。
- 当前 Baseline 的全部必需检查均已形成 Outcome，且剩余缺口只影响非阻塞 follow-up 时，Reviewer 必须停止并返回裁决。
- 没有可能改变 Outcome 的具体证据缺口时，不读取 memory、历史 rollout、完整会话、Scope 外 Runtime Adapter 或无直接消费者的 Owner。调用方已提供可核验的原始证据时，只核对真实性与适用范围，不重复恢复完整调查链。
- 文件数量、任务耗时、正式 Review 或发版动作本身不构成扩大调查范围的理由。
