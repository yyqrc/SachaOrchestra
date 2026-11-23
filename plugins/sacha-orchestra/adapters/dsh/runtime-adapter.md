# DeepSeek Harness Runtime Adapter（运行时适配器）

> 状态：DSH 运行规则。主路径使用可接收后续指令的子代理（`continuable`）。安装、新会话能否发现插件、面板显示和实际运行分别取证。

## 1. 边界

本文把 Core/Role 已决定的动作映射到 DeepSeek Harness（DSH）的 continuable subagent、Session 与 Human 交互能力。Owner 依据：

- [Intake Contract](../../core/intake-contract.md)
- [术语合同](../../core/terminology-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

术语沿用术语合同，入口、流程、授权、任务记录和验收由相应合同与技能规定。适配器负责 DSH 调用、处理能力缺口、恢复、观测记录和取证。派发和集成由 Root Session 所在的主任务独占，整项任务是否结束也由它判断。

## 2. 能力发现与选择

仓库配套包及以下子代理调用说明以 DSH `0.2.0-rc.1` 为验证基准。首次派发前，主任务按当前会话实际暴露的工具名和参数核对该版本的子代理能力。其他版本须按实际接口和兼容证据核对。主路径要求以下能力。

- 至少一个可启动 continuable child 的 delegation tool；Sacha 组合推荐暴露 `sacha_research`、`sacha_worker`、`sacha_review` 三个具名入口；
- `send_message`、`interrupt_agent`、`list_agents`；
- child settlement 能以 Runtime notice 回到直接 parent；
- 需要 child 主动回报时可选 `report` child capability。

派发时按第 5 节核对调用参数和 `continuable` 创建结果。

以当前工具声明、子代理 `request/header` 和实际调用结果核对上述能力。磁盘源码、Profile 配置、安装记录和其他会话先例只说明预期。同名 `list_agents` 只有实际暴露 `scope=children|descendants` 才能控制 continuable 子代理。若被 Agent Teams 等 Profile 组件覆盖成其他 schema，记录为恢复能力缺口。

具名派发入口不可达时，可在完整核对 `backgroundMode`、fresh/fork 语义、child route、depth 与 capability 限制后使用等价的 continuable 工具。无法证明等价时停止该单元的派发并报告能力缺口。已调用具名入口但失败时按第 5 节处理。

`subagent` one-shot、ACP/远程 Provider、Codex/Claude Code provider 或其他 transport 不能在未核对 continuable、恢复和 child route 语义时替代本主路径。

可选观测工具 `sacha_visual_event` 按第 7 节使用。

目标 Profile 安装独立配套包 `@sacha-orchestra/dsh-companion` 时，运行中的主会话有 `bootstrap`、`resident` 两阶段工具集。模型可用 `sacha_tools` 查询、切换阶段和临时解锁工具。

- 从起步工具集自动切换到工作工具集，以会话记录的首个 `tool/call` 或 `assistant/message` 为准。排除 `sacha_tools` 自己的控制调用。用户消息的措辞不参与判断。
- 模型可以用 `sacha_tools` 的 `phase` 动作显式选择阶段。此后由显式选择决定阶段。
- 上下文压缩只遮蔽消息视图，原事件保留，因此工具集保持当前阶段。冷恢复按原生事件顺序重放阶段和成功配对的控制调用。切换之前发起的旧控制调用，不能用晚到结果重新解锁。
- 切换或解锁后，只在下一次模型请求实际提供目标工具时调用。直接模式核对 `request/header.tools`，PTC 模式核对模型实际收到的工具 SDK。切换失败时保留实际状态。工具是否已停止需单独核实。

该阶段只控制 DSH 的可见与可执行工具，不产生或改变 Direct、Role、Gate、readiness、Scope、授权、Outcome 或完成。Adapter 依据当前会话的工具声明、成功控制记录和恢复结果判断。隐藏工具须为当前工作所需且已有授权才能解锁，`sacha_tools` 成功不扩大目标工具的权限。

## 3. 主任务、Role 与 child 映射

| Sacha 语义 | DSH 映射 | 限制 |
| --- | --- | --- |
| 主任务 | 当前 Root Session | 独占工作流 Owner、Manager、派发、集成和根终态 |
| Manager | Root Session 内运行的协调控制面 | 不创建名为 Manager 的 child，不把 DAG 或调度权交给 child |
| Planner/Explore 的 `research-ready` 单元 | `sacha_research` 或经核对的等价 fresh continuable child | 默认只读，工具限于调查所需。返回事实、决定缺口、证据 reference 或协调请求 |
| Executor 的 `execution-ready` 单元 | `sacha_worker` 或经核对的等价 fresh continuable child | 按明确的 Scope 提供实施和验证所需工具。共享工作区沿用单一写入者规则 |
| 独立 Reviewer | `sacha_review` 或经核对的等价 fresh continuable child | 未参与方案和实现。允许读取、diff 和必要测试。写入能力和 sandbox 限制按第 4.1 节核对并记录，独立性按参与历史和输入来源判断 |
| 普通委派 Agent | Root Session 直接创建的 continuable child | 单层派发；child 不创建下级 Agent，需继续拆分时只返回协调请求 |

首次创建必须使用 fresh/self-contained 语义；fork/继承父对话只在 Human 明确要求且 Core/Role 独立性与上下文边界仍成立时使用，自动路线不得用 fork 代替最小自包含输入。

Coordination 已确认一个工作单元适合隔离高噪声的中间过程时，Root Session 可在 Manager Gate 关闭的情况下直接创建一个对应子任务。只读研究和需要写入的 `execution-ready` 单元分别按上表映射。上下文用量、日志长度或模型判断本身不能打开 Gate。

child prompt 必须包含：目标、Scope、输入 reference、允许写入范围或只读边界、完成检查、停止条件，以及发现需拆分/新增授权/Scope 变化时返回协调请求的要求。不得复制完整父对话。

## 4. Capability 与模型映射

Core 只产生 readiness、Role、Scope、授权与路由要求；本 Adapter 再映射 DSH child capability 和模型，不把具体工具名写回 Core。

### 4.1 Capability profile

具名 surface 的 `toolFilter`、persona、`maxDepth` 属部署/Adapter 传输约束，不拥有 Role 或授权语义。`maxDepth=1` 或当前 Runtime 可证明的等价限制用于落实 Sacha 单层派发；缺失时必须把“嵌套派发未由 Runtime 强制限制”保留为能力缺口。

`toolFilter` 只在当前 DSH provider 声明并实际接受该 capability 时使用；未知工具名、过滤失败或工具面无法回读时不得把提示词当作 enforcement。Reviewer 若依赖文件只读，应使用当前 DSH sandbox 的真实模式/结果，并区分 `full | partial | unknown`；read-only sandbox 不证明读隔离或网络隔离。

首次使用子代理入口，或 Profile、插件、版本变化后，按第 2 节从子代理实际收到的工具声明核对可用能力。分别记录本地文件、shell 或进程、Web、MCP/App 或外部系统、自动加载的技能与明确引用、权限和控制工具、下级代理、模型路线及继续和恢复能力。

工作单元缺少必需能力时，由主会话继续、改用已核对的等价入口，或只暂停这一单元。派发须以实际可用能力为依据，角色名称和 persona 只能提供线索。

独立配套包 `@sacha-orchestra/dsh-companion` 管理主会话的工具集，并提供三种可继续接收指令的子代理工具。在基准版中，`AgentRegistry.roots()` 也会列出已激活的 `continuable` 子代理。配套包用原生 `subagent/descriptor` 排除它们，并移除子代理继承的 `sacha_tools`。按核心合同判断 Sacha 的负责方，不得从 DSH 持久化的 `parentSession` 推断。目标 Profile 缺少必需工具、参数声明、执行限制、委派提供方或恢复能力时，停止安装或加载并报告具体原因。

### 4.2 子模型路由

仓库配套包的具名入口省略 `agentOptions`，沿用主会话的提供方和模型。需要固定的不同路线时，由 Profile 为另一个唯一 `toolName` 的实例配置 `agentOptions`，并核对该实例及实际路线。

DSH `0.2.0-rc.1` 的工具实例通过 `modelSelectionSettings: true` 使用宿主的会话选模设置。宿主为新主会话启用选模并配置允许的模型后，工具才提供逐次调用的 `provider`、`model` 和 `reasoning_effort`。以当前会话实际提供的参数为准。仓库配套包默认使用上段的模型配置方式。

DSH `0.2.2-rc.1` 把逐次选模和模型查询分别配置为 `modelSelection` 与 `modelDiscovery`。该版也会拒绝当前配套包仍使用的 `persona` 和 `toolFilter` 配置。使用这个版本时，先解决配套包的加载兼容问题，再核对会话提供的参数。

主任务只选择当前工具目录中已装配且质量满足要求的 surface，不把 Core route requirement 改写成目标 Runtime 不支持的逐调用字段。高风险 Planner、Executor 或独立 Reviewer 若继承 route 无法满足既定质量或独立性要求，停止该单元，不通过改名、fork、另一个 Role surface或自报模型降级。

配置中的 `agentOptions` 说明部署声明。`subagent/descriptor` 标识当前会话属于子代理，并记录运行模式，`provider` 标识创建子代理的委派提供方（例如 `spawn`）。continuable 描述符中可选的 `agentProvider`、`agentModel` 及版本支持的 `agentReasoningEffort` 属于恢复使用的配置声明。请求配置以子代理 `request/header` 的 `config` 为据。实际提供方和模型以对应 `assistant/message` 的 `source` 中 `provider`、`model` 为据。推理强度只记录请求头或可关联到该次调用的 Runtime 遥测明确返回的值，并区分请求值与实际值。配置和 Agent 自报不能证明实际模型。

## 5. 派发、并发、barrier 与返回

Manager 仍按 Coordination Contract 形成工作单元、依赖波次、readiness 与并发结论；DSH 不创建第二份 task DAG。

每个 ready work unit 的派发流程：

1. 主任务核对同一 Task/Scope revision、授权、单写入者和该单元的 capability/model route。
2. 调用一次对应派发工具，省略 `run_in_background` 或显式传 `true`。只接受 `{kind: continuable, subagentId}` 或等价的持久子代理标识。显式传 `false` 走前台单次执行，无法满足正式角色对直属子代理、完成通知和恢复的要求。返回单次执行结果、调用失败或没有持久标识时，记录本单元的能力缺口。不得换用 standard `subagent`、Agent Teams teammate 或另一个角色的派发工具重试。
3. 创建被拒且没有 child 发布时，只有输入或已装配 surface 发生可证实变化才可重新评估；已返回 child id 后不得重复创建同一 work unit。
4. 若 `sacha_visual_event` 可用，在 child id 已真实返回后记录一次 `delegation`，把当前 Sacha `unit_id` 映射到该 `child_id`；只有 Runtime 已证明的 route 才写 `effective_route`。记录失败只形成观测缺口，不撤销 child。
5. 派发后立即重算剩余 ready work。只要存在不依赖未完成结果且不冲突的工作，主任务继续执行或继续派发；不得因为已有 child 在跑就立刻阻塞。
6. 到达依赖屏障且没有其他可推进工作时，主任务停止主动推进并等待 Runtime settlement/report 作为下一次可消费输入；DSH 主路径不依赖 Agent Teams `wait_agent`。
7. 每次 child settlement/report 到达后，只消费新结果、实际验证、阻塞/风险、协调请求和必要 reference，再重算 Sacha 依赖图。只收到部分依赖时不得提前进入下一 Role 或根终态；已有 delegation 观测时可按真实结果更新其 `delegation_state` 为 `settled | interrupted | failed`。
8. `send_message` 只用于同一 child、同一 work unit/Owner 的后续 FIFO turn；它不能重定向已经运行中的当前 turn。新 Scope 或新的独立单元创建新 child。
9. Human 取消、失活或继续会造成双写/增险时使用 `interrupt_agent`；中断只停止当前 turn，后续是否复用或放弃 child 由主任务重新判断。
10. 只有 `list_agents` 当前 schema 含 continuable `scope` 时，才用于恢复/消歧 durable child id 与 `running | idle | ready` 快照，不用于忙轮询完成。同名工具被其他 Profile 能力覆盖时不得误用；外部运行者可用 DSH Host `subagent.list/history` 与 Session export 取证，但这不等于模型获得恢复工具。Runtime settlement 是完成通知，child transcript/reference 是详细工作事实来源。

Sacha 单层派发必须由当前 Runtime 的 direct-parent/depth 记录和 child 工具轨迹证明。发现 direct child 存在下级 child 时，当前 work unit 进入偏差处理；Visualizer 可显示该事实，但不拥有裁决。

## 6. 恢复、Human 与任务迁移

恢复先用当前 Root Session、`list_agents(scope="children")` 与必要 child Session/reference 重建 direct continuable child 状态，再按 Task/Scope revision、Entry Condition 和结果消费者核对 Sacha Owner。`ready` 只表示 child 可从持久化恢复，不表示工作完成或结果待领取。

普通批准由当前 Root Session 继续。continuable child 不是新的用户可见 task，不能代替 Workflow 的任务迁移或 Feedback Owner 转移。当前 DSH 工具面没有可查询、创建并返回唯一用户任务 reference 的等价能力时，明确迁移批准与需要新目标的 Feedback 停止在能力缺口；来源主任务保持唯一 Owner，不用 child、后台 turn 或 fork 冒充目标任务。

按[工作流合同的 Roadmap 后续任务规则](../../core/workflow-contract.md#4-生命周期与-human-路由)，通过能创建任务并返回唯一用户任务引用的宿主入口提交初始输入。输入携带 [Roadmap 技能](../../skills/roadmap/SKILL.md)提供的资料、显式 Planner 请求和实施授权边界。缺少该能力时，交付已完成的 Roadmap 和可直接使用的 Planner 请求，说明新任务尚未创建。continuable 子代理不能代替用户任务。

Human 进度与最终结果由当前 Root Session 按 Human Interaction Contract 展示。互斥选择使用当前 DSH 会话真实提供的选择能力；不可用或需要自由输入时使用普通文本，只询问一个关键差异。

## 7. Sacha 可视化记录

当前工具面存在 `sacha_visual_event` 时，主任务只在对应 Core/Skill/Adapter 事实已经提交后调用一次。记录只展示已提交的事实和原生子代理状态，不能用作实现、验证或用户验收证据。工具缺失、不可达或记录失败只形成观测缺口，不改变 Gate、不撤销已提交动作，也不阻塞能独立验证的工作。把失败证据留在任务记录中。只有面板信息影响用户对进度、结果或下一步的判断时，才说明哪项状态未同步。

| `event_type` | 记录时机 | 必填映射 |
| --- | --- | --- |
| `phase` | Intake 结果、进入/退出 Role、支持节点、Direct 或根终态已经确定 | `phase`、`phase_state`、中文 `summary`；Scope 修订存在时传 `scope_revision` |
| `gate` | Planner、Manager 或 Reviewer Gate 已由 Workflow 判定 | `gate`、`gate_decision`、中文 `summary` |
| `manager_wave` | Manager 已建立/更新当前波次，或完成派发、到达依赖屏障、耗尽/阻塞 | `wave_id`、`wave_state`、`manager_units`、中文 `summary`；`manager_units` 是当前 Sacha Manager 图快照，每项含 `id`、Human 可读 `label`、Sacha `state` 与 `blocked_by` |
| `delegation` | continuable child 已真实发布并返回 durable id；或该映射发生真实 settlement/interruption/failure | `unit_id`、`child_id`、`delegation_state`、中文 `summary`；已知时补 `role`、`surface`、`requested_route`，只有 Runtime 直接证据存在时补 `effective_route` |
| `review` | Reviewer 已形成 Assurance Contract Outcome | `outcome`、中文 `summary`；适用修订已知时传 `scope_revision` |
| `evidence` | source、package、runtime 或 human 证据层的结果已经存在 | `evidence_layer`、`evidence_status`、中文 `summary` 与必要 `references`；适用修订已知时传 `scope_revision` |

`manager_wave` 只回放 Manager 已经决定的依赖图，不创建或拥有 DAG；后续同一 `wave_id` 的事件用最新已提交快照更新展示。`delegation` 只把 Sacha work unit 与 DSH 已发布 child 对上；它不能从 child label 反推 Role，也不能把某个 child 的存在解释为该 unit 已完成。

不得为尚未发生的节点预写事件，不得根据计划把 Gate 写成已打开，不得把 Agent 自报写成 Runtime/Human 证据，也不得从面板颜色、DAG 节点或 child 状态反推 Scope、授权、Outcome 或完成。重复恢复时只记录真实的新转换；同一已提交转换的工具结果状态不明时不重放，保留观测缺口。

Visualizer 的 Runtime child 面只观察 Root 的 continuable direct child：durable id、label、活动状态与是否存在下级；Sacha 图面只回放 `manager_wave` 与 `delegation` 已提交事实。它不重建 task owner，不显示或推导 Agent Teams task revision、writeScopes 或 peer mailbox。

评审和证据只有明确对应当前阶段的 `scope_revision` 才进入当前结果卡。旧修订或未关联结果继续保留在原时间线，不推断为当前通过；连接失败时客户端保留上次快照并标为历史，不能沿用当前运行或通过的展示。

## 8. 证据边界

源码与文档检查只证明本映射存在。根据实际修改、交付声明和明确案例，从下列维度选择所需证据；这不是每次必跑矩阵。声明某项实际行为时，必须取得目标 DSH 版本的真实运行证据：

- 插件能否在新会话中被发现；
- Companion Root `bootstrap | resident` 两阶段的模型工具声明（直接模式查 `request/header.tools`，PTC 查工具 SDK）、same-scope schema/section/guard 对齐和隐藏工具负例；
- `sacha_tools` 的 `status`、`catalog`、`help`、`phase`、`unlock`、`reset` 与重启后恢复。直接模式核对同一回复中尚未声明的工具是否被拒，以及下一次请求能否使用。PTC 按模型收到的工具 SDK 和实际调用取证；
- 首条已记录的非 `sacha_tools` 工具调用或助手消息触发工具集切换，上下文压缩后阶段不回退，以及 `catalog` 能用多词查到隐藏工具；
- 具名 `sacha_research` / `sacha_worker` / `sacha_review` 或等价 continuable surface discovery；
- fresh child、实际模型路线、toolFilter、maxDepth 与 sandbox 实际值；
- research/review 的最终工具目录不含本地写入、MCP/App/外部系统、Agent Teams、Sacha sibling 或长尾控制能力；Reviewer 只按任务需要保留 shell；
- 两个以上 direct child 的并发启动；
- 主任务在 child 运行时继续推进其他 ready work；
- dependency barrier 后 settlement-driven resume；
- 只收到部分 settlement 时不提前完成；
- `send_message`、interrupt、cold resume、`list_agents`；
- child 无下级创建；
- independent Reviewer 的输入来源与实际参与历史；
- Sacha surface 只使用 continuable 路线；显式 foreground/one-shot 与 surface failure 不回退 standard subagent 或 Agent Teams；
- `list_agents` 同名工具的实际 schema、被 Profile 覆盖时的恢复能力缺口；
- subagent/teammate 不安装 Root policy，Root 阶段不改变 child toolFilter；
- visualizer 对 Manager dependency、unit↔child mapping、continuable child Host/Client snapshot 与 Session 回放。

静态测试、Profile 配置或执行者总结不能替代对应行为证据。没有实际运行的层次明确标为未验证，不为填满上述维度另造案例。
