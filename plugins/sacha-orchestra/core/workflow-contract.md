# Workflow Contract

> Contract Version: 4
> Status: Normative Core contract

## 1. 范围

本文是生产 Role、三个 Gate、Manager 控制面、生命周期和返修路由的唯一权威。Artifact 与九字段 Handoff 由 [Artifact Protocol](artifact-protocol.md) 定义。

Core 只定义平台中立、项目中立的协作语义。Runtime 工具与 transport 归 Adapter；项目命令、领域知识和证据规则归 Project Integration 或 Domain Skill；Role-local procedure 归对应 Skill。下游不得重定义 Core。

## 2. 不变量与入口

所有路线遵守以下不变量：

- 默认从 Executor 开始；Gate 没有事实依据时保持 Executor-only。
- Planner、Reviewer、Manager Gate 分别判断方案不确定性、后果与验证风险、协调复杂度。
- 同一写入 Scope 同时只有一个活跃写入者。
- Human Conductor 保留目标、Scope、高影响动作和外部状态变更的最终授权。
- 报告、自报和 Handoff 只索引事实；完成声明依赖真实状态和原始证据。
- Artifact 按持久化和恢复需要生成，不为形式完整强制创建。
- 非 Direct 流程由一个稳定 workflow owner 推进到根终态；Role 或 Work Packet 完成只是中间事件。

入口只有两种 Direct 路线：

- `L0 Local Direct`：任务没有进入 Sacha；仅遵循适用的 Global/Project 规则，不装载 Sacha Role、Core 或 Artifact。
- `D0 Sacha Direct`：任务已合法进入 Sacha，三个 Gate 均关闭且无需持久 Artifact 或正式 Handoff；当前 Executor 直接完成，不 dispatch。

Plugin 存在，或输入仅出现 workflow、AGENTS、setup、安装等词，不构成 Sacha 入口。Route owner 根据目标与事实选择最低路线；只有缺失的用户偏好会实质改变交付或授权且无法自行推出时才询问。

## 3. 最低足够强度

共享强度只保留四个正交维度：

| 维度 | 强度 |
| --- | --- |
| Planning | `P0 No Plan`、`P1 Inline Plan`、`P2 Durable Spec`、`P3 Breaking Spec` |
| Artifact | `A0 Final Response`、`A1 Evidence Index`、`A2 Role Artifact`、`A3 Recovery Set` |
| Coordination | `C0 Single Executor`、`C1 Managed Serial`、`C2 Managed Parallel`、`C3 Multi-environment` |
| Verification | `V0 Diff/Parse`、`V1 Focused`、`V2 Integration`、`V3 Release`、`V4 Real Environment/Human` |

每个维度只在当前强度无法覆盖已验证的 Scope、风险、消费者、恢复或证据要求时升级；一个维度升级不带动其他维度。文件数量、耗时、版本号、Role 名称和“更稳妥”不是升级事实。

Reviewer Gate 决定由谁验收，Verification 决定执行哪些检查，两者正交。自动化无法证明的具体 `check_id` 才叠加人工或外部检查；`agent_observed` 不得替代要求 Human 确认的 `human_confirmed`。

授权、Reviewer provenance、single writer、return identity/dedup、九字段 Handoff、安全边界和原始证据权威不可降级。

## 4. Role 与 Gate

### 4.1 生产 Role

| Role | 唯一责任 | 不得 |
| --- | --- | --- |
| Planner | 调查事实、比较实质方案、冻结 Scope、决策、依赖和验收 | 把规划授权当实施授权；把假设写成事实；实施生产修改 |
| Executor | 在批准 Scope 或明确目标内实施、验证并记录证据 | 静默改变 Scope 或冻结决策；把摘要当原始证据；虚报验证 |
| Reviewer | 以独立 provenance 对照批准 Scope 和原始证据作出稳定裁决 | 为通过而改合同；把缺证据当实现错误；默认修复 |

