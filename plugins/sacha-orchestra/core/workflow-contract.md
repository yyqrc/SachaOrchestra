# Workflow Contract（工作流合同）

> 合同版本：19
> 状态：规范性 Core 内核

## 1. 范围

本文是 Role、Gate、节点进入/退出条件和 Human 路由的唯一 Runtime Owner；显式 Clarify 保持窄授权。入口见 [Intake Contract](intake-contract.md)，Human 可见交互见 [Human Interaction Contract](human-interaction-contract.md)，Review 见 [Assurance Contract](assurance-contract.md)。
分解、就绪判定、调度、取消、归并、返回与迁移 Owner 转移见 [Coordination Contract](coordination-contract.md)，持久记录见 [Artifact Protocol](artifact-protocol.md)。

Core 不依赖平台或项目；Runtime 传输归 Adapter，项目知识归 Project Integration/Domain Skill，Role 流程归 Skill。只在当前消费者出现时加载对应合同，不预加载可能出现的下游面。

## 2. 运行原则

- 默认仅使用 Executor；Gate 无事实依据时关闭。同一文件或共享可变输出只有一个活跃写入者；隔离补丁/候选实现由集成 Owner 串行应用。
- Human 保留目标、Scope、高影响动作和工作区外状态授权。
- 原始文件、外部状态和命令结果决定事实；Artifact/报告/自报只索引。
- 工作流 Owner 推进到根终态；Role/辅助 Agent 的完成结果只是中间结果。
- 授权、Reviewer 来源独立性、单写入者、返回标识/去重、安全、Handoff 必要语义与原始证据权威不可降级。
- 能在当前上下文完成就不持久化；为防压缩丢失可先写最小决定记录，仅批准、破坏性变更或恢复需要才写 Spec Artifact。Plan 无消费者就不建 Artifact。
- 所有任务使用同一通用生命周期；新增特殊目标、隐藏旁路或额外生命周期前，必须向 Human 提交真实失败模式、现有路由缺口与影响并取得明确批准。
- 当前 Owner 发现多个候选单元、依赖、并发安全或正式恢复需要协调时打开 Manager Gate 并转到 Coordination；Owner 可在候选尚未完整拆分时调用。单一职责内工作仍可由当前 Owner 完成，验证范围按风险从 diff/解析扩到集成、发布或真实环境。
- 显式 Clarify 的研究保持只读窄授权；出现多个候选问题、依赖图或正式恢复需要协调时同样打开 Manager Gate。一个窄研究可由 Clarify Owner 直接消费，就绪判定与派发规则只由 Coordination 定义。
- 三个 Gate 全关且无需恢复时，Executor 在当前上下文完成，不加载无消费者的 Assurance、Coordination、Artifact 或 Runtime Adapter。

## 3. Role 与 Gate

| Role | 唯一责任 | 禁止 |
| --- | --- | --- |
| Planner | 调查事实、比较实质方案、冻结 Scope/决策/验收 | 把规划当授权；实施生产修改 |
| Executor | 在批准 Scope/明确目标内自主选择局部实现、实施、验证并记录证据 | 静默改变用户可见 Scope/冻结决策；虚报验证 |
| Reviewer | 以独立来源对照 Scope、真实状态和原始证据裁决 | 改合同求通过；默认修复 |

| Gate | 打开事实 | 不构成事实 |
| --- | --- | --- |
| Planner | 目标、验收/Owner 不清；实施前需关键 Human 澄清；需冻结/持久化 Spec；实质方案或难回退的跨 Owner 决策 | 复杂、文件多、耗时、多平台、无分歧修改 |
| Reviewer | 安全/权限/持久数据、破坏性变更、困难回退、关键验证缺失/证据冲突或 Human 要求 | 文档标签、版本封装、可回退且完整验证的局部修改 |
| Manager | 多个候选单元、依赖图、安全并发、正式恢复或多环境需要协调 Owner | 单一职责内工作；困难、耗时、多文件、只想增加 Agent |

