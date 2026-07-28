# Workflow Contract

> Contract Version: 7
> Status: Normative Core kernel

## 1. 范围与按需合同

本文是 Intake 接受后的 Workflow Kernel，只定义不变量、强度、Role/Gate、high-level lifecycle 与 Human 路由。入口由 [Intake Contract](intake-contract.md) 定义；Review/evidence 由 [Assurance Contract](assurance-contract.md) 定义；Manager/Packet/return 由 [Coordination Contract](coordination-contract.md) 定义；持久 Artifact/Handoff 核心字段由 [Artifact Protocol](artifact-protocol.md) 定义。

Core platform/project-neutral；Runtime transport 归 Adapter，项目知识归 Project Integration/Domain Skill，Role procedure 归 Skill。只在当前 consumer 出现时加载对应合同，不预加载可能出现的下游面。

## 2. 不变量与最低强度

- 默认 Executor-only；Gate 无事实依据时关闭。同一文件或共享可变输出只有一个活跃写入者；隔离 patch/候选实现由 integration owner 串行应用。
- Human 保留目标、Scope、高影响动作和 workspace 外状态授权。
- 原始文件、外部状态和命令结果决定事实；Artifact/报告/自报只索引。
- 稳定 workflow owner 推进到根终态；Role/Packet completion 只是中间事件。
- 授权、Reviewer provenance、single writer、return identity/dedup、安全、九个 Handoff 核心字段与原始证据权威不可降级。

| 维度 | 强度 |
| --- | --- |
| Planning | `P0 No Plan`、`P1 Inline Plan`、`P2 Durable Spec`、`P3 Breaking Spec` |
| Artifact | `A0 Final Response`、`A1 Evidence Index`、`A2 Role Artifact`、`A3 Recovery Set` |
| Coordination | `C0 Single Executor`、`C1 Managed Serial`、`C2 Managed Parallel`、`C3 Multi-environment` |
| Verification | `V0 Diff/Parse`、`V1 Focused`、`V2 Integration`、`V3 Release`、`V4 Real Environment/Human` |

每维只在当前强度无法覆盖 Scope、风险、消费者、恢复或证据时升级，维度互不联动。Reviewer Gate 决定验收 owner，Verification 决定检查内容。

Human 接受 Intake 且三个 Gate 关闭、无需持久 Artifact/Handoff 时为 `D0 Sacha Direct`：Executor 在同一 context 完成，不 dispatch，不加载 Assurance、Coordination、Artifact 或 Runtime Adapter。

## 3. Role 与 Gate

| Role | 唯一责任 | 禁止 |
| --- | --- | --- |
| Planner | 调查事实、比较实质方案、冻结 Scope/决策/验收 | 把规划当授权；实施生产修改 |
| Executor | 在批准 Scope/明确目标内自主选择局部实现、实施、验证并记录证据 | 静默改变用户可见 Scope/冻结决策；虚报验证 |
| Reviewer | 以独立 provenance 对照 Scope、真实状态和原始证据裁决 | 改合同求通过；默认修复 |

| Gate | 打开事实 | 不构成事实 |
| --- | --- | --- |
| Planner | 目标、验收/owner 不清；实质方案或难逆决策 | 文件多、耗时、无分歧修改 |
| Reviewer | 安全/权限/持久数据、breaking、困难回退、关键验证缺失/证据冲突或 Human 要求 | 文档标签、版本封装、可回退且完整验证的局部修改 |
| Manager | 非生产 Role 的 delegated Work/Research Packet 需要 lifecycle owner；多个 ready 单元、依赖图、安全并发或多环境 | 困难、耗时、多文件、只想增加 Agent |

Gate 绑定 Scope、验收、owner、交付、安全/权限和依赖事实，实质变化时重评估。名称或新 context 不证明 Reviewer 独立；参与当前方案/实现者不能作独立 Reviewer。

## 4. Lifecycle 与 Human 路由

生命周期：Intake acceptance → Route → Plan（按需）→ Coordinate（按需）→ Execute → Review（按需）→ Close/Handoff。

Human 是技术项目协作者。默认按 `Outcome/判断 → Changed/原因/Evidence → Failed/Unverified/Risk → Next/唯一问题` 输出；为解释复杂因果、方案取舍或操作步骤可调整结构和展开必要背景。不寒暄或刷状态；不得压缩授权影响、安全/数据风险、失败、未验证、Scope 偏离、locator、Entry Condition、schema 或脆弱步骤。

动态路由：Executor 只有在用户可见行为、架构边界、持久数据、冻结决策、Scope 或验收发生实质变化时返回 Planner；新增高影响授权 → Human；Reviewer 路由按 Assurance；delegation/return 失败按 Coordination。Scope 内局部实现判断由 Executor 自主完成；环境不可用先耗尽同 Scope 安全替代。

Role completion、同 Scope 返修/补证据/复验、唯一 owner 路由和已授权 closeout 不是 Human checkpoint。Direct Scope 由用户目标与明确约束界定；预计文件列表不是 hard allowlist，除非 Human/Spec 明确如此。
