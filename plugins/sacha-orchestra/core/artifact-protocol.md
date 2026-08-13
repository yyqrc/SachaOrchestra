# Artifact Protocol（产物协议）

> 合同版本：7
> 状态：规范性 Core 合同

## 1. 范围与权威

本文是 Artifact 生成条件、最小内容、权威关系和恢复规则的唯一权威。Artifact、Spec Artifact、澄清决定记录、Execution Report、Review Artifact 与 Handoff 的定义见[术语合同](terminology-contract.md)；入口/Role/Gate 由 [Intake Contract](intake-contract.md) 与 [Workflow Contract](workflow-contract.md) 定义，Human 可见交互由 [Human Interaction Contract](human-interaction-contract.md) 定义。
Review 与返回分别由 [Assurance Contract](assurance-contract.md)、[Coordination Contract](coordination-contract.md) 定义。

保存路径由 Project Integration/Adapter 决定，不改变语义、字段或权威。真实文件、外部状态、文件差异（diff）和命令原始输出仍是实现与验证事实；Artifact 只索引或承载消费者需要的信息。

报告与原始事实冲突时以原始事实为准并记录冲突。改变批准 Scope 必须修订 Spec 并取得所需授权，不能由报告静默覆盖。

## 2. 渐进且最小

| Artifact | 生成条件 | 最小内容 |
| --- | --- | --- |
| 最终任务记录 | 同一上下文简单完成 | 修改、验证、失败/未验证与剩余风险 |
| 澄清决定记录 | Spec 形成前已有确定决定供规划消费，或多轮/分支/压缩恢复需要保留澄清锚点 | 已确认决定、依据/约束、未决项与 reference；恢复确需时增加原始问题、当前关注点、暂存思路，以及尚未探索/解决的实质分支、依赖与关键排除依据；疑似跨任务术语按需记录定义、排除含义、证据、边界、任务外消费者和 `Unknown` |
| Spec Artifact | 持久 Scope、批准方案或跨上下文恢复 | Scope、决策、Acceptance、暂停/回退 |
| Execution Report | 续跑、证据索引或正式 Review | 实际变更（`delta`）、验证、偏差、风险、reference、恢复入口 |
| Review Artifact | 正式 Review | Findings、Verdict、证据缺口、下一路由 |

Artifact 只在存在消费者时创建。澄清决定记录优先使用项目既有载体；无约定且存在规划或恢复消费者时使用任务目录中的 `decisions.md`。它只保存已确认决定、未决项、必要 reference 和压缩后必须重建的最小恢复边界，旧项确认或失效后原位压缩。

Planner 读取决定记录形成 Spec 并沿用已确认术语；批准后的 Spec 是唯一执行基线。项目上下文候选在收尾时基于最终实现/Review 证据复核，并在文档授权覆盖后进入项目 `CONTEXT.md`。

一个事实只写一次：Spec 只吸收执行所需的冻结决定；Goal/Scope/AC/Handoff 引用该决定；Report/Review 只提供消费者所需的 `delta` 与原始证据 reference。Human 审查关注点（Review Focus）和当轮最终建议清单按 Human Interaction Contract 直接交付。
长度按风险和恢复需要自适应，不为格式拆文件。失败、未验证、授权、风险、Evidence 与 Entry Condition 不得为压缩而删除。

Execution Report 在恢复、证据索引或正式 Review 存在消费者时随任务形成，并保存到 Spec/任务约定的 Artifact 位置。Project Documentation 的候选与授权由 Workflow 收尾和 `document-project` 决定，目标位置由 Project Integration 决定；Execution Report 继续留在任务 Artifact 位置。

## 3. Handoff

只有正式跨 Role 或恢复消费者无法从现有 Scope、Artifact 和原生传输安全继续时才写 Handoff。它按需提供：

- 路由标识：稳定的 Task/Scope 修订号，以及 Source/Target/Owner 中传输未携带但消歧必需的部分；
- 结果：已完成且可核实的结果；
- 范围：批准 Spec/用户目标的 reference；
- 产物/证据：恢复材料与真实状态 reference；
- 风险/进入条件：偏离、未验证、风险及开始前必须满足的授权、状态和验证。

名称、顺序和载体由消费者决定；空内容省略。Human 可见内容遵循 Human Interaction Contract。确有领域或 Runtime 消费方时可增加带命名空间的扩展；扩展沿用本协议的权威与授权边界。

## 4. 恢复规则

- Handoff 嵌入承载 Artifact/消息，不单建 Handoff 文件。
- reference 必须稳定、可达，可移植 Artifact 优先相对位置或环境中立标识。
- 同环境恢复确需绝对路径时标记 `non-portable`，可用时同时给出相对或环境中立 reference；Runtime 实例 ID、模型、界面状态和内部存储标识只进入仅供 Runtime 的传输。
- Outcome、报告或 Role 自报不能替代证据 reference 指向的原始证据。
- 返修/重规划保持 Task ID，除非 Human 建立新 Scope。
- Target 核对可用路由标识、Scope、Artifact/Evidence 和 Entry Condition；不满足时暂停或报告部分完成。
- 恢复继续使用 Spec、Execution Report 和 Review 作为权威状态。
