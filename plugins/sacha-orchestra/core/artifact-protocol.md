# Artifact Protocol

> Contract Version: 2
> Status: Normative Core contract

## 1. 范围与权威

本文是 Artifact 语义、权威边界和九个稳定核心字段 Handoff Envelope 的唯一权威。入口/Role/Gate 由 [Intake Contract](intake-contract.md) 与 [Workflow Contract](workflow-contract.md) 定义；Review 与 return 分别由 [Assurance Contract](assurance-contract.md)、[Coordination Contract](coordination-contract.md) 定义。

保存路径由 Project Integration/Adapter 决定，不改变语义、字段或权威：

- Plan Artifact：目标、Scope、冻结决策、允许边界与验收；
- 真实文件、外部状态、diff 和命令原始输出：实现与验证事实；
- Execution Report：事实与证据的可恢复索引；
- Review Artifact：Reviewer 判断；
- Handoff Envelope：最小恢复协议，不是完成证据或独立状态系统。

报告与原始事实冲突时以原始事实为准并记录冲突。改变批准 Scope 必须修订 Plan 并取得所需授权，不能由报告静默覆盖。

## 2. 渐进且最小

| Artifact | 生成条件 | 最小内容 |
| --- | --- | --- |
| 最终任务记录 | 同一 context 简单完成 | 修改、验证、失败/未验证与剩余风险 |
| Plan Artifact | 持久 Scope、批准方案或跨 context 恢复 | Scope、决策、Acceptance、暂停/回退 |
| Execution Report | 续跑、证据索引或正式 Review | 实际 delta、验证、偏差、风险、locator、恢复入口 |
| Review Artifact | 正式 Review | Findings、Verdict、证据缺口、下一路由 |

没有消费者就不创建 Artifact。一个事实只写一次：Plan 不保存调查流水账，Goal/Scope/AC/Handoff 不复述同一决策；Report/Review 不重抄上游或原始日志，只给 delta 与 locator。Plan `200` 行/`12000` 字符、Execution Report `40` 行/`5000` 字符是默认 soft budget；按消费者、风险和恢复需要自适应，不为硬限额拆分文件。失败、未验证、授权、风险、Evidence 与 Entry Condition 不得为压缩而删除。

## 3. Handoff Envelope

每次正式跨 Role 交接按以下名称和顺序包含九个核心字段：

1. `Task ID`
2. `Source Role`
3. `Target Role`
4. `Outcome`
5. `Scope Reference`
6. `Artifact References`
7. `Evidence References`
8. `Deviations and Open Risks`
9. `Entry Condition`

`Task ID` 贯穿返修；Source/Target 是交接双方；Outcome 只写已完成可核实结果；Scope 指向批准 Plan/用户目标；Artifact 用于恢复；Evidence 指向真实状态；Deviations 保留偏离、未验证和风险；Entry Condition 写明开始前必须满足的授权、Artifact、状态与验证。

空核心字段写 `None`，不得省略、改名、拆分或用叙事掩盖空值。确有领域或 Runtime 消费方时可在九字段后增加可选 `Extensions`；扩展必须 namespaced，不得重定义核心字段、权威或授权，未知扩展可安全忽略。

## 4. 恢复规则

- Envelope 嵌入承载 Artifact/消息，不单建 Handoff 文件。
- locator 必须稳定、可达，可移植 Artifact 优先相对位置或环境中立标识。
- 同环境恢复确需绝对路径时标记 `non-portable`，可用时同时给出相对或环境中立 locator；Runtime 实例 ID、模型、界面状态和内部存储标识只进入 runtime-only transport。
- Outcome、报告或 Role 自报不能替代 Evidence References 指向的原始证据。
- 返修/重规划保持 Task ID，除非 Human 建立新 Scope。
- Target 核对 Task ID、Scope、Artifact/Evidence 和 Entry Condition；不满足时暂停或报告部分完成。
- 恢复不得另建与 Plan、Execution Report、Review 并行的权威状态。
