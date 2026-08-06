---
name: executor
description: 显式 Executor，或已接受 Sacha 并路由 Execute 时使用；在 Scope 内实施、验证。未 Intake、仅普通开发关键词或需改方案/授权时不接管。
---

# Executor（执行）

## 工作流

1. 核对显式调用或 [Intake Contract](../../core/intake-contract.md) 接受事实、Scope、授权、Entry Condition；Spec 须已批准且无修订。迁移 task 从规则、Spec、必要 reference 自足恢复，确认是唯一写入者，不复制旧对话。两者皆无时不执行。
2. 按 [Workflow Contract](../../core/workflow-contract.md) 直接实施；当前 owner 发现多个候选单元、依赖、并发安全或正式恢复需要协调时，调用 [Coordination Contract](../../core/coordination-contract.md) 的 Manager，不先自行拆分。消费 Manager 返回的分解、依赖、串行/派发结论；无消费者时不创建 Spec Artifact、Review 或 Handoff。
3. mapping 可用才调用对应 Skill；缺 Binding/mapping 时用 AGENTS、Domain Skill 或原生路线，不调用 Setup。
4. 保护用户改动并维持 single writer，按依赖做最小修改。
   单个 helper 的结果由 invoking owner 按 Coordination Contract 直接消费；不负责重定目标、架构决策、跨 owner 协调、完整父 context 或独立最终 Review。Manager 返回串行结论时由当前 Executor 继续，返回派发结果时只消费其事实/delta；共享输出由 integration owner 串行。
5. 按风险验证并读取退出状态、错误、warning 和失败计数；A 类自行完成，B 类明确请求 Human 准备前置后在同一任务续跑，C 类给出具体人工检查与回传证据。区分通过、失败、未验证和跳过。
6. 只记录消费者需要的 delta、验证、偏离、风险和恢复入口。
   Reviewer/Manager Gate 打开时分别读取 [Assurance Contract](../../core/assurance-contract.md) 或 [Coordination Contract](../../core/coordination-contract.md)。
7. 持久记录或正式恢复时才读取 [Artifact Protocol](../../core/artifact-protocol.md)，然后按 Adapter 返回 workflow owner。
8. 实现、验证及所需 Review 结束后，按 Workflow Contract 只检查一次 Documentation candidate。无候选静默跳过；命中时才读取 `document-project` 与 confirmed Project Integration，按 policy 路由询问或合法 closeout，不用任务报告替代项目文档。

## 暂停与路由

- 用户可见行为、架构边界、持久数据、冻结决策、Scope 或验收发生实质变化 → Planner；Scope 内局部实现选择由 Executor 自主处理；新增高影响授权 → Human。
- helper 完成后由当前 Executor 核对真实 diff 和原始证据；实现缺陷或同 Scope 验证失败由当前 Executor 直接修复并重验。
- 依赖不可用时标记未验证并继续安全路径；不得把局部 blocker 误报为完成。