正式跨 Role Handoff 使用 Artifact Protocol。名称、新 context 或新 task 本身不证明 Reviewer 独立；独立性取决于其未参与当前方案和实现。

### 4.2 Gate

| Gate | 打开条件 | 不构成打开条件 |
| --- | --- | --- |
| Planner | 目标、验收或 owner 不清；存在实质方案取舍；路径不可唯一确定；决策难逆 | 文件多、耗时、公共表面标签或无分歧修改 |
| Reviewer | 安全、权限、持久数据、breaking contract、困难回退、关键验证缺失、证据冲突或 Human 明确要求 | 文档、Skill、manifest、版本封装或可回退且完整验证的局部修改 |
| Manager | 至少两个可独立推进单元、依赖图、安全并发、多环境实例或显著协调成本 | 工作困难、耗时、多文件或单纯希望更多 Agent |

Gate 决策绑定当前 Scope、验收、owner、交付、安全/权限和依赖事实。这些事实实质变化时重新评估，但不自动打开 Gate；locator、日志、时间戳、证据补充和不改变语义的文案修正不会使旧判断失效。

## 5. Review 与证据

正式 Review 只维护一个实现 Baseline。Git 可覆盖的内容使用可解析 commit、range、diff 或文件集合；Git 无法覆盖的生成物、删除项、安装包、外部配置和运行产物才补 manifest/hash。

Baseline 或 `acceptance_revision` 变化使旧 verdict 失效。同一 Baseline 下的 evidence-only delta 记录 `changed_check_ids`、旧/新状态、locator、原因和风险，只复核受影响检查；不得无理由重建 Baseline、全量测试或完整重审。Review Entry append-only，历史状态与 locator 保持可达。

批准 Scope 含验收矩阵时，使用稳定 `check_id` 和 `acceptance_revision`。覆盖摘要至少包含：

- Scope/matrix locator 与 revision；
- required/attempted check ID；
- 每项 result、evidence locator、risk、resume entry；
- 人工项的 `human_assistance_state`；
- passed、failed、unverified、environment-blocked、human-assisted 计数。

人工项状态为 `pending | completed_passed | completed_failed | completed_inconclusive`；非人工项默认省略，定宽结构可写 `not_required`。缺失、未知、冲突、stale revision、未知 check、不可达 locator 或计数不一致保持未验证。Provider 只提供证据索引，不拥有 verdict。

Reviewer Outcome：

| Outcome | 使用边界 |
| --- | --- |
| `Accepted` | Scope 与全部 release-blocking 检查满足 |
| `Accepted with follow-up` | 仅剩非阻塞人工、环境或证据后续项 |
| `Needs Evidence` | 证据不足以裁决必需检查 |
| `Needs Fix` | 已知实现缺陷、真实失败或不可接受风险 |
| `Needs Replan` | 批准合同缺失、错误或失效 |
| `Blocked` | 安全替代路径耗尽，依赖 Human 或外部状态变化 |

`Needs Evidence` 是中间状态，不附加 Reject。只有批准矩阵明确为 release-blocking 的未完成项阻塞最终交付。

局部 blocker 不是新的根状态。Phase owner 记录受阻范围、原因和恢复条件，并继续其他安全且已授权的 ready branch；只有 ready branch 为 `0` 且继续需要 Human 决策、新授权、外部状态变化或 return transport 恢复时，才进入根阻塞路线。

## 6. Manager 控制面

Manager 是按 Gate 启用的控制面，不是第四个生产 Role，不代替 Planner 设计、Executor 写入、Reviewer 验收或 Human 授权。

每个 Work Packet 至少包含：

`owner`、`read scope`、`write scope`、`dependencies`、`input`、`expected output`、`verification`、`stop condition`。

只读 Packet 可并行；写入 Packet 仅在 exact write scope 静态不重叠时并行。共享生成物、公共 schema、Git 动作和整体验证由单一 integration owner 串行完成。Packet 不扩大 Scope 或授权。

