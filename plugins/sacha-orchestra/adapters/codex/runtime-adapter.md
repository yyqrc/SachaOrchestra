# Codex Runtime Adapter（运行时适配器）

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
| Human 提问 | 当前宿主允许的提问工具或普通文本 | 先按 Human Interaction 区分必要信息、可选偏好与动作批准，再核对当前工具用途。`request_user_input` 仅在当前宿主允许该类问题时使用；宿主限制其只用于可选澄清时，不用于必要输入或批准，改用宿主允许的方式；不得把无答复时的默认继续用于必需答案或批准 |
| Human 进度 | `commentary` | 只映射 Core 已判定需要展示的新事实、风险、阻塞或计划变化 |
| Human 最终结果 | `final` | 汇总当前 Owner 已产出的结果、证据、风险、未验证项与下一步 |
| 独立任务结果等待 | `wait_threads` | 仅用于有明确结果消费者的依赖或全新验证；Owner 转移不调用 |
| Roadmap 后续 Sacha Planner 任务创建 | `create_thread` + 一次有界 `wait_threads` | Human 已确认 Roadmap 明确推荐的 Sacha Planner 任务时创建；不是 Owner 迁移，不继承 Roadmap 授权 |
| Feedback 目标任务查询 | `list_threads` + 有界 `read_thread` | 只为唯一反馈标识查询；候选需要消歧或存活状态证据时才读对应任务 |
| Feedback 目标任务创建 | `create_thread` | Human 在另一真实任务显式调用 Feedback 且无唯一匹配时恰好一次；类型为单向用户任务 Owner 转移 |
| 用户可见任务迁移 | `create_thread` | 只处理明确迁移批准；类型为用户任务 Owner 转移，Source 交付 reference 后结束 |
| 目标任务消息交付 | `create_thread(prompt=...)` / `send_message_to_thread` | 新建目标把最小 Handoff 放入初始 `prompt`；复用目标按原生标识发送一次；交付失败时不转移 Owner |

### 2.1 v2 能力核对

首次子代理动作前，只接受当前会话实际提供的 `collaboration.spawn_agent` 及 `fork_turns` 参数，并核对 `send_message`、`followup_task`、`wait_agent`、`interrupt_agent`、`list_agents`。模型名、磁盘配置或其他会话先例不能替代本会话的工具说明。

还须按第 3 节核对能力类型与逐次模型字段能否组合；仅有 v2 名称不足以证明这些字段存在。接口不支持、配套能力缺失、结构冲突或无法唯一判断时，报告具体错误并停止受影响调用，不使用 v1、通用代理或其他接口替代。

### 2.2 子代理传输

| 动作 | v2 调用 | 约束 |
| --- | --- | --- |
| 首次创建 | `collaboration.spawn_agent` | 仅主任务调用，每个工作单元至多一次；参数按第 3 节 |
| 运行中补充或改向 | `send_message` | 仅同一标识、Owner 和连续目标；新独立目标重新判断就绪条件 |
| 已结束回合后继续同一目标 | `followup_task` | 复用原标识，不借复用绕过范围与就绪判断 |
| 等待 | `wait_agent` | 只在真实依赖处等待；通知或超时不等于进程终止 |
| 中断当前回合 | `interrupt_agent` | 仅取消、失活或继续会增险时使用；代理仍可接收后续消息 |
| 核对与恢复标识 | `list_agents` | 有界查询原目标；无唯一标识时停止，不创建替代写入者 |
| 释放已完成目标 | 无独立关闭工具 | 消费结果并保留原始标识与证据 |

中断成功只证明当前回合被中断。接管写入前还须从代理状态和相关进程、任务或工具结果确认写入已停止；若底层操作仍运行或状态未知，只暂停有双写风险的部分，不把通知记录成完全取消。

### 2.3 Codex Role 调用面

主任务按第 3 节为 Planner、Reviewer、Executor、Explore 研究和普通工作单元组装首次创建参数；Role 作为评估输入，协作界面只决定传输编码。Manager 在主任务内运行，不是委派 Agent。委派 Agent 满足条件时返回协调请求，不调用子代理传输。

#### 2.3.1 Roadmap 后续 Sacha Planner 任务

Roadmap 已完成、其当前推荐明确说明另开 Sacha Planner 任务形成完整 Spec，且 Human 随后确认创建时，Adapter 创建一个用户可见 Codex 任务：

