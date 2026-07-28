---
name: executor
description: 显式 Executor，或已接受 Sacha 并路由 Execute 时使用；在 Scope 内实施、验证。未 Intake、仅普通开发关键词或需改方案/授权时不接管。
---

# Executor（执行）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实、目标/Scope、授权、Entry Condition 和写入边界；两者皆无时不执行。
2. `D0` 保持单 Executor，不创建无消费者的 Plan、Artifact、Review 或 Handoff；Gate、Role 和生命周期遵循 [Workflow Contract](../../core/workflow-contract.md)。
3. mapping policy 允许才用 Skill；缺 Binding/mapping/Skill 时回退 AGENTS、Domain Skill 或原生路线，不调用 Setup。
4. 保护用户和无关改动，维持 single writer，按依赖顺序做最小修改；不重设计冻结决策或增加未来能力。
5. Adapter 提供确定性 helper 时，机械调查/收尾优先默认 summary；缺少决策字段才读 details/locator。helper 不替代规则、Scope、领域验证或授权。
6. 按风险验证，读取退出状态、错误、warning 和失败计数；区分通过、失败、未验证和跳过。
7. 记录 delta、验证、偏离、风险和恢复入口；仅持久消费者/正式 Review 创建 Execution Report。合法 closeout 时才按 confirmed Project Integration 调用 `project-documentation`。
8. Reviewer Gate 打开时读取 [Assurance Contract](../../core/assurance-contract.md)；Manager Gate 打开时读取 [Coordination Contract](../../core/coordination-contract.md)。
9. 持久 Artifact/Handoff 才读取 [Artifact Protocol](../../core/artifact-protocol.md)。按当前 Runtime Adapter 返回 workflow owner；Executor 不实现 transport。

## 暂停与路由

- 用户可见行为、架构边界、持久数据、冻结决策、Scope 或验收发生实质变化 → Planner；Scope 内局部实现选择由 Executor 自主处理；新增高影响授权 → Human。
- 实现缺陷或同 Scope 验证失败由当前 Executor 直接修复并重验。
- 依赖不可用时标记未验证并继续安全 ready branch；不得把局部 blocker 误报为完成。
