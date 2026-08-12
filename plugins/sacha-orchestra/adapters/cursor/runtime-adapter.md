# Cursor Runtime Adapter（运行时适配器）

> 实现：Intake Contract 8；Workflow Contract 21；Human Interaction Contract 2；Assurance Contract 2；Coordination Contract 12；Artifact Protocol 6
> 状态：规范性 Cursor 传输映射；源码接入，安装、fresh discovery 与真实 Runtime 行为需单独验证

## 1. 边界

本文把 Core/Role 已决定的动作映射到 Cursor Agent、Skills 与 Subagents。Owner 依据：

- [Intake Contract](../../core/intake-contract.md)
- [Workflow Contract](../../core/workflow-contract.md)
- [Human Interaction Contract](../../core/human-interaction-contract.md)
- [Assurance Contract](../../core/assurance-contract.md)
- [Coordination Contract](../../core/coordination-contract.md)
- [Artifact Protocol](../../core/artifact-protocol.md)

入口、Role、Gate、readiness、授权、Review 与 Artifact 语义由 Core/Skill 拥有。本 Adapter 只映射 Cursor 的发现、主对话、Subagent、等待、恢复和证据边界；只有主任务派发 Subagent，当前主对话可以完成的工作保持 Direct。

## 2. 部署与发现

Sacha 以 Agent Plugins `1.0.0` 开放标准部署：插件根 `plugin.json` 声明部署身份，Cursor 从 `skills/<name>/SKILL.md` 发现共用 Skill。Cursor 可通过 Customize/Marketplace 安装，开发时也可从 `~/.cursor/plugins/local` 加载；安装、刷新、用户目录写入和 Marketplace 发布均是另行授权的外部状态动作。

Agent Plugins 可移植面只包含 Skills 与 MCP；本插件不声明 MCP，也不增加 Cursor rules、commands、hooks 或 variables。`skills/*/agents/openai.yaml` 是 Codex metadata，不是 Cursor Subagent 定义；Cursor 通过当前 Runtime 的通用 Subagent 能力执行委派工作，不复制一套 Skill。

项目 `AGENTS.md` 由 Cursor 自身规则机制读取，不属于插件包，也不替代项目最近层规则。发现证据只证明 manifest/Skill 可达，不证明 Skill 已触发、Subagent 已派发或流程行为正确。

## 3. 主对话与 Human 交互

| Core 动作 | Cursor 映射 | 限制 |
| --- | --- | --- |
| 默认入口 | 自然语言触发 `using-sacha`，或在 chat 中显式调用 `/using-sacha` | Skill 名称以当前 Cursor 发现结果为准；不可达时报告发现缺口 |
| 高级 Role 入口 | 显式调用 `/planner`、`/executor`、`/reviewer` 或自然语言指定 | 仍须满足对应 Skill 的进入条件 |
| 主任务 | 当前持有工作流 Owner 的 Cursor 主对话 | Subagent 是被调用工作单元，不自动取得用户可见任务 Owner |
| Human 互斥选择 | 使用当前 Runtime 已暴露的选择交互；没有时用普通文本提出一个关键问题 | 不虚构选择工具或替 Human 决定 |
| Human 进度与结果 | 当前主对话展示新事实、风险、阻塞和最终结果 | 遵循 Human Interaction Contract，不转发工具流水账 |

## 4. Role 与 Subagent 传输

Cursor Subagent 使用独立上下文，只由主任务通过当前可用的 Task/Subagent 能力派发并消费返回结果。首次派发前核对当前 Runtime 是否实际提供前台/后台、并行、模型、恢复与停止能力；官方文档或磁盘文件不能替代当前会话工具面。

