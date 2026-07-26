# Codex Runtime Adapter

> Implements: Workflow Contract 4；Artifact Protocol 1
> Status: Normative Codex mapping

## 1. Responsibility boundary

本文只把 Sacha Orchestra Core 映射到 Codex 原生能力。稳定协作语义来自：

- [Workflow Contract](../../core/workflow-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

本 Adapter 不定义 Role、Gate、生命周期、Artifact、Handoff、项目命令、证据等级或发布流程。Project AGENTS 和 Domain Skills 拥有项目知识；Skill 拥有 Role-local procedure；Evolution 拥有版本与验证状态。

## 2. Role、owner 与 context

| Core responsibility | Codex mapping |
| --- | --- |
| Planner | 独立 Codex task 或明确隔离的 context 装载 `sacha-orchestra:planner` |
| Executor | 一个明确 owner 的 task/context 装载 `sacha-orchestra:executor` |
| Reviewer | 未参与当前方案或实现的独立 task/context 装载 `sacha-orchestra:reviewer` |
| Manager | 根 task 装载 `sacha-orchestra:manager`，以原生 subagent 协调已批准 Work Packet |
| Workflow owner | 接收用户 objective 的根 task；持有 runtime-only return address，并持续推进到 Core 根终态 |

独立性由输入与参与历史的 provenance 判断，不由 task 名称或标识符判断。Runtime thread/host/agent id 只用于当前调度，不写入 Core Artifact 或九字段 Handoff。

## 3. Formal Role transition

### 3.1 Create or reuse

首次正式 dispatch 前，根 owner 从当前 task 元数据或唯一查询结果解析自身 `threadId` 和可选 `hostId`。无法唯一解析或目标不能安全 return 时进入 `completion_return_blocked`，不得创建只能由 Human 手工发现结果的 Role task。

每次 transition：

1. 按 workspace、Task ID、Scope Reference、目标 Role、Artifact 可达性、provenance、owner 和可续发状态筛选候选。
2. 唯一合格候选存在时复用；没有候选时在同一 local project 创建目标 task；多个候选、身份不清或 owner 冲突时进入 `human_decision_required`。
3. 新 Task ID/Scope 的 Reviewer 必须使用未参与当前方案或实现的独立 task；fork 继承参与历史，不满足独立 provenance。
4. Source 发送一行 route intent，并附 runtime-only `<codex_delegation>`：

```text
workflow_owner_thread_id
workflow_owner_host_id?
task_id
scope_reference
expected_next_role
handoff_revision
callback_policy=required
```

5. create/reuse 成功后，根 owner 保持当前 phase，以目标 `threadId`/host 调用 `wait_threads`；不得用 list/read 轮询 Target，也不得结束为 idle receiver。

### 3.2 Terminal return

Target 先完成适用 Artifact 和九字段 Handoff，再在 final terminal output 写出一次短 `<codex_callback>`，包含 Core completion notice、delegation identity、Handoff locator/revision、Outcome 与 route intent。Target 写出后结束，不调用消息发送能力唤醒或监控 owner。

根 owner 从 `wait_threads` 的 terminal payload 核对 Task ID、Scope、Handoff revision、owner、Source/Target Role、snapshot/Packet identity 和 dedup key。错误或重复 payload 不产生额外 dispatch、写入或 terminal transition。验证通过后，owner 执行 Core 唯一合法的下一 transition。

`send_message_to_thread` 只用于向唯一既有 target 派发 route intent 或有界 follow-up，不能替代 owner join/restore。

### 3.3 Model configuration

`create_thread`/task reuse 和 `spawn_agent` 使用工具实际暴露的模型、推理强度与 context 参数。只有 Human 当前明确指定，或批准 Scope 原样保存了 Human 的精确配置时才传覆盖值；否则省略覆盖并使用 Runtime/default/custom-agent 配置。工具不支持显式配置时报告真实错误，不自行替换或降级。

### 3.4 Progress and failure

Codex required child 的默认 first-progress bound 为 `60s`。有效进展沿用 Core 定义；首窗无进展时检查真实 child 状态并发送一次定向 liveness 请求，再等待最多 `30s`。仍无进展时记录 `required_child_first_progress_missed`，中断并确认 terminal/cancelled 后才能接管。首次进展后的单次 wait/join 最长 `60s`。

当前 user-facing task 活跃时，每 `60s` 至少提供一次 bounded progress notice；phase transition、等待、blocker 或验证失败立即报告。

Transport、Identity 或 Progress 失败时，按 Core schema 生成 runtime deviation packet。Codex 只补充真实 thread/host、task/agent lifecycle、工具错误和可执行 repair/re-verification entry。

## 4. Manager and subagent mapping

Manager Gate 由 Core 或批准 Scope 决定。Gate 开启后：

1. 每个 ready Work Packet 使用一个 `spawn_agent` 实例；显式 Packet、known facts、约束和 evidence locators 足够时使用 `fork_turns=none`，确需尚未落盘的最近 Human 决定时只传最少正整数 turns。
2. required child 由 `wait_agent` 消费 completion；需要补充输入时使用 `send_message` 或 `followup_task`；需取消时使用 `interrupt_agent`。
3. `parallel_expected` 成立时，在首次 wait/join 前启动至少两个实例；槽位、依赖、Scope 或授权阻塞记录为 `parallel_blocked`，条件满足却未启动记录为 `parallel_dispatch_missed`。
4. 默认 report budget 为 `30` 行 / `6000` 字符。预算只限制报告，不删除 Core 最小事实集、失败、未验证项或 evidence locators。
5. integration owner 核对原始证据后串行处理共享生成物、Git 动作和整体验证。

独立 Executor task 只在 Work Packet、single writer、Artifact、callback 与 Human-explicit Runtime 配置均已冻结时使用；其他 Packet 保持 subagent。

## 5. Goal mapping

Core objective 与 `goal_complete` 不要求创建 Codex 原生 Goal。只有 Human 明确要求 exact Goal 时才使用原生 Goal 工具。Goal 不是第二份 Scope、授权、Artifact、Handoff 或完成证据，不跨 task 迁移。

局部 blocker 不直接映射为原生 Goal `blocked`。只有 Core ready branch 为 `0`，且 Runtime 的 blocked 条件也成立时，才更新原生状态。

## 6. Skill packaging and discovery

Plugin manifest 通过 `"skills": "./skills/"` 暴露：

- `sacha-orchestra:planner`
- `sacha-orchestra:executor`
- `sacha-orchestra:reviewer`
- `sacha-orchestra:manager`
- `sacha-orchestra:feedback`
- `sacha-orchestra:setup-project`
- `sacha-orchestra:clarify`

`agents/openai.yaml` 只提供 Codex UI metadata，不定义 Role 行为。`setup-project` 与 `clarify` 固定为 explicit-only；当前 Skill、Core 和 Project Integration 共同决定何时读取，不由关键词自动触发。

`setup-project` 只生成当前 Schema v3 Project Binding。它的 discovery、确认、事务、冲突和 capability reconciliation 由该 Skill 及 bundled generator 定义；Adapter 只提供当前 context 已暴露的 Skill/plugin metadata，不扫描 cache、全局目录、marketplace、网络或任意 workspace。

## 7. Artifact reachability and recovery

正式 dispatch 前，Source 必须证明目标 task 能读取批准 Scope、必要 Artifact、原始 evidence locators 和完整九字段 Handoff。保存位置由 Project Integration 决定；不得依赖隐藏历史、界面状态或 Runtime 内部标识。

Review 使用 Core 定义的唯一实现 Baseline 和 `acceptance_revision`。runtime-only delegation 只携带用于 Identity 核对的 locator/hash，不增加 Artifact 或 Handoff 字段。

## 8. Marketplace, installation and fresh discovery

源码 workspace 使用 repo-local marketplace：

- manifest：`<workspace-root>/.agents/plugins/marketplace.json`
- plugin source：`./plugins/sacha-orchestra`

注册、安装、refresh、remove 和 reinstall 会改变 workspace 外状态，必须有 Human 对精确动作的明确授权。先用当前 plugin-creator 的 `read_marketplace_name.py` 读取 marketplace 名称；不得猜测、手工编辑 marketplace 或 cache。

安装或刷新后，使用在该动作之后启动且重新装载 Skill registry 的新 task 验证：

1. `plugin list` 与安装 cache 的版本一致；
2. canonical Skill locator 直接解析到已安装版本；
3. 正式 Role、Manager、Feedback、`setup-project` 和 `clarify` 的 discovery policy 与 metadata 一致；
4. 代表性行为只声明真实执行覆盖的层级。

安装或刷新前已启动的 task、手工定位源码/cache 或仅证明文件可读不构成 fresh-context discovery。

## 9. Authorization and failure handling

- 未获 workspace 外授权：停止在 workspace-local 验证。
- task、agent、Goal、CLI 或 discovery 能力不可用：记录真实错误、影响和恢复入口，不静默换路线。
- Artifact、identity 或 return transport 不可验证：保持未完成并进入 Core 对应阻塞路线。
- Core 与本 Adapter 冲突：停止相关写入；Adapter 不修改 Core 迁就平台限制。
