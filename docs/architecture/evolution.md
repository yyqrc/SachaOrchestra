# Sacha Orchestra 演进路线图

> 当前 release：`0.8.0` Approved-Spec migration and Manager coordination
> 当前 source candidate：无
> 当前主线：批准 Spec 后的 workflow owner transfer、独立单元派发与最小恢复
> 发布边界：`0.8.0` 保持普通批准在当前 task 立即执行；只有持久 Spec 可恢复、context 膨胀信号可靠且 Human 明确选择时，Codex 才创建或复用一个用户可见 task并完整移交剩余 lifecycle，旧 task 交接后结束、不等待 return；已有上游 return consumer 的 task 不迁移；迁移不替代 Manager 对独立 ready 单元的实际派发或独立 Reviewer
> 本文只定义方向和 breaking boundary，不授权实现、安装或发布

Human 已于 2026-07-16 要求修复 dispatch 完成后依赖 Human 发现并手动返回的问题，并进一步冻结“任务应持续到目标完成”的原则。批准的 `0.1.12 Autonomous Goal Completion Spec` 由根 workflow owner 自动推进 Plan、Execute、Manager、Review、返修/补证据、re-review 和已授权 closeout，直到 `goal_complete`；required subagent completion 由父 Manager 消费。`0.1.12` 当时把独立 Role return 映射为向 root callback；`0.1.17` 根据真实偏差把 Codex 映射收紧为 root owner 主动 `wait_threads` terminal join，Target final payload 只承载 return 数据，不承担唤醒 owner 的责任。只有重大方案决策、Plan/实际不相容、新授权、不可消歧冲突或外部/Runtime 无法恢复才请求 Human。`0.1.11` 的 Reject 审计链保留且不改写。

## 1. 权威边界

| 内容 | 权威来源 |
| --- | --- |
| 当前开发方向、版本门槛、self-hosting | 本文 |
| Role、Gate 与 high-level lifecycle | `plugins/sacha-orchestra/core/workflow-contract.md` |
| Review、Baseline、Outcome | `plugins/sacha-orchestra/core/assurance-contract.md` |
| Manager、dispatch、return、identity/deviation | `plugins/sacha-orchestra/core/coordination-contract.md` |
| Artifact、Handoff 必要语义与扩展边界 | `plugins/sacha-orchestra/core/artifact-protocol.md` |
| Codex task、subagent、Goal、安装和恢复映射 | `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md` |
| 当前任务的批准 Scope | Human 明确目标或适用 Spec |
| 项目命令、领域证据和局部约束 | Project AGENTS / Domain Skill |

路线图只保留当前有效方向。已结束过程由 Git 和既有 Spec、Execution Report、Review 保存，不在本文重复累计。

## 2. 当前状态

