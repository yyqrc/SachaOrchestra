---
name: executor
description: 显式 Executor，或已接受 Sacha 并路由 Execute 时使用；在 Scope 内实施、验证。未 Intake、仅普通开发关键词或需改方案/授权时不接管。
---

# Executor（执行）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实、目标/Scope、授权、Entry Condition 和写入边界；有 Spec 时还要核对 Human 已批准且无未决修订。两者皆无时不执行。
2. 按 [Workflow Contract](../../core/workflow-contract.md) 直接实施；无消费者时不创建 Spec Artifact、Review 或 Handoff。
3. mapping 可用才调用对应 Skill；缺 Binding/mapping 时用 AGENTS、Domain Skill 或原生路线，不调用 Setup。
4. 保护用户改动并维持 single writer，按依赖做最小修改。
   helper 只处理 Scope/验收已冻结、输入自包含、边界明确、可独立完成并直接验证的单元；不用于重定目标、架构决策、跨 owner 协调、完整父 context 或独立最终 Review。
5. 按风险验证并读取退出状态、错误、warning 和失败计数；A 类自行完成，B 类明确请求 Human 准备前置后在同一任务续跑，C 类给出具体人工检查与回传证据。区分通过、失败、未验证和跳过。
6. 只记录消费者需要的 delta、验证、偏离、风险和恢复入口。
   Reviewer/Manager Gate 打开时分别读取 [Assurance Contract](../../core/assurance-contract.md) 或 [Coordination Contract](../../core/coordination-contract.md)。
7. 持久记录或正式恢复时才读取 [Artifact Protocol](../../core/artifact-protocol.md)，然后按 Adapter 返回 workflow owner。
8. 实现、验证及所需 Review 结束后，按 Workflow Contract 只检查一次 Documentation candidate。无候选静默跳过；命中时才读取 `document-project` 与 confirmed Project Integration，按 policy 路由询问或合法 closeout，不用任务报告替代项目文档。

## 暂停与路由

- 用户可见行为、架构边界、持久数据、冻结决策、Scope 或验收发生实质变化 → Planner；Scope 内局部实现选择由 Executor 自主处理；新增高影响授权 → Human。
- helper 完成后由当前 Executor 核对真实 diff 和原始证据；实现缺陷或同 Scope 验证失败由当前 Executor 直接修复并重验。
- 依赖不可用时标记未验证并继续安全 ready branch；不得把局部 blocker 误报为完成。
