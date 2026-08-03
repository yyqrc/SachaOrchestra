---
name: feedback
description: 显式流程反馈，或已接受的 lifecycle 出现 deviation 时使用；只读调查、路由唯一 repair target 并等待终态。普通开发不用。
---

# Feedback（流程反馈）

## 工作流

1. 显式 Feedback 视为接受调查与路由这一窄 Scope；自动调用须有现存 deviation。
   读取 [Workflow Contract](../../core/workflow-contract.md)、[Coordination Contract](../../core/coordination-contract.md) 和当前 Adapter 的调查/return 映射。
2. Source 只读核对真实 task/project、Scope、owner、失败和原始 evidence；不重复询问已知事实。
   有界只读 helper 只补证，不取得 owner、Role 或 repair identity，也不能替代目标 workspace/context。
3. 按 Coordination 的 identity/dedup 规则筛选 target；无法消歧就问 Human。
4. 通过 Adapter 复用或创建合法 target并等待 terminal，不以调查报告代替 repair route。自动 Feedback 仅在已接受 lifecycle 允许时路由。
5. Target 按 Coordination 独立核对实施与外部副作用授权。Source 不设计或实施修复，也不修改 repair source。
6. Source owner 按 Adapter 等待并消费一次 terminal result，核对 identity/revision 后返回原 workflow owner；不得在 dispatch 或报告后提前结束，也不向其他 task 发送结果或 follow-up。

## 边界

- 调查与路由不扩大 Target 实施或外部动作授权。
- 不重定义 Core、Artifact、Assurance Outcome 或根终态。
- 无安全 return path 时保留现场、精确错误和恢复入口，不让 Human 搬运内部 verdict。
