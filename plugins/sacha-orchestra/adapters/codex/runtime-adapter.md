# Codex Runtime Adapter

> Implements: Intake Contract 4；Workflow Contract 15；Assurance Contract 2；Coordination Contract 7；Artifact Protocol 6
> Status: Normative Codex transport mapping

## 1. Boundary

本文只把已经由 Core/Role 决定的动作映射到 Codex 原生 task/subagent transport。以下链接是 owner reference，不是预加载清单：

- [Intake Contract](../../core/intake-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

Adapter 不定义 Intake、Role、Gate、ready、Manager 职责、批准语义、Artifact schema、项目命令或发布状态。`using-sacha`、Role Skill 和 Coordination Contract 决定何时进入本 Adapter；本 Adapter 只消费 route requirement 并执行 Codex transport。Direct/current context 不切换模型或伪造 dispatch。

## 2. Native transport

| 调用面 | Codex 原生映射 | 约束 |
| --- | --- | --- |
| 有界 subagent | `spawn_agent` | 每个 unit 至多一次首次创建；参数来自第 3 节，不复制父历史 |
| 完成等待 | `wait_agent` | 只消费 terminal/result；timeout 只报告 liveness，不改变 route |
| 取消/接管 | `interrupt_agent`（下称 `cancel`） | 仅 Human 取消、失活或继续会造成双写/增险时使用；确认 `terminal/cancelled` 后才接管 |
| Feedback target 查询 | `list_threads` + 有界 `read_thread` | 只为唯一 repair identity 查询；候选需要消歧或进度证据时才读对应 task |
| Feedback repair owner | `create_thread` | 显式 Feedback、无唯一匹配时创建恰好一次；不是 migration 或 bounded helper |
| Feedback terminal join | `wait_threads` | Source 对唯一 target 等待根终态并消费一次；timeout 只作有界进度检查 |
| 用户可见 task migration | `create_thread` | 只处理明确迁移；不是 bounded helper，也不等待旧 owner 的 terminal return |

### 2.1 Codex role surface

Planner、Manager、Reviewer、Executor 和 Clarify research 都走同一套第 3 节 route；Role 只作为 assessment 输入，不改变 spawn 参数契约。当前 context 能完成的工作不调用 `spawn_agent`。

### 2.2 Explicit Feedback repair transport

Adapter 按 Coordination Contract 的 repair workspace、Scope、objective 和 owner identity 调用 `list_threads`；只有候选 identity、进度或 terminal 需要有界确认时才调用 `read_thread`。唯一匹配直接复用；多个匹配无法消歧时暂停；无匹配且显式 Feedback transport 可用时调用恰好一次 `create_thread`，保留原生 target identity。

Feedback Source 用 `wait_threads` 对该唯一 target 做带 cursor 的有界等待，timeout 只检查最新进度，不 busy polling、不创建替代 owner；收到根终态后消费一次并结束。repair target 因而有上游 return consumer，必须保持 workflow owner 到根终态，不得再进入下节的用户可见 task migration。`spawn_agent`、full-history helper 或 migration handoff 都不能代替这一 transport。

### 2.3 User-visible task migration

只有当前 task 没有上游 return consumer 时才可迁移。迁移 identity 由 Task/Scope revision、批准 Spec reference 和 workflow transfer 组成。Adapter 先按该 identity 查询可复用的 target：

1. 唯一 target 直接复用；不唯一或 Spec/Entry Condition/owner 不可证明时暂停。
2. 无匹配且 Human 已明确选择迁移时调用恰好一次 `create_thread`；创建失败且尚未产生 target owner 时可回当前 task，并保留原始错误。
3. 创建成功后只交付最小 handoff（规则入口、批准 Spec、必要 Artifact/evidence reference 和未携带的 identity）。Source 展示 target reference 后结束，不调用 `wait_agent`、`wait_threads` 或其他 terminal join；后续 Execute、subagent、Review、返修和 closeout 由 target 负责。
4. 重复批准、重试或恢复只复用同一 target reference；成功创建后 Source 不恢复写入者。`spawn_agent`、full-history fork 和 helper 都不取得 migration identity。

## 3. Subagent route contract

每次 `spawn_agent` 前按 A → B → C 顺序处理。A 只提供 runtime-neutral 事实，B 只做一次有序决策，C 才组装原生参数；首个命中即停止，后续条件不再参与。

### A. Assessment input（runtime-neutral）

Adapter 读取 Coordination Contract 产生的 route requirement，不自行判定 Gate 或拆分。只归纳四项：

| 输入 | 判断 |
| --- | --- |
| Human 或批准 Scope 的 exact route（若有） | 最高优先级；验证后原样使用，不自动改写 |
| 任务形态 | `broad`：需要跨 owner 综合、正式决策/复核、复杂集成或边界仍需推理；`bounded`：目标、输入、边界和直接验证均自包含 |
| 负荷 | broad 只分 `critical / standard`；bounded 只分 `nontrivial / light` |
| 安全状态 | Scope/revision、上下文需求、writer 状态和 Reviewer 独立性决定能否 dispatch/fallback |

安全、权限、持久数据、breaking、不可逆外部动作或广泛兼容风险至少按 broad 处理；其中困难回退、跨系统耦合或关键冲突为 critical。Role 只是这些事实的来源之一，不直接固定模型。

上述字段是 route requirement 的输入引用，不新增 Packet、Artifact 或 Handoff 必填字段；实际 readiness、依赖满足和 Manager dispatch 仍由 Core/Skill 负责。

### B. Ordered route decision（first hit wins）

除 exact route 外只判断“形态 × 负荷”，首个命中即停止：

1. `human_exact`：存在 Human/Scope exact route；无法解析或 Runtime 不支持时暂停，不自动换档。
2. `sol_xhigh`：`broad + critical`。
3. `sol_medium`：`broad + standard`。
4. `luna_max`：`bounded + nontrivial`。
5. `luna_xhigh`：`bounded + light`。

无法可靠判定 broad/bounded、bounded 输入不自包含、Scope 不明确或 Reviewer 独立性不足时暂停，不用增加分类来掩盖缺失事实。Planner、Manager、Reviewer、Executor 和 Clarify research 都复用这四档自动选择。

Clarify 不另开一套路由：单个 research helper、Manager 协调的 research unit 与其他 subagent 复用同一顺序；研究结果仍回 invoking owner。

### C. Exact `spawn_agent` mapping

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

### 3.1 Single fallback route

自动 fallback 是单独的一条 fallback route，不参与 B 的首次命中，也不是“再试一次同一 route”。它只能在 primary route 的原生调用**实际报告 unavailable/failed 且实例尚未 accepted/started**时，按同一 assessment 选择下表唯一替代映射并发生一次：

| primary route | 唯一 fallback 参数 |
| --- | --- |
| `luna_max` 或 `luna_xhigh` | `agent_type="default"`, `model="gpt-5.6-sol"`, `reasoning_effort="medium"`；沿用相同最小 `fork_turns` |
| `sol_xhigh`、`sol_medium` 或 `human_exact` | 停止，不 fallback |

Fallback route 本身不再触发第二次 fallback；自动路径不会因 fallback 引入第五种模型组合。

调用方必须同时证明：

- 仍是同一 Task/Scope/revision，且 fallback 不扩大授权、Scope、写入或验收；
- 没有写入迹象，旧 writer 已 `terminal/cancelled`，且 Reviewer 独立性仍明确；
- 失败发生在 `spawn_agent` 建立 owner 之前，并已记录 `requested/effective route` 与原始 `failure reason`。

任一条件不满足（包括可能已写入、旧 writer 未终止、独立性不明、精确 Human/Scope 配置失败或 fallback 再失败）立即暂停并生成 bounded deviation；不得连续试多档模型、静默改用 Runtime default 或再次创建同一 Scope writer。timeout、busy、结果失败和用户取消都不属于“尚未 started”的自动 fallback。

## 4. Progress and evidence boundary

Adapter 只回传 Codex 原生 identity、accepted/started/terminal/cancelled、工具错误和结果 reference。static source/test 只能证明本文结构与分支约束，不能证明真实 `spawn_agent`、`create_thread`、wait/cancel、模型可用性或 Runtime 行为；这些必须单独标为未验证。