| 里程碑 | 状态 | 已交付能力 | 边界 |
| --- | --- | --- | --- |
| Foundation | 已完成 | Core、Artifact Protocol、Planner/Executor/Reviewer、Codex Adapter、plugin 与 marketplace | `0.1.0` 是种子，不是正式版 |
| 首个 Project Integration | 已完成 | RenderDocAnalysis 接入、项目规则与 Core/Adapter 分层 | 历史接入不继续扩写 |
| Stage 2 maturity intake | 已收口 | 暴露了累计 Report、重复 Handoff 和人工 Checkpoint 的成本 | 不恢复矩阵、Checkpoint 或主动证据摄取 |
| Lean Hybrid | 已完成候选实现 | Direct、Plan、Assure、Full assurance、Goal-first、Project setup、Human-confirmed serial dispatch、Direct plugin development | `0.1.9` 的 bounded source changes 已验收 |
| Managed Parallel | 已接受源码并安装 `0.1.10` | Manager Gate、Work Packet、真实并行运行时断言、自动反馈与迭代路由 | 当前 task 的 Skill path 仍漂移，fresh-context 与真实并行行为未验证 |
| Subagent context/report budget | `0.1.11` 已安装、未发布 | additive report contract、Codex 最小 context、Manager 去重聚合、`report_limited` 与定向 follow-up | 独立 Final re-review 为 `Reject — Needs Evidence`；raw fidelity 与 natural `report_limited` 路径未通过 |
| Autonomous Goal Completion | `0.1.12` released | 根 workflow owner、subagent completion join、独立 Role callback、runtime transition assertions、自动返修/补证据/re-review 与 Human stop gate | source/static R3 `Accepted with follow-up`；fresh-installed §8.2 runtime re-review `Accepted`，最终 `goal_complete` |
| Workflow Feedback Intake | `0.1.13` released | Transport/Identity/Progress 三层断言、完整 deviation packet、显式 feedback intake/transport 与自动修复 callback | 已完成 source 验收并精确安装；不单独宣称 Project Binding 行为 |
| Project Binding v2 | `0.1.14` released | SCM/rule/Skill root 有界发现、Schema v1→v2 安全迁移、事务保护与 Role 渐进消费 | source/static 独立 Review `Accepted`；安装与 source/cache parity 已验证，真实消费项目写入仍需单独授权 |
| Setup Project Capability Mapping v3 | `0.1.15` released | `$setup-project [query ...]`、current-context 有界模糊解析、confirmed capability mapping、Schema v1/v2→v3 迁移与 managed capability 对账 | source/static R2 `Accepted`；exact installation、`19/19` parity、fresh `$setup-project` discovery 与 read-only query runtime smoke 已验证；真实消费项目写入仍不在发布 Scope，provider 仍为可选 |
| Workflow Hardening and Evidence Semantics | `0.1.16` released | review snapshot 双校验、bounded progress/liveness、AC 反例追踪、五态人工验收 canonical 与 legacy fallback provenance | source/static R3 `Accepted`；cgame-unity `0.3.3` source contract hash 已对账；exact installation、`19/19` parity 与 fresh-context Reviewer discovery 已验证 |
| Owner-Joined Terminal Return | `0.1.17` released | root owner 以 `wait_threads` 消费 formal Role terminal payload；message-only wake 退出 owner-restoration 路径；identity/dedup 后唯一 next transition | source/static、精确安装与 `19/19` parity 已通过；真实 Runtime 无 Human 消息地完成一次 `Needs Fix → 同一原 Executor → 同一 Reviewer Accepted` |
| Progressive Workflow and Layered Acceptance | `0.1.18` released | 八个维度分别选择最低足够强度；单一 Baseline、evidence-only scoped re-review、局部 blocker、Gate 失效与 Agent/Human evidence 隔离 | source/static 独立 Review `Accepted`；安装、source/cache parity、fresh discovery 与真实 Runtime 行为未在本 release Scope 执行 |
| 验收选择去重（ITER-04） | `0.1.19` released | 删除独立 `L0`～`L3` 分层验收 Profile：验收由谁判断只由 Reviewer Gate 决定，执行哪些检查由 `V0`～`V4` 独立选择；check-level 人工 overlay 绑定具体 `check_id` | source/static 独立 Review `Accepted with follow-up`；Core §2.2 规范性语义改变（breaking）；九字段 Handoff 与权威顺序未动，但同批为 Plan Artifact 新增权威段/推荐段结构；Workflow Contract 升 `Contract Version: 2`（Human 决策，不为无消费方的旧 L0～L3 写 migration 对照），Artifact Protocol 维持 1 |
| 减重与能力接入（批次0/1a/2） | `0.1.19` released | 路由入口 `S0 Sacha Direct` 改名 `D0` 消歧；入口歧义区主动询问（琐碎默认 L0、高风险强制、歧义区问一次）；新增 explicit-only `clarify` 需求澄清 Skill；能力消费证据胶囊规范可核对轨迹 | source/static 独立 Review `Accepted with follow-up`；plugin 安装、fresh discovery 与真实 Runtime 行为未在本 release Scope 执行 |
| Runtime Adapter and contract normalization | `0.1.20` released | Adapter 独立映射；Workflow Contract 4 去除单 Skill taxonomy 和重复 Conformance；Role Skills 只保留 Runtime-neutral 最小 procedure；停止旧字段、旧 Schema 和 Role alias 兼容 | source/static 验证通过并完成 source release；runtime promotion 未执行 |
| Using Sacha Intake | `0.2.0` released | `using-sacha` 唯一默认入口、Intake Contract 1、Workflow Contract 5、一次 opt-in、Role trigger 收紧、compact contracts 与技术型 Human Interface | source/static 独立 Review `Accepted with follow-up`；安装、source/cache parity 与真实自动感知行为未纳入 source release |
| Context Budget Hardening | `0.2.1` released | 精简 discovery metadata/Project AGENTS；D0 延迟 Adapter；工具/Artifact/transport 预算；Workflow 按需拆层；Manager 管理 Clarify 研究；Provider Catalog Schema v2；独立 Spec storage root / Project Documentation root | source/static 独立 Review 均为 `Accepted with follow-up`、阻塞 finding `0`；精确安装与 `35/35` parity 已通过；fresh discovery、真实 Planner/closeout 消费、Research Packet 调度和无效 catalog fallback 未验证 |
| Runtime Adapter Boundary Cleanup | `0.2.2` released | 删除 Codex Adapter 的插件发布维护段；移除两个 Adapter 无消费者的安装加载条件；压缩 Claude Code Adapter 重复授权枚举 | source/static、精确安装与 source/cache `33/33` parity 已通过；fresh discovery 与 Runtime 行为未验证 |
| Direct Iteration and Adaptive Runtime Rules | `0.2.3` released | 归档预设举证；打包 helper；清晰任务直执行、单 helper 直管、能力感知 transport、自适应 timeout/budget、扩展 Handoff 与完整终态 | breaking migration 已记录；source/static 独立 Review `Accepted with follow-up`，安装后发现与目标项目调用未验证 |
| Role-Aware Model Routing | `0.3.0` released；Codex 映射已被 `0.8.0` release superseded | 历史行为为 Codex `sol/terra` 与 Claude Code `opus/sonnet/haiku`；当前 Codex 自动组合以 §4.29 和 Codex Adapter 为准 | 保留当时 release 事实；不得从本行恢复旧路由 |
| Project Integration Compression | `0.3.1` released | 聚合 Rule/Capability load policy，删除空节点、重复 fallback/reference 与可推导 Storage 字段 | Schema v3 项目值与授权语义不变；setup/project-documentation 解析和 LookDev 幂等 dry-run 已通过，安装与真实 Runtime 消费未验证 |
| Setup Confirmation and Repair Isolation | `0.3.2` released | setup planned-delta 确认 guard；Feedback full-identity 复用、隔离 dispatch 与单次 terminal join 合同 | setup 行为测试与 Skill/plugin static 已通过；安装与真实 Runtime 自动建 task/join 未验证 |
| Project Skill Capability Admission | `0.3.3` released | setup 完整读取 authority/independent 项目 Skill 正文，拆分 goal unit 并只映射可调度能力 | 正文证据与 deterministic guard、真实项目只读 dry-run 已通过；安装、fresh Runtime discovery 与消费项目写入未验证 |
| Lean Dispatch and Claude CLI One-shot | `0.4.0` released | Codex 管理 Claude CLI 单次候选实现；dispatch/return/Handoff 只提供消费者需要的信息 | source/static R5 `Accepted with follow-up`；精确安装、`40/40` parity 与 fresh discovery 已通过 |
| Tooling Cleanup and Fable Routing | `0.4.1` released | Claude CLI helper 接受自定义 `fable` 模型；删除无消费者的本地读取和聚合验证脚本 | 快速发版；普通回归、安装、fresh discovery 与 runtime 未执行 |
| Pi One-shot External Executor | `0.5.0` released | Codex 管理 Pi 单次候选实现；`standard/pro/lite` 路由、工具前置路径 guard、JSONL 结构化终态、事后 containment 与 `sacha` marketplace 身份 | fake CLI、guard 单测、真实 Pi smoke、source/static、安装与 cache 验证见 4.24 |
| Spec Artifact and Feedback Repair | `0.6.0` released | 持久权威统一为 Spec Artifact、Planner 默认 `spec.md`、Project Integration 只使用 Spec storage root；Feedback 创建或复用唯一 owner repair task并等待终态 | 无旧 Plan storage 读取或迁移；安装、cache、fresh discovery 与真实跨 task 行为未纳入 source release |
| Planner Alignment and Project Context | `0.6.5` released | Planner 实质新方案 Human Review、批准后自动执行、Clarify 可恢复决定、A/B/C 验收、项目 Context 有界维护与 Sacha Agent 命名空间 | source/static 已验证；安装、cache、fresh discovery、真实 Planner/Clarify/Project Documentation Runtime 行为不在本次 Scope |
| Semantic-preserving Prompt Compression | `0.6.6` released | 恢复 Clarify/Planner 的顺序、进入/退出、恢复与决策原则；移除说明正文长度和逐句文案锁定 | 普通 source/static 验证与精确安装、cache parity 纳入本次发版；fresh task 行为留待新任务使用验证 |
| Clarification Loop and Path Semantics | `0.7.0` released | 复合模糊需求重评估、Human-owned 提问过滤、自由输入续接、及时 `decisions.md`、Spec 先落盘；Spec base 派生 storage/context path并统一 base/root/path/reference | `--spec-root*` 与 `SetupConfig.spec_root*` 被 `--spec-base*` / `spec_base*` 取代，不保留旧接口；普通 source/static、精确安装与 source/cache `46/46` parity 已通过，fresh task 行为未验证 |
| Project Documentation Closeout and Template Determinism | `0.7.1` released | 有持久产品变化的复杂 Spec 在 closeout 检查 change archive/system guide 候选；项目绑定模板 catalog path并按 manifest 决定 profile；`document-project` 统一 Skill 命名；setup 与文档输出减少重复 hash 和固定元数据卡片 | execution report、项目发布文档与 Project CONTEXT 分属不同 owner；简单修复、纯问答和无持久 delta 静默跳过；模板目录不作运行时随机文风样本；fresh task 行为未验证 |
| Approved-Spec Executor Task Migration | `0.8.0` released | 普通批准同 task 立即执行；可靠长历史信号下明确建议独立 task；Codex create/reuse exactly once、最小恢复与完整 owner transfer；Feedback 使用独立 query/create/wait transport；Manager 继续派发独立 ready 单元并独立 Review | source/static、精确安装、`45/45` parity 与 fresh installed dry-run 已通过；真实 task/subagent transport 未执行 |