1. 使用当前项目对应的已保存 Codex Project；无法唯一确定时先让 Human 消歧，不创建 projectless 替代任务。
2. `create_thread(prompt=...)` 的初始输入必须显式写明“使用 Sacha Planner”，并携带唯一 Roadmap path、候选 Spec 目标/Scope、已确认决定、阻塞性未决项、当前只读边界与未授予的实施动作。不得把“冻结完整 Spec”弱化为普通调查或聊天草案，也不得复制整份 Roadmap。
3. 创建成功后只调用一次有界 `wait_threads` 核对目标任务已经按显式 Planner 请求开始；目标再次询问是否使用 Sacha、按 Direct 展开完整领域调查或初始输入丢失时，报告交接偏差并保留唯一目标 reference，不创建第二个任务。
4. 目标任务独立读取项目规则、Workflow 和 Planner Skill；Roadmap 的写入授权、任务状态与未落盘上下文不随创建传递。来源任务交付目标 reference 后结束，不等待完整 Spec 终态。

Roadmap 只推荐普通任务、推荐没有明确 Sacha Planner，或 Human 没有确认创建时，不进入本节；新任务按普通 Intake 重新判断。

### 2.4 Human 手动调用的 Feedback 转移

Adapter 消费 Coordination Contract 返回的反馈标识、匹配和 Owner 转移判断，不核对执行任务迁移前提。查询使用 `list_threads`；候选标识或存活状态需要确认时有界调用 `read_thread`。唯一活跃/可恢复目标按原生标识调用一次 `send_message_to_thread`；需要新目标时把同一最小 Handoff 放入初始 `prompt`，恰好调用一次 `create_thread` 并保留原生目标任务标识；`no_op` 只返回既有 reference；无法消歧时保留候选和原始缺口。

目标任务消息成功交付反馈目标、必要规则/证据 reference 和 Owner 转移说明后，来源任务展示原生目标任务 reference 并结束；消息或创建失败时来源任务保持 Owner。该 Owner 转移不等待目标终态。

### 2.5 用户可见任务迁移

Adapter 消费 Workflow/Coordination 已确认的迁移标识与转移动作。进入本节后，来源主任务不再实施或派发写入：

1. 唯一现有目标只有在按原生标识调用一次 `send_message_to_thread`，成功交付最小 Handoff 与 Owner 转移说明后才复用；不唯一或 Spec/Entry Condition/Owner 不可证明时暂停。
2. 无匹配且已有明确迁移批准时，把最小 Handoff 放入初始 `prompt` 并调用恰好一次 `create_thread`；查询、消息交付或创建失败且未完成 Owner 转移时，来源主任务保持唯一 Owner 并报告恢复条件，不进入 Executor。
3. 唯一目标取得最小 Handoff（规则入口、批准 Spec、必要 Artifact/证据 reference 和未携带的标识）后才完成 Owner 转移。Source 展示目标 reference 后结束，不调用`wait_agent`、`wait_threads` 或其他终态等待；后续 Execute、委派 Agent、Review、返修和收尾由目标任务负责。
4. 重复批准、重试或恢复只复用同一目标 reference；成功创建后 Source 不恢复写入者。`spawn_agent`、完整历史分叉和委派 Agent 都不取得迁移标识。

### 2.6 依赖等待

Adapter 消费 Coordination 的依赖屏障与结果消费者结论：

- 子代理依赖使用`collaboration.wait_agent`；独立依赖或全新验证任务使用带 `cursor` 的 `wait_threads`。
- 调用等待前推进其他不依赖结果且不冲突的就绪工作。
- 超时返回存活状态快照；相同进度沿用现有快照，目标标识保持不变。
- Owner 转移在交付目标 reference 后结束。

### 2.7 Code Mode 只读批量传输

主任务只在当前会话实际暴露可执行 Code Mode、[canonical Runtime asset](code-mode-batch.js) 可达、`ALL_TOOLS` 能唯一访问全部目标工具且参数结构可核对时选择该传输；产品说明、磁盘配置、模型能力或其他会话先例不能替代当前工具面证据。任一前置不足时在嵌套调用前说明未选择 Code Mode 的具体原因并使用直接读取，不把 Code Mode 设为正确性前提或失败恢复。

当前宿主映射为 `functions.exec(<JavaScript>)`。调用方先设置 `globalThis.CODE_MODE_CALLS` 与 `globalThis.CODE_MODE_OUTPUT_LIMIT`，再原样附加 asset 内容；不得修改 asset 控制流或把其副本写入 Adapter、Skill 或测试。asset 从 `ALL_TOOLS` 核对嵌套工具，通过 `tools.<normalized_name>(args)` 调用，并用 `text(...)` 返回 `schema_version: 1` 的有界结构化结果。

Code Mode 只接收调用节点已确认的非 Agent 只读调用：至少两个调用已就绪、输入自足且相互独立；调用之间不需要模型解释、授权、风险或 Scope 判断；结果消费者和失败处理已明确。Agent 创建/消息/等待/取消/恢复/关闭、文件或配置写入、消息发送和外部资源动作必须直接调用，不得进入 `CODE_MODE_CALLS`。asset 不生成工作单元、不判断副作用，也不选择 Role、模型、路由、依赖、授权或重试。

