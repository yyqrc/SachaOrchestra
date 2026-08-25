# Workflow Contract（工作流合同）

> 状态：规范性 Core 内核

## 1. 范围

本文是 Role、Gate、节点进入/退出条件、主流程外 Roadmap 跨 Skill 路由和 Human 路由的唯一 Runtime Owner；显式 Explore 保持窄授权。提炼术语见[术语合同](terminology-contract.md)，入口见 [Intake Contract](intake-contract.md)，Human 可见交互见 [Human Interaction Contract](human-interaction-contract.md)，Review 见 [Assurance Contract](assurance-contract.md)。
分解、就绪判定、调度、取消、归并、返回与迁移 Owner 转移见 [Coordination Contract](coordination-contract.md)，持久记录见 [Artifact Protocol](artifact-protocol.md)。

Core 不依赖平台或项目；Runtime 传输归 Adapter，项目知识归 Project Integration/Domain Skill，Role 流程归 Skill。只在当前消费者出现时加载对应合同，不预加载可能出现的下游面。

## 2. 运行原则

- 默认仅使用 Executor；Gate 无事实依据时关闭。同一文件或共享可变输出只有一个活跃写入者；隔离补丁/候选实现由集成 Owner 串行应用。
- Human 保留目标、Scope、高影响动作和工作区外状态授权。
- 原始文件、外部状态和命令结果决定事实；Artifact/报告/自报只索引。
- 主任务推进到根终态并独占 Manager 与派发；委派 Agent 的完成结果和协调请求只是中间结果。
- 授权、Reviewer 来源独立性、单写入者、返回标识/去重、安全、Handoff 必要语义与原始证据权威不可降级。
- 能在当前上下文完成就不持久化；为防压缩丢失可先写最小决定记录，仅批准、破坏性变更或恢复需要才写 Spec Artifact。Plan 无消费者就不建 Artifact。
- 所有任务使用同一通用生命周期；新增特殊目标、隐藏旁路或额外生命周期前，必须向 Human 提交真实失败模式、现有路由缺口与影响并取得明确批准。
- 主任务发现多个候选单元、依赖、并发安全或正式恢复需要协调时打开 Manager Gate 并转到 Coordination；可在候选尚未完整拆分时调用。委派 Agent 发现相同事实时向主任务返回协调请求。单一职责内工作仍可由主任务完成，验证范围按风险从 diff/解析扩到集成、发布或真实环境。
- 显式 Explore 的研究保持只读窄授权；主任务发现多个候选问题、依赖图或正式恢复时打开 Manager Gate。一个窄研究可由主任务直接派发；Explore 委派 Agent 只返回研究结果或协调请求，就绪判定与派发规则由 Coordination 定义。
- 主任务 → 通过显式入口、Planner 或 Roadmap 进入 Explore → 必须完整读取 Explore Skill，并按其输入、动作、输出与停止边界推进 → Explore 结果返回调用节点。
- 显式 Roadmap 不接受 Sacha 或进入生产 Role；事实或 Human 决定不足时只路由 Explore 并把结果返回 Roadmap，自包含正文就绪后只路由 document-project，写入结果返回 Roadmap 并结束当前独立规划。
- 三个 Gate 全关且无需恢复时，Executor 在当前上下文完成，不加载无消费者的 Assurance、Coordination、Artifact 或 Runtime Adapter。

### 2.1 能力加载

本节沿用[术语合同](terminology-contract.md)的能力加载策略；Project Integration 没有已确认 Binding 时不推导策略：

- `on-demand`：当前节点需要该 capability 的领域结果时加载。
- `after-write-authorization`：目标 Scope 已有 Human 写入授权，且当前节点需要实施前约束或领域输入时加载；不表示可以执行 Skill 内的写入或运行操作。
- `review-only`：当前节点是显式或本合同路由的 Reviewer，且该 capability 会改变裁决时加载。
- `risk-matched`：当前 Scope、验收或已识别风险需要该 capability 的验证输入或证据时加载；不为形式完整自动执行编译、Runtime 或其他高成本动作。
- 当前节点 → 策略允许加载 → 完整读取规范 Skill 并另行核对 Role 边界、前置、副作用与授权 → 任一项不满足时只使用安全子集或回退项目规则、可发现 Domain Skill 和原生路线，并保留未验证项。

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

通用生命周期只按本合同推进：Direct 在当前任务完成；接受 Sacha 后按 Gate 进入 Planner/Explore、Executor、Reviewer 和文档候选；Manager 只在主任务内运行并返回调用节点。Planner 进入后必须先判断目标结果、Scope/Non-goals、验收及会改变方案的 Human 决定是否足以冻结；任一项未收口时必须路由 Explore，不得冻结或持久化 Spec，全部收口后才可形成 Spec。显式 Roadmap 使用第 2 节的独立路线，不进入该生产生命周期。进入 closeout 后按本合同第 5 节流转；显式调用 document-project 时直接进入当前文档目标，不接受 Sacha 或补走生产 Role；正常 Sacha 生命周期仍独立执行文档候选检查。Feedback 是主流程之外由 Human 在另一个真实任务手动调用的独立支持入口。不得新增隐藏阶段或旁路。

