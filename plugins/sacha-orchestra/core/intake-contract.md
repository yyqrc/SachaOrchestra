# Intake Contract

> Contract Version: 2
> Status: Normative Core contract

## 1. 范围

本文是 Sacha 入口判断、接受/拒绝、重复抑制和授权边界的唯一权威。接受后的 Role、Gate 与生命周期由 [Workflow Contract](workflow-contract.md) 定义。

Intake platform-neutral、project-neutral。Runtime discovery 归 Adapter；入口 procedure 归 `using-sacha`；项目知识仍归 Project Integration 或 Domain Skill。

## 2. 最小加载

Runtime 常驻发现面只需要 `using-sacha` metadata。Skill 触发后可读取本文；Human 接受前不得仅为 Sacha 路由加载 Workflow Contract、Artifact Protocol、Project Integration 或生产 Role。

`L0 Local Direct` 允许 metadata、入口 Skill 与本文，但不进入生产 Sacha lifecycle，不生成 Goal、Artifact 或 Handoff。

## 3. 入口判断

- `L0 Local Direct`：目标、Scope、授权与验收足够明确，当前 context 可安全完成的查询、诊断、实施或验证；无论文件数和耗时，默认直接执行。
- `D0 candidate`：没有 Planner Gate 事实，但持久 owner、跨 context 恢复或正式编排会实质改变执行方式，且 Human 尚未选择是否进入 Sacha。
- `Planner candidate`：目标、Scope、Acceptance、owner 或路径存在实质不确定性，或需要冻结方案、难逆决策或 breaking migration。

Reviewer 与 Manager 不是入口选项。已存在的下游 Gate 事实可进入推荐路线，接受后仍由 Workflow Contract 正式裁决。文件数量、耗时、Skill/plugin 关键词或 plugin 已安装不构成入口事实。

## 4. Entry Decision

- 清晰且已授权的任务不得仅因需要持续实施、验证、文件较多或耗时而询问；保持 L0 并直接执行。
- 自动感知到 candidate 时，说明 Sacha 会增加的具体能力、成本和下游 Gate，只在该选择会实质改变执行方式时询问一次。
- Human 接受后，当前 root owner 按需加载 Workflow Contract、当前 Adapter、confirmed Project Integration 与目标 Role。
- Human 拒绝后，当前 objective/Scope 保持 L0；不得重复推销或创建 Sacha Artifact。
- objective、Scope、Acceptance、风险、授权或交付模型实质变化时可重评估；locator、日志、进度或非语义文案变化不触发重问。
- 重复抑制只依赖当前 context 或正式恢复证据；不得新增跨会话 Registry。

以下输入视为已接受：显式 `using-sacha`、明确要求使用 Sacha，或直接调用 Planner、Executor、Reviewer、Manager、Feedback canonical capability。Clarify 与 Setup Project 只授权其 explicit-only narrow scope，后续开发目标重新判断入口。

入口判断是当前 objective/Scope 的临时事实，不是 Role、Gate、Artifact、Handoff 字段、完成证据或写入授权。接受 Sacha 不授权 workspace 写入、安装、Git、发布、远程资源、权限或高影响动作；拒绝也不关闭适用的安全与工程规则。

Hook 可以由 Runtime 在另行授权后预加载环境信息，但不得接受 Sacha、替代 `using-sacha`、扩大授权或成为正确性与恢复前提。
