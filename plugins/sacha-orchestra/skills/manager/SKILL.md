---
name: manager
description: 主任务按 Workflow 进入协调时使用，统一安排实际工作单元的依赖、并发与归属并返回调用节点；不接受用户直接调用或委派 Agent 接管。
---

# Manager（协调）

## 功能

执行 [Coordination Contract](../../core/coordination-contract.md) 定义的协调流程，为调用节点评估、拆分、建立依赖与就绪条件、执行单层派发或给出串行结论、必要等待、归并并返回。

## 输入与首查

1. 消费 [Workflow Contract](../../core/workflow-contract.md) 已确定的协调路由与调用方范围，沿用[术语合同](../../core/terminology-contract.md)的主任务身份。通过 Planner、显式入口或 Roadmap 进入的 Explore 均保留自身授权和返回位置，不要求另行接受完整 Sacha。
2. 用户直接调用 Manager 时，把当前目标返回 `using-sacha` 或当前流程节点判断。委派 Agent 调用时返回协调请求；其他非主任务上下文停止并返回入口缺口。Manager Gate 关闭时返回调用节点。

## 动作顺序

按 Coordination Contract 安排实际工作单元，选择本地执行、复用或新建；派发时读取当前 Adapter 的完整参数映射，不另做一次协调预检。消费结果后继续剩余依赖，直至交付或有具体阻塞；当前波次只有一个单元不结束剩余协调。可选观测只记录已提交事实，失败不改变调度。

## 输出

- 向调用节点返回串行结论、派发状态、聚合事实、`delta`、阻塞/风险和 reference。
- 实现返修返回原 Executor，研究结果返回原 Explore；活跃 Planner 继续核对 Spec 就绪条件。

## 停止与禁止边界

- Manager 是控制面，只在主任务内运行；委派 Agent 遵守单层派发。
- Planner 设计、Executor 写入、Reviewer 裁决和 Human 授权由各自 Owner 处理。
- 协调过程使用现有 Runtime 传输，不创建跨会话注册表、后台服务或自动反馈任务。
