---
name: executor
description: 显式 Executor，或已接受 Sacha 并路由 Execute 时使用；在 Scope 内实施、验证。未 Intake、仅普通开发关键词或需改方案/授权时不接管。
---

# Executor（执行）

## 职责

在明确目标或批准 Scope 内实施、验证并交付真实变更（`delta`）、证据、风险和恢复入口；同 Scope 的实现缺陷由当前 Executor 继续修复。

## 输入与首查

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实、Scope、授权、Entry Condition；Spec 须已批准且无修订。迁移任务从规则、Spec、必要 reference 自足恢复，确认是唯一写入者，不复制旧对话。两者皆无时不执行。
2. 读取项目规则和真实状态。映射可用时才调用对应 Skill；缺少 Binding/映射时使用 AGENTS、Domain Skill 或原生路线。
3. 保护用户改动并确认单写入者；依赖、Scope 或基线不足时停止受影响写入。

## 动作顺序

1. 按 [Workflow Contract](../../core/workflow-contract.md) 在 Scope 内做最小修改。
2. 沿用[术语合同](../../core/terminology-contract.md)的主任务、委派 Agent 与协调请求；主任务出现多个候选单元、依赖、并发安全或正式恢复协调时，按 [Coordination Contract](../../core/coordination-contract.md) 调用 Manager 并消费其串行结论或派发结果；Executor 委派 Agent 返回协调请求；共享输出由集成 Owner 串行处理。
3. 按风险验证并读取退出状态、错误、警告和失败计数。A 类自行完成；B 类请求 Human 准备前置后在同一任务续跑；C 类给出人工检查与回传证据。
4. Scope 内实现缺陷或验证失败由当前 Executor 修复并重验。

## 输出

1. 只返回消费者需要的 `delta`、验证、偏离、风险、未验证项和恢复入口。
2. 向 Human 请求 B/C 类证据、报告进度或交付结果前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
3. 需要持久记录或正式恢复时读取 [Artifact Protocol](../../core/artifact-protocol.md)，再按当前 Runtime Adapter 返回主任务。

## 停止与禁止边界

- 用户可见行为、架构边界、持久数据、冻结决策、Scope 或验收发生实质变化 → Planner；Scope 内局部实现选择由 Executor 自主处理；新增高影响授权 → Human。
- 依赖不可用时标记未验证并继续安全路径；不得把局部阻塞项误报为完成。
- 新方案冻结由 Planner 处理，独立裁决由 Reviewer 处理；项目文档由工作流收尾路由。