## 3. 不变量

1. 生产 Role 只有 Planner、Executor、Reviewer；Manager 是控制面，不是第四个生产 Role。
2. Planner、Reviewer、Manager Gate 独立；接受 Intake 且三个 Gate 关闭时默认 Executor-only。
3. 简单、明确、局部、可逆且可完整验证的任务保持 Direct。
4. 同一文件或共享可变输出同时只有一个写入者；隔离 patch/候选实现可并行，由 integration owner 串行应用。
5. Human 保留 Scope、高影响动作和 workspace 外状态变更的最终授权。
6. Core 保持 platform-neutral、project-neutral；Codex 机制只进入 Adapter 或 Role-local Skill。
7. Goal 是 task 的执行载体，不是第二份 Scope；存在 Spec 时以 Spec 为 Scope 权威。
8. Artifact 按持久化和交接需要渐进生成；简单任务不制造 Spec、Report、Review 或 Handoff。
9. Reviewer 独立性由 provenance 判断，不由 task 名称判断。
10. 报告、Handoff 和 Agent 自报只索引事实；真实文件、Diff、运行状态和命令输出才是完成证据。
11. 不建立 Runtime Registry、数据库、后台服务、自动授权或完整会话采集。
12. 已通过的 self-hosting 能力成为后续同类工作的默认路线；无法使用时必须说明真实缺口。
13. 非 Direct 流程由根 workflow owner 持续推进到与真实结果匹配的合法根终态；Role/subagent completion 和同 Scope 返修/复验不是 Human checkpoint。

改变生产 Role、Gate、Handoff 必要语义、扩展边界、权威边界或用户授权属于 Core breaking change，必须由 Spec 冻结兼容/迁移决定（可以明确为无兼容迁移）并保留独立 Review 边界。

## 4. 核心能力：Managed Parallel

目标：单个职责内有界 helper 由当前 owner 直接管理；出现多个候选单元、依赖图、安全并发或正式恢复协调时，由 Manager 控制面评估、拆分、建立依赖并决定串行或使用 Runtime 原生 agent。具体 readiness、派发、归并与 return 只有 [Coordination Contract](../../plugins/sacha-orchestra/core/coordination-contract.md) 一个规范 owner。

### 4.1 Manager Gate

以下事实之一可开启 Manager Gate：

- 多个候选单元需要统一评估和拆分；
- 明确依赖图或安全并发分支；
- 多个环境或执行实例需要协调；
- 需要集中处理取消、失败、恢复、去重或单一写入者约束。

困难、耗时、多文件或“想用更多 Agent”本身不打开 Manager Gate。

Manager 是协调控制面，不是生产 Role。它按 Coordination Contract 统一负责 assessment、拆分、依赖波次、两类 readiness、逐单元 route requirement、派发/等待/取消、去重归并和 return；不足两个 ready 或无法隔离时返回串行结论。Manager 不设计方案、不写集成实现、不做独立验收，也不扩大授权。

### 4.2 Work Packet

Work Packet 是 dispatch 内容，不是固定字段文件。至少使 Target 明确目标/交付、允许范围、完成检查与停止条件；存在依赖或并发时再补依赖与隔离边界。原生 transport 已携带的 owner/identity 不重复。

只读 Packet 可以并行。共享工作树不并行写同一文件或输出；隔离 worktree、patch-only 和候选实现可并行，由单一 integration owner 串行应用并处理共享生成物、公共 Schema、Git 操作和整体验证。

### 4.3 运行时断言

当下列条件同时成立：

- Manager Gate 已开启；
- 至少两个 Work Packet 已 ready；
- Scope 不重叠；
- 依赖、授权和 Runtime 槽位允许并行；

则形成断言：

```text
parallel_expected == true
-> before_first_wait_or_join_spawned_agents >= 2
```

结果只分三类：

| 结果 | 含义 | 动作 |
| --- | --- | --- |
| `parallel_started` | 首次 wait/join 前已启动至少两个 subagent | 继续聚合 |
| `parallel_blocked` | Runtime、槽位、依赖、Scope 或授权出现真实阻塞 | 报告阻塞和恢复条件 |
| `parallel_dispatch_missed` | 条件满足但没有实际启动并行 | 立即自分析并进入反馈或迭代路线 |

Manager Gate 开启但不足两个 ready Packet 时保持 managed serial，不伪装成并行遗漏。

### 4.4 自分析与自动迭代

`parallel_dispatch_missed` 不能静默降级为串行成功。当前任务必须先生成最小分析：

- 为什么判定应该并行；
- 哪些 Packet 已 ready；
- 预期与实际 spawn 数；
- Runtime、Scope、依赖和授权状态；
- 责任层属于 Manager Skill、Runtime Adapter、Project Integration 还是 Runtime；
- 对当前任务的影响和可定位证据。

若责任层属于 Sacha Orchestra plugin，自动查询现有 Codex task，并判断是否存在合格插件迭代目标。合格目标必须同时满足：

- cwd 精确属于 Sacha Orchestra plugin 源码 workspace；
- 当前用途是插件实现、迭代或缺陷修复，不是 Planner-only、Reviewer-only、历史安装或已关闭发布；
- Goal/Scope 与 Manager、并行、Runtime Adapter、Role Skill 或通用 workflow defect 相容；
- task 可接收消息，且没有 unfinished Goal、活跃写入 owner 或 Scope 冲突。

只有唯一合格目标存在时才直接转发分析包，并携带 runtime-only 根 return address。转发只进入目标 task 的 intake，不扩大其写入、安装、Git 或外部动作授权；Manager 不监控目标 task，目标完成后 callback 根 workflow owner 并继续 objective loop。

没有合格目标、存在多个候选、责任层不属于 plugin 或发送失败时，在当前任务输出可直接转发的分析包，并说明未转发原因。不得为了反馈自动创建新 task。

