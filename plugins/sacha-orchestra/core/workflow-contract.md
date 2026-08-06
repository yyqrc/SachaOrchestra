# Workflow Contract

> Contract Version: 15
> Status: Normative Core kernel

## 1. 范围

本文定义 Intake 接受后的 Role、Gate、生命周期和 Human 路由；显式 Clarify 保持窄授权，不因此进入完整 lifecycle。入口见 [Intake Contract](intake-contract.md)，Review 见 [Assurance Contract](assurance-contract.md)。
分解、readiness、调度、取消、归并、return 与迁移 owner transfer 见 [Coordination Contract](coordination-contract.md)，持久记录见 [Artifact Protocol](artifact-protocol.md)。

Core platform/project-neutral；Runtime transport 归 Adapter，项目知识归 Project Integration/Domain Skill，Role procedure 归 Skill。只在当前 consumer 出现时加载对应合同，不预加载可能出现的下游面。

## 2. 运行原则

- 默认 Executor-only；Gate 无事实依据时关闭。同一文件或共享可变输出只有一个活跃写入者；隔离 patch/候选实现由 integration owner 串行应用。
- Human 保留目标、Scope、高影响动作和 workspace 外状态授权。
- 原始文件、外部状态和命令结果决定事实；Artifact/报告/自报只索引。
- workflow owner 推进到根终态；Role/helper completion 只是中间结果。
- 授权、Reviewer provenance、single writer、return identity/dedup、安全、Handoff 必要语义与原始证据权威不可降级。
- 能在当前 context 完成就不持久化；为防压缩丢失可先写最小决定记录，仅批准、breaking 或恢复需要才写 Spec Artifact。Plan 无消费者就不建 Artifact。
- 当前 owner 发现多个候选单元、依赖、并发安全或正式恢复需要协调时打开 Manager Gate 并转到 Coordination；Workflow 不要求 owner 先完整拆分。单一职责内工作仍可在当前 owner 内完成，验证按风险从 diff/parse 扩到集成、发布或真实环境，不联动固定套餐。
- 显式 Clarify 的研究保持只读窄授权；出现多个候选问题、依赖图或正式恢复需要协调时同样打开 Manager Gate。一个窄研究可由 Clarify owner 直接消费，readiness 与派发规则只由 Coordination 定义。
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
| Manager | 多个候选单元、依赖图、安全并发、正式恢复或多环境需要协调 owner | 单一职责内工作；困难、耗时、多文件、只想增加 Agent |

Gate 绑定 Scope、验收、owner、交付、安全/权限和依赖事实。Direct 或 active workflow 出现表中新的打开事实时必须重评估。
名称或新 context 不证明 Reviewer 独立；参与当前方案/实现者不能作独立 Reviewer。

## 4. Lifecycle 与 Human 路由

生命周期：Intake acceptance → Route → Plan（按需）→ Human 确认实质新方案（按需）→ Coordinate（按需）→ Execute → Review（按需）→ Documentation candidate check（按需）→ Close/Handoff。

Human 是技术项目协作者。先给判断及证据，再给影响或下一步；按问题自然组织，不要求 Human 理解内部 Gate、Packet、状态码或字段表。
只有缺失决定会改变实现、验收或高影响动作时才问一个具体问题，并给推荐与取舍。进度只报新事实、风险或阻塞。

Planner 的实质新方案先给 Human 看 Spec；确认前不 Execute。无未决方案、额外授权或阻塞性 Entry Condition时，`批准`、`都 OK` 已足够立即路由，不再问“开始实施”。普通批准默认在同一任务执行，不得静默创建用户可见任务。

Spec 已持久化且可达，并有 Runtime 高 context 占用/compaction 事实，或可直接观察的多阶段长历史且执行不依赖未落盘对话时，可明确推荐“批准并新开执行任务”；没有可靠信号时不得伪造占用遥测。只有 Human 明确选择新开才由 Adapter 迁移。Spec/批准/Entry Condition/唯一 owner 任一不足，或旧写入者未 terminal 时不得迁移；identity/dedup、single writer 与 owner transfer 归 Coordination。

task migration 把剩余 lifecycle 交给新 workflow owner；旧 task handoff 后结束，不等待 return。新 owner 继续同一 lifecycle 与独立 Review，迁移不改变 Gate；调度和 owner transfer 由 Coordination 处理。

一次回复含多个问题、建议、取舍或异议点时，正文后用稳定编号收齐结论、关键影响、待决定事项及是否需 Human 决定；不得遗漏或新增方案。单一结论、进度或纯事实不强制总结。这只是沟通收口，不是 Artifact、Gate、状态或决定日志。

不得为简短而隐藏授权影响、安全/数据风险、失败、未验证、Scope 偏离、reference、Entry Condition、schema 或脆弱步骤。

动态路由：出现 Planner Gate 新事实 → Planner；新增高影响授权 → Human；Reviewer 路由按 Assurance；delegation/return 失败按 Coordination。
Scope 内局部实现判断由 Executor 自主完成；环境不可用先耗尽同 Scope 安全替代。

Role completion、已批准方案向 Executor 的 transition、同 Scope 返修/补证据/复验、唯一 owner 路由和已授权 closeout 不是 Human checkpoint。Direct Scope 由用户目标与明确约束界定；预计文件列表不是 hard allowlist，除非 Human/Spec 明确如此。

## 5. Project Documentation closeout

完成实现及所需验证/Review 后，workflow owner 只用当前任务最终事实检查一次项目文档候选。候选必须有持久产品 delta，并至少满足一项：已批准 Spec 的实质方案已经落地；形成对后续消费者有用的新/改能力、架构、数据、运维或恢复知识；存在经最终实现和证据证实、且有跨任务消费者的 Project Context 候选。实际 Runtime 验证可加强候选证据，但不能把无持久 delta 的任务变成候选。

纯问答、无持久 delta、仅完成任务证据索引，或没有上述持久知识的一行/局部修复，均静默跳过；没有 confirmed Project Integration、策略为 `disabled` 或候选不成立时也不询问 Human。候选成立时才读取 `document-project`：`on-request` 只询问一次是否生成，并以 Human 的肯定答复形成 request；`required-at-closeout` 进入合法 closeout。写入仍服从 Project Integration 的 `bounded-closeout | per-write-confirmation`，不得用候选判断扩大授权。

Documentation 跳过、Human 拒绝或尚待写入确认不改变 Execution Report/Review 的事实，也不阻止如实关闭已完成任务；项目策略明确把文档列为 blocking Acceptance 时除外。