| 动作 | Cursor 映射 | 约束 |
| --- | --- | --- |
| Planner/Clarify 研究 | 新委派 Agent，输入对应 Skill、目标、Scope、事实 reference 与返回检查 | Cursor Subagent 从干净上下文开始；满足条件时返回协调请求 |
| Executor | 当前主对话，或 Scope/写入边界明确的新委派 Agent | 委派 Agent 只完成当前单元并返回；同一文件或共享输出保持单一活跃写入者 |
| Reviewer | 未参与方案和实现的新 Subagent | 名称不同不构成来源独立；核对实际参与历史与输入来源 |
| Manager 就绪单元 | 主任务为每个隔离单元创建一个委派 Agent | 至少两个单元同时就绪且输出隔离时才并行派发；遵守单层派发 |
| 前台等待 | 前台 Subagent 调用直接返回终态结果 | 只在当前步骤确实依赖结果时使用 |
| 后台等待 | 保留原生 Agent ID/完成通知，在依赖屏障消费结果 | 等待前推进其他不冲突的就绪工作；超时只报告存活状态 |
| 同一目标继续 | 用原生 Agent ID resume | 仅同一 Owner、Scope 和连续目标；新 Scope 新建工作单元 |
| 取消/停止 | 只使用当前 Runtime 明确暴露的停止能力，并确认旧写入者终止 | 没有可靠停止或终态证据时暂停，不创建替代写入者 |

每个委派 Agent 输入必须自包含目标、Scope、规则/Skill 入口、必要 reference、完成检查、停止条件和协调请求返回条件。并行派发使用主任务同一父动作中的多个独立调用；后台模式只用于主任务仍有可推进工作或确有依赖屏障的长任务。

### 4.1 模型映射

默认预算档为 Cursor Teams Premium seat（当前月付 `$120/seat`，年付折算 `$96/seat`）：它有彼此独立的 First-party models 与 Third-party API 用量池，包含量是 Standard seat 的 5 倍。具体 token/金额额度与剩余量不写死；派发前只在 Dashboard 或当前 Runtime 可读时使用实时值。

当前主对话使用 Human 已选模型；没有精确选择时优先 `Auto` 或 Cursor Grok 4.5 medium non-fast。Subagent 按下表首次命中路由，Human/批准 Scope 的精确模型始终优先：

| `route_id` | 进入条件 | 请求模型 | 预算意图 |
| --- | --- | --- | --- |
| `human_exact` | Human 或批准 Scope 指定精确模型/参数 | 当前 Runtime 验证支持后原样使用 | 不因套餐自动改写；不可用时暂停 |
| `premium_review_frontier` | Reviewer 处理 release、安全、权限、持久数据、不可逆外部动作或广泛兼容风险 | `claude-opus-5[effort=high]` | 使用 Third-party API 池换取正式独立复核；同一波次至多一个活跃 frontier Reviewer |
| `premium_grok_high` | Planner/Executor 属于上述高风险，或跨 Owner 关键集成失败会造成困难回退 | 当前 Runtime 发现的 Cursor Grok 4.5 high non-fast 精确 ID | 在 First-party models 池内处理关键长程推理/集成；同一波次至多一个 high 工作单元 |
| `premium_grok_standard` | 其他 Planner、Executor、Reviewer，且不是两个以上同类并行委派 Agent | 当前 Runtime 发现的 Cursor Grok 4.5 medium non-fast 精确 ID | 生产 Role 默认；用较高单次成本换取长程执行、调查与验证质量 |
| `premium_composer_standard` | Manager 协调的有界研究单元、Clarify 研究、只读探索、可自包含轻任务，或两个以上隔离委派 Agent | `composer-2.5[fast=false]` | First-party models 池的吞吐档；避免 Grok 成本随并行数量线性放大 |
| `premium_composer_fast` | Human 明确要求低延迟，或当前依赖屏障的短任务以延迟而非 token 成本为主要约束 | `composer-2.5[fast=true]` | First-party models 池的显式加速档；不得因“Premium 额度多”默认启用 |

