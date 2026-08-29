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

主任务按第 3 节为 Planner、Reviewer、Executor、Explore 研究和普通工作单元组装首次创建参数；Role 作为评估输入，协作界面只决定传输编码。Manager 在主任务内运行，不是委派 Agent。委派 Agent 满足条件时返回协调请求，不调用子代理传输。

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

调用节点需要工具时，按当前任务实际暴露的入口处理：目标工具已在模型工具面时直接调用；目标工具不可见且原生 `tool_search` 可用时，用 capability 或 namespace 搜索，并只调用唯一匹配的返回结果；搜索不可用、没有匹配或结果不唯一时，使用同一 Scope 与副作用边界内已经确认的原生 fallback，或者报告能力缺口。

根任务与每个 child 分别执行上述判断，并在 spawn、resume、compaction 或 Runtime 重连后重新检查。MCP 工具使用当前实际表面；Code Mode 工具只按第 2.7 节从当前 `ALL_TOOLS` 选择已确认目标，不能替代模型工具面或 `tool_search` 结果。

工具发现和 fallback 不改变 Scope、授权或外部副作用边界。Researcher 只使用直接可见或搜索得到的只读工具；需要 `exec_command`、`apply_patch` 或其他写入入口时返回调用节点。

## 3. 能力载体与模型路由

主任务每次首次创建前必须按 A → B → C 顺序处理：A 读取 Core 已判定事实与所需能力边界，B 选择模型路线，C 按当前协作界面组合 Agent 类型、模型和传输字段。自定义 Agent 提供 developer instructions、模型设置及 feature/Skill 降权；permission profile、sandbox、MCP、工具暴露和 Code Mode 集合沿用当前 Runtime。Role、readiness、Scope、授权和派发合法性仍由 Core/Skill 决定。

### A. 评估输入（不依赖 Runtime）

| 输入 | 判断 |
| --- | --- |
| Human 或批准 Scope 的精确路由（若有） | 最高优先级；验证后原样使用，不自动改写 |
| 能力边界 | 只读研究；正式独立 Reviewer；获授权的写入/验证单元 |
| Role | 正式独立 Reviewer 使用 Sol；其他 Role 不单独决定模型 |
| 任务形态 | `broad`：需要跨 Owner 综合、复杂集成或边界仍需推理；`bounded`：目标、输入、边界和直接验证均自包含 |
| 负荷 | `broad` 只分 `critical / standard`；`bounded` 只分 `nontrivial / light` |
| 安全状态 | Scope/revision、上下文需求、写入者状态和 Reviewer 独立性决定能否派发/回退 |

Coordination 判定的 `research-ready` 只读单元使用只读调查 Agent；正式独立 Reviewer 使用复核 Agent；`execution-ready` 写入单元使用实施 Agent。上下文污染风险只决定是否派发及选择哪类 Agent，不改变模型档位、Gate 或授权。

安全、权限、持久数据、破坏性变更、不可逆外部动作或广泛兼容风险至少按 `broad` 处理；其中困难回退、跨系统耦合或关键冲突为 `critical`。正式独立 Reviewer 不存在 `critical` 事实时选择 `sol_medium`，存在时选择 `sol_xhigh`；文件数量、发版动作或 Review 名称本身不得触发 `sol_xhigh`。

### B. 有序模型路由（首次命中即停止）

1. `human_exact`：存在 Human/Scope 精确路由；无法解析或 Runtime 不支持时暂停，不自动换档。
2. `sol_xhigh`：正式独立 Reviewer 存在 `critical` 事实，或其他工作单元为 `broad + critical`。
3. `sol_medium`：正式独立 Reviewer 不存在 `critical` 事实，或其他工作单元为 `broad + standard`。
4. `luna_max`：`bounded + nontrivial`。
5. `luna_xhigh`：`bounded + light`。

