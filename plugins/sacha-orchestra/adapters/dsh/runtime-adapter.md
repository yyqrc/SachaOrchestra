# DeepSeek Harness Runtime Adapter（运行时适配器）

> 状态：规范性 DSH 传输映射；官方 Agent Teams 仍为 experimental，安装、组合、fresh discovery、可视化与真实行为需分别验证

## 1. 边界

本文把 Core/Role 已决定的动作映射到 DeepSeek Harness（DSH）的 Agent Teams、Session 与 Human 交互能力。Owner 依据：

- [Intake Contract](../../core/intake-contract.md)
- [术语合同](../../core/terminology-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

提炼术语、入口、Role、Gate、readiness、授权、Review、Artifact 与完成判断仍由对应 Core/Skill 拥有。本 Adapter 只负责 DSH 传输、能力降级、恢复、观测记录与证据映射；只有 Team Lead 所在主任务拥有派发、集成和根终态责任。可视化只投影已经提交的转换和 DSH 原生状态，不参与判断，也不能作为实现、验证或 Human 验收证据。

## 2. 能力发现与选择

首次使用 DSH Agent 传输前，主任务必须按当前会话实际暴露的工具名与参数结构核对以下官方 Agent Teams 工具集：

`spawn_teammate`、`send_message`、`followup_task`、`list_agents`、`wait_agent`、`interrupt_agent`、`team_task_create`、`team_task_list`、`team_task_get`、`team_task_update`。

只有全部必需工具来自同一官方 Team 作用域，且任务工具提供 `revision`、`blockedBy`、`writeScopes` 与 compare-and-set 更新时，才选择本 Adapter 的 Team 传输。磁盘源码、官方说明、Profile 配置或其他会话先例不能替代当前工具面。第三方 `agent_teams_*` 命名空间属于另一套状态与恢复协议；本 Adapter 不混用两套工具，也不把其中一套的任务 id、owner、mailbox 或终态交给另一套继续。

`sacha_visual_event` 是可选观测能力。它存在时，主任务按第 6 节记录已经提交的 Sacha 转换；缺失、失败或不可达只形成观测缺口，不打开或关闭 Gate，不撤销已提交动作，也不阻塞能够独立验证的工作流。

## 3. 主任务、Role 与 Team 映射

| Sacha 语义 | DSH 映射 | 限制 |
| --- | --- | --- |
| 主任务 | 当前 Root Session 的 Team Lead | Root Session id 同时作为官方 Team 身份；teammate 不取得用户任务 Owner |
| Manager | Team Lead 内运行的协调控制面 | 不创建名为 Manager 的 teammate，不把调度权交给成员 |
| Planner/Explore | 自包含的 `fresh` teammate，或当前主任务直接完成 | 研究默认只读；返回事实、决定缺口或协调请求 |
| Executor | 当前主任务，或 Scope/写入边界明确的 `fresh` teammate | 共享 checkout；同一文件、生成物、Git 与整体验证保持单一写入者 |
| Reviewer | 未参与方案和实现的 `fresh` teammate | 名称不同不构成独立；按实际参与历史和输入来源核对 |
| 委派 Agent | Team Lead 通过 `spawn_teammate` 创建的直接 teammate | 单层派发；teammate 不创建下级 Agent，需继续拆分时返回协调请求 |

首次创建使用 `context="fresh"`，并在 `prompt` 中完整提供目标、Scope、允许写入范围、输入 reference、完成检查、停止条件和协调请求返回条件。自动路线不得使用 `fork` 复制 Lead 已完成历史来代替自包含输入；缺少未落盘 Human 决定且无法形成最小自包含消息时暂停派发。

DSH 官方 `spawn_teammate` 当前不接受逐成员 `model` 或 `reasoning_effort`。Profile 配置的 continuable-subagent provider 与其模型设置决定实际路由：

- Human 或批准 Scope 要求精确逐成员模型/强度时，只有当前 Runtime 提供可核实的等价配置并在创建前满足，才能派发；否则暂停该单元，不静默使用默认值。
- 自动派发使用当前已确认的 DSH Team provider；高风险 Planner、Executor 或独立 Reviewer 若该 provider 无法满足既定质量/独立性要求，返回 Runtime 能力缺口，不通过改名或 `fork` 降级。
- 实际 provider/model 只有 `list_agents`、原生创建结果或可绑定遥测明确返回时才记录；配置或自报不构成实际模型证据。

## 4. 任务 DAG、派发与等待

Manager 先按 Coordination Contract 形成工作单元、依赖波次、Sacha readiness 与路由要求，再映射官方 Team task：

1. `team_task_create` 的 `subject/description` 保存自包含工作单元，`blocked_by` 只映射已确认依赖，`write_scopes` 保存预计修改的 workspace-relative path 前缀。
2. DSH 的 `ready` 只表示 `blockedBy` 已完成；`writeScopeWarnings` 只提示重叠。二者都不授予 Scope、文件写入、模型、授权或并发安全，不能替代 Sacha `execution-ready` / `research-ready`。
3. Team Lead 在派发前用 `team_task_get` 读取最新 `revision`，以 `team_task_update(action="reassign", expected_revision=..., owner=...)` 原子设置 owner；成功后才用 `followup_task` 唤醒该 teammate。任务 ready 或 reassign 本身不会启动成员。
4. teammate 开始前读取自己的最新 task；未由 Lead reassign 时，以当前 `revision` 执行 `claim`。完成真实工作和直接验证后，以最新 `revision` 执行 `complete`；失败、阻塞或协调请求不能伪装为 `completed`。
5. 陈旧 revision 只触发重新读取和重新评估；不得盲目重放变更。转派前由 Lead 读取最新 task，必要时 `interrupt_agent`，确认旧写入者停止，再 reassign 或释放 owner。
6. 派发后先 `list_agents` 和 `team_task_list` 重算就绪工作。只要还有不依赖未完成结果且不冲突的单元，Lead 继续推进；到达真实依赖屏障时，先确认所需成员为 `running` 或 `provisioning`，再调用 `wait_agent`。`wait_agent` 不唤醒 inactive 成员，超时或 `noProgress` 后重新列出状态。

静默信息使用 `send_message`；需要目标开始新 turn 时使用 `followup_task`。返回 `accepted` 或 `queued` 都表示消息已经持久化，不重复发送。取消只在 Human 取消、失活或继续会造成双写/增险时调用；`interrupt_agent` 不释放 task owner，后续必须由 Lead 显式处理 task。

## 5. Human 交互、任务迁移与 Feedback

Human 进度与最终结果由当前 Lead 按 Human Interaction Contract 在主会话展示。互斥选择使用当前 DSH 会话真实提供的选择能力；不可用或需要自由输入时使用普通文本，只询问一个关键差异。

普通批准由当前 Root Session 继续。官方 Agent Teams teammate 不是新的用户可见 task，不能代替 Workflow 的任务迁移或 Feedback Owner 转移。当前 DSH 工具面没有可查询、创建并返回唯一用户任务 reference 的等价能力时，明确迁移批准与需要新目标的 Feedback 停止在能力缺口；来源主任务保持唯一 Owner，不用 teammate、后台 turn 或 fork 冒充目标任务。

## 6. Sacha 可视化记录

当前工具面存在 `sacha_visual_event` 时，主任务只在对应 Core/Skill 转换已经提交后调用一次。工具记录失败不回滚真实流程；主任务保留失败 reference，并在本轮下一次 Human 进度或最终结果中披露“可视化未同步”。

| `event_type` | 记录时机 | 必填映射 |
| --- | --- | --- |
| `phase` | Intake 结果、进入/退出 Role、支持节点、Direct 或根终态已经确定 | `phase`、`phase_state`、中文 `summary`；Scope 修订存在时传 `scope_revision` |
| `gate` | Planner、Manager 或 Reviewer Gate 已由 Workflow 判定 | `gate`、`gate_decision`、中文 `summary` |
| `manager_wave` | Manager 已建立波次、完成派发、到达依赖屏障、耗尽或阻塞 | `wave_id`、`wave_state`、`unit_ids`、中文 `summary` |
| `review` | Reviewer 已形成 Assurance Contract Outcome | `outcome`、中文 `summary` |
| `evidence` | source、package、runtime 或 human 证据层的结果已经存在 | `evidence_layer`、`evidence_status`、中文 `summary` 与必要 `references` |

不得为尚未发生的节点预写事件，不得根据计划把 Gate 写成已打开，不得把 Agent 自报写成 Runtime/Human 证据，也不得从面板颜色或节点状态反推 Scope、授权、Outcome 或完成。重复恢复时只记录真实的新转换；同一已提交转换的工具结果状态不明时不重放，保留观测缺口。

## 7. 恢复与证据边界

恢复先用当前 Root Session、`list_agents`、`team_task_list` 与必要的 `team_task_get` 重建官方 Team 状态，再按 Scope/revision、Entry Condition、直接父子身份和结果消费者核对 Sacha Owner。Agent status、task revision、mailbox delivery 与 Sacha 可视化事件分别保留原生 reference；任一层缺失不由另一层补写。

源码与文档检查只证明本映射存在。官方 Agent Teams experimental 组合、Sacha Agent Plugin discovery、`spawn_teammate`、共享 task CAS、消息、等待/取消、模型实际值、companion plugin Host/Client bundle、Session 回放和 Human 界面必须用目标 DSH 版本的真实 Runtime 证据分别验证。
