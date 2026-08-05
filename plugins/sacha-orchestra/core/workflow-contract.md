# Workflow Contract

> Contract Version: 11
> Status: Normative Core kernel

## 1. 范围

本文只定义 Intake 接受后的 Role、Gate、生命周期和 Human 路由。入口见 [Intake Contract](intake-contract.md)，Review 见 [Assurance Contract](assurance-contract.md)。
调度与 return 见 [Coordination Contract](coordination-contract.md)，持久记录见 [Artifact Protocol](artifact-protocol.md)。

Core platform/project-neutral；Runtime transport 归 Adapter，项目知识归 Project Integration/Domain Skill，Role procedure 归 Skill。只在当前 consumer 出现时加载对应合同，不预加载可能出现的下游面。

## 2. 运行原则

- 默认 Executor-only；Gate 无事实依据时关闭。同一文件或共享可变输出只有一个活跃写入者；隔离 patch/候选实现由 integration owner 串行应用。
- Human 保留目标、Scope、高影响动作和 workspace 外状态授权。
- 原始文件、外部状态和命令结果决定事实；Artifact/报告/自报只索引。
- workflow owner 推进到根终态；Role/helper completion 只是中间结果。
- 授权、Reviewer provenance、single writer、return identity/dedup、安全、Handoff 必要语义与原始证据权威不可降级。
- 能在当前 context 完成就不持久化；澄清决定需防止压缩丢失时先写最小决定记录，只有批准、breaking 或恢复需要才写 Spec Artifact。Plan 只表示按需规划活动或 inline plan，没有消费者就不建 Artifact。
- 单个 Executor 或有界 helper 足够时不启用 Manager；多个独立单元、依赖图或多环境才协调。验证按真实风险从 diff/parse 扩到集成、发布或真实环境，不按固定套餐联动。
- 三个 Gate 全关且无需恢复时，Executor 在当前 context 完成，不加载无消费者的 Assurance、Coordination、Artifact 或 Runtime Adapter。

## 3. Role 与 Gate

| Role | 唯一责任 | 禁止 |
| --- | --- | --- |
| Planner | 调查事实、比较实质方案、冻结 Scope/决策/验收 | 把规划当授权；实施生产修改 |
| Executor | 在批准 Scope/明确目标内自主选择局部实现、实施、验证并记录证据 | 静默改变用户可见 Scope/冻结决策；虚报验证 |
| Reviewer | 以独立 provenance 对照 Scope、真实状态和原始证据裁决 | 改合同求通过；默认修复 |

| Gate | 打开事实 | 不构成事实 |
| --- | --- | --- |
| Planner | 目标、验收/owner 不清；实施前需关键 Human 澄清；需冻结/持久化 Spec；实质方案或难回退跨 owner 决策 | 复杂、文件多、耗时、多平台、无分歧修改 |
| Reviewer | 安全/权限/持久数据、breaking、困难回退、关键验证缺失/证据冲突或 Human 要求 | 文档标签、版本封装、可回退且完整验证的局部修改 |
| Manager | 多个 delegated 单元、依赖图、安全并发、正式恢复或多环境需要 owner | 困难、耗时、多文件、只想增加 Agent |

Gate 绑定 Scope、验收、owner、交付、安全/权限和依赖事实。Direct 或 active workflow 出现表中新的打开事实时必须重评估。
名称或新 context 不证明 Reviewer 独立；参与当前方案/实现者不能作独立 Reviewer。

## 4. Lifecycle 与 Human 路由

生命周期：Intake acceptance → Route → Plan（按需）→ Human 确认实质新方案（按需）→ Coordinate（按需）→ Execute → Review（按需）→ Close/Handoff。

Human 是技术项目协作者。先给判断及证据，再给影响或下一步；按问题自然组织，不要求 Human 理解内部 Gate、Packet、状态码或字段表。
只有缺失决定会改变实现、验收或高影响动作时才问一个具体问题，并给推荐与取舍。进度只报新事实、风险或阻塞。

Planner 形成 Human 此前未确认的实质方案时，先把拟执行 Spec 交给 Human 看见并说明本轮优先检查处；确认前不得进入 Execute。Human 批准后，若没有未决方案、额外授权或阻塞性 Entry Condition，workflow owner 必须在同一任务立即路由 Executor；`批准`、`都 OK` 等清晰短答已足够，不得再索要“开始实施”。

一次回复处理多个问题，或形成多项建议、取舍、异议点时，正文之后用自然中文和稳定编号收齐本轮最终建议与待决定事项，说明结论、关键影响以及是否仍需 Human 决定；不得遗漏正文建议或新增正文未论证方案。单一简单结论、进度或纯事实回报不强制总结。它只是当轮沟通收口，不是 Artifact、Gate、状态或第二份决定日志。

不得为简短而隐藏授权影响、安全/数据风险、失败、未验证、Scope 偏离、locator、Entry Condition、schema 或脆弱步骤。

动态路由：出现 Planner Gate 新事实 → Planner；新增高影响授权 → Human；Reviewer 路由按 Assurance；delegation/return 失败按 Coordination。
Scope 内局部实现判断由 Executor 自主完成；环境不可用先耗尽同 Scope 安全替代。

Role completion、已批准方案向 Executor 的 transition、同 Scope 返修/补证据/复验、唯一 owner 路由和已授权 closeout 不是 Human checkpoint。Direct Scope 由用户目标与明确约束界定；预计文件列表不是 hard allowlist，除非 Human/Spec 明确如此。
