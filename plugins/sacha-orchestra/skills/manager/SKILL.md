---
name: manager
description: 当 Manager Gate 已开启，需要协调多个 ready 工作单元、依赖图、安全并发或多执行实例时使用；把批准 Scope 组织为 Work Packet 并聚合结果。困难、耗时、多文件或单纯希望更多 Agent 时不使用。
---

# Manager（协调）

Manager 是控制面，不是第四个生产 Role。

## 工作流

1. 读取 [Workflow Contract](../../core/workflow-contract.md) 的 Manager Gate、Work Packet 和 Parallel assertion，核对批准 Scope、授权、依赖和 owner。Gate 关闭时返回单 Executor 路线。
2. 为每个 ready 单元定义 owner、read/write scope、依赖、输入、输出、验证和停止条件；写入 Scope 必须静态不重叠，共享生成物和整体验证交给 integration owner。
3. 按当前 Runtime Adapter 为每个实例提供最小必要 Packet、约束和 evidence locator，不用宽泛历史上下文补偿缺失输入。
4. Parallel assertion 成立时，在首次 wait/join 前实际启动至少两个实例；否则记录 managed serial、`parallel_blocked` 或 `parallel_dispatch_missed`。
5. 按 Adapter 消费 completion、执行 liveness/取消并维护 single writer。只聚合新的事实、冲突、状态和 locator，不拼接完整子报告。
6. 报告预算不得隐藏失败、未验证项、风险或授权阻塞；达到预算时标记 `report_limited`，按需发起定向 follow-up。
7. 调度或 transition 失败时生成 Core deviation packet 并进入 Feedback；phase 完成后按 Adapter 返回 workflow owner。

## 边界

- 不代替 Planner 设计、Executor 写入、Reviewer 验收或 Human 授权。
- Packet blocked 只暂停依赖分支；继续其他安全 ready branch。
- 不创建新的 Registry、后台服务或自动反馈任务。
