---
name: clarify
description: 显式澄清，或已接受 Sacha 且 Planner Gate 仍缺目标、验收/边界时使用；产出 Planner 可用事实与未决项。目标清晰时不用；不拥有 Scope、授权或裁决。
---

# Clarify（需求澄清）

## 工作流

1. 先自行核对可从代码、项目规则和已提供 Domain Skill 获得的事实，只向 Human 询问无法自行推出且会改变方案的决策。
2. 根据当前输入收敛目标、调查现状或挑战已有方案；不要先让 Human 选择“澄清模式”。
3. 每轮只问会改变方案的最少技术问题，给出推荐和主要取舍；互相独立的问题可同轮提出。
4. 分清已验证事实、Human 决定、假设和未决项。事实冲突时指出证据，不替用户静默选择。
5. 必要事实不可低成本取得时，给一个有界只读 helper 明确问题、范围、预期证据和停止条件；多个研究单元或正式恢复才按 [Coordination Contract](../../core/coordination-contract.md) 交给 Manager。
6. Planner 已能明确目标、边界和验收时立即停止，只返回事实、已确认决定、唯一未决项和 locator。

## 边界

- 不选择 Gate，不冻结 Scope，不授予权限，不创建 Handoff，不实施或验收。
- 研究默认只读；结果不授予规划、Review、写入或外部动作权限。
- 不硬编码项目文档路径、领域 provider 或 Artifact 结构；按 Project Integration 和 Artifact Protocol 使用已有载体。
- 无法澄清的实质决策返回 Planner/Human，不用更多问题掩盖阻塞。
