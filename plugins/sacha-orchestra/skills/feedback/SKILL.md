---
name: feedback
description: 当 Human 在另一个真实任务中显式提交流程问题、使用反馈或插件开发想法时使用；有界只读调查并单向移交唯一反馈目标任务。
---

# Feedback（插件反馈）

## 功能

执行 [Coordination Contract](../../core/coordination-contract.md) 定义的 Feedback 单向 Owner 转移：Human 在另一个真实任务手动调用，来源任务有界只读调查、定位并交付唯一反馈目标任务后结束。

## 输入与首查

1. 输入为 Human 在另一个真实任务中显式提交的流程问题、使用反馈、插件开发建议或能力想法。该调用授权来源任务执行有界只读调查和一次 Owner 转移。
2. 读取 [Intake Contract](../../core/intake-contract.md) 的显式 Feedback 授权、[Coordination Contract](../../core/coordination-contract.md) 的反馈标识、去重与 Owner 转移规则，以及当前 Adapter 的调查/转移映射；当前入口已经确定，不加载 Workflow Contract。
3. 围绕具体反馈目标核对插件现状，以及 Human 已提供的任务、项目或原始证据。

## 动作顺序

1. 把具体反馈目标、Human 已提供的来源 reference 和有界调查结果交给 Coordination Contract，消费其目标筛选、去重、创建或消歧结论；只有无法消歧时读取 [Human Interaction Contract](../../core/human-interaction-contract.md) 并询问唯一关键差异。
2. 通过当前 Adapter 执行 Coordination Contract 已确定的目标复用或创建，并按其要求交付原生目标任务 reference。
3. 来源任务的 Owner 转移、结束、重复输入与失败恢复均以 Coordination Contract 为准；本 Skill 不另定义第二套判断。

## 输出

- 向 Human 交付目标任务 reference、已核实事实和未验证边界；格式遵循 [Human Interaction Contract](../../core/human-interaction-contract.md)。
- 来源任务在交付 reference 后结束，不等待或转述目标任务终态。

## 停止与禁止边界

- 显式调用只授权来源任务的调查与 Owner 转移；目标任务独立核对方案、实施、Review 和外部动作授权。
- 来源任务保持只读；辅助 Agent 只补证，目标工作区/上下文承担后续 Owner 职责。
- 没有安全的 Owner 转移路径时保留现场、精确错误和恢复入口并停止。