若当前任务本身就是已授权的插件迭代 Scope，且修复不改变批准合同，则保持同一 Task ID 直接迭代；出现新架构、Scope、授权、外部写入或验收变化时返回 Planner/Human。

这是一条运行时断言和修复闭环，不是案例收集系统。只有真实任务触发时才运行，不主动制造失败、不累计案例、不建立 Registry。

### 4.5 开发与验证方式

Managed Parallel 先实现并安装 candidate，然后直接用于真实开发任务：

1. 在真实任务中评估 Manager Gate 和 ready Packet；
2. 应并行时实际启动 subagent；
3. 运行时断言失败则自分析、直接迭代或转发；
4. 修复后重装 candidate；
5. 后续真实任务继续使用。

官方 Skill/plugin validator、JSON/YAML/Markdown 引用和边界检查只证明 packaging/static 正确，不能代替真实并行行为。并行能力不以 synthetic behavior fixture、固定样本数、矩阵或主动制造任务验收。

### 4.6 已安装但独立 Review 拒绝：Subagent 上下文与报告预算

Human 已授权按 `docs/plans/2026-07-16-subagent-context-report-budget/spec.md` 实现并发布 `0.1.11`。精确安装和 source/cache parity 已完成，但 Final re-review 判定 controlled raw payload fidelity 与自然超限 `report_limited`/follow-up 路径仍缺证据，因此 `0.1.11` 未发布。该 Review 保留为历史判断，不由 `0.1.12` 改写。

### 4.7 当前实施：Autonomous Goal Completion

`docs/plans/2026-07-16-completion-return-routing/spec.md` 冻结 `0.1.12`：根 workflow owner 对用户 objective 负责，自动推进 Plan、Execute、Manager、Review、返修/补证据、re-review 和已授权 closeout。Manager 必须在父 lifecycle 消费 required subagent completion；独立 Role 通过 runtime-only 根 return address 主动 callback。只有重大方案决策、Plan/实际不相容、新高影响授权、不可消歧冲突，或证据冲突已使下一步无法诚信判断且继续写入有覆盖用户工作/制造错误完成声明的风险，或外部/Runtime 无法恢复才暂停给 Human。

该能力不建立后台服务、Runtime Registry 或第四生产 Role，不修改九字段 Handoff，也不扩大安装/Git/发布授权。`0.1.12` 已在精确安装且 source/cache `16/16` parity 的 fresh context 中完成真实 child join、独立 task callback、`Needs Evidence`→原 Executor 补证→同 Reviewer re-review、Accepted callback、duplicate/错误身份拒绝、invalid-owner `completion_return_blocked` 与根 `goal_complete`；同一独立 Reviewer接受 runtime evidence。

### 4.8 已发布：Workflow Feedback Intake

`docs/plans/2026-07-16-workflow-feedback-intake/spec.md` 冻结 `0.1.13`：沿用 `0.1.12` 唯一 runtime transition assertion 机制，将其正式整理为 Transport、Identity、Progress 三层，并锁定可恢复的 runtime deviation packet。新增 `sacha-orchestra:feedback` 作为 intake、补充调查与 transport 入口，不改变三个生产 Role，也不是 Manager、assertion owner 或授权层。

显式 feedback 可以在真实 task/project 状态唯一时复用或创建唯一 SachaOrchestra 修复 task；自动 runtime deviation 没有唯一既有目标时不得创建。两者都把 bounded packet 送入现有 Planner→Executor→独立 Reviewer→repair/evidence→re-review 路线，并 callback 原 feedback workflow owner。该 release 不新增 hook、MCP、App、后台服务、Runtime Registry、硬编码项目注册表，也不隐含安装、Git 或发布授权。

### 4.9 已发布：Project Binding v2

`docs/plans/2026-07-16-project-binding-v2/spec.md` 冻结 `0.1.14` 的 Project Integration schema 升级：`setup-project` 从 Project AGENTS 开始执行最多两跳的规则发现，探测根级 Git/SVN 证据和 Skill root 候选，并由 Human 分别确认 rule binding、authority/mirror/independent/ignore 与 Legacy alias 决策。generated Binding 只保存项目相对定位和关系，不复制规则正文、不保存扫描 hash、不猜测领域能力。

Schema v1 默认只 dry-run 展示 v2 planned content、preimage/planned SHA-256 与迁移动作；写入继续要求显式授权、matching expected hash、完整决定、marker/并发保护和补偿恢复。Planner、Executor、Reviewer 只在需要项目定位时渐进读取 confirmed Binding；Binding/v2/provider 缺失时保留 Project AGENTS、Domain Skill 和 Executor-only fallback。该 release 不包含 Capability Mapping 自动生成、真实消费项目迁移或必选领域 provider。

### 4.10 已发布：Setup Project Capability Mapping v3

`docs/plans/2026-07-17-setup-capability-mapping-v3/spec.md` 冻结 `0.1.15` 的 `setup-project` 迭代：Human 可直接输入 `$setup-project cgame_unity custom-review` 一类宽松查询，Skill 从当前 Codex context 组织显式 catalog，由纯 resolver 执行确定性候选匹配，并在集中确认后只把 canonical capability binding 交给生成器。项目根默认从当前 workspace、Project AGENTS/confirmed Binding 与 SCM root 推断；仍有多个有效根时才请求消歧。

Schema v3 只保存 capability id、canonical Skill、最小 load policy 与 fallback，不保存查询词、分数、provider 正文、版本、机器路径或 discovery hash。再次 setup 对 managed capability 执行 `keep/add/replace/remove/warning` 对账；当前 context 暂时不可见不构成自动删除理由。Schema v1/v2 仍先 dry-run，写入继续沿用 expected hash、marker、并发保护、补偿恢复和 `partial_write` 证据。Provider 是可选能力来源，不拥有 Role、Gate、Scope、Artifact、授权或 verdict；mapping/provider 缺失时保留 Project AGENTS、可发现 Domain Skill 与 Role 原生 fallback。

该 release 不修改 Core，不引入必选领域 plugin，也不包含真实消费项目写入。`0.1.15` 已精确安装并完成 source/cache `19/19` parity；fresh `$setup-project` 简写调用解析到安装 cache `0.1.15`，read-only query smoke 自动推断当前项目，把 `cgame_unity` 解析为 `cgame-unity` 并展开五项能力，同时将无唯一候选的 `custom-review` 保持 unresolved、阻止写入。该 smoke 不等于真实消费项目写入验收。

### 4.11 已发布：Workflow Hardening and Evidence Semantics

`docs/plans/2026-07-17-self-hosting-workflow-hardening/spec.md` 冻结 `0.1.16` 的 review snapshot、required-child first-progress/liveness、validator isolation、测试 consumer 推导、AC 反例追踪、最长 60 秒用户可见进度，以及 Human-explicit 独立 Executor 配置边界。R3 独立 Review 保留 R1/R2 provenance，并裁决 source/static 为 `Accepted`。