本节沿用术语合同定义的普通批准、明确迁移批准、可靠迁移信号和执行任务迁移前提；本合同只规定这些判断产生的流程路由。

主任务 → Human 审阅 Spec 前 → 只依据可核实事实判断可靠迁移信号，并按 Human Interaction Contract 给出普通批准、明确迁移批准和要求调整 → 信号成立时将明确迁移批准置首，否则将普通批准置首。

Human → 选择普通批准 → 主任务进入 Executor。

Human → 选择明确迁移批准 → 主任务停止实施和写入派发并核对执行任务迁移前提 → 全部满足时由 Adapter 查询、复用或创建唯一目标任务；标识/去重、单写入者与 Owner 转移归 Coordination。

Human → 要求调整 → 返回 Planner。

Human → 取消或不再继续 → 主任务结束。

主任务 → 明确迁移批准不满足执行任务迁移前提 → 报告缺口与恢复条件并停止迁移 → 条件恢复后重新核对；只有 Human 改为普通批准才进入 Executor。

目标任务唯一确定并取得最小 Handoff 后，任务迁移才把工作流 Owner、剩余生命周期与派发权交给目标任务；来源主任务交付目标任务 reference 后结束，不等待返回。目标任务成为主任务并继续同一生命周期与独立 Review，迁移不改变 Gate；调度和 Owner 转移由 Coordination 处理。

Human 可因具体流程问题、使用反馈、插件开发建议或能力想法，在另一个真实任务手动调用 Feedback。该调用本身授权来源任务进行有界只读调查，并查询、复用或创建唯一反馈目标任务，不再追加创建确认，也不进入批准 Spec 后的执行任务迁移分支。来源任务交付 reference 后结束且不等待目标任务终态；目标任务按 Intake Contract 作为普通任务重新判断，并使用通用的 Direct、Planner、Explore、Executor、Reviewer、Manager、迁移和收尾规则。Feedback 调用不授权目标任务写入或执行外部动作。

动态路由：出现 Planner Gate 新事实 → Planner；Planner 冻结条件不足 → Explore；Explore 返回后仍不足 → 继续 Explore，足够后才冻结 Spec；Roadmap 事实不足 → Explore → Roadmap，正文就绪 → document-project → Roadmap 结束；新增高影响授权 → Human；Reviewer 路由按 Assurance；委派/返回失败按 Coordination。
Scope 内局部实现判断由 Executor 自主完成；环境不可用先耗尽同 Scope 安全替代。

主任务直接推进 Role 完成结果、已批准方案向 Executor 的转换、同 Scope 返修/补证据/复验、唯一 Owner 路由和已授权收尾。Direct Scope 由用户目标与明确约束界定；只有 Human 或 Spec 明确指定时，预计文件列表才成为硬性允许列表。

## 5. closeout 流转

closeout 当前动作为项目文档请求时，主任务将其作为 `human-request` 交给 `document-project`；不检查或修改 Spec，也不替代本合同第 6 节的正常文档候选。

closeout 当前动作为 Spec 完成时，主任务只在当前任务已是 `goal_complete`、必需验证与适用 Review 已满足后，按 Artifact Protocol 原位完成当前唯一已批准 Spec；任何条件不足都失败关闭，且不把 Human 请求当作完成证据。

closeout 当前动作为组合动作时，主任务先核对两个动作的目标与授权。Spec 状态写入需要明确 Human 授权；项目文档仍服从 Project Integration，`per-write-confirmation` 不被组合请求替代。两个动作预检完成前不写；通过后先完成 Spec，再以 `human-request` 进入 `document-project`。文档动作后续失败时保留合法的 Spec 完成结果，并报告部分完成与文档恢复入口。

## 6. 项目文档

Human 显式调用 document-project 时，当前请求直接形成该 Skill 的输入，不要求先存在 Workflow 收尾候选。显式发布文档目标绕过 Project Integration，使用明确的 `create | update`、update preimage 和模板来源完成原子写入；其他请求继续服从已确认的 Project Integration。Roadmap 路由时，当前显式 Roadmap 请求和已形成正文构成文档输入。

完成实现及所需验证/Review 后，主任务只用当前任务最终事实检查一次项目文档候选。候选必须有持久产品变更（delta），并至少满足一项：已批准 Spec 的实质方案已经落地；形成对后续消费者有用的新/改能力、架构、数据、运维或恢复知识；存在经最终实现和证据证实、且有跨任务消费者的项目上下文（Project Context）候选。

纯问答、无持久变更、仅完成任务证据索引，或没有上述持久知识的一行/局部修复，均静默跳过。没有已确认的 Project Integration、策略为 `disabled` 或候选不成立时结束检查；候选成立时才读取 `document-project`：`on-request` 只询问一次是否生成，并以 Human 的肯定答复形成请求；`required-at-closeout` 进入合法收尾。写入服从 Project Integration 的 `bounded-closeout | per-write-confirmation`。

文档状态独立于 Execution Report/Review；只有项目策略把文档列为阻塞性 Acceptance 时才阻止关闭已完成任务。
