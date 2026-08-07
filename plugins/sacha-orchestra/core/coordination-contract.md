# Coordination Contract

> Contract Version: 10
> Status: Normative Core coordination contract

## 1. 范围与 owner

本文是 Manager 协调闭环和 owner transfer 的唯一 Core owner：定义评估、拆分、依赖、execution/research readiness、逐单元 runtime-neutral route requirement、派发/必要等待/取消、归并/return、identity/dedup、owner transfer 与 deviation；不得改变 Workflow Contract 的 Runtime 路由或把协调闭环变成新的 lifecycle。
Gate/lifecycle 见 [Workflow Contract](workflow-contract.md)，Human 可见交互见 [Human Interaction Contract](human-interaction-contract.md)，持久记录见 [Artifact Protocol](artifact-protocol.md)。
无 delegation、跨 context owner transfer/return 或恢复 consumer 时不加载。

Manager 是调用后返回原 invoking owner 的协调控制面。当前 workflow owner 发现多个候选单元、依赖图、并发安全、跨 context 恢复或其他需要协调的 owner 时调用 Manager；invoking owner 可提交尚未完整拆分或判定 ready 的候选。
普通同 task Executor、迁移 target 与 Clarify research 共用本合同的评估、拆分、依赖、readiness、派发、等待、取消、归并和 return 算法；差异只在 execution/research readiness 与返回 owner。
当前 owner 在其既有 Scope 与授权内只有一个有界 helper 时可直接管理，并负责同等 assessment、等待、取消和证据核对；仅拥有相应写入授权时才集成候选 patch。Clarify 的研究 helper 保持只读；helper 返回 reference，Role 与 verdict 仍由 invoking owner 持有。

## 2. 评估、拆分、依赖与就绪判定

Manager 先按 objective、Scope、授权、完成条件和输入事实拆分候选单元，建立依赖图和依赖波次；原授权与 single writer 约束继续适用。

每个候选单元在派发前做同一套 runtime-neutral assessment：target kind、风险、难度/歧义、依赖/上下文、自包含性、可验证性、返工成本和独立性；必要时补权限、breaking、持久数据与独立 Reviewer 事实。Manager 为派发单元负责，单 helper 由 invoking owner 负责。

execution-ready 要求 Scope/验收已冻结、边界和输入自足、依赖与授权满足、可独立交付并直接验证；research-ready 要求问题/查询范围、预期证据和停止条件明确、输入自足、依赖满足且默认只读，可在实施 Scope/验收冻结前成立。Core 只产生 route requirement，Adapter 拥有模型名与 Runtime 参数映射。

## 3. 派发、等待、取消与 single writer

派发消息向 Target 提供目标、允许范围、完成检查和停止条件；有依赖或并发时增加隔离边界。单个 helper 直接使用 prompt/message；原生 transport 已绑定的 identity 不重复编码。研究任务另给问题、查询范围、预期证据和停止条件，默认 read-only。

只读任务可并行。共享工作树中同一文件或可变输出不得并行写；隔离 worktree、patch-only 或候选实现可重叠分析，由 integration owner 串行应用。共享生成物、公共 schema、Git 和整体验证保持串行。

Manager 对同一 Task/Scope revision 的剩余依赖图持续承担调度责任；workflow owner 始终保留 Role、写入、集成和根终态责任。每个波次按同一闭环推进：

```text
评估当前波次 → 串行执行或并行派发 → 聚合本波结果 → 重算剩余依赖图 → 下一波 / 阻塞 / 耗尽
```

串行结论只约束当前波次。invoking owner 串行完成本波 ready 单元并把结果交回同一 Task/Scope revision，Manager 随后重算剩余依赖图；不得据此把后续波次整体改为串行或结束协调。并行波次完成后同样聚合并重算。只有依赖图耗尽、当前无可推进单元而返回阻塞/恢复条件、命中停止条件或进入 deviation，当前调度责任才结束。

对每个依赖波次，若至少两个单元 ready 且写入/输出隔离，Manager 必须在该波次首次 wait 前实际派发至少两个实例；Gate、计划记录、迁移 task 或 full-history helper 都不能代替实际派发。若只有一个 ready，或多个 ready 的写入/输出不能隔离，Manager 返回当前波次的串行结论，不为并行而拆分；若没有 ready，或输入、依赖、授权使当前波次不可推进，则返回阻塞与恢复条件，不伪装成串行执行。

派发不自动触发 wait。每次派发后先重算当前依赖图；只要还有不依赖未完成结果、且不与活跃工作冲突的 ready 单元，当前 owner 就先执行或继续派发。只有目标已真实启动、当前 owner 是其结果 consumer、下一 transition 依赖该结果，并且没有其他 ready 工作时，才到达依赖屏障并等待：

```text
派发目标 → 重算 ready → 推进不冲突工作 → 依赖屏障 → wait → 消费结果 → 重算剩余依赖图
```

Manager 通过 Adapter 执行派发、必要等待和取消；等待前核对当前 revision、result consumer、下一 transition、写入者与隔离边界。timeout 只接受新的 liveness 证据，不 busy polling、不重复读取相同进度，也不触发重复创建或 transition。取消后不得留下活跃写入者。完成或取消后只归并新事实、delta、实际验证、阻塞/风险和必要 reference；错误、陈旧或重复结果不得产生第二次写入、等待或 transition。无 result consumer 的 owner transfer 不等待。

返回只写结果/delta、实际验证、阻塞/风险和必要 reference；不为格式新建 Artifact，也不隐藏失败、未验证、Scope 偏离或授权阻塞。

## 4. Clarify research

