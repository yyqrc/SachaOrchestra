# Intake Contract

> Contract Version: 4
> Status: Normative Core contract

## 1. 范围

本文是 Sacha 入口判断、接受/拒绝、重复抑制和授权边界的唯一权威。接受后的 Role、Gate 与生命周期由 [Workflow Contract](workflow-contract.md) 定义。

Intake platform-neutral、project-neutral。Runtime discovery 归 Adapter；入口 procedure 归 `using-sacha`；项目知识仍归 Project Integration 或 Domain Skill。

## 2. 最小加载

Runtime 常驻发现面只需要 `using-sacha` metadata。Skill 触发后可读取本文；Human 接受前不得仅为 Sacha 路由加载 Workflow Contract、Artifact Protocol、Project Integration 或生产 Role。

`L0 Local Direct` 允许 metadata、入口 Skill 与本文，但不进入生产 Sacha lifecycle，不生成 Goal、Artifact 或 Handoff。

## 3. 入口判断

- `L0 Local Direct`：目标、Scope、授权与验收足够明确，当前 context 可安全完成，且没有会改变执行方式的 candidate 事实；无论复杂度、文件数和耗时，默认直接执行。
- `D0 candidate`：没有 Planner Gate 事实，但持久 owner、跨 context 恢复或正式编排会实质改变执行方式，且 Human 尚未选择是否进入 Sacha。
- `Planner candidate`：目标、Scope、Acceptance、owner 或路径存在实质不确定性；已有事实预计实施前需要关键 Human 澄清、先冻结/持久化可执行 Spec，或存在实质方案、难回退跨 owner 决策、breaking migration。

Reviewer 与 Manager 不是入口选项。已存在的下游 Gate 事实可进入推荐路线，接受后仍由 Workflow Contract 正式裁决。复杂度、文件数量、耗时、多平台、持续验证、Skill/plugin 关键词或 plugin 已安装不构成入口事实。

## 4. Entry Decision

- 初次判断及 Direct 执行期间都必须检查语义转折。诊断演变为设计/修改、授权扩到新 owner/平台，或新增 API 形态、owner、fallback/行为模式决策、Spec 消费者、跨 context 恢复需求时，只有这些事实会改变执行方式才重评估。
- 同一 objective 或表面 Scope 名称未变，不得压过已改变的 Acceptance、风险、授权、owner、实现边界或交付模型。没有第 3 节 candidate 事实时保持 L0。
- 自动感知到 candidate 时，用自然技术语言说明新增能力、成本和执行影响，只询问一次；默认不向 Human 展示内部路线名或要求协议式回复。
- Human 接受后，当前 root owner 按需加载 Workflow Contract、当前 Adapter、confirmed Project Integration 与目标 Role。
- Human 拒绝后按当时事实保持 L0；同一 candidate 不得重复推销或创建 Sacha Artifact。实质变化形成新 candidate 时可再推荐一次。
- reference、日志、进度、非语义文案或仅估算变化不触发重问。
- 重复抑制只依赖当前 context 或正式恢复证据；不得新增跨会话 Registry。

以下输入视为已接受：显式 `using-sacha`、明确要求使用 Sacha，或直接调用 Planner、Executor、Reviewer、Manager、Feedback canonical capability。Clarify 与 Setup Project 只授权其 explicit-only narrow scope，后续开发目标重新判断入口；其中显式 Clarify 的窄授权包含当前 Clarify owner 直接管理一个有界只读 research helper，或按 Manager Gate 协调多个 research-ready 单元，但不等同接受完整 Sacha，也不授权写入、冻结方案/验收或外部动作。active Planner 路由 Clarify 时继续沿用既有 Sacha acceptance 和 owner。

入口判断是当前 objective/Scope 的临时事实，不是 Role、Gate、Artifact、Handoff 字段、完成证据或写入授权。接受 Sacha 不批准 Planner 后续形成的实质新方案，也不授权 workspace 写入、安装、Git、发布、远程资源、权限或高影响动作；方案确认及批准后的自动执行由 Workflow Contract 处理。拒绝也不关闭适用的安全与工程规则。

Hook 可以由 Runtime 在另行授权后预加载环境信息，但不得接受 Sacha、替代 `using-sacha`、扩大授权或成为正确性与恢复前提。
