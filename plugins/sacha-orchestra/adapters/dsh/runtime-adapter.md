# DeepSeek Harness Runtime Adapter（运行时适配器）

> 状态：规范性 DSH 传输映射；以正式 continuable subagent 能力为主路径，安装、fresh discovery、可视化与真实行为需分别验证

## 1. 边界

本文把 Core/Role 已决定的动作映射到 DeepSeek Harness（DSH）的 continuable subagent、Session 与 Human 交互能力。Owner 依据：

- [Intake Contract](../../core/intake-contract.md)
- [术语合同](../../core/terminology-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

提炼术语、入口、Role、Gate、readiness、授权、Review、Artifact 与完成判断仍由对应 Core/Skill 拥有。本 Adapter 只负责 DSH 传输、能力降级、恢复、观测记录与证据映射；只有 Root Session 所在主任务拥有派发、集成和根终态责任。可视化只投影已经提交的转换、Manager 图和 DSH 原生 subagent 状态，不参与判断，也不能作为实现、验证或 Human 验收证据。

## 2. 能力发现与选择

首次使用 DSH Agent 传输前，主任务必须按当前会话实际暴露的工具名与参数结构核对 continuable subagent 组合。主路径要求：

- 至少一个可启动 continuable child 的 delegation tool；Sacha 组合推荐暴露 `sacha_research`、`sacha_worker`、`sacha_review` 三个具名入口；
- `send_message`、`interrupt_agent`、`list_agents`；
- child settlement 能以 Runtime notice 回到直接 parent；
- 需要 child 主动回报时可选 `report` child capability。

只有当前工具面和 Runtime 结果能证明上述能力；磁盘源码、Profile 配置、安装记录和其他会话先例只能说明预期。若具名 Sacha delegation tool 不可达，但当前 Runtime 存在等价 continuable tool，Adapter 可在完整核对其 `backgroundMode`、fresh/fork 语义、child route、depth 与 capability 限制后使用；无法证明等价时停止该派发单元并报告 Runtime 能力缺口。

`subagent` one-shot、ACP/远程 Provider、Codex/Claude Code provider 或其他 transport 不能在未核对 continuable、恢复和 child route 语义时替代本主路径。

`sacha_visual_event` 是可选观测能力。它存在时，主任务按第 7 节记录已经提交的 Sacha 转换；缺失、失败或不可达只形成观测缺口，不打开或关闭 Gate，不撤销已提交动作，也不阻塞能够独立验证的工作流。

## 3. 主任务、Role 与 child 映射

| Sacha 语义 | DSH 映射 | 限制 |
| --- | --- | --- |
| 主任务 | 当前 Root Session | 独占工作流 Owner、Manager、派发、集成和根终态 |
| Manager | Root Session 内运行的协调控制面 | 不创建名为 Manager 的 child，不把 DAG 或调度权交给 child |
| Planner/Explore 研究单元 | `sacha_research` 或核对等价的 fresh continuable child | 默认只读；返回事实、决定缺口、证据 reference 或协调请求 |
| Executor 工作单元 | `sacha_worker` 或核对等价的 fresh continuable child | Scope/写入边界明确；共享 checkout 继续服从单一写入者 |
| Reviewer | `sacha_review` 或核对等价的 fresh continuable child | 必须未参与方案和实现；独立性按真实参与历史与输入来源核对 |
| 普通委派 Agent | Root Session 直接创建的 continuable child | 单层派发；child 不创建下级 Agent，需继续拆分时只返回协调请求 |

首次创建必须使用 fresh/self-contained 语义；fork/继承父对话只在 Human 明确要求且 Core/Role 独立性与上下文边界仍成立时使用，自动路线不得用 fork 代替最小自包含输入。

Coordination 已判定一个工作单元适合隔离高噪声中间过程时，Root Session 可在 Manager Gate 关闭的情况下直接创建一个对应子任务：只读研究使用 `sacha_research`，需要写入的 `execution-ready` 单元使用 `sacha_worker`。该映射只消费 Core 结论，不根据上下文用量、日志长度或模型判断自行打开 Gate。

child prompt 必须包含：目标、Scope、输入 reference、允许写入范围或只读边界、完成检查、停止条件，以及发现需拆分/新增授权/Scope 变化时返回协调请求的要求。不得复制完整父对话。

## 4. Capability 与模型映射

Core 只产生 readiness、Role、Scope、授权与路由要求；本 Adapter 再映射 DSH child capability 和模型，不把具体工具名写回 Core。

### 4.1 Capability profile

| Work unit | 推荐 DSH delegation surface | 目标 |
| --- | --- | --- |
| `research-ready` | `sacha_research` | 缩小到调查/读取所需能力，避免实现工具和嵌套派发进入 child attention surface |
| `execution-ready` | `sacha_worker` | 保留实施/验证需要的工具，但禁止 child 再拥有 Sacha 派发权 |
| 正式独立 Reviewer | `sacha_review` | 允许读取、diff、必要测试；写能力与 sandbox enforcement 按当前 Runtime 真实配置记录 |

具名 surface 的 `toolFilter`、persona、`maxDepth` 属部署/Adapter 传输约束，不拥有 Role 或授权语义。`maxDepth=1` 或当前 Runtime 可证明的等价限制用于落实 Sacha 单层派发；缺失时必须把“嵌套派发未由 Runtime 强制限制”保留为能力缺口。

`toolFilter` 只在当前 DSH provider 声明并实际接受该 capability 时使用；未知工具名、过滤失败或工具面无法回读时不得把提示词当作 enforcement。Reviewer 若依赖文件只读，应使用当前 DSH sandbox 的真实模式/结果，并区分 `full | partial | unknown`；read-only sandbox 不证明读隔离或网络隔离。

仓库内可选 bundle `integrations/dsh/sacha-subagents` 提供当前标准 DSH coding preset 的三种默认 surface。它只组合官方 `dsh-tool-subagent`，不拥有 Sacha 语义；目标 Profile 不满足其显式工具前提时应响亮失败或不安装，不静默退化。

### 4.2 子模型路由

具名 delegation tool 或当前等价 tool 暴露 `provider`、`model`、`reasoning_effort` 时，主任务按 Human 精确要求优先，其次按当前 work unit 的风险/成本选择完整 route，并在创建前执行 Runtime 可用的 route discovery/preflight。

未暴露逐 child route 时，使用该 delegation surface 的已确认 provider/default；高风险 Planner、Executor 或独立 Reviewer 若默认 route 无法满足既定质量或独立性要求，停止该单元，不通过改名、fork 或自报模型降级。

实际 provider/model/reasoning 只有原生创建结果、child Session/Agent 遥测或可绑定 Runtime 证据明确返回时才记录；配置和 Agent 自报不构成实际模型证据。

## 5. 派发、并发、barrier 与返回

Manager 仍按 Coordination Contract 形成工作单元、依赖波次、readiness 与并发结论；DSH 不创建第二份 task DAG。

每个 ready work unit 的派发流程：

1. 主任务核对同一 Task/Scope revision、授权、单写入者和该单元的 capability/model route。
2. 调用一次对应 continuable delegation tool；后台/continuable 为默认时保留返回的 durable child id。创建被拒且 child 未发布时才可重新评估并重试；已返回 child id 后不得重复创建同一 work unit。
3. 若 `sacha_visual_event` 可用，在 child id 已真实返回后记录一次 `delegation`，把当前 Sacha `unit_id` 映射到该 `child_id`；只有 Runtime 已证明的 route 才写 `effective_route`。记录失败只形成观测缺口，不撤销 child。
4. 派发后立即重算剩余 ready work。只要存在不依赖未完成结果且不冲突的工作，主任务继续执行或继续派发；不得因为已有 child 在跑就立刻阻塞。
5. 到达依赖屏障且没有其他可推进工作时，主任务停止主动推进并等待 Runtime settlement/report 作为下一次可消费输入；DSH 主路径不依赖 Agent Teams `wait_agent`。
6. 每次 child settlement/report 到达后，只消费新结果、实际验证、阻塞/风险、协调请求和必要 reference，再重算 Sacha 依赖图。只收到部分依赖时不得提前进入下一 Role 或根终态；已有 delegation 观测时可按真实结果更新其 `delegation_state` 为 `settled | interrupted | failed`。
7. `send_message` 只用于同一 child、同一 work unit/Owner 的后续 FIFO turn；它不能重定向已经运行中的当前 turn。新 Scope 或新的独立单元创建新 child。
8. Human 取消、失活或继续会造成双写/增险时使用 `interrupt_agent`；中断只停止当前 turn，后续是否复用或放弃 child 由主任务重新判断。
9. `list_agents` 只用于恢复/消歧 durable child id 与当前 `running | idle | ready` 快照，不用于忙轮询完成。Runtime settlement 是完成通知，child transcript/reference 是详细工作事实来源。

Sacha 单层派发必须由当前 Runtime 的 direct-parent/depth 记录和 child 工具轨迹证明。发现 direct child 存在下级 child 时，当前 work unit 进入偏差处理；Visualizer 可显示该事实，但不拥有裁决。

## 6. 恢复、Human 与任务迁移

恢复先用当前 Root Session、`list_agents(scope="children")` 与必要 child Session/reference 重建 direct continuable child 状态，再按 Task/Scope revision、Entry Condition 和结果消费者核对 Sacha Owner。`ready` 只表示 child 可从持久化恢复，不表示工作完成或结果待领取。

普通批准由当前 Root Session 继续。continuable child 不是新的用户可见 task，不能代替 Workflow 的任务迁移或 Feedback Owner 转移。当前 DSH 工具面没有可查询、创建并返回唯一用户任务 reference 的等价能力时，明确迁移批准与需要新目标的 Feedback 停止在能力缺口；来源主任务保持唯一 Owner，不用 child、后台 turn 或 fork 冒充目标任务。

Human 进度与最终结果由当前 Root Session 按 Human Interaction Contract 展示。互斥选择使用当前 DSH 会话真实提供的选择能力；不可用或需要自由输入时使用普通文本，只询问一个关键差异。

## 7. Sacha 可视化记录

当前工具面存在 `sacha_visual_event` 时，主任务只在对应 Core/Skill/Adapter 事实已经提交后调用一次。工具记录失败不回滚真实流程；主任务保留失败 reference，并在本轮下一次 Human 进度或最终结果中披露“可视化未同步”。

| `event_type` | 记录时机 | 必填映射 |
| --- | --- | --- |
| `phase` | Intake 结果、进入/退出 Role、支持节点、Direct 或根终态已经确定 | `phase`、`phase_state`、中文 `summary`；Scope 修订存在时传 `scope_revision` |
| `gate` | Planner、Manager 或 Reviewer Gate 已由 Workflow 判定 | `gate`、`gate_decision`、中文 `summary` |
| `manager_wave` | Manager 已建立/更新当前波次，或完成派发、到达依赖屏障、耗尽/阻塞 | `wave_id`、`wave_state`、`manager_units`、中文 `summary`；`manager_units` 是当前 Sacha Manager 图快照，每项含 `id`、Human 可读 `label`、Sacha `state` 与 `blocked_by` |
| `delegation` | continuable child 已真实发布并返回 durable id；或该映射发生真实 settlement/interruption/failure | `unit_id`、`child_id`、`delegation_state`、中文 `summary`；已知时补 `role`、`surface`、`requested_route`，只有 Runtime 直接证据存在时补 `effective_route` |
| `review` | Reviewer 已形成 Assurance Contract Outcome | `outcome`、中文 `summary` |
| `evidence` | source、package、runtime 或 human 证据层的结果已经存在 | `evidence_layer`、`evidence_status`、中文 `summary` 与必要 `references` |

`manager_wave` 只回放 Manager 已经决定的依赖图，不创建或拥有 DAG；后续同一 `wave_id` 的事件用最新已提交快照更新展示。`delegation` 只把 Sacha work unit 与 DSH 已发布 child 对上；它不能从 child label 反推 Role，也不能把某个 child 的存在解释为该 unit 已完成。

不得为尚未发生的节点预写事件，不得根据计划把 Gate 写成已打开，不得把 Agent 自报写成 Runtime/Human 证据，也不得从面板颜色、DAG 节点或 child 状态反推 Scope、授权、Outcome 或完成。重复恢复时只记录真实的新转换；同一已提交转换的工具结果状态不明时不重放，保留观测缺口。

Visualizer 的 Runtime child 面只观察 Root 的 continuable direct child：durable id、label、活动状态与是否存在下级；Sacha 图面只回放 `manager_wave` 与 `delegation` 已提交事实。它不重建 task owner，不显示或推导 Agent Teams task revision、writeScopes 或 peer mailbox。

## 8. 证据边界与必须验证的场景

源码与文档检查只证明本映射存在。以下行为必须使用目标 DSH 版本的真实 Runtime evidence：

- Agent Plugin fresh discovery；
- 具名 `sacha_research` / `sacha_worker` / `sacha_review` 或等价 continuable surface discovery；
- fresh child、逐 child route、toolFilter、maxDepth 与 sandbox 实际值；
- 两个以上 direct child 的并发启动；
- 主任务在 child 运行时继续推进其他 ready work；
- dependency barrier 后 settlement-driven resume；
- 只收到部分 settlement 时不提前完成；
- `send_message`、interrupt、cold resume、`list_agents`；
- child 无下级创建；
- independent Reviewer 的输入来源与实际参与历史；
- visualizer 对 Manager dependency、unit↔child mapping、continuable child Host/Client snapshot 与 Session 回放。

对应 Runtime task pack 见 `tests/runtime-scenarios/packs/dsh-continuable-parallel-barrier` 与 `dsh-continuable-review-isolation`。静态测试、Profile 配置或执行者总结不能替代这些行为证据。
