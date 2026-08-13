# Codex Runtime Adapter（运行时适配器）

> 实现：Intake Contract 9；术语合同 4；Workflow Contract 26；Human Interaction Contract 2；Assurance Contract 3；Coordination Contract 14；Artifact Protocol 7
> 状态：规范性 Codex 传输映射

## 1. 边界

本文把 Core/Role 已决定的动作映射到 Codex 原生任务/子代理传输。Owner 依据：

- [Intake Contract](../../core/intake-contract.md)
- [术语合同](../../core/terminology-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

提炼术语、Intake、Role、Gate、readiness、Manager 职责、批准路由和 Artifact 结构由对应 Core/Skill 拥有。本 Adapter 消费已确定的 Human 交互动作与路由要求；只有主任务执行 Codex 子代理传输。Direct/当前上下文保持当前模型与 Owner。

## 2. 原生传输与协作界面选择

Human 交互和独立任务传输不随子代理协作界面改变：

| 调用面 | Codex 原生映射 | 约束 |
| --- | --- | --- |
| Human 互斥选择 | `request_user_input` | Human Interaction 判定需要选择后调用；推荐项置首。能力不可用或需要自由输入时使用普通文本提问 |
| Human 进度 | `commentary` | 只映射 Core 已判定需要展示的新事实、风险、阻塞或计划变化 |
| Human 最终结果 | `final` | 汇总当前 Owner 已产出的结果、证据、风险、未验证项与下一步 |
| 独立任务结果等待 | `wait_threads` | 仅用于有明确结果消费者的依赖或全新验证；Owner 转移不调用 |
| Feedback 目标任务查询 | `list_threads` + 有界 `read_thread` | 只为唯一反馈标识查询；候选需要消歧或存活状态证据时才读对应任务 |
| Feedback 目标任务创建 | `create_thread` | Human 在另一真实任务显式调用 Feedback 且无唯一匹配时恰好一次；类型为单向用户任务 Owner 转移 |
| 用户可见任务迁移 | `create_thread` | 只处理明确迁移批准；类型为用户任务 Owner 转移，Source 交付 reference 后结束 |
| 目标任务消息交付 | `create_thread(prompt=...)` / `send_message_to_thread` | 新建目标把最小 Handoff 放入初始 `prompt`；复用目标按原生标识发送一次；交付失败时不转移 Owner |

### 2.1 协作界面判定

首次子代理动作前，Adapter 只按当前会话实际暴露的命名空间、工具集和参数结构选择一次协作界面：

| 协作界面 | 必须同时成立 | 不属于该界面 |
| --- | --- | --- |
| `v1` | `multi_agent_v1.spawn_agent` 的参数结构含 `fork_context`，并存在 `send_input`、`wait_agent`、`close_agent` | `fork_turns`、`send_message`、`followup_task`、`interrupt_agent`、`list_agents` |
| `v2` | `collaboration.spawn_agent` 的参数结构含 `fork_turns`，并存在 `send_message`、`followup_task`、`wait_agent`、`interrupt_agent`、`list_agents` | `fork_context`、`send_input`、`close_agent`、`resume_agent` |

模型名、模型目录的 `multi_agent_version`、功能开关、OpenCodex 配置和父会话先例都不能替代当前工具面证据；它们最多说明新会话的预期。两套工具同时出现、必需配套工具缺失、参数结构与上表冲突或协作界面无法唯一判定时暂停，不混用命名空间、参数或恢复动作。协作界面在当前会话内保持不变；外部切换后由新会话重新判定。

### 2.2 子代理传输

| 动作 | `v1` | `v2` | 共同约束 |
| --- | --- | --- | --- |
| 首次创建 | `multi_agent_v1.spawn_agent` | `collaboration.spawn_agent` | 只由主任务调用；每个工作单元至多一次；使用第 3 节参数 |
| 运行中补充或改向 | `send_input`；立即改向时显式 `interrupt=true` | `send_message` | 只复用同一 Owner 下、强依赖既有上下文的委派 Agent；新 Scope 新建工作单元 |
| 终态后继续同一目标 | 目标仍未关闭时直接 `send_input`；已关闭时先 `resume_agent` 再 `send_input` | `followup_task` | 仅同一标识、Owner 和连续目标；不得借复用绕过新的 readiness 判断 |
| 等待结果 | `wait_agent` | `wait_agent` | 仅在 Coordination 判定依赖屏障后消费终态/结果；超时只报告存活状态 |
| 取消或停止写入者 | `close_agent`，再用 `wait_agent` 确认 `shutdown` 或其他终态 | `interrupt_agent`，再用 `wait_agent` 确认 `terminal/cancelled` | 仅 Human 取消、失活或继续会造成双写/增险时使用；确认终止后才接管 |
| 释放已完成目标 | 消费结果后调用 `close_agent` | 无独立关闭工具 | 不丢失终态结果 reference |
| 标识恢复 | 保留首次创建返回的 id；已关闭目标只用 `resume_agent` 恢复 | 用 `list_agents` 有界查找原生标识 | 无唯一标识时暂停，不创建替代写入者 |

### 2.3 Codex Role 调用面

主任务按第 3 节为 Planner、Reviewer、Executor、Clarify 研究和普通工作单元组装首次创建参数；Role 作为评估输入，协作界面只决定传输编码。Manager 在主任务内运行，不是委派 Agent。委派 Agent 满足条件时返回协调请求，不调用子代理传输。

### 2.4 Human 手动调用的 Feedback 转移

Adapter 消费 Coordination Contract 返回的反馈标识、匹配和 Owner 转移判断，不核对执行任务迁移前提。查询使用 `list_threads`；候选标识或存活状态需要确认时有界调用 `read_thread`。唯一活跃/可恢复目标按原生标识调用一次 `send_message_to_thread`；需要新目标时把同一最小 Handoff 放入初始 `prompt`，恰好调用一次 `create_thread` 并保留原生目标任务标识；`no_op` 只返回既有 reference；无法消歧时保留候选和原始缺口。

目标任务消息成功交付反馈目标、必要规则/证据 reference 和 Owner 转移说明后，来源任务展示原生目标任务 reference 并结束；消息或创建失败时来源任务保持 Owner。该 Owner 转移不等待目标终态。

### 2.5 用户可见任务迁移

Adapter 消费 Workflow/Coordination 已确认的迁移标识与转移动作。进入本节后，来源主任务不再实施或派发写入：

1. 唯一现有目标只有在按原生标识调用一次 `send_message_to_thread`，成功交付最小 Handoff 与 Owner 转移说明后才复用；不唯一或 Spec/Entry Condition/Owner 不可证明时暂停。
2. 无匹配且已有明确迁移批准时，把最小 Handoff 放入初始 `prompt` 并调用恰好一次 `create_thread`；查询、消息交付或创建失败且未完成 Owner 转移时，来源主任务保持唯一 Owner 并报告恢复条件，不进入 Executor。
3. 唯一目标取得最小 Handoff（规则入口、批准 Spec、必要 Artifact/证据 reference 和未携带的标识）后才完成 Owner 转移。Source 展示目标 reference 后结束，不调用任一协作界面的 `wait_agent`、`wait_threads` 或其他终态等待；后续 Execute、委派 Agent、Review、返修和收尾由目标任务负责。
4. 重复批准、重试或恢复只复用同一目标 reference；成功创建后 Source 不恢复写入者。`spawn_agent`、完整历史分叉和委派 Agent 都不取得迁移标识。

### 2.6 依赖等待

Adapter 消费 Coordination 的依赖屏障与结果消费者结论：

- 子代理依赖使用已选协作界面的 `wait_agent`；独立依赖或全新验证任务使用带 `cursor` 的 `wait_threads`。
- 调用等待前推进其他不依赖结果且不冲突的就绪工作。
- 超时返回存活状态快照；相同进度沿用现有快照，目标标识保持不变。
- Owner 转移在交付目标 reference 后结束。

## 3. 子代理路由合同

主任务每次首次创建前必须按 A → B → C 顺序处理：A 提供不依赖 Runtime 的事实，B 进行一次有序路由决策，C 按第 2.1 节已选协作界面组装完整原生参数；路由与协作界面是两个独立判断。A、B 或 C 任一步未完成时不得调用 `spawn_agent`。

### A. 评估输入（不依赖 Runtime）

Adapter 读取 Coordination Contract 产生的路由要求，归纳四项 Runtime 路由输入：

| 输入 | 判断 |
| --- | --- |
| Human 或批准 Scope 的精确路由（若有） | 最高优先级；验证后原样使用，不自动改写 |
| Role | Workflow 与 Reviewer Skill 已确定的正式独立 Reviewer 使用 Sol；其他 Role 不单独决定模型 |
| 任务形态 | `broad`：需要跨 Owner 综合、复杂集成或边界仍需推理；`bounded`：目标、输入、边界和直接验证均自包含 |
| 负荷 | `broad` 只分 `critical / standard`；`bounded` 只分 `nontrivial / light` |
| 安全状态 | Scope/revision、上下文需求、写入者状态和 Reviewer 独立性决定能否派发/回退 |

安全、权限、持久数据、破坏性变更、不可逆外部动作或广泛兼容风险至少按 `broad` 处理；其中困难回退、跨系统耦合或关键冲突为 `critical`。

按 Workflow 与 Reviewer Skill 已确定的正式独立 Reviewer 使用 Sol，不因 Scope 自包含而改用 Luna：Scope、Baseline、裁决问题、原始证据和停止条件明确，且没有上述 `critical` 事实时选择 `sol_medium`；存在 `critical` 事实时选择 `sol_xhigh`。文件数量、发版动作或正式 Review 名称本身不得触发 `sol_xhigh`。

上述字段只供本 Adapter 选择 Runtime 路由；就绪状态、依赖满足和 Manager 派发由 Core/Skill 负责。

### B. 有序路由决定（首次命中即停止）

除精确路由外先判断正式独立 Reviewer，再对其他工作单元判断“形态 × 负荷”，首个命中即停止：

1. `human_exact`：存在 Human/Scope 精确路由；无法解析或 Runtime 不支持时暂停，不自动换档。
2. `sol_xhigh`：正式独立 Reviewer 存在 `critical` 事实，或其他工作单元为 `broad + critical`。
3. `sol_medium`：正式独立 Reviewer 不存在 `critical` 事实，或其他工作单元为 `broad + standard`。
4. `luna_max`：`bounded + nontrivial`。
5. `luna_xhigh`：`bounded + light`。

正式独立 Reviewer 的 Baseline、裁决问题、原始证据、停止条件、独立性或 `critical/standard` 无法可靠判定时暂停；其他工作单元无法可靠判定 `broad/bounded`、`bounded` 输入不自包含或 Scope 不明确时暂停。Planner、Reviewer、Executor、Clarify 研究和普通委派 Agent 共用这四档自动选择。

Clarify 的单个研究委派 Agent 和 Manager 协调的研究单元复用同一顺序；研究结果返回调用节点。

### C. 按协作界面映射 `spawn_agent`

C 只接受 B 的 `route_id` 和第 2.1 节唯一确定的协作界面。调用参数必须由“协作界面字段 + 路由字段”完整组成并原样提交；表中未列出的界面参数不得传入另一版本。不得用单独的通用 `agent_type`、父任务默认模型/推理强度继承，或只修补某个被拒字段来替代 B/C。调用因协作界面或路由字段不完整、不匹配而在 `accepted/started` 前被拒绝时，主任务必须从 A 重新核对并执行完整 A → B → C，不得只修补被拒字段后重试。已按 B/C 完整提交的主路由实际报告 `unavailable/failed` 时，不重新提交主路由；只有满足第 3.1 节全部条件时才直接执行该节唯一回退。

#### C.1 协作界面字段

| 协作界面 | 调用与必填字段 | 上下文参数 |
| --- | --- | --- |
| `v1` | `multi_agent_v1.spawn_agent(message=<工作单元>)`；v1 没有 `task_name` | 自包含输入固定 `fork_context=false`。不得自动使用 `true` 复制完整父历史；缺少未落盘事实时先把最小事实写入 `message`，无法自包含则暂停 |
| `v2` | `collaboration.spawn_agent(message=<工作单元>)`；参数结构暴露 `task_name` 时另传 `task_name=<稳定短名>`，未暴露时禁止发送 | 自包含输入固定 `fork_turns="none"`；确需携带未落盘 Human 决定时只传能补足决定的最小正整数轮数。不得使用完整历史分叉 |

`message` 必须自包含该工作单元的目标、Scope、输入 reference、完成检查和停止条件，并要求满足条件时返回协调请求；可用的 `task_name` 只标识工作单元，不承载语义。Adapter 不根据旧版本先例向当前参数结构添加未声明字段。

#### C.2 路由字段

| `route_id` | 精确路由字段 |
| --- | --- |
| `human_exact` | 使用当前协作界面参数结构已验证支持的精确 `agent_type/model/reasoning_effort/service_tier`；Human 可指定其他 `model`/推理强度，Adapter 不替换或降级。无法形成当前界面接受的完整参数、`model` 不在当前创建能力内或覆盖值被拒绝时暂停 |
| `sol_xhigh` | `model="gpt-5.6-sol"`, `reasoning_effort="xhigh"`；参数结构暴露 `agent_type` 时另传 `agent_type="default"`，未暴露时省略 |
| `sol_medium` | `model="gpt-5.6-sol"`, `reasoning_effort="medium"`；参数结构暴露 `agent_type` 时另传 `agent_type="default"`，未暴露时省略 |
| `luna_max` | `agent_type="sacha_luna_worker"`；命名定义固定 Luna/max，不覆盖 `model`、`reasoning_effort` 或 `service_tier` |
| `luna_xhigh` | `agent_type="sacha_luna_worker_xhigh"`；命名定义固定 Luna/xhigh，不覆盖 `model`、`reasoning_effort` 或 `service_tier` |

自动路由只有上述四种组合，不选择 Terra、Sol `high/max/ultra`、带提供方前缀的模型或未限定的通用 `explorer/worker/default`。除表内明确要求的组合外，主任务不得单独传入这些通用 `agent_type`，也不得省略路由字段以继承父任务默认值。其他模型只在 `human_exact` 中按当前协作界面能力原样使用，不因模型目录可见或一次冒烟验证自动进入路由表。

`sol_xhigh` 与 `sol_medium` 要求当前参数结构支持覆盖 `model` 和 `reasoning_effort`。`luna_max` 与 `luna_xhigh` 要求当前参数结构支持 `agent_type` 且已发现对应带命名空间的 Agent 类型；仅有磁盘配置或安装记录不构成运行时发现。任一要求不成立时按主路由不可用处理，且只有满足第 3.1 节全部条件才可走一次回退。

记录请求与实际协作界面、请求与实际路由；只有 Runtime 明确返回或可绑定遥测时才记录实际模型/推理强度。Direct/当前上下文不调用该映射。

### 3.1 单次回退路由

自动回退是独立的一次性路由。它只在主路由的原生调用**实际报告 `unavailable/failed` 且实例尚未 `accepted/started`**时，按同一评估使用下表唯一替代映射：

| 主路由 | `v1` 唯一回退 | `v2` 唯一回退 |
| --- | --- | --- |
| `luna_max` 或 `luna_xhigh` | `multi_agent_v1.spawn_agent`：`agent_type="default"`, `model="gpt-5.6-sol"`, `reasoning_effort="medium"`, `fork_context=false`，沿用原 `message` | `collaboration.spawn_agent`：`model="gpt-5.6-sol"`, `reasoning_effort="medium"`, `fork_turns="none"`，沿用原 `message`；参数结构暴露 `agent_type`/`task_name` 时分别沿用 `agent_type="default"`/原 `task_name`，未暴露时不传 |
| `sol_xhigh`、`sol_medium` 或 `human_exact` | 停止，不回退 | 停止，不回退 |

回退路由至多执行一次；自动路径保持表内四种主模型组合与一条替代映射。

调用方必须同时证明：

- 仍是同一 Task/Scope/revision，且回退不扩大授权、Scope、写入或验收；
- 没有写入迹象，旧写入者已进入 `terminal/cancelled`，且 Reviewer 独立性仍明确；
- 失败发生在 `spawn_agent` 建立 Owner 之前，并已记录请求/实际协作界面、请求/实际路由与原始失败原因。

任一条件不满足（包括可能已写入、旧写入者未终止、独立性不明、精确 Human/Scope 配置失败或回退再失败）立即暂停并生成有界偏差；不得连续试多档模型、静默改用 Runtime 默认值或再次创建同一 Scope 写入者。超时、忙碌、结果失败和用户取消都不属于“尚未 `started`”的自动回退。

## 4. 进度与证据边界

Adapter 回传 Codex 原生标识、直接父子关系、协作界面/命名空间、`accepted/started/terminal/cancelled`、工具错误和结果 reference。`spawn_agent` 被接受只证明参数有效且委派 Agent 已创建；单层派发须由首次等待前的实时 Agent 树证明。委派 Agent 自报只证明其输出，不能替代实际模型/提供方遥测。静态源码/测试的证据范围为本文结构与分支约束；协作界面发现、`spawn_agent`、`create_thread`、等待/取消、模型可用性和 Runtime 行为使用当前会话的真实 Runtime 证据。
