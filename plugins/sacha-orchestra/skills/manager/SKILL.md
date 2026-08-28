---
name: manager
description: 主任务已接受 Sacha 或显式 Explore 且 Manager Gate 打开时使用；其他上下文、直接调用或 Gate 关闭时不接管。
---

# Manager（协调）

## 功能

执行 [Coordination Contract](../../core/coordination-contract.md) 定义的协调流程，为调用节点评估、拆分、建立依赖与就绪条件、执行单层派发或给出串行结论、必要等待、归并并返回。

## 输入与首查

1. 按[术语合同](../../core/terminology-contract.md)核对当前上下文是主任务，并已有 [Intake Contract](../../core/intake-contract.md) 的 Sacha 接受状态或显式 Explore 窄授权，再按 [Workflow Contract](../../core/workflow-contract.md) 核对 Manager Gate。
2. 用户直接调用 Manager 时，把当前目标返回 `using-sacha` 或当前流程节点判断。委派 Agent 调用时返回协调请求；其他非主任务上下文停止并返回入口缺口。Manager Gate 关闭时返回调用节点。

## 动作顺序

1. 调用 Coordination Contract，先按 Owner、输入、输出和验证入口识别可独立单元，再完成拆分、依赖、就绪判定、路由要求、单层派发、等待、取消、归并、去重和返回；不能独立完成或验证的局部动作留给调用节点。
2. 同一普通任务、迁移目标任务与 Explore 共用同一算法；当前波次存在应派发的已就绪单元时，Manager 必须按 Coordination Contract 读取当前 Runtime Adapter，由主任务取得逐单元完整首次创建参数并原样派发；一个单元因上下文隔离而派发时也继续由 Manager 管理剩余依赖。未取得参数时按 Coordination Contract 返回偏差。当前 Adapter 映射了观测能力时，只在波次状态已经提交后记录，记录失败不改变调度结论。

## 输出

- 向调用节点返回串行结论、派发状态、聚合事实、`delta`、阻塞/风险和 reference。
- 实现返修返回原 Executor，研究结果返回原 Explore；活跃 Planner 继续核对 Spec 就绪条件。

## 停止与禁止边界

- Manager 是控制面，只在主任务内运行；委派 Agent 遵守单层派发。
- Planner 设计、Executor 写入、Reviewer 裁决和 Human 授权由各自 Owner 处理。
- 协调过程使用现有 Runtime 传输，不创建跨会话注册表、后台服务或自动反馈任务。
