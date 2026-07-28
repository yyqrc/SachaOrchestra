---
name: clarify
description: 显式澄清，或已接受 Sacha 且 Planner Gate 仍缺目标、验收/边界时使用；产出 Planner 可用事实与未决项。目标清晰时不用；不拥有 Scope、授权或裁决。
---

# Clarify（需求澄清）

Clarify 是 Planner 的可选输入能力，不是生产 Role。

## 工作流

1. 先自行核对可从代码、项目规则和已提供 Domain Skill 获得的事实，只向 Human 询问无法自行推出且会改变方案的决策。
2. 按输入状态选择一种模式：
   - `brainstorm`：从模糊想法收敛目标、候选方案和取舍；
   - `survey`：调查现状并形成可比较事实；
   - `grill`：检查已有方案的边界、反例和可证伪验收。
3. 每轮只询问当前依赖已满足的决策，并给出推荐及主要取舍；相互独立的问题可同轮提出。
4. 明确区分已验证事实、Human 决策、假设和未决项。出现冲突时指出证据与输入差异，不替用户静默选择。
5. 当前 context 无法低成本取得必要事实时，形成 research question、read scope、expected evidence、依赖和停止条件。一个有界只读 helper 足够时直接管理；多个单元、依赖图、并行生命周期或正式恢复才按 [Coordination Contract](../../core/coordination-contract.md) 交给 Manager。
6. 当 Planner 已能唯一表达目标、边界和验收时立即停止。输出精简的事实、已确认决策、未决项和 evidence locator，由 Planner 决定是否持久化。

## 边界

- 不选择 Gate，不冻结 Scope，不授予权限，不创建 Handoff，不实施或验收。
- Research Packet 默认只读；研究结果不授予规划、Review、写入或外部动作权限。
- 不硬编码项目文档路径、领域 provider 或 Artifact 结构；按 Project Integration 和 Artifact Protocol 使用已有载体。
- 无法澄清的实质决策返回 Planner/Human，不用更多问题掩盖阻塞。