`premium_grok_standard` 是生产 Role 自动路径默认值，`premium_composer_standard` 是辅助/并行默认值。Grok 4.5 与 Composer 2.5 都消耗 First-party models 池；Grok standard 单 token 成本更高，但官方长程 Agent/代码基准整体更强，而 Grok standard 仍低于 Composer fast 的当前 token 单价。Adapter 不硬编码近期变更过的 Grok slug，只使用当前 Runtime 模型列表返回的 medium/high non-fast 精确 ID。

`Auto` 只留在当前主对话或 Runtime 无法为 Subagent 固定 Grok/Composer、且 Human 接受动态模型时使用；正式 Reviewer 不用不可追踪的动态选择替代请求模型记录。Max/超长 context 只在输入实际超过普通上下文或 Human 精确指定时启用，套餐充足本身不是开启条件。

预算与并发按以下顺序约束：

1. 多个就绪单元仍由 Coordination 决定能否并行；Adapter 只限制 `premium_grok_high` 与第三方 frontier 路由同一波次单实例，两个以上委派 Agent 使用 Composer 2.5 standard。
2. Third-party API 池接近团队告警线时，尚未开始且不属于 `human_exact` 的 Review 改用 `premium_grok_standard`；高风险 Reviewer 必须披露模型变化和证据影响，不能把同模型参与历史误作独立来源。
3. First-party models 池接近告警线时先关闭 fast，再把尚未开始且非高风险的 `premium_grok_standard` 降到 `premium_composer_standard`，同时减少无消费者的委派 Agent 并保持 Direct；高风险 Grok 路由不得静默降级，也不得通过改用更贵的第三方模型规避 First-party 限额。
4. Background/Cloud Agent 有独立 usage/spend control 时，派发前同时满足对应限额；Premium seat 不自动授权额外消费或 Cloud 动作。

团队限制、区域、套餐限制、BYOK 或 Runtime fallback 可能覆盖 Subagent 的 `model`。主路由在实例尚未 accepted/started 且没有写入迹象时，可从 `premium_grok_high` 或 `premium_grok_standard` 回退一次到 `premium_composer_standard`，但高风险证据要求仍能满足才执行；`human_exact`、已启动实例、结果失败、超时或用户取消不回退。只有原生结果或可绑定遥测明确返回时才记录实际模型/参数，否则标记未验证。

### 4.2 用户任务迁移与 Feedback

Cursor Subagent 不是新的用户可见 task，不能代替 Workflow 定义的用户任务 Owner 转移。当前 Runtime 没有暴露可查询、创建并返回唯一用户 task reference 的能力时：

1. 普通批准 Scope 继续在当前主对话执行，不强制迁移。
2. Human 明确要求迁移时报告能力缺口并保留当前 Owner，不用后台 Subagent 或 Cloud Agent 冒充目标 task。
3. Feedback 能复用唯一现有用户 task reference 时返回该 reference；需要创建新目标而 Runtime 无等价能力时停止转移并给出恢复条件。

将来当前工具面提供等价用户 task 查询/创建能力时，仍须按 Workflow/Coordination 的唯一标识、单向 Handoff 和 Source 结束条件映射，不能由 Adapter 自增流程节点。

## 5. 恢复与证据边界

恢复使用原生 Agent ID、直接父子关系、当前 Owner、Scope/revision、Entry Condition 和结果消费者；无唯一标识、结果陈旧、旧写入者状态不明或返回路径不完整时暂停。单层派发由首次等待前的实时 Agent 树证明；委派 Agent 自报只证明其输出，不能替代工作树、命令退出状态、运行结果或 Human 验收。

源码/Schema 校验只证明 Agent Plugin manifest、Skill 结构和本文映射存在。Cursor 安装、本地加载、IDE/CLI/Cloud discovery、Skill 触发、Subagent 前后台/并行/resume/stop、模型覆盖和用户任务能力必须分别以目标 Cursor 版本的真实 Runtime 证据验证。
