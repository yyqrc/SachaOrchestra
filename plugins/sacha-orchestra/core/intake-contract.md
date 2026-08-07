# Intake Contract

> Contract Version: 6
> Status: Normative Core contract

## 1. 范围

本文是 `using-sacha / 显式生产 Role / 显式 Clarify` 主 workflow 入口、独立显式 Feedback task、接受/拒绝、重复抑制和入口授权边界的唯一 Runtime 权威。接受后的路由由 [Workflow Contract](workflow-contract.md) 定义；Human 可见提问与结果遵循 [Human Interaction Contract](human-interaction-contract.md)。

Intake platform-neutral、project-neutral。Runtime discovery 归 Adapter；入口 procedure 归 `using-sacha`；项目知识仍归 Project Integration 或 Domain Skill。

## 2. 最小加载

Runtime 常驻发现面只需要 `using-sacha` metadata。Skill 触发后可读取本文；Human 接受前不得仅为 Sacha 路由加载 Workflow Contract、Artifact Protocol、Project Integration 或生产 Role。

`L0 Local Direct` 允许 metadata、入口 Skill 与本文，但不进入生产 Sacha lifecycle，不生成 Goal、Artifact 或 Handoff。

## 3. 入口判断

- `L0 Local Direct`：目标、Scope、授权与验收足够明确，当前 context 可安全完成，且没有会改变执行方式的 candidate 事实；无论复杂度、文件数和耗时，默认直接执行。
- `D0 candidate`：没有 Planner Gate 事实，但持久 owner、跨 context 恢复或正式编排会实质改变执行方式，且 Human 尚未选择是否进入 Sacha。
- `Planner candidate`：目标、Scope、Acceptance、owner 或路径存在实质不确定性；已有事实预计实施前需要关键 Human 澄清、先冻结/持久化可执行 Spec，或存在实质方案、难回退跨 owner 决策、breaking migration。

- Planner、Executor、Reviewer 接受 Human 直接调用。
- Clarify 接受 Human 显式窄授权，或由 active Planner 路由。
- Feedback 接受 Human 在另一个真实任务手动提交的流程问题、使用反馈、插件开发建议或能力想法。
- Manager 和 document-project 只接受内部 owner 路由；Reviewer Gate 与 Manager Gate 由 Workflow 在接受后判断。

复杂度、文件数量、耗时、多平台、持续验证、Skill/plugin 关键词或 plugin 已安装不构成入口事实。

## 4. 入口决定

- 初次判断及 Direct 执行期间都必须检查语义转折。诊断演变为设计/修改、授权扩到新 owner/平台，或新增 API 形态、owner、fallback/行为模式决策、Spec 消费者、跨 context 恢复需求时，只有这些事实会改变执行方式才重评估。
- 同一 objective 或表面 Scope 名称未变，不得压过已改变的 Acceptance、风险、授权、owner、实现边界或交付模型。没有第 3 节 candidate 事实时保持 L0。
- 自动感知到 candidate 时，只询问一次是否进入 Sacha，并按 Human Interaction Contract 说明新增能力、成本、执行影响与推荐。
- Human 接受后，当前 root owner 按需加载 Workflow Contract、当前 Adapter、confirmed Project Integration 与目标 Role。
- Human 拒绝后按当时事实保持 L0；同一 candidate 不得重复推销或创建 Sacha Artifact。实质变化形成新 candidate 时可再推荐一次。
- reference、日志、进度、非语义文案或仅估算变化不触发重问。
- 重复抑制只依赖当前 context 或正式恢复证据；不得新增跨会话 Registry。

| Human 输入 | 授权范围与下一路由 |
| --- | --- |
| 显式 `using-sacha`、明确要求使用 Sacha，或直接调用 Planner、Executor、Reviewer | 接受当前 objective/Scope 的 Sacha 路由；当前 owner 按 Workflow Contract 推进 |
| 显式 Clarify | 授权当前 Clarify owner 在窄 Scope 内澄清并管理一个有界只读研究 helper；多个研究就绪单元可按 Manager Gate 协调 |
| active Planner 路由 Clarify | 沿用既有 Sacha acceptance 与 owner，结果返回 Planner |
| 显式 Setup Project | 只授权本次项目配置 Scope；后续开发目标重新判断入口 |
| 在另一个真实任务显式调用 Feedback | 授权来源任务围绕具体反馈目标有界只读调查，并查询、复用或创建唯一反馈目标任务；Human 可提供原任务、项目或 evidence reference；目标任务另行核对写入与外部动作授权 |
| 直接调用 Manager 或 document-project | 返回当前 objective 给 `using-sacha` 或原 owner；两者分别由 Manager Gate 与 Workflow 收尾候选路由 |

入口授权只作用于当前 objective/Scope。workspace 写入、安装、Git、发布、远程资源、权限、高影响动作和 Planner 后续形成的实质方案分别取得对应授权；安全与工程规则持续生效。

Hook 可以由 Runtime 在另行授权后预加载环境信息，但不得接受 Sacha、替代 `using-sacha`、扩大授权或成为正确性与恢复前提。
