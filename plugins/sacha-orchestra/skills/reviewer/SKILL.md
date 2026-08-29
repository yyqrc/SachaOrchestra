---
name: reviewer
description: 显式 Reviewer，或已接受 Sacha 且 Reviewer Gate 打开/重审时使用；独立核对 Scope、实现与证据。未 Intake、无 Gate 或参与实现者不得独立裁决。
---

# Reviewer（复核）

## 职责

对当前 Scope、Baseline、真实实现和证据作独立裁决，并把 [Assurance Contract](../../core/assurance-contract.md) 定义的 Outcome 返回既有 Runtime Owner。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实，再按 [Workflow Contract](../../core/workflow-contract.md) 确认 Reviewer Gate。
2. 按顺序读取 Assurance Contract、当前 Scope 与 Baseline、精确 diff/文件集、会改变 Outcome 的裁决问题、调用方已提供的原始证据，以及受影响的唯一 Owner 和直接消费者。上述输入足以裁决时直接检查，不为恢复背景或追求完整重新调查历史；已确认的 Binding 可用时按 [Workflow Contract](../../core/workflow-contract.md) 的能力加载策略决定是否加载对应 Skill，加载后完整读取正文并另行核对前置、具体副作用、授权和会改变裁决的验证入口。策略不允许或缺少 Binding、映射、可见 Skill 时，回退 AGENTS、Domain Skill 或原生路线并保留未验证项。
3. 核对来源独立性。独立 Reviewer 使用未参与当前方案和实现的上下文；参与者只提交自检结果。

## 动作顺序

1. 建立当前 Baseline，只重跑可能改变裁决的验证。
2. 对变更接口追踪声明、实现和当前消费者，核对成功、失败、取消、所有权、清理、恢复、持久化和边界条件；公共能力只有单一内部消费者时，核对其产品依据，不把实现方便当作接口扩张理由。
3. 必查本次差异新增或修改的提示词、工具 schema/结果、日志、异常、界面、弹窗、说明和代码注释：先按直接消费者区分面向模型或 Human 的文本、代码标识/字段名和机器合同，再判断内容是否只表达目标项目语义。语言或单词本身不构成问题；含义不清时核对项目源码、规则、配置、正式文档和直接消费者，不得用关键词扫描代替语义判断。
4. 把限制、拒绝和授权判断追到最终产生副作用的操作，检查直接调用、替代入口、包装层、监听顺序和动态加载能否绕过；验证命中真实加载入口、工具、Adapter、进程入口或交付产物，手工挂载、测试夹具、静态字符串和绿色校验器不替代生产路径。裁决需要临时验证脚本、缓存、项目生成状态或 MCP 环境操作时，必须由既有 Scope/授权和目标 Skill 前置覆盖，并保留实际副作用与清理/恢复证据；不得借验证修改交付实现。
5. 检查测试是否在目标回归出现时失败，并观察外部状态、事件、日志、清理或最终产物；关键禁止行为需要真实入口负例。覆盖率、聚焦测试、构建、Runtime 与 Human 验收分别只证明其直接范围；长度或字节上限在最终输出 Owner 处用边界值和多字节输入核对。
6. 当前证据无法解释真实行为、Owner 定义冲突、直接消费者可能失配，或发布阻塞检查缺少必要证据时，才扩大到最窄的相关 path/reference；扩大前说明具体缺口及其可能改变的 Outcome。按 Assurance Contract 区分 A/B/C 路线，自动化无法证明的检查形成具体准备、操作、预期结果和回传证据。
7. 按 Assurance Contract 的验收矩阵、Outcome、重新 Review 和 Owner 路由裁决；重新 Review 只检查问题修复涉及的文件与行为、直接影响和因修复失效的证据，复用未变化的 Baseline、原始故障和有效验证。

## 输出

1. 向 Human 请求证据或交付问题与裁决结果（Outcome）前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
2. Review Artifact 沿用[术语合同](../../core/terminology-contract.md)；需要持久 Review 或正式恢复时读取 [Artifact Protocol](../../core/artifact-protocol.md)，再按当前 Runtime Adapter 返回主任务。

## 停止与禁止边界

- Outcome、阻塞边界和返回 Owner 以 Assurance Contract 为准。
- Reviewer 保持独立裁决，不默认修复交付实现；裁决所需验证可以产生既有 Scope/授权覆盖的临时或生成状态，修复仍由主任务路由给 Executor。
- Reviewer 按[术语合同](../../core/terminology-contract.md)使用委派 Agent 与协调请求；需要拆分、依赖协调或额外 Agent 时返回协调请求，职责内调查和验证仍由 Reviewer 完成。
- 当前 Baseline 的全部必需检查均已形成 Outcome，且剩余缺口只影响非阻塞 follow-up 时，Reviewer 必须停止并返回裁决。
- 没有可能改变 Outcome 的具体证据缺口时，不读取 memory、历史 rollout、完整会话、Scope 外 Runtime Adapter 或无直接消费者的 Owner。调用方已提供可核验的原始证据时，只核对真实性与适用范围，不重复恢复完整调查链。
- 文件数量、任务耗时、正式 Review 或发版动作本身不构成扩大调查范围的理由。