正式独立 Reviewer 的 Baseline、裁决问题、原始证据、停止条件、独立性或风险无法可靠判定时暂停；其他工作单元无法可靠判定形态/负荷、输入不自足或 Scope 不明确时暂停。Planner、Reviewer、Executor、Explore 研究和普通委派 Agent 共用本顺序。

### C. 按协作界面组合 `spawn_agent`

C 只接受 A 的能力边界、B 的 `route_id` 和第 2.1 节唯一确定的协作界面。首次创建参数由协作界面字段、`agent_type` 与模型路由组成；任一部分缺失时不得调用 `spawn_agent`。

#### C.1 协作界面字段

| 协作界面 | 调用与上下文 |
| --- | --- |
| `v1` | `multi_agent_v1.spawn_agent(message=<工作单元>, fork_context=false)`；v1 没有 `task_name`。缺少未落盘事实时先把最小事实写入 `message`，无法自足则暂停 |
| `v2` | `collaboration.spawn_agent(message=<工作单元>, fork_turns="none")`；参数结构暴露 `task_name` 时传稳定短名。确需携带未落盘 Human 决定时只传最小正整数轮数 |

`message` 必须自包含目标、Scope、输入 reference、完成检查、停止条件与协调请求返回条件；不得复制完整父历史。

工作单元消费已确认 Capability Binding 时，主任务在首次创建前按以下顺序组装；解析结果只进入本次调用，不写回 Project Integration：

1. 从 Binding 取得唯一 capability id、canonical Skill 身份与 load policy；当前节点不满足 policy 时停止，不加载或派发降级 child。
2. 只用当前 Runtime 的 Skill catalog/schema 把 canonical 身份解析为唯一可见项，并采用该项给出的绝对 `SKILL.md` path；不得扫描磁盘目录猜版本。path 不是绝对文件、不可读、身份不唯一或 Skill 不可见时停止。主任务完整读取该 Skill，并核对其插件/MCP 前置、具体副作用与当前 Role、Scope 和授权。
3. `message` 除上述通用内容外，还必须给出 capability id、canonical 身份、绝对 path、允许的能力/副作用边界，并要求 child 在任何任务动作前完整读取该文件，不依赖自动 Skill instructions 或目录发现。Skill 所需插件/MCP 在 child 工具面不可达，或其副作用超过当前边界时，必须在 `spawn_agent` 前停止，不派发不带 Skill 的 fallback child。
4. 只有当前 `spawn_agent` schema 自身暴露结构化 Skill input 时，才把同一 Runtime catalog 项的 `name/path` 一并传入；App Server `turn/start` 支持 `skill` input 不能证明 child transport 支持。当前 `collaboration.spawn_agent` 未暴露该字段时，使用上述自包含 `message`，不得只传名称。

#### C.2 能力 Agent

| 单元用途 | `agent_type` | 边界 |
| --- | --- | --- |
| 只读研究 | `sacha_researcher` | 必须由 Runtime 发现；只接收无写入授权的 `research-ready` 单元，并使用 Capability Binding 指向的插件 Skill/MCP 只读查询 |
| 正式独立 Reviewer | `sacha_reviewer` | 必须核对真实参与历史和输入来源；可执行裁决所需、已有 Scope/授权覆盖的临时验证与插件 Skill/MCP 操作，不默认修复交付实现 |
| 写入/验证 | `sacha_executer` | 必须由 Runtime 发现；不设置 `sandbox_mode`，沿用父任务实际 `sandbox_mode`，写入继续服从 Scope、授权和单写入者 |

`sacha_researcher`、`sacha_executer` 与 `sacha_reviewer` 的定义不得固定 `model` 或 `model_reasoning_effort`。DeepSeek 与 DeepSeek Pro 定义继续作为固定模型 Agent，仅供精确路线或兼容回退；它们不承载上述能力边界。Luna 由逐次 `model/reasoning_effort` 直接派发，不再使用固定模型 Agent。

