# Artifact Protocol（取样片段）

## 2. 渐进且最小

| Artifact | 生成条件 | 最小内容 |
| --- | --- | --- |
| 最终任务记录 | 同一上下文简单完成 | 修改、验证、失败/未验证与剩余风险 |
| 探索决定记录 | Spec 形成前已有确定决定供规划消费，或多轮/分支/压缩恢复需要保留探索锚点 | 已确认决定、依据/约束、未决项与 reference；恢复确需时增加原始问题、当前关注点、暂存思路，以及尚未探索/解决的实质分支、依赖与关键排除依据；疑似跨任务术语按需记录定义、排除含义、证据、边界、任务外消费者和 `Unknown` |
| Spec Artifact | 持久 Scope、批准方案或跨上下文恢复 | 目标项目实施规格；内容格式见第 2.1 节 |
| Execution Report | 续跑、证据索引或正式 Review | 实际变更（`delta`）、验证、偏差、风险、reference、恢复入口 |
| Review Artifact | 正式 Review | 问题、裁决结果（Outcome）、证据缺口、下一路由 |

### 2.1 Spec Artifact

Spec Artifact 面向目标项目的 Human、Executor 和 Reviewer。只给三者项目规则、项目事实和 Spec 时，必须仍能理解目标、边界、方案与验收；移除 Sacha 上下文不得改变其技术含义或可执行性。
