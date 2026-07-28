---
name: feedback
description: 显式 Sacha 流程反馈，或已接受 lifecycle 产生 deviation 时使用；调查并路由唯一 owner。普通开发不用；不授权修复或外部动作。
---

# Feedback（流程反馈）

Feedback 是 deviation intake，不是生产 Role 或修复 owner。

## 工作流

1. 显式 Feedback 视为接受该窄 Scope；自动调用须有现存 deviation。读取 [Workflow Contract](../../core/workflow-contract.md)、[Coordination Contract](../../core/coordination-contract.md) 和当前 Adapter 的调查/return 映射。
2. 只读核对真实 task/project、Skill locator、Task ID、Scope、Handoff、lifecycle、失败和原始 evidence；用户已描述问题时不重复提问。
3. 补全 expected/actual、责任层、影响、授权、evidence locator、唯一 repair/re-verification entry、return address 和 dedup key；不猜测缺失事实。
4. 同 Scope 且责任明确时交给当前 owner 修正；存在唯一合格 repair owner 时发送 bounded packet；目标、Scope、授权或 owner 无法消歧时请求 Human。
5. 按 Adapter 消费一次 terminal result，验证 identity/revision 后返回原 workflow owner。

## 边界

- 不设计或实施修复，不重定义 Core、Artifact、Assurance Outcome 或根终态。
- 不授权安装、系统配置、Git、发布或其他外部动作。
- 无安全 return path 时保留现场、精确错误和恢复入口，不让 Human 手工搬运 verdict。