当前协作界面必须实际暴露 `agent_type`、`model` 和 `reasoning_effort` 的组合参数，并发现目标 Agent 类型，才能组合能力 Agent 与逐次模型路线。当前 `v2` schema 具备这三个字段；覆盖优先级、feature/Skill 降权、permission profile、工具面与有效模型由场景证据确认。`v1` 只在当前工具面满足同一组合时使用统一映射；其他分支按已发现的兼容路线处理，目标 Role 缺少完成条件时停止派发。

#### C.3 模型路由字段与优先级

| `route_id` | 逐次字段 |
| --- | --- |
| `human_exact` | 使用当前协作界面已验证支持的精确 `model/reasoning_effort/service_tier`；不支持时暂停 |
| `sol_xhigh` | `model="gpt-5.6-sol"`, `reasoning_effort="xhigh"` |
| `sol_medium` | `model="gpt-5.6-sol"`, `reasoning_effort="medium"` |
| `luna_max` | `model="gpt-5.6-luna"`, `reasoning_effort="max"` |
| `luna_xhigh` | `model="gpt-5.6-luna"`, `reasoning_effort="xhigh"` |

模型解析顺序为当前 `spawn` 的显式字段 → Agent TOML 默认字段 → 父任务模型路线。自动路线必须传入本表的逐次字段，不依赖父任务模型；能力 Agent 没有模型默认值，显式字段省略时才沿用父任务路线。每一级优先级都必须用实际模型与推理强度遥测验证，参数被接受、配置文件和 Agent 自报都不能代替。

调用在 `accepted/started` 前因参数组合不支持而拒绝时，主任务从 A 重新核对一次，不只修补被拒字段。当前界面无法证明组合支持时按本节分支停止或使用唯一兼容路线，不根据另一版本先例猜测。

### 3.1 单次模型回退

只有 `luna_max` 或 `luna_xhigh` 的原生调用实际报告 `unavailable/failed`，且实例尚未 `accepted/started` 时，才在保持同一 `agent_type`、上下文字段与 `message` 的前提下回退一次到 `model="gpt-5.6-sol"`, `reasoning_effort="medium"`。能力 Agent 不可用、`sol_*`/`human_exact` 失败或回退失败时停止。

调用方还必须证明 Task/Scope/revision 与授权未变、没有写入迹象、旧写入者已终止且 Reviewer 独立性仍明确，并记录请求/实际协作界面、`agent_type`、模型路线与原始失败。超时、忙碌、结果失败和用户取消不属于创建前模型不可用。

## 4. 进度与证据边界

Adapter 回传 Codex 原生标识、直接父子关系、协作界面/命名空间、请求的 `agent_type` 与模型路线、`accepted/started/terminal/cancelled`、工具错误和结果 reference。工具面证据分别保存当前任务或 child 的初始模型可见 schema、原生 `tool_search` 是否存在及其加载结果、实际调用轨迹；Code Mode 另回传 asset path/hash、外层调用 reference、`ALL_TOOLS` 中命中的目标、稳定单元标识、完整嵌套参数、逐项结果和最终 `schema_version`。只返回最终摘要或丢失逐项结果/reference 不构成批量传输证据。`spawn_agent` 被接受只证明参数有效且委派 Agent 已创建；实际模型、推理强度、permission profile、feature/Skill 降权、工具暴露与行为分别需要 Runtime 遥测、子任务配置回读、原生 schema 或工具轨迹，配置文件、schema 接受和委派 Agent 自报都不能互相替代。单层派发由宿主原始调用、父任务/session/depth 元数据与子任务工具轨迹证明，只有当前 Runtime 不提供其中必要记录时才保留精确缺口。静态源码/测试的证据范围为本文结构与分支约束；Tool Search、Code Mode、嵌套调用、协作界面发现、`spawn_agent`、`create_thread`、等待/取消、模型可用性和 Runtime 行为使用当前会话的真实 Runtime 证据。
