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
4. 按 project/workspace、Task ID/Scope、repair objective、owner/Role、revision/provenance 和可续发状态筛选 repair target；同 cwd、仓库、Skill、owner 或标题相近均不足。只有唯一完整匹配才复用。
5. 无匹配且 objective、Scope、owner 唯一时，显式 Feedback 创建一个独立 repair task/context 并发送 bounded packet；自动 Feedback 仅在已接受 lifecycle 允许 transport 时创建。多项完整匹配或任一项无法消歧时请求 Human。新 task/context 只继承 packet 已有授权，不扩大源码写入、安装、Git、发布或外部动作。
6. Source owner 按 Adapter join 并消费一次 terminal result，验证 identity/revision 后返回原 workflow owner；不得向其他 task 发送 packet、result 或 follow-up。

## 边界

- 不设计或实施修复，不重定义 Core、Artifact、Assurance Outcome 或根终态。
- 不授权安装、系统配置、Git、发布或其他外部动作。
- 无安全 return path 时保留现场、精确错误和恢复入口，不让 Human 手工搬运 verdict。
