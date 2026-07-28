# Codex Runtime Adapter

> Implements: Intake Contract 2；Workflow Contract 7；Assurance Contract 1；Coordination Contract 2；Artifact Protocol 2
> Status: Normative Codex mapping

## 1. Boundary

本文只映射 Codex 原生能力。以下是可选 owner locator，不是预加载清单：

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
| Manager | root task 装载 `sacha-orchestra:manager`，以 subagent 协调 Work/Research Packet |
| Workflow owner | 接受 Sacha 后的 root task；持有 runtime-only return address并推进到根终态 |

Runtime 只常驻暴露 Skill metadata。`using-sacha` 触发后先加载 Intake Contract；L0 不读取生产 Core/Role/Binding。显式 using-sacha、明确 Sacha 请求或直接 canonical Role 调用视为接受；Clarify/Setup 仍是 explicit-only narrow scope。

同 task 的 Executor-only D0 若不使用 task/subagent dispatch、return、恢复或 Runtime 验证，不读取本 Adapter。首次出现对应 consumer 时再加载所需章节，不因已接受 Sacha 或可能存在后续 Gate 预加载。

入口决定只保留在当前 task context/正式恢复证据中，不写 Artifact。Human 交互默认使用 Core 的技术紧凑顺序，复杂因果或操作步骤按需展开；当前 user-facing task 活跃时仍满足最长 `60s` 的 bounded progress。

独立性由参与历史和输入 provenance 判断，不由 task/thread 名称判断。Runtime id 只用于调度，不写入 Core Artifact/Handoff。

## 3. Formal Role transition

### 3.1 Capability selection and join

dispatch 前先读取当前可用能力和宿主授权，不假定 `threadId`、`hostId`、task 创建或特定 join 工具存在。

1. 不要求独立 provenance 的同 context 工作保持当前 task；一个有界 helper 可由 owner 直接使用 `spawn_agent` 并以 `wait_agent` 消费。
2. 正式 Role transition 选择当前可用且能保留 identity/terminal 的原生 subagent 或 task transport。只有 Human 明确要求/授权用户可见 task 时才创建；已有 task 按 workspace、Task ID、Scope、Role、provenance、owner 和可续发状态筛选。
3. 独立 Reviewer 使用未参与方案/实现的 context；fork 继承参与历史，不证明独立。
4. Source 发送最小 route intent、owner、Task/Scope、expected Role、Handoff revision 和 callback policy。
5. owner 使用 transport 对应的 `wait_agent`/`wait_threads` 等 terminal join。定点 list/read 可诊断 identity 或工具异常，不得忙轮询；一种 transport 不可用时尝试同 Scope 安全替代，全部耗尽才进入 `completion_return_blocked`。

Feedback target 须同时匹配 workspace/project、Task ID/Scope、repair objective、owner/Role、revision/provenance、可续发状态；同 cwd/仓库/Skill/owner/近似标题均不足。唯一完整匹配才复用；无匹配且 objective/Scope/owner 唯一时，显式 Feedback 创建隔离 repair task 并 dispatch bounded packet，自动 Feedback 仅在已接受 lifecycle 允许 transport 时创建；其他情况请求 Human。新 task 只继承 packet 授权，不扩大源码写入、安装、Git、发布或外部动作。Source owner 只 join/消费一次其 terminal result；不得发送到或写入其他 task。

### 3.2 Terminal return

Target 先完成必要的 Artifact/Handoff，再在 final 输出当前 revision 的 terminal callback：completion notice、delegation identity、Handoff locator/revision、Outcome、route intent；随后结束，不发消息唤醒/监控 owner。更正使用新 revision。

Owner 从 terminal payload 核对 Task/Scope/revision/owner/Source/Target/snapshot或Packet/dedup。错误、陈旧或重复 payload 为零额外 dispatch/write/terminal；正确结果只触发唯一下一 transition。`send_message_to_thread` 仅用于 route intent/follow-up，不替代 join。

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

高风险优先于普通 Executor，复杂高风险优先于普通高风险；模型强度不替代 Planner Gate。普通 Executor 输入不自包含时不套用 `terra`。自包含 Packet 使用 `spawn_agent` 的 `fork_turns=none`、`model` 和 `reasoning_effort`；只有缺少未落盘 Human 决定时传最少 turns。不得为模型覆盖创建用户可见 task；必须继承完整 context 时使用继承模型并报告未应用。Direct/current context 不改变模型或宣称路由已应用。

Human/Scope 精确配置不受支持时暂停；自动配置不可用时使用 Runtime default。owner 记录 requested/effective 配置和 fallback 原因；旧写入者 terminal/cancelled 前不得以其他配置启动同 Scope 写入。

