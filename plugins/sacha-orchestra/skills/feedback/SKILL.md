---
name: feedback
description: 当 Human 明确反馈 Sacha 流程/plugin 偏差，或 Role、Manager、Runtime 已产生 deviation packet 时使用；调查真实状态并把问题路由到唯一责任 owner。只授权有界调查和运输，不授权修复或外部副作用。
---

# Feedback（流程反馈）

Feedback 是 deviation intake，不是生产 Role 或修复 owner。

## 工作流

1. 读取 [Workflow Contract](../../core/workflow-contract.md) 的 deviation 语义和当前 Runtime Adapter 的调查、return 映射。
2. 只读核对真实 task/project、Skill locator、Task ID、Scope、Handoff、lifecycle、失败和原始 evidence；用户已描述问题时不重复提问。
3. 补全 expected/actual、责任层、影响、授权、evidence locator、唯一 repair/re-verification entry、return address 和 dedup key；不猜测缺失事实。
4. 同 Scope 且责任明确时交给当前 owner 修正；存在唯一合格 repair owner 时发送 bounded packet；目标、Scope、授权或 owner 无法消歧时请求 Human。
5. 按 Adapter 消费一次 terminal result，验证 identity/revision 后返回原 workflow owner。

## 边界

- 不设计或实施修复，不重定义 Core、Artifact、Outcome 或根终态。
- 不授权安装、系统配置、Git、发布或其他外部动作。
- 无安全 return path 时保留现场、精确错误和恢复入口，不让 Human 手工搬运 verdict。