当前工具已能以一次调用接收整个目标集合时直接使用原生批量入口；调用少于两个、非只读、结果无需代码缩减或需要中途语义判断时直接调用。分页、排序、过滤、去重、计数和固定字段分支只有在上限与停止条件已给定时才可留在 asset；字段缺失、冲突或需要语义解释时立即返回模型。

输入校验、输出上限预检或工具解析在 Promise 创建前失败时没有嵌套调用，主任务可重新评估直接读取。任一嵌套调用已开始、返回不完整或状态未知时保留原始 call/reference 并暂停受影响批次，不直接重放；`Promise.allSettled` 中单项拒绝只形成对应逐项结果，不掩盖或重放其他调用。

#### 2.7.1 Runtime asset 输入与结果

`CODE_MODE_CALLS` 每项只携带稳定 `unit_id`、当前 `ALL_TOOLS` 中的 `normalized_name`、完整 `args`，以及消费者决定的 `result_fields`/`reference_fields`；两个投影字段都必须显式传入字符串数组，`[]` 表示不返回该类字段。`CODE_MODE_OUTPUT_LIMIT` 必须是正整数。

asset 在创建 Promise 前校验调用数、单元标识、投影、输出上限和工具唯一可调用性，并预检最小 `outcome_unknown` 包络；随后每项只调用一次并按输入顺序返回 `settled`、`output_limit_exceeded` 或 `outcome_unknown`。Runtime 场景必须保留 asset path/hash、实际外层程序、嵌套 caller 关系、逐项原始结果和最终输出；源码字符串、fixture 或执行者自报不能替代真实行为证据。

### 2.8 原生工具搜索

调用节点需要工具时，按当前任务实际暴露的入口处理：目标工具已在模型工具面时直接调用；目标工具不可见且原生 `tool_search` 可用时，用 capability 或 namespace 搜索，并只调用唯一匹配的返回结果；所需能力不可见、搜索没有匹配或结果不唯一时，报告能力缺口并停止受影响调用，继续独立工作。普通事实读取可重新评估当前已暴露、输入输出和副作用已核对且在授权内的等价能力；接口身份本身属于验证目标、已有更严格传输约束，或写入状态未知时不得替换或重放。没有新证据、不同且可检验的假设或已确认的等价能力时，保留结果并报告恢复条件，不反复搜索或重试。

根任务与每个 child 分别执行上述判断，并在 spawn、resume、compaction 或 Runtime 重连后重新检查。MCP 工具使用当前实际表面；Code Mode 工具只按第 2.7 节从当前 `ALL_TOOLS` 选择已确认目标，不能替代模型工具面或 `tool_search` 结果。

工具发现不改变 Scope、授权或外部副作用边界。Researcher 只使用直接可见或搜索得到的只读工具；需要 `exec_command`、`apply_patch` 或其他写入入口时返回调用节点。

## 3. 能力类型与模型路由

首次创建前，主任务依次核对工作单元的能力边界、模型路线和当前 v2 参数。角色、就绪、范围与授权仍由核心合同和技能决定；当前主任务的模型保持用户选择。

### A. 判断所需事实

- 用户或已批准范围有精确型号/强度要求时优先消费；不支持时停止，不能自动换档。
- 只读研究、获授权实施和正式独立复核分别需要对应能力类型。角色不等于型号，正式复核的独立性不能由更强模型替代。
- `bounded` 表示输入、边界、完成检查自足；其负荷区分 `light / nontrivial`。`broad` 表示需要跨负责位置综合、集成或仍有重要边界推理，区分 `standard / critical`。
- 同时检查实施边界和失败影响：破坏性删除/覆盖、跨消费者持久身份或数据解释变化，以及依赖并发、兼容和跨系统生命周期的正确性，至少按 broad；困难回退、跨系统耦合或关键冲突为 critical。普通可重建文件输出本身不自动升级。
- 较大有效上下文的依据是多个模块、调用/数据链或约束必须共同参与判断。文件数量、仓库体积、累计 token、正式复核或发布名称本身不决定型号或强度。
- 输入、范围、写入者、完成检查或独立性无法可靠判断时停止派发。只保存会改变当前选择的事实，复用仍有效的评估。

### B. 有序自动路线

首次命中即停止；不建立核心合同的新状态或固定上下文阈值。

| route_id | 判断 | 请求字段 |
| --- | --- | --- |
| `human_exact` | 用户或批准范围精确指定 | 原样使用当前工具支持的型号与强度；额外参数不支持时停止 |
| `astra_high` | broad + critical，包括有对应事实的独立复核 | `model="gpt-6-astra"`, `reasoning_effort="high"` |
| `astra_medium` | 非 critical，但需要联合持有较大有效上下文，包括相应复核 | `model="gpt-6-astra"`, `reasoning_effort="medium"` |
| `sol_medium` | 其余 broad + standard 或普通正式独立复核 | `model="gpt-5.6-sol"`, `reasoning_effort="medium"` |
| `luna_max` | bounded + nontrivial | `model="gpt-5.6-luna"`, `reasoning_effort="max"` |
| `luna_xhigh` | bounded + light | `model="gpt-5.6-luna"`, `reasoning_effort="xhigh"` |