Gate 绑定 Scope、验收、Owner、交付、安全/权限和依赖事实。Direct 或活跃工作流出现表中新的打开事实时必须重评估。
名称或新上下文不证明 Reviewer 独立；参与当前方案/实现者不能作独立 Reviewer。

## 4. 生命周期与 Human 路由

通用生命周期只按本合同推进：Direct 在当前任务完成；接受 Sacha 后按 Gate 进入 Planner/Clarify、Executor、Reviewer 和文档候选；Manager 是任一调用 Owner 内的协调闭环。Feedback 是主流程之外由 Human 在另一个真实任务手动调用的独立支持入口。不得新增隐藏阶段或旁路。

Planner 的实质新方案先给 Human 看 Spec；确认前不 Execute。无未决方案、额外授权或阻塞性 Entry Condition 时，`批准`、`都 OK` 已足够立即路由，不再问“开始实施”。普通批准默认在同一任务执行，不得静默创建用户可见任务。

Spec 已持久化且可达，并有 Runtime 上下文占用高/压缩事实，或可直接观察的多阶段长历史且执行不依赖未落盘对话时，可明确推荐“批准并新开执行任务”；没有可靠信号时不得伪造占用遥测。只有 Human 明确选择新开才由 Adapter 迁移。Spec/批准/Entry Condition/唯一 Owner 任一不足或旧写入者尚未终止时不得迁移；标识/去重、单写入者与 Owner 转移归 Coordination。

任务迁移把剩余生命周期交给新工作流 Owner；旧任务交接后结束，不等待返回。新 Owner 继续同一生命周期与独立 Review，迁移不改变 Gate；调度和 Owner 转移由 Coordination 处理。

Human 可因具体流程问题、使用反馈、插件开发建议或能力想法，在另一个真实任务手动调用 Feedback。该调用本身授权来源任务进行有界只读调查，并查询、复用或创建唯一反馈目标任务，不再追加创建确认。来源任务交付 reference 后结束且不等待目标任务终态；目标任务按 Intake Contract 作为普通任务重新判断，并使用通用的 Direct、Planner、Clarify、Executor、Reviewer、Manager、迁移和收尾规则。Feedback 调用不授权目标任务写入或执行外部动作。

动态路由：出现 Planner Gate 新事实 → Planner；新增高影响授权 → Human；Reviewer 路由按 Assurance；委派/返回失败按 Coordination。
Scope 内局部实现判断由 Executor 自主完成；环境不可用先耗尽同 Scope 安全替代。

当前 Owner 直接推进 Role 完成结果、已批准方案向 Executor 的转换、同 Scope 返修/补证据/复验、唯一 Owner 路由和已授权收尾。Direct Scope 由用户目标与明确约束界定；只有 Human 或 Spec 明确指定时，预计文件列表才成为硬性允许列表。

## 5. 项目文档收尾

完成实现及所需验证/Review 后，工作流 Owner 只用当前任务最终事实检查一次项目文档候选。候选必须有持久产品变更（delta），并至少满足一项：已批准 Spec 的实质方案已经落地；形成对后续消费者有用的新/改能力、架构、数据、运维或恢复知识；存在经最终实现和证据证实、且有跨任务消费者的项目上下文（Project Context）候选。

纯问答、无持久变更、仅完成任务证据索引，或没有上述持久知识的一行/局部修复，均静默跳过。没有已确认的 Project Integration、策略为 `disabled` 或候选不成立时结束检查；候选成立时才读取 `document-project`：`on-request` 只询问一次是否生成，并以 Human 的肯定答复形成请求；`required-at-closeout` 进入合法收尾。写入服从 Project Integration 的 `bounded-closeout | per-write-confirmation`。

文档状态独立于 Execution Report/Review；只有项目策略把文档列为阻塞性 Acceptance 时才阻止关闭已完成任务。
