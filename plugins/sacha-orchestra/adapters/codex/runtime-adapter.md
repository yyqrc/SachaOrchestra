# Codex Runtime Adapter

> Implements: Intake Contract 3；Workflow Contract 9；Assurance Contract 1；Coordination Contract 3；Artifact Protocol 3
> Status: Normative Codex mapping

## 1. Boundary

本文映射 Codex 原生 task/subagent，以及由 Codex owner 管理的本地 one-shot helper。以下是可选 owner locator，不是预加载清单：

- [Intake Contract](../../core/intake-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

Adapter 不定义入口、Role、Gate、Artifact、项目命令或发布状态。Project AGENTS/Domain Skill 拥有项目知识；Skill 拥有 local procedure；Evolution 拥有版本与验证状态。

## 2. Intake、Role 与 owner

| Core responsibility | Codex mapping |
| --- | --- |
| Intake/Route owner | 接收 objective 的 root task 装载 `sacha-orchestra:using-sacha` |
| Planner | 独立 task 或隔离 context 装载 `sacha-orchestra:planner` |
| Executor | 明确 owner 的 task/context 装载 `sacha-orchestra:executor` |
| Reviewer | 未参与当前方案/实现的独立 task/context 装载 `sacha-orchestra:reviewer` |
| Manager | root task 装载 `sacha-orchestra:manager`，以 subagent 协调独立任务 |
| Workflow owner | 接受 Sacha 后的 root task；持有 runtime-only return address并推进到根终态 |

Runtime 常驻面只暴露 Skill metadata。`using-sacha` 先加载 Intake；直接任务不读生产 Core/Role/Binding。显式 using-sacha/Sacha 请求或 canonical Role 调用视为接受；Clarify/Setup 仍 explicit-only。

同 context 直接执行且不使用 dispatch、return、恢复或 Runtime 验证时不读本 Adapter；首次出现 consumer 时才加载对应章节。

独立性按参与历史/input provenance 判断，不按 task/thread 名称。Runtime id 只进 transport。

## 3. Formal Role transition

### 3.1 Capability selection and join

dispatch 前先读取当前可用能力和宿主授权，不假定 `threadId`、`hostId`、task 创建或特定 join 工具存在。

1. 不要求独立 provenance 的同 context 工作保持当前 task；一个有界 helper 可由 owner 直接使用 `spawn_agent` 并以 `wait_agent` 消费。
2. 正式 Role transition 选择当前可用且能保留 identity/terminal 的原生 subagent 或 task transport。只有 Human 明确要求/授权用户可见 task 时才创建；已有 task 按 workspace、Task/Scope、Role、provenance、owner 和可续发状态筛选。
3. 独立 Reviewer 使用未参与方案/实现的 context；fork 继承参与历史，不证明独立。
4. Source 只发送目标/交付、允许范围、完成检查/停止条件和必要 locator；依赖、隔离、route identity 或 revision 只在当前 transport/consumer 需要时增加。
5. owner 使用 transport 对应的 `wait_agent`/`wait_threads` 等 terminal join。定点 list/read 可诊断 identity 或工具异常，不得忙轮询；一种 transport 不可用时尝试同 Scope 安全替代，全部耗尽才进入 `completion_return_blocked`。

Feedback Source-local helper 只读补证，不取得 target workspace、owner/Role 或 repair identity，不能充当 repair target。

按 Skill identity 消歧：唯一匹配就复用且不调用 `create_thread`；不唯一请 Human 决定。显式修复、目标唯一、transport 可用且无匹配时，Source 只调用一次 `create_thread`，在 owner workspace 创建一个 repair task。自动 Feedback 还需已接受 lifecycle。新 task 不扩权；Target 独立核对写入、Git、安装、发布授权，缺少时暂停。

Source 用 `wait_threads` terminal join并消费一次结果；`send_message_to_thread`、helper 或报告不能替代；且不修改 repair source、不重复创建或写其他 task。

### 3.2 Terminal return

Target 先完成必要 Artifact/Handoff，再在 final 返回结果/delta、实际验证、阻塞/风险和 locator；原生 join 未携带且消歧必需时才补 route identity/revision/dedup。随后结束，不发消息唤醒或监控 owner；更正使用新 revision。

Owner 结合原生 join 与 payload 核对当前 consumer 必需的 Task/Scope revision、owner、Source/Target、snapshot 和 dedup。错误、陈旧或重复结果不产生额外 dispatch/write/terminal；正确结果只触发唯一下一 transition。`send_message_to_thread` 仅用于补充输入，不替代 join。

### 3.3 Configuration、progress、failure

正式跨 context dispatch 的配置优先级为 Human 本次精确配置、批准 Scope 的精确配置、下表自动路由、Runtime default：

| Target | Model / reasoning_effort | 首个命中条件 |
| --- | --- | --- |
| Planner | `gpt-5.6-sol` / `xhigh` | breaking contract/schema、跨 Runtime/系统、难逆决策、耦合方案或验收冲突 |
| Planner | `gpt-5.6-sol` / `high` | 其他需要冻结实质方案的规划 |
| Executor | `gpt-5.6-sol` / `high` | 安全、权限、持久数据、breaking、不可逆外部动作或广泛兼容/发布风险，同时涉及跨系统、长依赖链、复杂迁移/集成或多阶段昂贵验证 |
| Executor | `gpt-5.6-sol` / `medium` | 其他路径与直接验证已确定的高风险实施 |
| Executor | `gpt-5.6-terra` / `xhigh` | 多模块、长依赖链、复杂调试/集成或多阶段验证，且不属于高风险 |
| Executor | `gpt-5.6-terra` / `high` | 其他 Scope/验收已冻结、模式既有且验证明确的实施 |

高风险优先，复杂高风险再优先；模型不替代 Planner Gate。普通 Executor 输入不自包含时不用 `terra`。自包含任务使用 `spawn_agent` 的 `fork_turns=none`、`model` 和 `reasoning_effort`；未落盘 Human 决定只传最少 turns。不得为覆盖模型创建用户可见 task；必须继承完整 context 时保留继承模型。Direct/current context 不切模型。

Human/Scope 精确配置不受支持时暂停；自动配置不可用时使用 Runtime default。owner 记录 requested/effective 配置和 fallback 原因；旧写入者 terminal/cancelled 前不得以其他配置启动同 Scope 写入。

单次 wait/join 最长 `60s`；timeout 只触发进度/liveness 检查。存在可证明活动时不按墙钟中断；仅在失活、越界、用户取消或继续会双写/增险时中断，确认 terminal/cancelled 后再接管。

Transport/Identity/Progress 失败按 Coordination Contract 生成 deviation；本 Adapter 只补原生结果未携带且恢复必需的 thread/host、task/agent lifecycle、工具错误与 repair/re-verification entry。

搜索、diff、日志和列表默认返回短摘要，缺少决策信息时定向展开。大原文有消费者时写 task-local/Artifact，否则保留工具 locator；截断不得丢失失败、warning、未验证、Scope 偏离或授权阻塞。

### 3.4 本地 Pi one-shot

目标/验收冻结、输入自包含且不依赖未提交改动、写入隔离、验证确定、无需 Human/外部副作用且失败可接管时，Executor 可选本地 Pi。它是候选实现 helper，不是 Role/Reviewer/workflow owner；否则使用 Codex 原生路线。

Human/Scope 精确 model/effort 优先；自动路由只选择项目配置中的通用槽位：

| 条件 | Route | Setup family filter |
| --- | --- | --- |
| 高复杂度、长依赖链、复杂调试/集成或多阶段验证 | `pro` | `kimi k3` |
| 普通自包含实现 | `standard` | `glm-5.2` |
| 低返工且追求轻量性价比 | `lite` | `deepseek`，优先 v4/pro；`gpt-5.6 luna` 为备选 |

精确 `provider/model` 只来自 `setup-project` 读取本机 `pi --list-models` 的巡检或 Human 确认的 Project Integration；plugin 不保存 provider 清单或完整型号。优先级是 Human 本次精确配置、已确认项目 route、按上表筛出的候选、Pi Runtime default；项目配置即使当前清单缺失也不被自动替换，而是 warning。显式型号与 effective 不一致时失败，不静默换型。

integration owner 准备干净、精确 HEAD 的 linked worktree和自包含任务，再调用 [pi once](../../scripts/pi_once.ps1)，给出 Prompt、显式读写路径及可选完整 model。helper 使用 JSON event stream、无 session、关闭自动 extension/Skill/prompt/context，只启用 `read,edit,write,sacha_result`；显式 guard 在工具执行前拒绝越界、控制目录、symlink/junction 和多链接写目标，Pi 只能以终止型结构化结果收尾。

guard 和事后检查是应用层 containment，不是原生 Windows OS sandbox；调用方必须信任 `PiPath` 指向的 executable。owner 仍核对 ignored 文件、Git metadata、HEAD、退出码、JSONL、结构化 outcome 和真实 diff，并重跑验收。失败不集成、不 resume；旧进程 terminal 后由 Codex subagent 消费原任务、候选 diff、实际失败和审查意见。

## 4. Manager、Goal 与 Artifact

单个职责内有界 helper 不打开 Manager Gate，由当前 owner 直接管理。Manager Gate 开启后，每个 ready 单元使用一个 `spawn_agent`；自包含时 `fork_turns=none`，缺少未落盘 Human 决定时才传最少 turns。completion 用 `wait_agent`；补充输入/取消使用 Runtime 对应能力。

`parallel_expected` 成立时首次 wait/join 前启动至少两个实例。结果按消费者和风险保留必要 delta，不为格式强制落 Artifact。integration owner 串行应用隔离 patch/候选实现并处理共享生成物、Git 与整体验证。

Core objective 不要求原生 Goal；只有 Human 明确要求 exact Goal 时创建。Goal 不是 Scope、授权、Artifact/Handoff 或证据；局部 blocker 不直接映射为原生 blocked。

正式 dispatch 前证明 Target 可读取 Scope、必要 Artifact、原始 locator 和当前 consumer 所需 Handoff 语义。Review 使用 Core Baseline/`acceptance_revision`；Runtime 实例 ID、模型、界面状态和内部存储标识只进入 transport。

## 5. Skill discovery 与 Project setup

Manifest `"skills": "./skills/"` 在 `sacha-orchestra:` 下暴露 `using-sacha`、`planner`、`executor`、`reviewer`、`manager`、`feedback`、`project-documentation`、`setup-project`、`clarify`。

`agents/openai.yaml` 只定义 metadata。Setup/Clarify explicit-only；Documentation 受 confirmed policy/授权约束；生产 Role 须显式调用或经 Intake 接受。

Setup 只在目标项目扫描已配置/约定的 Skill root；完整读取 authority/independent `SKILL.md` 及调用必需 locator，mirror 不重复。文件存在不证明 Runtime 可调用，须核对当前 metadata；不得扫描 cache、全局目录、marketplace、网络或其他 workspace。

Setup 只从当前 context 已知的 plugin Skill locator 定点读取同 plugin catalog。项目 Skill 先按正文证据判定 `schedulable`，再由 Human 确认 load policy；id/目录/metadata 不替代正文。Role 按需读 binding/Skill；mapping 不预加载、不证明安装、不授权，也不转移 Gate/Scope/verdict。