验收证据语义以 `human_assistance_state = not_required | pending | completed_passed | completed_failed | completed_inconclusive` 为 canonical；人工项只允许后四态，canonical 存在时优先于冲突的三态投影，缺失时才使用 `observed_outcome` legacy fallback 并记录 provenance。`completed_inconclusive` 表示人工已完成但证据不足，进入 `Needs Evidence`。该跨插件契约曾以 cgame-unity `0.3.3` source hash 完成对账；原 repo-local fixture 无现行消费者，不再作为当前 Gate。Provider 仍不拥有 Reviewer verdict。`0.1.16` 已精确安装并完成 source/cache `19/19` parity；ephemeral fresh context 将 `$sacha-orchestra:reviewer` 直接解析到安装 cache `0.1.16`。

### 4.12 Released：Owner-Joined Terminal Return

`docs/plans/2026-07-23-runtime-owner-restoration/spec.md` 处理已确认的 `Progress` 偏差：Reviewer 已产生完整 `Needs Fix` verdict，旧 Adapter 却让 Source turn 结束并依赖 `send_message_to_thread` 唤醒 idle root；真实 Runtime 只投递了消息，没有恢复 owner，直到 Human 再发消息才继续。

`0.1.17` 的冻结修复保持 Core、Artifact Protocol、Role/Gate 和授权模型不变。root owner 在 formal dispatch 后保持当前 phase，以 target thread/host 调用 `wait_threads`；Target 在 final terminal output 提供一次短 callback payload。owner 对 Task ID、Scope、revision、owner、Source/Target Role 与 dedup 完成验证后，从实际 task 工具结果启动唯一 next transition。timeout 只产生 bounded progress 并继续 event wait；Manager required subagent 仍使用 `wait_agent`。

### 4.13 Released：Progressive Workflow and Layered Acceptance

`docs/plans/2026-07-23-layered-acceptance-review-delta/spec.md` 冻结并发布 `0.1.18`：对 Planning、Artifact、Coordination、Verification、Runtime evidence、Context/report、Feedback 与 Project setup 分别选择最低足够强度，不形成总分或固定流水线；`L0`～`L3` 验收 Profile 使 Direct 与普通工程任务避免无事实的完整 Review，风险工作继续由既有 Reviewer Gate 独立保证。

正式 Review 只维护一个实现 Baseline。相同 Scope、Baseline 与 `acceptance_revision` 下的 evidence-only delta 以稳定 `changed_check_ids` scoped re-review，并在既有 Review Artifact append Entry；不新增 Evidence/Verdict Revision Artifact。局部 blocker 只暂停冲突范围，存在安全且已授权 ready branch 时根 workflow owner 继续推进。Scope、验收、owner、交付、安全/权限或依赖图的实质变化使旧 Gate 判断失效，但证据 reference、结果或文案变化不自动打开 Gate。Agent-observed evidence 不替代 Human-confirmed canonical check。

该 release 保持三个生产 Role、三个 Gate、Artifact Protocol 精确九字段 Handoff、single writer、Human 授权、Reviewer provenance、callback identity/dedup、历史证据和 owner-joined terminal return；不修改 Binding/Setup schema、resolver/generator，不新增 Registry、后台服务、hook、MCP 或 App。source/static 独立 Review 已通过；安装、fresh-context runtime 与真实行为仍是后续独立授权层。

### 4.14 Released：Progressive Acceptance + Clarify + Multi-Runtime

`0.1.19` 已完成 source release，独立 Review 为 `Accepted with follow-up`；本次不改变安装授权，也不宣称 runtime promotion 已完成。Evolution 是 current release、source candidate 与验证层级的唯一权威；manifest 表示当前源码版本，Git annotated tag 表示已发布版本，其他 README、Adapter 与项目规则只链接该 authority。

收尾分为 `source release` 与 `runtime promotion`：前者在 source/static Accepted 后只做一致性检查、精确暂存、commit、tag 与原子 push；后者需要 Human 对精确版本另行授权安装/refresh 后取得 R2～R4 证据。新增 release coherence validator 检查 source/release 状态、版本和 tag identity；历史 Artifact Protocol 保护改为比较真实 Git preimage，避免过期硬编码 hash 制造无关发布红灯。

### 4.15 Released：Runtime Adapter and contract normalization

`0.1.20` 将两个 Runtime Adapter 收敛为相同骨架的独立映射：它们只引用 Core/Artifact Protocol，不互相引用，不维护 release、验证或迭代历史。Workflow Contract 4 只保留跨 Role 的协作语义与四个共享强度维度；单 Skill taxonomy、Runtime transport、重复 Conformance 和展示规则不再占用 Core。Role Skill 只保留 trigger、最小 procedure 和暂停/路由。

该 release 停止 `source_thread_id`、`observed_outcome`、Goal 路线 taxonomy、非 Schema v3 Project Binding 与 Role alias 兼容。历史说明保留在 README、Evolution、冻结 Spec/Report/Review 和 Git 中，不进入当前 Core、Adapter 或 Skill。source/static 验证已通过；本次不执行安装、refresh、source/cache parity、fresh discovery 或 Runtime behavior 验证。

### 4.16 Released：Using Sacha Intake

`docs/plans/2026-07-27-using-sacha-intake/spec.md` 冻结 `0.2.0`：`using-sacha` 成为跨 Runtime 唯一默认 Intake/Route 入口。Runtime 先以最小 Intake Contract 区分 L0、D0 candidate 与 Planner candidate；候选路线说明具体事实并询问一次，显式 using-sacha/Role 调用视为接受。接受只选择编排方式，不扩大写入、安装、Git、发布或外部动作授权。

Workflow Contract 5 从 Intake acceptance 开始；三个生产 Role、三个 Gate、Manager 控制面、single writer、Reviewer provenance、owner return 和九字段 Handoff 不变。Hook 只可在另行授权后预加载环境信息，不得替代入口、授权或恢复。

该 release 把 Consumer-Minimal Information 和 Technical Compact Human Interface 固化到 Core、Artifact、Adapter、Skill、README、generated Binding 与维护规则：一个事实只有一个 owner，Human 输出默认结论优先且技术紧凑；安全、授权、失败、未验证、Evidence 和 Entry Condition 不得为压缩而删除。source/static 独立 Review 为 `Accepted with follow-up`；安装、source/cache parity、fresh discovery 和真实自动感知行为仍是独立 runtime promotion 层。

### 4.17 Released：Context Budget Hardening

