---
name: manager
description: 已接受 Sacha 或显式 Clarify 的调用 Owner 打开 Manager Gate 时使用；直接调用、Gate 关闭或仅任务大/耗时/多文件时不接管。
---

# Manager（协调）

## 功能

执行 [Coordination Contract](../../core/coordination-contract.md) 定义的协调流程，为原调用 Owner 评估、拆分、建立依赖与就绪条件、派发或给出串行结论、必要等待、归并并返回。

## 输入与首查

1. 核对原调用 Owner 已有 [Intake Contract](../../core/intake-contract.md) 的 Sacha 接受状态，或显式 Clarify 的窄授权，再按 [Workflow Contract](../../core/workflow-contract.md) 核对 Manager Gate。
2. Manager Gate 关闭时返回原调用 Owner。用户直接调用 Manager 时，把当前目标返回 `using-sacha` 或原 Owner 执行入口判断。

## 动作顺序

1. 调用 Coordination Contract 的评估、拆分、依赖、就绪判定、路由要求、派发、等待、取消、归并、去重和返回算法。
2. 同一普通任务、迁移目标任务与 Clarify 共用同一算法；Runtime 调用参数由目标 Adapter 映射。

## 输出

- 向原调用 Owner 返回串行结论、派发状态、聚合事实、`delta`、阻塞/风险和 reference。
- 实现返修返回原 Executor，研究结果返回原 Clarify；活跃 Planner 继续核对 Spec 就绪条件。

## 停止与禁止边界

- Manager 是控制面，只由已有调用 Owner 携带接受状态/窄授权与 Manager Gate 调用。
- Planner 设计、Executor 写入、Reviewer 裁决和 Human 授权由各自 Owner 处理。
- 协调过程使用现有 Runtime 传输，不创建跨会话注册表、后台服务或自动反馈任务。
