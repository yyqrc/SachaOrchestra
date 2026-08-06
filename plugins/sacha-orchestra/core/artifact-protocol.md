# Artifact Protocol

> Contract Version: 6
> Status: Normative Core contract

## 1. 范围与权威

本文是 Artifact 语义、权威边界和 Handoff 必要语义的唯一权威。入口/Role/Gate 由 [Intake Contract](intake-contract.md) 与 [Workflow Contract](workflow-contract.md) 定义。
Review 与 return 分别由 [Assurance Contract](assurance-contract.md)、[Coordination Contract](coordination-contract.md) 定义。

保存路径由 Project Integration/Adapter 决定，不改变语义、字段或权威：

- Spec Artifact：目标、Scope、冻结决策、允许边界与验收；
- 澄清决定记录：在 Spec 形成前保存后续会消费的已确定决定；多轮、分支或上下文压缩需要恢复时，按需保存能回到原问题的最小澄清锚点与 frontier；疑似跨任务术语可作为项目 context 候选保留到 closeout 复核；
- 真实文件、外部状态、diff 和命令原始输出：实现与验证事实；
- Execution Report：事实与证据的可恢复索引；
- Review Artifact：Reviewer 判断；
- Handoff：最小恢复信息，不是完成证据、固定表格或独立状态系统。

报告与原始事实冲突时以原始事实为准并记录冲突。改变批准 Scope 必须修订 Spec 并取得所需授权，不能由报告静默覆盖。

## 2. 渐进且最小

| Artifact | 生成条件 | 最小内容 |
| --- | --- | --- |
| 最终任务记录 | 同一 context 简单完成 | 修改、验证、失败/未验证与剩余风险 |
| 澄清决定记录 | Spec 形成前已有确定决定供规划消费，或多轮/分支/压缩恢复需要保留澄清锚点 | 已确认决定、依据/约束、未决项与 reference；恢复确需时增加原始问题、当前关注点、暂存思路，以及尚未探索/解决的实质分支、依赖与关键排除依据；疑似跨任务术语按需记录定义、排除含义、证据、边界、任务外消费者和 Unknown |
| Spec Artifact | 持久 Scope、批准方案或跨 context 恢复 | Scope、决策、Acceptance、暂停/回退 |
| Execution Report | 续跑、证据索引或正式 Review | 实际 delta、验证、偏差、风险、reference、恢复入口 |
| Review Artifact | 正式 Review | Findings、Verdict、证据缺口、下一路由 |

没有消费者就不创建 Artifact。澄清决定记录使用项目既有载体；无约定且确有规划或恢复消费者时可用任务目录中的 `decisions.md`，不保存完整对话、调查流水账或完整决策树。恢复 frontier 只保留会改变方案且压缩后必须重建的最小分支信息，旧项确认或失效后原位压缩。Planner 读取它形成 Spec 并沿用已确认术语，批准后 Spec 成为唯一执行基线；两者不要求合并为同一文件，也不建立并行状态系统。项目 context 候选不因记录而成为项目事实，只有 closeout 基于最终实现/Review 证据复核且文档授权覆盖后才可进入项目 `CONTEXT.md`。
一个事实只写一次：Spec 只吸收执行所需的冻结决定，不重抄澄清过程；Goal/Scope/AC/Handoff 不复述同一决策；Report/Review 不重抄上游或原始日志，只给消费者所需 delta 与 reference。Human Review Focus 和当轮最终建议清单直接出现在回复中，不因沟通收口写入业务 Spec。
长度按风险和恢复需要自适应，不为格式拆文件。失败、未验证、授权、风险、Evidence 与 Entry Condition 不得为压缩而删除。

Execution Report 只在恢复、证据索引或正式 Review 有消费者时随任务形成，保存到 Spec/任务约定的 Artifact 位置。Project Documentation 不属于本协议的任务 Artifact：`change-archive`/done 文档面向变更后的项目消费者，`system-guide` 面向长期使用与维护，二者写入 Project Documentation root；项目 `CONTEXT.md` 只保存跨任务稳定术语和约束，写入 Project Integration 指定的 Project Context path。它们都不能复制任务状态或把 Execution Report 当作发布正文，具体候选与写入授权由 Workflow closeout 和 `document-project` 决定。

## 3. Handoff

只有正式跨 Role 或恢复 consumer 无法从现有 Scope、Artifact 和原生 transport 安全继续时才写 Handoff。它按需提供：

- route identity：稳定 Task/Scope revision 与 Source/Target/owner 中 transport 未携带且消歧必需的部分；
- outcome：已完成且可核实的结果；
- scope：批准 Spec/用户目标的 reference；
- artifact/evidence：恢复材料与真实状态 reference；
- risk/entry：偏离、未验证、风险及开始前必须满足的授权、状态和验证。

名称、顺序和载体由消费者决定；空内容省略，不写 `None`。面向 Human 时用自然技术说明，不展示无助于决策或恢复的字段。确有领域或 Runtime 消费方时可增加 namespaced extension；扩展不得重定义权威或授权。

## 4. 恢复规则

- Handoff 嵌入承载 Artifact/消息，不单建 Handoff 文件。
- reference 必须稳定、可达，可移植 Artifact 优先相对位置或环境中立标识。
- 同环境恢复确需绝对路径时标记 `non-portable`，可用时同时给出相对或环境中立 reference；Runtime 实例 ID、模型、界面状态和内部存储标识只进入 runtime-only transport。
- Outcome、报告或 Role 自报不能替代 Evidence References 指向的原始证据。
- 返修/重规划保持 Task ID，除非 Human 建立新 Scope。
- Target 核对可用 route identity、Scope、Artifact/Evidence 和 Entry Condition；不满足时暂停或报告部分完成。
- 恢复不得另建与 Spec、Execution Report、Review 并行的权威状态。
