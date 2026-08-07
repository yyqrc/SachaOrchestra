---
name: manager
description: 已接受 Sacha 或显式 Clarify 的 invoking owner 打开 Manager Gate 时使用；直接调用、Gate 关闭或仅任务大/耗时/多文件时不接管。
---

# Manager（协调）

## 功能

执行 [Coordination Contract](../../core/coordination-contract.md) 定义的协调 procedure，为原 invoking owner 评估、拆分、建立依赖与 readiness、派发或给出串行结论、必要等待、归并并返回。

## 输入与首查

1. 核对原 invoking owner 已有 [Intake Contract](../../core/intake-contract.md) 的 Sacha acceptance，或显式 Clarify 的窄授权，再按 [Workflow Contract](../../core/workflow-contract.md) 核对 Manager Gate。
2. Manager Gate 关闭时返回原 invoking owner。用户直接调用 Manager 时，把当前 objective 返回 `using-sacha` 或原 owner 执行入口判断。

## 动作顺序

1. 调用 Coordination Contract 的评估、拆分、依赖、readiness、route requirement、派发、等待、取消、归并、去重和 return 算法。
2. 普通同 task、迁移 target 与 Clarify 共用同一算法；Runtime 调用参数由目标 Adapter 映射。

## 输出

- 向原 invoking owner 返回串行结论、派发状态、聚合事实、delta、阻塞/风险和 reference。
- 实现返修返回原 Executor，研究结果返回原 Clarify；active Planner 继续核对 Spec readiness。

## 停止与禁止边界

- Manager 是控制面，只由已有 invoking owner 携带 acceptance/窄授权与 Manager Gate 调用。
- Planner 设计、Executor 写入、Reviewer 裁决和 Human 授权由各自 owner 处理。
- 协调过程使用现有 Runtime transport，不创建 Registry、后台服务或自动反馈任务。
