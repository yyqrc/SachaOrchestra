---
name: clarify
description: 显式澄清、调查或方案打磨，或 Planner 仍缺目标、边界、验收/实质决定时使用；目标清晰时不用，不拥有 Scope、授权或裁决。
---

# Clarify（需求澄清）

## 工作流

1. 仅响应 Human 显式调用，或 active Planner 对未收口的目标、Scope/Non-goals、验收或实质决定的显式路由；不是 Intake 默认阶段。
2. 先查代码、规则、Domain/项目 Skill；有 context locator 时只查相关 `CONTEXT.md`，不遍历历史任务目录。只问无法自行推出且会改变方案的决定。
3. 按输入组合 `brainstorm`、`survey`、`grill`；它们不是让 Human 选择的模式、固定阶段或顺序。用反例和具体场景核对前提、生命周期、恢复、兼容与可证伪验收。
4. 维护不展示的有界挑战图。一个问题锁定一个决定并给推荐/取舍；独立问题可编号同问，依赖问题先问上游。技术事实先核对，猜想与推测只作调查线索。
5. Human 要解释时先调查真实来源再解释，以概要、数据流、locator 渐进回答，再回到刚才尚未解决的决策。术语或证据冲突先展示差异，不静默选边。
6. 必要事实难以取得时派一个有界只读 helper；多个研究单元或正式恢复才按 [Coordination Contract](../../core/coordination-contract.md) 交 Manager。
7. 多未决项、打断或压缩风险时复用澄清锚点；无约定时用最小 `decisions.md`。只记原始问题/目标、决定、当前焦点、阻塞性未决项、暂存的新思路、locator 与最小可恢复 frontier。
8. 恢复后处理依赖最靠前的未决项。新思路不能静默替换澄清锚点；只能解决/新增未决项或暂存，改变目标、Scope 或验收则返回 Planner/Human。
9. 已确认术语写决定记录；稳定项目术语只作 project-context 候选，记录定义、排除含义、证据、边界、消费者和 Unknown，交 closeout 复核。
10. 退出前确认无尚未询问的重要分支，关键前提已解决、暂缓、路由或阻塞。Human 只说“够了”“开始吧”但仍有阻塞性未决项时给最小清单。

## 边界

- 不选择 Gate，不冻结 Scope，不授予权限，不创建 Handoff，不实施或验收。
- 研究默认只读；结果不授予规划、Review、写入或外部动作权限。
- 按 Project Integration 与 Artifact Protocol 使用 locator/载体；决定记录不冻结 Scope、不替代 Spec，context 候选不授权文档写入。
- 不把工作意图拆成 Role、Gate、Skill 或固定产物；领域 Skill 可提供事实与压力场景，不拥有 Human 对话和退出判断。
- 无法澄清的实质决策返回 Planner/Human，不用更多问题掩盖阻塞。
