---
name: feedback
description: 显式 Sacha 流程反馈，或已接受 lifecycle 产生 deviation 时使用；只读取证并完成唯一 repair target 的路由与终态返回。普通开发不用；不授权目标写入或外部动作。
---

# Feedback（流程反馈）

## 工作流

1. 显式 Feedback 视为接受调查与路由这一窄 Scope；自动调用须有现存 deviation。读取 [Workflow Contract](../../core/workflow-contract.md)、[Coordination Contract](../../core/coordination-contract.md) 和当前 Adapter 的调查/return 映射。
2. Source 只读核对真实 task/project、Scope、owner、失败和原始 evidence；用户已描述的问题不重复提问。可用有界只读 helper 补证，但 helper 仍属于 Source，不取得 owner、Role 或 repair identity，不能替代目标 workspace/context。
3. 用 workspace、Task/Scope、repair objective、owner/Role、revision/provenance 和可续发状态筛选 repair target；相近 cwd、仓库、Skill、owner 或标题都不足。只有唯一完整匹配才复用且不得重复创建；无法消歧就问 Human。
4. 显式 Feedback 已要求处理/修复，且 objective、Scope、owner 唯一、transport 可用时，Source 必须完成路由：无匹配就创建恰好一个 owner workspace 的 repair context；有匹配就复用。不得只返回报告，也不得要求 Human 为创建同一目标再次授权。自动 Feedback 仅在已接受 lifecycle 允许创建时采用同一路线；新 context 不扩权。
5. Target 按原 repair objective 独立核对源码写入及 Git、安装、发布等副作用授权；缺少授权时由 Target 暂停。Source 不设计或实施修复，也不修改 repair source。
6. Source owner 按 Adapter 等待并消费一次 terminal result，核对 identity/revision 后返回原 workflow owner；不得在 dispatch 或报告后提前结束，也不向其他 task 发送结果或 follow-up。

## 边界

- 调查与路由授权不等于 Target 实施授权，也不授权安装、系统配置、Git、发布或其他外部动作。
- 不重定义 Core、Artifact、Assurance Outcome 或根终态。
- 无安全 return path 时保留现场、精确错误和恢复入口，不让 Human 搬运内部 verdict。
