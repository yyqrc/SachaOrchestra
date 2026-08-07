# Codex Runtime Adapter

> 实现：Intake Contract 6；Workflow Contract 19；Human Interaction Contract 1；Assurance Contract 2；Coordination Contract 10；Artifact Protocol 6
> 状态：Normative Codex transport mapping

## 1. 边界

本文把 Core/Role 已决定的动作映射到 Codex 原生 task/subagent transport。owner reference：

- [Intake Contract](../../core/intake-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

Intake、Role、Gate、readiness、Manager 职责、批准语义和 Artifact schema 由对应 Core/Skill 拥有。本 Adapter 消费已确定的 Human 交互动作与 route requirement，执行 Codex transport。Direct/current context 保持当前模型与 owner。

## 2. 原生传输

| 调用面 | Codex 原生映射 | 约束 |
| --- | --- | --- |
| Human 互斥选择 | `request_user_input` | Human Interaction 判定需要选择后调用；推荐项置首。能力不可用或需要自由输入时使用普通文本提问 |
| Human 进度 | `commentary` | 只映射 Core 已判定需要展示的新事实、风险、阻塞或计划变化 |
| Human 最终结果 | `final` | 汇总当前 owner 已产出的结果、证据、风险、未验证项与下一步 |
| 有界 subagent | `spawn_agent` | 每个 unit 至多一次首次创建；参数来自第 3 节，不复制父历史 |
| Subagent 结果等待 | `wait_agent` | 仅在 Coordination 判定依赖屏障后消费 terminal/result；timeout 只报告 liveness |
| 独立 task 结果等待 | `wait_threads` | 仅用于有明确 result consumer 的依赖或 fresh 验证；owner transfer 不调用 |
| 取消/接管 | `interrupt_agent`（下称 `cancel`） | 仅 Human 取消、失活或继续会造成双写/增险时使用；确认 `terminal/cancelled` 后才接管 |
| Feedback 目标任务查询 | `list_threads` + 有界 `read_thread` | 只为唯一反馈身份查询；候选需要消歧或进度证据时才读对应任务 |
| Feedback 目标任务创建 | `create_thread` | Human 在另一真实任务显式调用 Feedback 且无唯一匹配时恰好一次；类型为单向 user-task owner transfer |
| 用户可见 task migration | `create_thread` | 只处理明确迁移；类型为 user-task owner transfer，Source 交付 reference 后结束 |

### 2.1 Codex Role 调用面

Planner、Manager、Reviewer、Executor 和 Clarify research 共用第 3 节 route；Role 作为 assessment 输入，spawn 参数由 route 统一映射。当前 context 可完成的工作保持 Direct。

### 2.2 Human 手动调用的 Feedback 转移

Adapter 消费 Coordination Contract 返回的反馈 identity、匹配和 owner transfer 判断。查询使用 `list_threads`；候选 identity 或 liveness 需要确认时有界调用 `read_thread`。唯一匹配或 `no_op` 返回既有 reference；需要新目标时恰好调用一次 `create_thread` 并保留原生目标任务 identity；无法消歧时保留候选和原始缺口。

目标任务确认后，来源任务交付反馈 objective、必要规则/evidence reference 和原生目标任务 reference，然后结束；该 owner transfer 不调用 terminal join。

### 2.3 用户可见任务迁移

Adapter 消费 Workflow/Coordination 已确认的 migration identity 与 transfer 动作：

1. 唯一 target 直接复用；不唯一或 Spec/Entry Condition/owner 不可证明时暂停。
2. 无匹配且 Human 已明确选择迁移时调用恰好一次 `create_thread`；创建失败且尚未产生 target owner 时可回当前 task，并保留原始错误。
3. 创建成功后只交付最小 handoff（规则入口、批准 Spec、必要 Artifact/evidence reference 和未携带的 identity）。Source 展示 target reference 后结束，不调用 `wait_agent`、`wait_threads` 或其他 terminal join；后续 Execute、subagent、Review、返修和 closeout 由 target 负责。
4. 重复批准、重试或恢复只复用同一 target reference；成功创建后 Source 不恢复写入者。`spawn_agent`、full-history fork 和 helper 都不取得 migration identity。

### 2.4 依赖等待

Adapter 消费 Coordination 的依赖屏障与 result consumer 结论：

- subagent 依赖使用 `wait_agent`；独立依赖或 fresh 验证 task 使用带 cursor 的 `wait_threads`。
- 调用等待前推进其他不依赖结果且不冲突的 ready 工作。
- timeout 返回 liveness snapshot；相同进度沿用现有 snapshot，target identity 保持不变。
- owner transfer 在交付 target reference 后结束。

## 3. Subagent 路由合同

每次 `spawn_agent` 前按 A → B → C 顺序处理：A 提供 runtime-neutral 事实，B 进行一次有序决策，C 组装原生参数；首个命中结束决策。

### A. 评估输入（Runtime-neutral）

Adapter 读取 Coordination Contract 产生的 route requirement，归纳四项 Runtime route 输入：

| 输入 | 判断 |
| --- | --- |
| Human 或批准 Scope 的 exact route（若有） | 最高优先级；验证后原样使用，不自动改写 |
| 任务形态 | `broad`：需要跨 owner 综合、正式决策/复核、复杂集成或边界仍需推理；`bounded`：目标、输入、边界和直接验证均自包含 |
| 负荷 | broad 只分 `critical / standard`；bounded 只分 `nontrivial / light` |
| 安全状态 | Scope/revision、上下文需求、writer 状态和 Reviewer 独立性决定能否 dispatch/fallback |

安全、权限、持久数据、breaking、不可逆外部动作或广泛兼容风险至少按 broad 处理；其中困难回退、跨系统耦合或关键冲突为 critical。

上述字段只供本 Adapter 选择 Runtime route；readiness、依赖满足和 Manager dispatch 由 Core/Skill 负责。

### B. 有序路由决定（首次命中即停止）

除 exact route 外只判断“形态 × 负荷”，首个命中即停止：

1. `human_exact`：存在 Human/Scope exact route；无法解析或 Runtime 不支持时暂停，不自动换档。
2. `sol_xhigh`：`broad + critical`。
3. `sol_medium`：`broad + standard`。
4. `luna_max`：`bounded + nontrivial`。
5. `luna_xhigh`：`bounded + light`。

无法可靠判定 broad/bounded、bounded 输入不自包含、Scope 不明确或 Reviewer 独立性不足时暂停。Planner、Manager、Reviewer、Executor 和 Clarify research 共用这四档自动选择。

Clarify 的单个 research helper 和 Manager 协调的 research unit 复用同一顺序；研究结果返回 invoking owner。

### C. `spawn_agent` 精确映射

C 只接受 B 的 `route_id`。下表是完整参数映射；`task_name`、`message` 为该 unit 的最小目标/Scope/完成检查/停止条件，不能夹带完整父历史。

| route_id | 精确参数 |
| --- | --- |
| `human_exact` | 使用已验证的精确配置；Human 可指定其他 model/effort（包括 Terra 或 Sol max/ultra），Adapter 不替换或降级。缺配置或不支持即暂停。 |
| `sol_xhigh` | `agent_type="default"`, `model="gpt-5.6-sol"`, `reasoning_effort="xhigh"` |
| `sol_medium` | `agent_type="default"`, `model="gpt-5.6-sol"`, `reasoning_effort="medium"` |
| `luna_max` | `agent_type="sacha_luna_worker"`；named definition 固定 Luna/max，不传 `model`/`reasoning_effort` override |
| `luna_xhigh` | `agent_type="sacha_luna_worker_xhigh"`；named definition 固定 Luna/xhigh，不传 `model`/`reasoning_effort` override |

自动 route 只有上述四种组合，不选择 Terra、Sol high/max/ultra 或未限定 generic `worker/default`。自包含输入传 `fork_turns="none"`；确需未落盘 Human 决定时只传能补足决定的最少 turns，不能偷渡完整父历史。

Human/Scope exact config 必须验证后原样映射。`requested/effective route` 只记录实际结果；Direct/current context 不调用该映射。

### 3.1 单次回退路由

自动 fallback 是独立的一次性 route。它只在 primary route 的原生调用**实际报告 unavailable/failed 且实例尚未 accepted/started**时，按同一 assessment 使用下表唯一替代映射：

| primary route | 唯一 fallback 参数 |
| --- | --- |
| `luna_max` 或 `luna_xhigh` | `agent_type="default"`, `model="gpt-5.6-sol"`, `reasoning_effort="medium"`；沿用相同最小 `fork_turns` |
| `sol_xhigh`、`sol_medium` 或 `human_exact` | 停止，不 fallback |

Fallback route 至多执行一次；自动路径保持表内四种 primary 模型组合与一条替代映射。

调用方必须同时证明：

- 仍是同一 Task/Scope/revision，且 fallback 不扩大授权、Scope、写入或验收；
- 没有写入迹象，旧 writer 已 `terminal/cancelled`，且 Reviewer 独立性仍明确；
- 失败发生在 `spawn_agent` 建立 owner 之前，并已记录 `requested/effective route` 与原始 `failure reason`。

任一条件不满足（包括可能已写入、旧 writer 未终止、独立性不明、精确 Human/Scope 配置失败或 fallback 再失败）立即暂停并生成 bounded deviation；不得连续试多档模型、静默改用 Runtime default 或再次创建同一 Scope writer。timeout、busy、结果失败和用户取消都不属于“尚未 started”的自动 fallback。

## 4. 进度与证据边界

Adapter 回传 Codex 原生 identity、accepted/started/terminal/cancelled、工具错误和结果 reference。static source/test 的证据范围为本文结构与分支约束；`spawn_agent`、`create_thread`、wait/cancel、模型可用性和 Runtime 行为使用真实 Runtime 证据。