Packet report 默认 `delta-only`，保留 `status/outcome`、changed files、validation、blockers、risks/unknowns 和 evidence locators；无内容写 `None`。报告预算不得隐藏失败、未验证项、Scope 偏离或授权阻塞；达到预算时标记 `report_limited`，原始证据仍由 locator 指向。

当 Manager Gate 开启、至少两个 Packet ready、Scope 不重叠且依赖、授权和 Runtime 槽位允许时：

```text
parallel_expected == true
-> before_first_wait_or_join_started_instances >= 2
```

结果只有：

- `parallel_started`：首次 wait/join 前至少启动两个实例；
- `parallel_blocked`：存在可定位的 Runtime、槽位、依赖、Scope 或授权阻塞；
- `parallel_dispatch_missed`：条件满足但未实际并行。

不足两个 ready Packet 时使用 managed serial，不属于遗漏。具体实例、wait/join、liveness 和取消由 Adapter 映射。

## 7. 生命周期与路由

标准阶段为 Intake → Route → Plan（按需）→ Coordinate（按需）→ Execute → Review（按需）→ Close/Handoff。

Workflow owner 保存 objective、Scope、授权和完成条件。每个 delegated unit 或正式 Role 终态只返回一次 completion notice：

`Task ID`、`Source Role or Unit`、`Outcome`、`Scope Reference`、`Artifact or Evidence Locators`、`Workflow Owner`、`Next Role`、`Human Decision Required` 及理由。

Notice 是 transport，不是 Artifact、Handoff、授权或完成证据。Owner 验证 identity、Scope、Handoff、真实状态和授权后，只执行唯一合法的下一 transition，并对同一 Outcome/revision 去重。

根流程只有三种终态：

- `goal_complete`：objective、Scope 和 required verification 已满足；
- `human_decision_required`：继续需要实质方案、Scope/验收变化、新高影响授权、不可消歧 owner，或只有 Human/外部状态能恢复；
- `completion_return_blocked`：安全 return transport 和替代路径均不可用。

每个 transition 检查：

- `Transport`：required child terminal 被 owner 消费；成功 return 恰好一次；重复 return 不触发第二次 transition。
- `Identity`：Task ID、Scope、Handoff revision、owner、Source/Target、Review Baseline 或 Packet revision 与预期一致；不一致时拒绝且不产生额外写入或 dispatch。
- `Progress`：owner 恢复后，唯一下一 transition 已启动，或合法进入一个根终态。

断言失败产生 bounded runtime deviation packet，包含：

- assertion layer、expected/actual transition；
- Task ID、Scope、Handoff revision、owner、Source/expected/actual Target；
- 原始 evidence locators、责任层、影响和已有授权；
- Human stop gate、唯一 repair/re-verification entry；
- return address 和 revision/dedup key。

Packet 是 transport payload，不是 Artifact、授权或完成证据；平台调查方式归 Adapter。

动态路由：

- Executor 遇到新方案、Scope 或验收变化 → Planner；新增授权 → Human。
- Reviewer 发现实现缺陷 → 原 Executor；合同问题 → Planner；缺证据 → 唯一证据 owner。
- Manager 或 Runtime assertion 失败 → Feedback intake 或责任 owner。
- 环境不可用 → 先耗尽同 Scope 安全替代路径，再决定是否进入 `human_decision_required`。

普通 Role completion、同 Scope 返修、补证据、复验、唯一 owner 路由和已授权 closeout 不是 Human checkpoint。

Direct Scope 以用户语义目标和明确约束为边界；预计文件列表不是 hard allowlist，除非 Human 或批准 Spec 明确如此。当前 Executor 可修复同一目标直接必需的遗漏、路径、格式和定向验证失败；实质新方案、breaking contract/schema、权限、安全、持久数据、验收变化、未授权外部动作或无法完整验证时停止并重新路由。