单次 wait/join 最长 `60s`，timeout 只触发 bounded progress 和 liveness 检查。根据最近事件、活跃工具/构建、任务类型与 Runtime 状态决定继续等待或取消；存在可证明的活动时不得仅按墙钟中断。只有失活、越界、用户取消或继续会产生双写/风险时才中断，并确认 terminal/cancelled 后接管。

Transport/Identity/Progress 失败按 Coordination Contract 生成 deviation packet；本 Adapter 只补 thread/host、task/agent lifecycle、工具错误与 repair/re-verification entry。

搜索/diff/日志/列表以 `80` 行/`6000` 字符为默认 soft budget；按消费者、风险和信号密度自适应，可直接扩展必要片段。大原文已有消费者时写 task-local/Artifact，否则保留在工具结果并定向读取；不为硬限额制造文件，失败、warning、未验证、Scope 偏离和授权阻塞不得因截断丢失。

从 Adapter locator 得 `<plugin-root>`，不读正文或扫描 marketplace/cache/global：

```powershell
pwsh -File <plugin-root>/scripts/context_probe.ps1 -Root <root> [-Path <paths>] [-Query <texts>] [-Anchor <path:line>] [-Details]
pwsh -File <plugin-root>/scripts/change_closeout.ps1 -Root <root> -Profile <docs|plugin|unity|engine> [-ChangedPath <paths>] [-PluginValidatorPath <p>] [-Version <v> [-Phase release]] [-Details]
```

[probe](../../scripts/context_probe.ps1) 聚合 search/anchor/VCS；[closeout](../../scripts/change_closeout.ps1) 聚合 diff/check/profile 与全仓链接。默认/`-Summary` 给有界 JSON；`-Details` 展开，`raw_dir` 存原文。仅写 `.temp/`，不执行 Git 写入/安装/Refresh；`-RunBuild` 还需 Root 内 `-BuildWrapper` 和已有授权。

## 4. Manager、Goal 与 Artifact

单个职责内有界 helper 不打开 Manager Gate，由当前 owner 直接管理。Manager Gate 开启后，每个 ready Packet 使用一个 `spawn_agent`；Packet 足够时 `fork_turns=none`，只在缺少未落盘 Human 决定时传最少 turns。completion 用 `wait_agent`；补充输入/取消使用 Runtime 对应能力。

`parallel_expected` 成立时首次 wait/join 前启动至少两个实例。Packet report/notice 分别以 `20` 行/`3500` 字符和 `12` 行/`2000` 字符为 soft budget，按消费者和风险扩展；不为限额强制落 Artifact。integration owner 串行应用隔离 patch/候选实现并处理共享生成物、Git 与整体验证。

Core objective 不要求原生 Goal；只有 Human 明确要求 exact Goal 时创建。Goal 不是 Scope、授权、Artifact/Handoff 或证据；局部 blocker 不直接映射为原生 blocked。

正式 dispatch 前证明 Target 可读取 Scope、必要 Artifact、原始 locator 和九个核心 Handoff 字段。Review 使用 Core Baseline/`acceptance_revision`；只有 Handoff-safe 数据可进入 namespaced `Extensions`。Runtime 实例 ID、模型、界面状态和内部存储标识只进入 transport，不改变核心字段语义。

## 5. Skill discovery 与 Project setup

Manifest `"skills": "./skills/"` 在 `sacha-orchestra:` 下暴露 `using-sacha`、`planner`、`executor`、`reviewer`、`manager`、`feedback`、`project-documentation`、`setup-project`、`clarify`。

`agents/openai.yaml` 只定义 metadata。Setup/Clarify explicit-only；Documentation 受 confirmed policy/授权约束；生产 Role 须显式调用或经 Intake 接受。

Setup Project 只在目标项目内扫描已配置或约定的 Skill root；完整读取 authority/independent `SKILL.md` 及其声明为调用必需的项目内 locator，mirror 不重复评估。Skill 文件存在不证明当前 Runtime 可调用；须另以当前 context metadata 核对可见性。不得扫描 cache、全局目录、marketplace、网络或其他 workspace。generated Schema v3 Binding 只在接受 Sacha 后按需读取。

Codex 只允许 Setup 从当前 context 已知的 plugin Skill locator 定点读取同 plugin 的 provider catalog。项目 Skill 必须先由 Setup 按正文证据判定 `schedulable`，再由 Human 确认 load policy；id、目录名和 metadata 不得替代正文判定。Role 仅在任务确需某 capability 时读取对应 binding 和 Skill；mapping 不触发预加载、不证明安装、不授予副作用，也不把 Gate、Scope 或 verdict 交给 provider。
