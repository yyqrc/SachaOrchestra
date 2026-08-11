---
name: feedback
description: 当 Human 在另一个真实任务中显式提交流程问题、使用反馈或插件开发想法时使用；有界只读调查并单向移交唯一反馈目标任务。
---

# Feedback（插件反馈）

## 功能

执行 [Coordination Contract](../../core/coordination-contract.md) 定义的 Feedback 单向 Owner 转移：Human 在另一个真实任务手动调用，来源任务有界只读调查、定位并交付唯一反馈目标任务后结束。

## 输入与首查

1. 输入为 Human 在另一个真实任务中显式提交的流程问题、使用反馈、插件开发建议或能力想法。该调用授权来源任务执行有界只读调查和一次 Owner 转移。
2. 读取 [Workflow Contract](../../core/workflow-contract.md)、Coordination Contract 和当前 Adapter 的调查/Owner 转移映射。
3. 围绕具体反馈目标核对插件现状，以及 Human 已提供的任务、项目或原始证据。

## 动作顺序

1. 按 Coordination Contract 的反馈身份、可恢复状态与去重规则筛选目标任务。无法消歧时读取 [Human Interaction Contract](../../core/human-interaction-contract.md) 并询问唯一关键差异。
2. 通过 Adapter 复用合法目标任务；无可复用目标时，在本次调用授权内创建唯一目标任务。
3. 来源任务向目标任务交付反馈目标、必要规则/证据 reference 和原生目标任务 reference，然后结束。
4. 精确重复返回既有目标任务 reference；目标任务按 [Intake Contract](../../core/intake-contract.md) 执行普通任务流程。

## 输出

- 向 Human 交付目标任务 reference、已核实事实和未验证边界；格式遵循 [Human Interaction Contract](../../core/human-interaction-contract.md)。
- 来源任务在交付 reference 后结束，不等待或转述目标任务终态。

## 停止与禁止边界

- 显式调用只授权来源任务的调查与 Owner 转移；目标任务独立核对方案、实施、Review 和外部动作授权。
- 来源任务保持只读；辅助 Agent 只补证，目标工作区/上下文承担后续 Owner 职责。
- 没有安全的 Owner 转移路径时保留现场、精确错误和恢复入口并停止。
