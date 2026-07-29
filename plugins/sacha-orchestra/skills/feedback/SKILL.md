---
name: feedback
description: 显式 Sacha 流程反馈，或已接受 lifecycle 产生 deviation 时使用；调查并路由唯一 owner。普通开发不用；不授权修复或外部动作。
---

# Feedback（流程反馈）

## 工作流

1. 显式 Feedback 视为接受该窄 Scope；自动调用须有现存 deviation。读取 [Workflow Contract](../../core/workflow-contract.md)、[Coordination Contract](../../core/coordination-contract.md) 和当前 Adapter 的调查/return 映射。
2. 只读核对真实 task/project、Scope、owner、失败和原始 evidence；用户已描述的问题不重复提问。只补 expected/actual/impact、证据和恢复/停止条件。
3. 用 workspace、Task/Scope、repair objective、owner/Role、revision/provenance 和可续发状态筛选 repair target；相近 cwd、仓库、Skill、owner 或标题都不足，只有唯一完整匹配才复用。
4. 无匹配且 objective、Scope、owner 唯一时，显式 Feedback 可建一个 repair context；自动 Feedback 只有已接受 lifecycle 允许 transport 时才能创建。无法消歧就问 Human；新 context 不扩权。
5. Source owner 按 Adapter join 并消费一次 terminal result，核对 identity/revision 后返回原 workflow owner；不向其他 task 发送结果或 follow-up。

## 边界

- 不设计或实施修复，不重定义 Core、Artifact、Assurance Outcome 或根终态。
- 不授权安装、系统配置、Git、发布或其他外部动作。
- 无安全 return path 时保留现场、精确错误和恢复入口，不让 Human 搬运内部 verdict。