`0.2.1` 在不改变 Role、Gate、授权、九字段 Handoff 或证据权威的前提下减少 Codex active context：压缩常驻 Skill description；Executor-only D0 不预加载 Runtime Adapter；大工具输出使用摘要、计数、关键片段与 reference；Plan、Execution Report、Packet report 和 completion notice 使用可超限但不得丢失失败/风险的 soft budget；Sacha workspace 的常驻 AGENTS 只保留当前 authority、维护和验证纪律；release coherence 只检查机器可判定边界，不以自然语言 marker 代替语义 Review。

同一 candidate 为 Schema v3 Project Integration 增加 Human-confirmed 文档策略、可移植或 non-portable root 及 bounded closeout 授权，并新增可执行的自包含 `change-archive`/`system-guide` generator/parser。Spec storage root 与 Project Documentation root 独立配置，支持项目相对或外部绝对 root；持久 Spec 才渐进消费 Spec storage root，Setup 不创建目标 root。发布型项目文档不属于 Artifact，不复制 Scope、Role 状态或证据权威。

### 4.18 Released：Runtime Adapter Boundary Cleanup

`0.2.2` 删除 Codex Adapter 中本仓库 Marketplace 路径、creator helper、安装/重装、source/cache、fresh discovery 与 source/static 发布收尾说明。这些事实继续由 Project AGENTS、Evolution、deployment manifest 和 release validator 拥有，不再进入插件运行合同。

两个 Adapter 同时移除无消费者的“安装”加载条件；Claude Code Adapter 的重复外部动作枚举收紧为 Hook 与 workspace 外动作授权边界。Core、Skill、合同版本、Role/Gate、授权和 Runtime transport 均不改变。

source/static、精确安装和 source/cache `33/33` parity 已通过；fresh discovery 与 Runtime 行为未执行。

### 4.19 Released：Direct Iteration and Adaptive Runtime Rules

`0.2.3` 收口了 2026-07-24 已实施的批次设计。根路线图不再把 Runtime reference、跨 Runtime 证明、SH3 或历史 Review 追溯写成预设任务，只保留入口轻路径、Planner/Clarify、Provider 接入、自然并行、Setup/项目文档、目标 Runtime Adapter 和高频步骤脚本化等可直接推进的方向。

同一 release 根据规则全量审查升级 Intake 2、Workflow 7、Coordination 2 与 Artifact 2：清晰已授权任务保持 Direct；单个有界 helper 不强制 Manager；Runtime transport、liveness、context/report budget 按能力与风险自适应；根终态表达完成、部分完成、取消、替代、Human 决策、return 阻塞与外部失败；九个 Handoff 核心字段保持稳定并允许 namespaced `Extensions`。

能力具备可执行 owner 和入口后即可投入使用；真实运行失败用于收紧边界、补充案例并防止回归，不再单独建立“证明能够运行”的举证工程。历史 verdict 只保留在归档，不转写为当前待办。

同一 release 归档 CGame 能力接入设计，补充 Provider、Spec storage root、Project Documentation 与 experience candidate 的边界，取消以真实案例、SH3 或安装后验收作为 `1.0.0` 举证门槛，并刷新 root/Plugin README。跨会话规律和高频步骤接口记录在 [`maintenance-tooling.md`](maintenance-tooling.md)。

Codex 本地读取使用 FastCtx，VCS diff 使用全局 `diff_digest.ps1`，项目验证由 Project AGENTS/Domain Skill 选择。

### 4.20 Released：Role-Aware Model Routing

> Historical snapshot / superseded：本节只记录 `0.3.0` 发布时的路由，不是当前操作说明。Codex 当前自动模型与 fallback 已由 `0.8.0` release 改写；现行唯一 owner 是 [`adapters/codex/runtime-adapter.md`](../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md) §3，方向摘要见 §4.29。不得用下述 `Sol/Terra` 组合覆盖当前 Adapter。

Human 批准 `0.3.0 Role-Aware Model Routing Spec`：Codex 正式跨 context dispatch 使用原生 subagent 的 `model`/`reasoning_effort`，Planner 选择 `gpt-5.6-sol high/xhigh`，普通 Executor 选择 `gpt-5.6-terra high/xhigh`，高风险 Executor 选择 `gpt-5.6-sol medium/high`；Claude Code 独立映射 `opus/sonnet/haiku`。

精确 Human/Scope 配置优先；自动配置不可用时回退 Runtime default 并记录 requested/effective，显式配置不可用时暂停。Direct/current context 不切模型，模型强度不替代 Gate，旧写入者结束前不得以其他配置启动同 Scope 写入。该 candidate 不修改 Core、Skill、九个 Handoff 核心字段、Manager 并行条件或授权语义。

本轮 Project Setup tests `20/20`、官方 plugin validator、`0.3.0` candidate release coherence 与 `git diff --check` 已通过。未安装 source candidate，因此 fresh discovery、自动档位选择、requested/effective model 和 terminal join 的真实 Runtime 行为未验证。

### 4.21 Released：Lean Dispatch and Claude CLI One-shot

Human 已确认 `0.4.0 Spec`：Codex 可把低返工、自包含、隔离且可确定验证的工作交给本地 Claude CLI 单次执行；同时删除 dispatch、completion、Handoff 与 deviation 的固定重复格式。Codex 仍拥有 Scope、授权、集成、验证和返修。

Workflow 8、Coordination 3 与 Artifact 3 保留授权、single writer、Reviewer provenance、原始证据、恢复和根终态。普通消息直接派发；Handoff 只补当前消费者无法取得的恢复信息。面向 Human 使用自然技术说明，不展示内部字段表。

Codex Adapter 提供 `claude_once.ps1`。helper 只接受干净、精确 HEAD 的 linked worktree，只开放路径限定的 Read/Edit/Write，并拒绝 ignored 越界写入、Git metadata/HEAD 改变和越界 diff；native Windows 不宣称自定义 executable 受 OS sandbox 隔离。

fake CLI 行为测试、Project Setup `27/27`、受影响 Skill quick validate、plugin validator、candidate coherence 和 diff check 已通过；独立 R5 为 `Accepted with follow-up`。`0.4.0` 已精确安装并完成 source/cache `40/40` parity；fresh task 从安装 cache 读取 using-sacha/Executor 并确认清晰已授权任务保持 Direct。真实 Claude API/认证/模型/工具行为和消费项目行为未验证。

### 4.22 Released：Tooling Cleanup and Fable Routing

`0.4.1` 允许 `claude_once.ps1` 把供应商配置的 `fable` 模型原样传给 Claude CLI。Codex 本地文件定位改用 FastCtx，VCS diff 保留全局 `diff_digest.ps1`，验证由项目规则或 Domain Skill 选择；无直接消费者的重复聚合脚本和测试已删除。

本次按快速发版收尾。普通回归、Plugin validator、安装、cache parity、fresh discovery 和真实 Claude runtime 未执行。

### 4.23 Released：Task Evolution Intake Reassessment

