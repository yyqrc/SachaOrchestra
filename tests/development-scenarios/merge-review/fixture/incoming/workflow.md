# Workflow Contract（取样片段）

## 2. 运行原则

- 默认仅使用 Executor；Gate 无事实依据时关闭。同一文件或共享可变输出只有一个活跃写入者；隔离补丁/候选实现由集成 Owner 串行应用。
- Human 保留目标、Scope、高影响动作和工作区外状态授权。
- 设计与实施选择满足当前目标、影响范围最小且可回退的方案。新增机制必须有当前需求或已确认可达的失败依据，并说明现有实现或局部修改为何不足；通用化必须有明确的复用需求。依据不足的扩展必须删除或收缩。数据兼容风险按项目与领域规则核对；迁移未获决定时，先说明影响并询问是否处理，不默认建设迁移或恢复机制。
- 原始文件、外部状态和命令结果决定事实；Artifact/报告/自报只索引。
- 主任务推进到根终态并独占 Manager 与派发；委派 Agent 的完成结果和协调请求只是中间结果。
- 授权、Reviewer 来源独立性、单写入者、返回标识/去重、安全、Handoff 必要语义与原始证据权威不可降级。
- 能在当前上下文完成就不持久化；为防压缩丢失可先写最小决定记录，仅批准、破坏性变更或恢复需要才写 Spec Artifact。Plan 无消费者就不建 Artifact。
- 所有任务使用同一通用生命周期；新增特殊目标、隐藏旁路或额外生命周期前，必须向 Human 提交真实失败模式、现有路由缺口与影响并取得明确批准。
- 主任务在实施或有界探索前，先判断当前目标能否形成至少两个输入自足、输出可隔离且有独立完成检查的工作单元；能够形成时打开 Manager Gate 并转到 Coordination 统一协调；就绪不等于必须派发，主任务可完成部分单元或串行处理。已有多个候选、依赖、并发安全或正式恢复需要协调时同样打开 Gate；候选尚未完整拆分也可调用。只有一个单元且适合隔离中间过程时，主任务按 Coordination 直接管理一个委派 Agent，不打开 Manager Gate。不得只因困难、耗时或文件多而人为拆分。
- 显式 Explore 的研究保持只读窄授权；主任务发现多个候选问题、依赖图或正式恢复时打开 Manager Gate。一个窄研究可由主任务直接派发；Explore 委派 Agent 只返回研究结果或协调请求，就绪判定与派发规则由 Coordination 定义。
- 主任务 → 通过显式入口、Planner 或 Roadmap 进入 Explore → 必须完整读取 Explore Skill，并按其输入、动作、输出与停止边界推进 → Explore 结果返回调用节点。
- 显式 Roadmap 不接受 Sacha 或进入生产 Role；事实或 Human 决定不足时只路由 Explore 并把结果返回 Roadmap，自包含正文就绪后只路由 document-project，写入结果返回 Roadmap 并结束当前独立规划。Roadmap 完成后若建议为一个候选 Spec 另开任务，必须先按 Human Interaction Contract 明确说明这是 Sacha Planner 任务及其执行影响；只有 Human 确认创建后，Runtime Adapter 才创建新任务并把显式 Planner 请求写入初始输入。
- 三个 Gate 全关且无需恢复时，Executor 处理不能形成独立工作单元的局部动作；一个已就绪实施单元满足 Coordination 的安全条件且派发有实际收益时才直接派发。只有发生派发时才加载 Coordination 与目标 Runtime Adapter，不加载无消费者的 Assurance 或 Artifact。

## 3. Role 与 Gate

| Role | 唯一责任 | 禁止 |
| --- | --- | --- |
| [Planner](../skills/planner/SKILL.md) | 调查事实、比较实质方案、冻结 Scope/决策/验收 | 把规划当授权；实施生产修改 |
| [Executor](../skills/executor/SKILL.md) | 在批准 Scope/明确目标内自主选择局部实现、实施、验证并记录证据 | 静默改变用户可见 Scope/冻结决策；虚报验证 |
| [Reviewer](../skills/reviewer/SKILL.md) | 以独立来源对照 Scope、真实状态和原始证据裁决 | 改合同求通过；默认修复 |

| Gate | 打开事实 | 不构成事实 |
| --- | --- | --- |
| Planner | 会改变实施路线的目标、验收、负责边界或关键方案仍待比较与冻结；原始材料不足以核实目标结果所需的实际行为、期望行为、适用范围/边界、复现或完成条件；用户要求或实际后续消费者需要完整 Spec；难回退的跨 Owner 决策 | 复杂、文件多、耗时、跨插件、已明确的行为修改；不影响目标、范围、验收或路线的局部补齐信息；Agent 自行提议写 Spec |
| Reviewer | 安全/权限/持久数据、破坏性变更、困难回退、证据冲突、无法判断关键证据缺口的阻塞性、安全补证路径耗尽后需要正式裁决或 Human 要求 | 文档标签、版本封装、可回退且完整验证的局部修改；当前 Executor 仍可按既定验收完成的补证 |
| Manager | 至少两个输入自足、输出可隔离且可独立检查的工作单元；多个候选、依赖图、安全并发、正式恢复或多环境需要协调 Owner | 无法形成独立完成检查的局部动作；困难、耗时、多文件或只想增加 Agent；一个单元仅需隔离中间过程 |

Executor 先在既有职责与授权内完成可完成的必需验证和补证，不为已明确且可处理的缺口先做一次 Review。其他 Reviewer Gate 事实、证据冲突或缺口阻塞性不明时仍进入独立 Review；未完成的必需验证不得记为完成。

Gate 绑定 Scope、验收、Owner、交付、安全/权限和依赖事实。Direct 或活跃工作流出现表中新的打开事实时必须重评估。
名称或新上下文不证明 Reviewer 独立；参与当前方案/实现者不能作独立 Reviewer。

动态路由：出现 Planner Gate 新事实 → Planner；Planner 先核对小事实；仍需持续探索、实质事实或 Human 决定，或原始材料不足以核实目标结果所需的实际行为、期望行为、适用范围/边界、复现或完成条件 → Explore；在 Explore 返回前不得把标题、附件、技术常识或 Agent 推断当作已冻结的目标或验收，也不得据此继续单一路线实施；Explore 返回后按剩余问题继续核对或探索，足够后才冻结 Spec；Roadmap 事实不足 → Explore → Roadmap，正文就绪 → document-project → Roadmap 结束；Roadmap 明确推荐独立 Sacha Planner 任务且 Human 确认创建 → 新任务从显式 Planner 入口开始；新增高影响授权 → Human；Reviewer 路由按 Assurance；委派/返回失败按 Coordination。
Scope 内局部实现判断由 Executor 自主完成；环境不可用先耗尽同 Scope 安全替代。
