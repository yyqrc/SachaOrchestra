# Intake Contract（入口合同）

> 合同版本：6
> 状态：规范性 Core 合同

## 1. 范围

本文是 `using-sacha / 显式生产 Role / 显式 Clarify` 主工作流入口、独立显式 Feedback 任务、接受/拒绝、重复抑制和入口授权边界的唯一 Runtime 权威。接受后的路由由 [Workflow Contract](workflow-contract.md) 定义；Human 可见提问与结果遵循 [Human Interaction Contract](human-interaction-contract.md)。

Intake 不依赖平台或项目。Runtime 发现归 Adapter；入口流程归 `using-sacha`；项目知识仍归 Project Integration 或 Domain Skill。

## 2. 最小加载

Runtime 常驻发现面只需要 `using-sacha` 元数据。Skill 触发后可读取本文；Human 接受前不得仅为 Sacha 路由加载 Workflow Contract、Artifact Protocol、Project Integration 或生产 Role。

`L0 Local Direct` 允许元数据、入口 Skill 与本文，但不进入生产 Sacha 生命周期，不生成 Goal、Artifact 或 Handoff。

## 3. 入口判断

- `L0 Local Direct`：目标、Scope、授权与验收足够明确，当前上下文可安全完成，且没有会改变执行方式的候选事实；无论复杂度、文件数和耗时，默认直接执行。
- `D0 candidate`：没有 Planner Gate 事实，但持久 Owner、跨上下文恢复或正式编排会实质改变执行方式，且 Human 尚未选择是否进入 Sacha。
- `Planner candidate`：目标、Scope、Acceptance、Owner 或路径存在实质不确定性；已有事实预计实施前需要关键 Human 澄清、先冻结/持久化可执行 Spec，或存在实质方案、难回退的跨 Owner 决策、破坏性迁移。

- Planner、Executor、Reviewer 接受 Human 直接调用。
- Clarify 接受 Human 显式窄授权，或由活跃 Planner 路由。
- Feedback 接受 Human 在另一个真实任务手动提交的流程问题、使用反馈、插件开发建议或能力想法。
- Manager 和 document-project 只接受内部 Owner 路由；Reviewer Gate 与 Manager Gate 由 Workflow 在接受后判断。

复杂度、文件数量、耗时、多平台、持续验证、Skill/插件关键词或插件已安装不构成入口事实。

## 4. 入口决定

- 初次判断及直接执行期间都必须检查语义转折。诊断演变为设计/修改、授权扩到新 Owner/平台，或新增 API 形态、Owner、回退/行为模式决策、Spec 消费者、跨上下文恢复需求时，只有这些事实会改变执行方式才重评估。
- 同一目标或表面 Scope 名称未变，不得压过已改变的 Acceptance、风险、授权、Owner、实现边界或交付模型。没有第 3 节候选事实时保持 L0。
- 自动感知到候选事实时，只询问一次是否进入 Sacha，并按 Human Interaction Contract 说明新增能力、成本、执行影响与推荐。
- Human 接受后，当前根 Owner 按需加载 Workflow Contract、当前 Adapter、已确认的 Project Integration 与目标 Role。
- Human 拒绝后按当时事实保持 L0；同一候选事实不得重复推销或创建 Sacha Artifact。实质变化形成新候选事实时可再推荐一次。
- reference、日志、进度、非语义文案或仅估算变化不触发重问。
- 重复抑制只依赖当前上下文或正式恢复证据；不得新增跨会话注册表（Registry）。

| Human 输入 | 授权范围与下一路由 |
| --- | --- |
| 显式 `using-sacha`、明确要求使用 Sacha，或直接调用 Planner、Executor、Reviewer | 接受当前目标/Scope 的 Sacha 路由；当前 Owner 按 Workflow Contract 推进 |
| 显式 Clarify | 授权当前 Clarify Owner 在窄 Scope 内澄清并管理一个有界只读研究辅助 Agent；多个研究就绪单元可按 Manager Gate 协调 |
| 活跃 Planner 路由 Clarify | 沿用既有 Sacha 接受状态与 Owner，结果返回 Planner |
| 显式 Setup Project | 只授权本次项目配置 Scope；后续开发目标重新判断入口 |
| 在另一个真实任务显式调用 Feedback | 授权来源任务围绕具体反馈目标有界只读调查，并查询、复用或创建唯一反馈目标任务；Human 可提供原任务、项目或证据 reference；目标任务另行核对写入与外部动作授权 |
| 直接调用 Manager 或 document-project | 返回当前目标给 `using-sacha` 或原 Owner；两者分别由 Manager Gate 与 Workflow 收尾候选路由 |

入口授权只作用于当前目标/Scope。工作区写入、安装、Git、发布、远程资源、权限、高影响动作和 Planner 后续形成的实质方案分别取得对应授权；安全与工程规则持续生效。

Hook 可以由 Runtime 在另行授权后预加载环境信息，但不得接受 Sacha、替代 `using-sacha`、扩大授权或成为正确性与恢复前提。
