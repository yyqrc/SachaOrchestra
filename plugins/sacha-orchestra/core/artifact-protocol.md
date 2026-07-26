# Artifact Protocol

> Contract Version: 1
> Status: Normative Core contract

## 1. 范围与权威

本文是 Artifact 语义、权威边界和九字段 Handoff Envelope 的唯一权威。Role、Gate、生命周期和路由由 [Workflow Contract](workflow-contract.md) 定义。

保存路径由 Project Integration 或 Adapter 决定，不得改变本文语义、字段或权威顺序。

权威按信息类型划分：

- Plan Artifact：目标、Scope、冻结决策、允许边界和验收标准；
- 真实文件、外部状态和命令原始输出：实现与验证事实；
- Execution Report：事实和证据的可恢复索引；
- Review Artifact：Reviewer 判断；
- Handoff Envelope：最小恢复协议，不是完成证据或独立状态系统。

报告与原始事实冲突时以原始事实为准并记录冲突。实现需要改变批准 Scope 时，必须修订 Plan 并重新获得所需授权，不能由报告静默覆盖。

## 2. 渐进 Artifact

| Artifact | 生成条件 | 内容 |
| --- | --- | --- |
| 最终任务记录 | 同一 context 内简单完成 | 修改、验证和剩余风险 |
| Plan Artifact | 需要持久 Scope、批准方案或跨 context 恢复 | 目标、Scope、决策、暂停条件和验收 |
| Execution Report | 需要续跑、证据索引或正式 Review | 实际修改、证据、验证、偏离和恢复入口 |
| Review Artifact | 正式 Review | 独立判断、发现、证据可信度和下一路由 |

简单任务不得为形式完整创建无消费者的 Artifact。这些名称是通用约定，不要求固定目录。

## 3. Handoff Envelope

每次正式跨 Role 交接必须按以下名称与顺序包含九个字段：

1. `Task ID`
2. `Source Role`
3. `Target Role`
4. `Outcome`
5. `Scope Reference`
6. `Artifact References`
7. `Evidence References`
8. `Deviations and Open Risks`
9. `Entry Condition`

字段语义：

- `Task ID`：贯穿规划、执行、Review 和返修的稳定标识；
- `Source Role` / `Target Role`：交接双方；
- `Outcome`：Source 已完成且可核实的结果；
- `Scope Reference`：批准 Plan 或明确用户目标的稳定引用；
- `Artifact References`：恢复所需 Artifact；
- `Evidence References`：真实文件、状态或原始输出的 locator；
- `Deviations and Open Risks`：偏离、未解决问题、未验证项和残余风险；
- `Entry Condition`：Target 开始前必须满足的授权、Artifact、状态和验证条件。

空字段写 `None`，不得省略、改名、拆分或增加合同字段。

## 4. Envelope 与恢复规则

- Envelope 嵌入承载它的 Artifact 或交接消息，不单独创建 Handoff 文件。
- 引用必须稳定、可达，并优先使用相对位置或环境中立标识。
- Envelope 不承载 Runtime 实例 ID、模型、界面状态、本机绝对路径或内部存储标识。
- Outcome、报告状态和 Role 自报不能替代 Evidence References 指向的原始证据。
- 返修和重规划保持同一 Task ID，除非 Human 明确建立新 Scope。
- Target 必须核对 Task ID、Scope、Artifact/Evidence locator 和 Entry Condition；条件不满足时暂停或报告部分完成。
- 恢复不得另建与 Plan、Execution Report 或 Review Artifact 并行的权威状态。