`0.4.2` 要求 `using-sacha` 在初次判断及 Direct 执行中的语义转折点重新评估。预计需要关键 Human 澄清、先冻结/持久化 Spec、跨 context owner/恢复、难回退跨 owner 决策、正式协调或独立验收会改变执行方式时，可形成新的 Sacha candidate；同一 candidate 仍只询问一次。

Intake 3 与 Workflow 9 对齐 Planner candidate/Gate 和动态返回条件；复杂调试、耗时、文件多、多平台或持续验证本身仍保持 Direct。本次按快速发版收尾，只核对版本与 Git 发布身份；普通回归、Skill/Plugin validator、完整 release coherence、fresh discovery 和 Runtime smoke 不作为发布 Gate，安装证据在发布后单独核对。

### 4.24 Released：Pi One-shot External Executor

`0.5.0` 删除 Codex 下的 `claude_once.ps1`，由 `pi_once.ps1` 接管低返工、自包含、隔离且可确定验证的单次候选实现，并把 repo-local marketplace 身份从 `personal` 改为 `sacha`。plugin 只定义 `standard`、`pro`、`lite` 路由槽位；setup-project 优先保留项目配置，其余按 `glm-5.2`、`kimi k3`、`deepseek`、`gpt-5.6 luna` 家族名巡检 Pi 候选，其中 lite 优先 DeepSeek、以 GPT Luna 为备选。源码不硬编码完整 provider/model，无匹配时使用 Pi Runtime default。

helper 固定关闭 session、自动 extension、Skill、prompt template 与 context file，只启用 `read,edit,write,sacha_result`。显式 `pi_guard.mjs` 在工具执行前拒绝越界、控制目录、symlink/junction 与多链接写目标；owner 仍在执行后核对 ignored 文件、Git metadata、HEAD、JSONL 终态和真实 diff。该应用层 guard 不声明 Windows OS sandbox。

guard、巡检器与 fake Pi 正反例已通过；四个当时可用的配置模型都经 `pi_once.ps1` 在独立 linked worktree 完成 `read → edit → read → sacha_result`，均为 `candidate/completed`、只修改目标文件且内容正确，耗时 `76.126s`、`21.448s`、`14.580s`、`14.013s`。该次本机清单只作 Runtime 证据，不进入源码。Project Setup `29/29`、setup Skill、官方 plugin validator、`0.5.0` candidate coherence 与 `git diff --check` 已通过。`sacha-orchestra@sacha` 已精确安装为 `0.5.0`，source/cache `40/40`、缺失/多余/hash mismatch 均为 `0`；fresh task 从安装 cache 加载 `using-sacha`，确认版本并保持 Direct。

### 4.25 Released：Spec Artifact 与 owner-routed Feedback

`docs/plans/2026-07-30-spec-artifact-storage-repair/spec.md` 冻结由 `G:\COD\Client` 真实消费偏差触发的修复：持久 Scope 权威只称 `Spec Artifact`，Planner 需要持久化时在任务目录默认生成 `spec.md`；`Plan` 只保留为 lifecycle 中按需规划活动或 `inline plan`。

Project Integration 的公开配置、生成器 Python API/JSON/CLI 当前统一为 `Spec base`、`spec_base*`、`--spec-base*`，并由 `<Spec base>/plan` 唯一推导 `Spec storage root`；生成输出仍使用 `- Spec：...`。本 repair 明确不读取或迁移旧 Plan storage 形态，也不修改外部消费项目文件。Artifact Contract 4 与 Workflow Contract 10 承载当前语义。

同一 `0.6.0` candidate 收紧显式 Feedback：repair workspace、Scope、objective、owner 唯一且 transport 可用时，Source 必须复用唯一匹配目标，或创建恰好一个 owner workspace task并以原生 terminal join消费结果。Source-local investigation helper 只读补证，不取得 repair identity；调查与路由不授权 Target 写入、Git、安装或发布。

source/static 已通过 Spec Artifact 合同 `3/3`、Project Setup `29/29`、五个受影响 Skill official validator、plugin validator、`0.6.0` candidate coherence 与 combined diff check。独立 Reviewer、安装/cache parity、fresh discovery、真实 Planner `spec.md` 写入及 Feedback `create_thread → wait_threads` 行为未执行。

### 4.26 Released：Planner 对齐、可执行 Spec 与项目 Context

`docs/plans/2026-08-04-planner-alignment-executable-spec/spec.md` 冻结 `0.6.5`：Planner 形成 Human 此前未确认、会改变用户可见行为、架构、数据/资产、owner、迁移/兼容、难回退选择或验收方式的实质方案时，先交付拟执行 Spec 与 Human Review Focus；批准且没有额外授权、未决方案或阻塞性 Entry Condition 后，原 workflow owner 立即进入 Executor，不再请求第二次“开始实施”。Clarify 按需保存最小决定与恢复 frontier，并把稳定项目术语作为 closeout 候选而非直接事实。

同一 candidate 将验收输入按实际执行者区分为 Agent 执行、Human 提供前置后 Agent 执行、Human 观察判断三类，不新增 Outcome。Project Integration 首次默认使用 `docs/plan/<YYYY-MM-DD>-<short-slug>/` 保存 `spec.md` 与按需 `decisions.md`，并暴露确定的Project Context path；Project Documentation 只在授权和 preimage 保护下有界维护 managed 术语区。`setup-agents` 改用 Sacha-owned `sacha_luna_worker` 与 `sacha_luna_worker_xhigh`，拒绝覆盖非 Sacha 身份。

Project Setup `38/38`、单元测试 `18/18`、九个受影响 Skill official validator、plugin validator、`0.6.5` candidate coherence 与 diff check 已通过。本次只发布 source/static 层；安装、cache parity、fresh discovery、真实 Planner/Clarify/Project Documentation Runtime 行为及 Domain Provider 跨仓实施均不在发布 Scope。

### 4.27 Released：澄清闭环与路径语义

`0.7.0` 根据真实 LightmapSizeEstimate 规划偏差收紧入口、Clarify 与 Planner：列出多个功能点、文件或入口不再证明数据语义、用户行为、持久化和验收已明确；Clarify 只询问无法自行查明、会改变方案且决定权属于 Human 的事项。多选自由输入按选择、纠正、疑问或新方向继续对话，疑问先回答再恢复原问题；已知会形成 Spec 时，第一个关键决定确认后、下一问题前写最小 `decisions.md`。需要批准或恢复的 Planner 方案先写入并回读 `spec.md`，对话只交付摘要、path 与重点检查项。

同一 release 按项目术语规则把配置输入目录称为 `base`、派生生效目录称为 `root`、文件位置称为 `path`、非文件指向称为 `reference`。Setup 的公开 Python/CLI 输入从 `spec_root*` / `--spec-root*` 改为 `spec_base*` / `--spec-base*`，再唯一派生 `<base>/plan` Spec storage root 与 `<base>/CONTEXT.md` Project Context path；旧接口不保留兼容，属于 `0.7.0` breaking boundary。

