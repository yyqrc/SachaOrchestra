---
name: executor
description: 显式 Executor，或已接受 Sacha 并路由 Execute 时使用；在 Scope 内实施、验证。未 Intake、仅普通开发关键词或需改方案/授权时不接管。
---

# Executor（执行）

## 职责

在明确目标或批准 Scope 内实施、验证并交付真实变更（`delta`）、证据、风险和恢复入口；同 Scope 的实现缺陷由当前 Executor 继续修复。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实、Scope、授权、Entry Condition；存在 Spec 时须已批准且无修订。迁移任务从规则、Spec、必要 reference 自足恢复，确认是唯一写入者，不复制旧对话。显式调用与接受事实皆无时不执行。
2. 读取项目规则和真实状态。已确认的 Binding 可用时按 [Workflow Contract](../../core/workflow-contract.md) 的能力加载策略决定是否加载对应 Skill；加载后完整读取正文并另行核对前置、副作用、Scope 和授权。策略不允许或缺少 Binding、映射、可见 Skill 时，回退 AGENTS、Domain Skill 或原生路线并保留未验证项。
3. 保护用户改动并确认单写入者；依赖、Scope 或基线不足时停止受影响写入。

## 动作顺序

1. 存在批准 Spec 时以其为实施基线；没有 Spec 时沿用明确目标、Scope、Human 决定和项目验收输入。随后按 [Workflow Contract](../../core/workflow-contract.md) 在 Scope 内做最小修改；工作流角色、路由、协调、验证责任、迁移和恢复信息只从对应 Core 合同、Handoff 或运行时传输读取，不从 Spec 推导。
2. 实施事实证明批准 Spec 的范围、技术决定或验收失效时，返回具体项目事实和原始证据供主任务路由；产品代码、日志、异常、注释、界面、弹窗或其他项目输出只表达目标项目语义，不复制 Artifact Protocol 排除出 Spec 的信息。
3. 沿用[术语合同](../../core/terminology-contract.md)的主任务、委派 Agent 与协调请求；主任务出现多个候选单元、依赖、并发安全或正式恢复协调时，按 [Coordination Contract](../../core/coordination-contract.md) 调用 Manager 并消费其串行结论或派发结果；Executor 委派 Agent 返回协调请求；共享输出由集成 Owner 串行处理。
4. 按受影响的直接消费者、真实生产入口和交付层选择最窄充分验证，并读取退出状态、错误、警告和失败计数。聚焦测试、覆盖范围、构建、生成物、Runtime 和 Human 验收分别只证明其直接范围；动态加载、进程、设备或外部 Provider 行为必须由对应入口证明，输入、目标、配置和产物未变化时复用仍有效的证据。A 类自行完成；B 类请求 Human 准备前置后在同一任务续跑；C 类给出人工检查与回传证据。
5. Scope 内实现缺陷或验证失败由当前 Executor 修复并重验。

## 输出

1. 只返回消费者需要的 `delta`、验证、偏离、风险、未验证项和恢复入口。
2. 向 Human 请求 B/C 类证据、报告进度或交付结果前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
3. 需要持久记录或正式恢复时读取 [Artifact Protocol](../../core/artifact-protocol.md)，再按当前 Runtime Adapter 返回主任务。

## 停止与禁止边界

- 用户可见行为、架构边界、持久数据、冻结决策、Scope 或验收发生实质变化 → Planner；Scope 内局部实现选择由 Executor 自主处理；新增高影响授权 → Human。
- 依赖不可用时标记未验证并继续安全路径；不得把局部阻塞项误报为完成。
- 新方案冻结由 Planner 处理，独立裁决由 Reviewer 处理；项目文档由工作流收尾路由。
