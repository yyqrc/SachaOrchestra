# Claude Code Runtime Adapter

> Implements: Intake Contract 4；Workflow Contract 15；Assurance Contract 2；Coordination Contract 7；Artifact Protocol 6
> Status: Normative Claude Code mapping

## 1. Boundary

本文只映射 Claude Code 原生能力。以下是可选 owner reference，不是预加载清单：

- [Intake Contract](../../core/intake-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

Adapter 不定义入口、Role、Gate、Artifact、项目知识或发布状态。Project rules/Domain Skills、Role Skill/agent definition 与 Evolution 分别拥有本层信息。

## 2. Intake、Role 与 context

| Core responsibility | Claude Code mapping |
| --- | --- |
| Intake/Route owner | 主对话通过正式 Skill discovery 装载 `using-sacha` |
| Planner | 独立 `Agent` context 装载 Planner 指令 |
| Executor | 明确 owner 的主对话或独立 `Agent` context |
| Reviewer | 未参与方案/实现的独立 `Agent` context |
| Manager | 主对话或控制面 `Agent` 协调独立任务 |
| Workflow owner | 默认是 Human 接受后的主对话；明确会话迁移后转为唯一 target |

Runtime 常驻面只暴露 metadata。`using-sacha` 先加载 Intake Contract；直接任务不读取生产 Core/Role/Binding。显式 using-sacha、明确 Sacha 请求或 direct canonical Role 调用视为接受；Clarify/Setup 只授权 narrow scope。

同一主对话直接执行且不使用 Agent dispatch/return、恢复或 Runtime 验证时，不读取本 Adapter。首次出现 consumer 时再加载所需章节。

独立性由参与历史/input provenance 判断，不由 agent 名称判断。Runtime id 只用于调度。若 canonical entry/Role/Artifact 不可达，报告真实 discovery 缺口，不用临时长提示模拟合同。

## 3. Transition 与 return

每次 transition 先核对 Runtime 可用能力，不假定特定 Agent 模式存在：

1. 核对 Task/Scope、Role、Artifact 可达性、provenance、owner 和 return path。
2. 不要求独立 provenance 的同 context 工作保持主对话；一个有界 helper 可由 owner 直接管理。正式 Role transition 才选择可保留 identity/terminal 的 Agent transport。
3. Source 只传 route intent、Scope/Handoff reference、必要约束与 runtime identity，不复制长报告/隐藏历史。
4. 独立 Review 使用新 `Agent` context；同 Task/Scope 的 repair、补证据和 re-review 保持原 owner。
5. 当前 transport 不可用时先尝试同 Scope 安全替代；owner/Role/return 仍无法唯一确定才进入 Core 阻塞路线。

前台执行由主对话消费 terminal result；后台执行由 owner 保持 phase，以正式 completion notification 和 identity 消费一次结果，不留给 Human 唤醒，也不因启动成功提前结束。

Planner 提案由主对话展示并等待 Human；普通批准且无其他阻塞时，主对话在同一 Task 立即进入 Executor，不创建第二个用户会话或再次询问是否开始。本 Adapter 不把 Codex `create_thread` 语义映射为 Agent helper；只有 Human 明确选择且 Runtime 有可验证的等价用户会话 transport、唯一 owner 与单向 handoff 时才可迁移，旧会话不等待 return；否则保持同一 Task 或报告能力缺口。

Target completion 返回结果/delta、实际验证、阻塞/风险和必要 reference；原生 notification 未携带且消歧必需时才补 route identity/revision/dedup。错误、陈旧或重复结果不产生额外 transition。

正式跨 context dispatch 先应用 Human 本次或批准 Scope 的精确配置，否则按 Role/risk 选择：

| Target | Model | 条件 |
| --- | --- | --- |
| Planner | `opus` | 需要冻结实质方案 |
| Executor | `opus` | 安全、权限、持久数据、breaking、不可逆外部动作或广泛兼容/发布风险 |
| Executor | `sonnet` | Scope/验收已冻结、实现与验证明确且不属于高风险 |
| Reviewer | `opus` | 独立验收 |
| bounded read-only helper | `haiku` | 自包含调查，不取得 Role verdict |

模型强度不替代 Planner/Reviewer/Manager Gate；普通 Executor 只有输入自包含时使用 `sonnet`。Human/Scope 精确配置不受支持时暂停；自动配置不可用时使用 Runtime default。owner 核对并记录 requested/effective model 与宿主覆盖原因；旧写入者 terminal/cancelled 前不得以其他模型启动同 Scope 写入。Direct/current context 不改变模型或宣称路由已应用。

Transport/Identity/Progress 失败按 Coordination Contract 生成 deviation；本 Adapter 只补原生结果未携带且恢复必需的 agent/task、前后台模式、notification/return、工具错误和恢复入口。

Human 输出遵循 Core 技术紧凑顺序；liveness 由当前前台调用或后台 completion/cancel 状态证明，timeout 不替代 terminal/cancel/完成证据。

搜索、diff、日志和列表默认返回短摘要，缺少决策信息时定向展开。大原文已有消费者时写入 task-local 文件或既有 Artifact，否则保留工具 reference；不为限额制造文件，截断不得隐藏失败、warning、未验证、Scope 偏离或授权阻塞。

## 4. Manager 与 Artifact

单个职责内有界 helper 不打开 Manager Gate。Manager Gate 开启后，每个 ready 单元使用独立 `Agent` context；`parallel_expected` 成立时在消费 completion 前启动至少两个实例。共享工作树同一文件/输出不并行写；隔离 patch/候选实现可并行，由 integration owner 串行应用并处理共享生成物、Git 与整体验证。

completion 只在 transport 需要时核对 revision/dedup；结果按消费者和风险保留必要 delta，不为格式强制落 Artifact。真实 Runtime/槽位/依赖/Scope/授权阻塞为 `parallel_blocked`，条件满足却未启动为 `parallel_dispatch_missed`。

Agent context 通过稳定 reference 读取 Scope、Artifact、原始 evidence 和当前 consumer 所需 Handoff 语义。恢复先核对可用 route identity、Scope、revision 与 Entry Condition，不从隐藏历史猜测；不可达时停止 transition 并记录唯一入口。

## 5. Discovery 与 Hook 边界

项目规则、`using-sacha`、canonical Role 和 Domain Skill 必须由当前 Runtime 的正式 discovery/加载机制暴露。发现只证明入口可达；lifecycle、并行、恢复与验收需要真实行为证据。

SessionStart Hook 仅在 Human 另行授权且项目正式配置时预加载环境信息；不得接受 Sacha、替代 `using-sacha`、扩大授权、恢复 owner 或成为正确性前提。正式 discovery 不能稳定暴露入口时报告该 Runtime 未支持，不扫描 cache 或静默改用 Hook。

Hook 或 workspace 外动作需要精确授权。Runtime 能力不可用时记录原始错误，不静默换成不完整路线；平台限制不得通过修改 Core 掩盖。