Project Setup `40/40`、Spec Artifact contract `3/3`、单元测试 `17/17`、Pi fake CLI、六个受影响 Skill official validator、plugin validator 与 `0.7.0` candidate coherence 已通过。Codex 已精确安装 `sacha-orchestra@sacha 0.7.0`，source/cache `46/46`、missing/extra/hash mismatch 均为 `0`；fresh task discovery 和真实 Planner/Clarify 行为仍未验证。

### 4.28 Released：项目文档收尾与确定性模板

`0.7.1` 修复真实 closeout 偏差：完整批准并执行、产生持久代码变化且完成实际运行验证的复杂 Spec，必须在根任务结束前检查一次项目文档候选；只有项目 policy 要求 Human 决定或写入授权为 `per-write-confirmation` 时才询问一次。简单一行修复、纯问答、无持久 delta 或没有合格发布内容的任务静默跳过。Execution Report 继续记录本次执行证据，change archive/system guide 面向项目读者，Project CONTEXT 只维护跨任务稳定术语与入口，三者不互相替代。

Project Integration 可显式绑定 document-template catalog path。运行时先读取固定 `profiles.json` 做 profile 决策，再只读取选中的模板；禁止扫描文档根目录、随机抽样或隐式模仿既有文风，没有绑定时使用 plugin bundled fallback。Canonical fallback 保留语义主题而不输出固定“档案卡片”；项目发布文档中的范围、版本、验证边界只在影响读者判断时自然进入正文。Skill 从 `project-documentation` 统一更名为 `document-project`，display name 保持 `Sacha Orchestra` 命名空间。

同一 release 删除 setup/project-rules/setup-agents 和文档模板绑定中无消费者、重复或展示性的 hash。精确内容仍只在并发/覆盖保护、不可变产物身份或跨边界字节一致性确有消费者时保留；工具可传递的 planned delta 不要求 Human 手工复述。Project Setup `45/45`、Spec Artifact contract `4/4`、单元测试 `17/17`、十个 Skill official validator、plugin validator 与 `0.7.1` candidate coherence 已通过；安装与 cache parity 作为发布后的独立证据核对，不替代 source release 身份。

### 4.29 Released：批准 Spec 后迁移独立 Executor task

`docs/plan/2026-08-06-executor-task-migration/spec.md` 冻结真实 MobileDevTool iOS 任务暴露的缺口：大量调查已经压缩进持久 Spec 后，普通批准仍应立即推进，但可靠高占用/compaction 或可直接观察的多阶段长历史可触发一次明确建议。只有 Human 选择“批准并新开执行任务”才授权用户可见 task migration；普通“批准”不得被静默解释为创建 task，无可靠 Runtime 信号时不得伪造遥测。

Workflow 15、Coordination 7 与 Codex Adapter 以 Task/Scope revision、批准 Spec reference 和 workflow transfer 去重，只 create/reuse 一个 target。新 task 只消费 AGENTS、Spec、必要 Artifact/evidence reference 与最小 Entry/identity，不复制完整历史，并接管 Execute、Review/返修与 closeout；旧 task 展示 target reference 后结束，不 wait/join。创建前失败可回退原 task，创建后恢复和最终结果只在 target 推进。显式 Feedback 则由 Source 以原生 query/create/wait 复用或建立唯一 repair target 并消费根终态；该 target 已有上游 return consumer，不再嵌套迁移。

迁移不替代 Manager/Reviewer Gate。当前 owner 发现多个候选单元、依赖或恢复协调时调用 Manager；Manager 统一评估、拆分、建立依赖并逐波判定 readiness。串行结论只约束当前波次，本波结果回到同一 Task/Scope revision 后重算剩余依赖图；后续波次至少两个 ready 且隔离时，仍须在该波次首次 wait 前实际派发 subagent。普通同-task、迁移 target 与 Clarify research 共用该算法；共享输出由 integration owner 串行处理，正式 Reviewer 使用未参与方案/实现的独立 provenance。

Codex Adapter 把 route assessment 简化为“任务形态 broad/bounded × 负荷 critical/standard 或 nontrivial/light”。自动 route 只有 Sol xhigh、Sol medium、Luna max、Luna xhigh；Human exact 可指定其他 model/effort，但 Adapter 不主动选择 Terra 或 Sol high/max/ultra。自动 Luna 未启动即失败时只允许一次 Sol medium fallback；Sol、Human exact 或可能已开始工作时停止。Pi one-shot 调用从 Adapter active surface 移除，既有脚本、Setup 配置与历史发布记录保留。文本预算只告警；本 candidate 不新增 Artifact/Handoff 字段、Registry、Hook、MCP 或生产 Role，也不修改外部消费项目。

## 5. `1.0.0` 决策

`0.x` 保持为 `1.0.0` 前的 candidate line。当 Core、Adapter、Skill 的职责和 breaking boundary 已稳定，且没有已知 release-blocking 缺陷时，Human 可直接决定进入 `1.0.0` 发布收尾。

真实并行、自主 closeout、自举升级、第二 Runtime、安装后案例或独立 Review 都不是版本举证门槛。真实使用暴露失败后，把案例固化为约束或回归检查；没有失败时不制造任务证明能力。

## 6. Self-hosting

Self-hosting 是可选使用方式，不是成熟度等级或版本门槛。当前维护任务自然适合 Sacha 时直接使用；不为完成自举路线强制拆分 Manager Packet、并行、Review 或安装验证。

## 7. `1.0.0` 之后

只有真实需求出现后再评估：

- Advanced coordination：跨仓库依赖、复杂取消/恢复、动态并行度和更大规模 Work Packet；
- Portability：第二项目或其他 Agent Runtime 的 Adapter 审计。

不得为证明通用性预建第四生产 Role、Agent OS、全局状态机、数据库、后台服务或跨项目特例。

## 8. 变更方式

- 涉及本文长期架构、成熟度 Stage、self-hosting、`1.0.0`、Manager、并行、alias removal 或 Core breaking change 的任何修改，只有 Human 明确确认具体改动后才可写入；该确认本身不要求额外 Spec。
- 需要比较实质方案、冻结新实现 Scope、跨 context 恢复、改变 Core contract 或执行 breaking migration 时，才创建 Planner Spec。
- 普通 plugin change/fix/iterate 保持 Direct；路径遗漏和同目标验证失败在原 Scope 内修复。
- 安装、外部项目写入、commit、push、tag 和发布仍需 Human 对具名动作明确授权。

路线图复审只在当前主线完成、Runtime 能力实质变化、开始 `1.0.0` 发布、启动第二 Runtime/项目或提出 Core breaking change 时进行。