Astra 最高自动档为 high；用户以后精确指定且工具支持的其他强度仍走 human_exact。长上下文需求不自动要求最高档。计费和窗口不写成模型无关规则，采用宿主已确认的配置与证据，不预置窗口或压缩比例。

### C. 组合首次创建参数

| 单元 | agent_type | 能力边界 |
| --- | --- | --- |
| 只读研究 | `sacha_researcher` | 只接收 research-ready 单元及其必需的只读工具 |
| 实施/验证 | `sacha_executer` | 只接收已有授权的 execution-ready 单元，沿用父任务实际权限边界 |
| 正式独立复核 | `sacha_reviewer` | 未参与当前方案和实现；验证副作用必须在既有授权内 |

当前 v2 必须实际暴露 `agent_type`、`model`、`reasoning_effort` 与 `fork_turns` 的组合，并发现所选能力类型；不能把某一 Desktop 的字段推广到 Work 或其他会话。缺失类型或必需字段时停止，不省略能力类型改用普通代理。

调用 `collaboration.spawn_agent`，默认 `fork_turns="none"`；当前 schema 提供 task_name 时使用稳定短名，必填字段不得省略。只有未落盘用户决定确需携带时才使用最小正整数轮数，不复制完整父历史。message 自包含目标、范围、输入、能力/副作用、完成检查、停止及协调请求返回条件。

能力类型不固定 model 或 reasoning effort，自动路线显式传 B 节字段。固定模型类型只供与其固定设置一致的精确请求，不能覆盖不可改写的模型，也不能作自动回退。显式字段、类型默认值和父任务继承的优先级只在当前工具允许该组合时取证；参数被接受不等于实际模型、权限或工具面已经验证。

工作单元需要 Project Integration 已确认的 Skill loading 时：

1. 先取得唯一 canonical Skill 与适用 load policy；策略不允许当前节点时停止。
2. 从当前 Runtime catalog 取得唯一可见、可读的绝对 SKILL.md path，完整读取并核对角色、依赖、能力与副作用；不得扫描磁盘猜版本。
3. message 同时给出身份、path、允许能力和要求 child 在任务动作前读取原文。必需插件或工具在 child 不可达时停止，不发送省略 Skill 的替代单元。
4. 只有 spawn schema 自身支持结构化 Skill input 时才传其字段；App Server 的 skill input 不证明子代理接口支持。未暴露时，明确的自包含 message 是该接口的 Skill 输入方式。

### 3.1 错误与继续

接口、能力类型或所选模型不支持时均报告原始错误并停止受影响调用，不自动切换接口、类型、型号或强度。调用已启动、返回标识或结果未知时保留原目标；忙碌、超时、执行失败与取消不能触发替代创建。

用户给出新的明确选择或原目标的前提已发生可证明变化时，重新核对该部分范围、授权、写入者和独立性；合法继续使用原生标识与相应继续工具，不把恢复误作自动回退。

## 4. 进度与证据边界

Adapter 回传 Codex 原生标识、直接父子关系、协作界面/命名空间、请求的 `agent_type` 与模型路线、决定自动路线中任务形态与负荷的最小直接事实 reference、实际启动、完成、回合中断及相关写入操作状态、工具错误和结果 reference。工具面证据分别保存当前任务或 child 的初始模型可见 schema、原生 `tool_search` 是否存在及其加载结果、实际调用轨迹；Code Mode 另回传 asset path/hash、外层调用 reference、`ALL_TOOLS` 中命中的目标、稳定单元标识、完整嵌套参数、逐项结果和最终 `schema_version`。只返回最终摘要或丢失逐项结果/reference 不构成批量传输证据。`spawn_agent` 被接受只证明参数有效且委派 Agent 已创建；实际模型、推理强度、permission profile、feature/Skill 降权、工具暴露与行为分别需要 Runtime 遥测、子任务配置回读、原生 schema 或工具轨迹，配置文件、schema 接受和委派 Agent 自报都不能互相替代。单层派发由宿主原始调用、父任务/session/depth 元数据与子任务工具轨迹证明，只有当前 Runtime 不提供其中必要记录时才保留精确缺口。源码与结构检查不证明实际派发或模型选择；Tool Search、Code Mode、嵌套调用、v2 能力核对、`spawn_agent`、`create_thread`、等待/取消、模型可用性和 Runtime 行为使用当前会话的真实 Runtime 证据。
