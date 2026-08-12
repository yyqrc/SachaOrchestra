# 单层 Manager 派发 Spec

> 状态：Human 已批准实施
> 日期：2026-08-12

本文沿用 [Workflow Contract](../../../plugins/sacha-orchestra/core/workflow-contract.md) 定义的“主任务”，以及 [Coordination Contract](../../../plugins/sacha-orchestra/core/coordination-contract.md) 定义的“单层派发”“委派 Agent”和“协调请求”。

## 目标与失败模式

Sacha 只允许主任务执行 Manager 协调和单层派发。现有 Core 未明确禁止委派 Agent 再派发，Claude Code Adapter 还允许控制面 Agent 调用 Manager，可能形成嵌套派发并绕过顶层 Adapter 路由。

## Scope

- 顶层设计与 Workflow 明确主任务、Manager 和委派 Agent 的单层关系。
- Coordination 作为唯一 Core Owner 定义单层派发、委派 Agent、协调请求和迁移后的派发权转移。
- Manager、Planner、Executor、Reviewer、Clarify 只消费该边界，不建立第二套判断。
- Codex、Claude Code、Cursor Adapter 只允许主任务执行首次创建；委派 Agent 遵守单层派发。
- Luna Agent 定义拒绝 Manager 调用和下级 Agent 创建。
- Runtime 场景以首次等待前的实时 Agent 树和原始创建参数验收单层派发。

## 决定

1. 只有主任务拥有派发权；Manager 在主任务内运行，不是委派 Agent。
2. Planner、Executor、Reviewer、Clarify 或普通 Agent 成为委派 Agent 后，只完成当前单元并返回结果或协调请求。
3. 主任务消费协调请求后，按 Coordination 重评估并通过当前 Runtime Adapter 执行单层派发。
4. 用户任务迁移成功后，派发权随工作流 Owner 转移；来源任务和委派 Agent 不再派发。
5. 不新增 Role、Gate、状态、字段、特殊生命周期或跨会话注册表。

## 验收与证据边界

- 顶层设计、Workflow、Coordination、直接 Skill 和三个 Adapter 对主任务、单层派发、委派 Agent 与协调请求一致。
- Manager 场景的实时 Agent 树中，所有委派 Agent 都是主任务的直接子级且没有后代；首次创建参数符合当前 Runtime Adapter。
- 项目测试、Skill/Plugin validator 与有界变更审计只证明源码/静态状态；全新任务中的派发层级、参数和返回仍需另行授权的真实 Runtime 场景。

## 授权边界

本次批准覆盖 SachaOrchestra workspace 内上述源码、文档、场景和静态验证；不包含安装、创建全新验证任务、提交、push、tag 或发布。