Clarify 先使用当前 context 可达事实。一个研究单元由当前 Clarify owner 直接管理；出现多个候选研究问题、依赖图或正式恢复时调用同一 Manager 算法。Manager 依第 2、3 节判定 research-ready、依赖波次和派发数量，聚合事实、冲突、未验证项及 evidence reference 后返回原 invoking Clarify owner。

显式 Clarify 的窄授权足以调用上述只读 Manager coordination，但不等同接受完整 Sacha。研究任务不授权写入、冻结方案/验收、Review 或外部动作；发现需写入、新 Scope/方案或新授权时停止并返回 Planner/Human。Clarify 只消费 Manager 返回的事实，active Planner 继续核对其是否足以冻结 Spec。

## 5. Executor 任务迁移

Human 明确选择把批准的持久 Spec 交给用户可见 task 执行时，迁移 identity 是 Task/Scope revision、批准 Spec reference 与 workflow transfer。首次创建后保留原生 target identity；重复批准、重试或恢复只复用，不得再次创建，也不建 Registry。

新 target 接管 workflow owner、Execute、Review/返修和 closeout；原 owner 停止写入，交付原生 task reference 后结束，不 join、不等待 return。target 只消费项目规则、Spec、必要 Artifact/evidence reference 与 transport 未携带的最小 Handoff，不得复制完整对话。helper/subagent 不取得迁移 identity 或 workflow owner，full-history helper 也不得冒充 context 减负。

target 按第 2、3 节通用规则评估、拆分、建立依赖并派发单元；Gate 沿用 Workflow Contract，派发 ownership 沿用本合同。实现完成后按 Reviewer Gate 进入独立 Reviewer。

创建失败且没有产生 target owner 时可回退并报告；成功后恢复、失败处理和最终结果都由 target 持续推进，原 task 不恢复 owner。重复输入只返回既有 target reference。唯一 identity 或 Spec/Entry Condition 不可证明时停止迁移并走 deviation。

## 6. 完成、返回与 deviation

Owner 保存 objective、Scope、授权和完成条件。每个 delegated unit/Role 对同一 revision 只返回一次结果、实际验证、阻塞/风险和必要 reference。
原生 transport 无法消歧时才补 Task/Scope revision、Source/Target、owner 或 dedup；更正使用新 revision。

Feedback 由 Human 在另一个真实任务手动调用。该显式调用本身授权来源任务围绕具体反馈目标进行有界只读调查，并查询、复用或创建唯一反馈目标任务。Human 可提供原任务、项目或 evidence reference。完整反馈身份由反馈 workspace、具体 objective、owner，以及 Human 已提供时的来源 reference 组成；transport 可用时，来源任务只复用身份精确匹配且仍 active/resumable 的唯一目标任务；无此匹配时在本次调用授权内创建恰好一个目标任务，不再追加创建确认。已 terminal 的同一反馈身份精确重复只按 `no_op` 返回既有 reference，不产生新 owner transfer；其他 terminal/stale 候选不算匹配。身份、状态或唯一性无法证明时停止并请求消歧。
来源任务必须交付原生目标任务 reference；调查报告不能代替 owner 路由。只读调查 helper 仅补证，不取得反馈 owner、Role 或身份。完成 owner transfer 后，来源任务结束，不 join、不等待 terminal，也不转述目标任务最终结果。Feedback 调用只授权来源任务调查与路由；目标任务另行核对写入和外部副作用授权，并按 Intake Contract 使用通用的协调、迁移、Role、验证、收尾与根终态规则。

同一 payload 兼作 report/completion 时只返回一次；仅有消费者时落完整 report/evidence Artifact。Return consumer 必须通过当前调用或 transport 的 completion 路径消费结果；Human 可见结果只呈现已消费的结果并遵循 Human Interaction Contract。

根终态及结果：

- `goal_complete`：objective、Scope 和 required verification 已满足；
- `goal_partial`：已授权子集完成，剩余部分明确未完成且当前 objective 不再继续；
- `goal_cancelled`：Human 或上游 owner 明确取消；
- `goal_superseded`：objective 被新目标替代；
- `human_decision_required`：继续需要实质方案、Scope/验收变化、新高影响授权、不可消歧 owner 或 Human/外部恢复；Planner 提案获批且无其他阻塞时，原 workflow owner 立即消费该回复并启动 Executor；
- `completion_return_blocked`：安全 return transport 与替代路径均不可用；
- `external_failure`：外部系统已终止且同 Scope 安全恢复路径耗尽。

无改动但目标已满足时使用 `goal_complete`/`no_op`。其他非完成终态保留已完成范围、未完成原因、证据与恢复条件。

有 return consumer 的 delegation/Role transition 检查：

- Transport：terminal 被消费且 return 一次；
- Identity：核对当前 transport/consumer 实际需要的 Task/Scope revision、owner、Source/Target、Baseline；原生 join 已唯一绑定的标识不重复编码；
- Progress：下一 transition 已启动、处于可证明的 Runtime wait/用户 steering，或进入合法根终态。

用户可见 task migration 的 Transport 与 Progress 按第 5 节核对。

失败产生 bounded deviation，保留 expected/actual/impact、证据、恢复/停止条件及 transport 缺失的必要 identity/dedup。错误、陈旧或重复 completion 不产生额外 transition/write/terminal；环境不可用先耗尽同 Scope 安全替代。实现缺陷和同 Scope 证据补齐返回原 Executor；研究任务的失败、冲突或证据缺口返回原 invoking owner（Clarify 由原 Clarify owner 消费，active Planner 继续核对），旧写入者未 terminal 前不得另开写入者或盲目重试。
