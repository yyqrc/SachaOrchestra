---
name: manager
description: 显式 Manager、已接受 Sacha 且 Manager Gate 打开，或显式 Clarify 的窄授权发现多个候选单元、依赖或恢复协调时使用；Gate 关闭或仅任务大/耗时/多文件时不接管。
---

# Manager（协调）

## 工作流

1. 核对显式 Manager、[Intake Contract](../../core/intake-contract.md) 的 Sacha acceptance，或显式 Clarify 的窄授权，再按 [Workflow Contract](../../core/workflow-contract.md) 核对 Manager Gate。当前 owner 发现多个候选单元、依赖或恢复协调时可直接调用，不要求已有 delegation 或预先拆分；Gate 关闭时返回原 invoking owner（Clarify、Planner、Executor 等），不得固定改路由到 Executor。
2. 按 [Coordination Contract](../../core/coordination-contract.md) 执行其中唯一的评估、拆分、依赖、readiness、route requirement、派发、等待、取消、归并、去重和 return 算法；普通同 task、迁移 target 与 Clarify 共用该算法。不要在 Skill 重复 assessment 字段、派发数量或宿主调用细节。
3. 只消费 Coordination 返回的串行结论、派发状态、聚合事实、delta、阻塞/风险和 reference，并返回原 invoking owner；实现返修回原 Executor，研究结果回原 Clarify，active Planner 继续核对是否足以冻结 Spec。Manager 不代替 Planner 设计、Executor 写入、Reviewer 验收或 Human 授权。

## 边界

- 不创建新的 Registry、后台服务或自动反馈任务。
