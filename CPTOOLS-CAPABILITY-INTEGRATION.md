# cpTools 能力接入候选

> 状态：后续迭代输入，不是已批准的实施 Spec
> 目标：提炼 cpTools 中可复用的协作能力，供 Sacha Orchestra 后续规划
> 边界：不授权修改 Core、Adapter、Project Integration、Role Skill 或发布状态

## 1. 目的

cpTools 长期实践形成了一些可跨项目复用的能力，但其中大量内容仍是 PySide6、ADB、EditorConnect 和本机工具链知识。后续接入应只提炼与领域无关的协作语义，避免把项目命令、固定路径、工具名称或第二套生命周期带入 Sacha。

## 2. 候选能力

| 能力 | cpTools 中的来源 | 可复用语义 | 不应上移的内容 |
|---|---|---|---|
| 风险匹配验证 | `AGENTS.md`、项目验证矩阵 | claim 必须对应本轮原始证据；验证按风险与改动面选择 | cpui、unittest、PyInstaller、真机命令 |
| 复杂故障反馈环 | `diagnose` | 复现、可证伪假设、定向探针、最小修复、回归证据 | Qt/ADB/HTTP 高频假设和日志前缀 |
| 项目地图与 owner 定位 | `zoom-out` | 先确认 owner、入口、直接调用链和跨边界影响 | cpTools 子系统表与项目术语 |
| Skill 渐进加载 | `.agents/skills/README.md` | metadata 用于触发，主体保持最小，详细资料按需读取 | `.claude` 镜像命令和项目目录结构 |
| Source/mirror parity | `sync_agent_skills.py` | 明确唯一权威源，派生镜像必须可检查、可同步、可验证 | cpTools 的具体源目录和兼容平台名称 |
| 动态能力发现 | `cptools-operator` | 运行时工具 schema 优先于静态速查表；缺失能力不得伪造 | MCP Tool 名称、端口、设备和包信息 |
| 轻量架构健康检查 | `architecture-health` | 用事实识别膨胀、浅模块和跨边界耦合，只给有界候选 | 固定行数阈值和 Mixin 方案 |
| 有界交接报告 | `handoff` 的压缩经验 | delta-first，保留 blocker、risk、unverified 和 evidence locator | 自定义 Handoff 格式；正式交接仍以 Artifact Protocol 为准 |

## 3. 所有权边界

Sacha 继续拥有：

- Planner、Executor、Reviewer、Manager 的职责与 Gate；
- Scope、授权、single-writer、生命周期和自动 transition；
- Artifact、九字段 Handoff、callback、返修和 re-review；
- 是否需要持久 Goal、Spec、Report 或独立 Review。

消费项目继续拥有：

- 项目命令、目录、owner、领域术语和风险约束；
- 测试、lint、build、真机或外部环境验证入口；
- Domain Skill 的触发条件、领域决策树和证据等级；
- 项目自己的 source/mirror 同步关系。

候选能力只能作为 Role 的方法或 Project Integration 的可选输入，不能自行打开 Gate、扩大 Scope、授权写入、创建 Artifact 或决定下一 Role。

## 4. 推荐合入位置

| 候选能力 | 推荐层 | 原因 |
|---|---|---|
| claim 与证据绑定 | Executor/Reviewer 共享合同或直接引用 | 已是 Sacha 基础语义，只需补最窄验证选择原则 |
| 复杂故障反馈环 | Domain Skill / Executor 可选方法 | 调试方法有价值，但不应成为所有任务的流程 Gate |
| owner/调用链发现 | Project Integration 可选能力映射 | 项目知道真实 owner，Core 不应维护目录地图 |
| source/mirror parity | Adapter 或项目验证能力 | 属于部署与派生状态验证，不是 Core 生命周期 |
| 动态能力发现 | Adapter/Provider 接入约束 | 防止静态工具表漂移，保持缺失能力 fallback |
| 架构健康检查 | 独立可选 Skill | 只读、按需触发，不进入默认生产路线 |
| delta-first 报告 | Manager report policy / Artifact 引用规则 | 复用压缩原则，不创建新报告或 Handoff schema |

## 5. 推荐切片

### C1. 验证选择函数

在不复制项目命令的前提下，允许 Project Integration 或 Domain Skill提供“改动面 → 最窄证明命令 → 成功信号 → 未覆盖范围”。Executor 执行，Reviewer按成本与风险独立复验。

验收：

- 不把 lint、test、build、runtime 互相替代；
- 未运行的检查保持未验证；
- Direct 路线不因存在验证矩阵而自动打开 Reviewer Gate；
- 项目命令不进入 Core。

### C2. Provider 动态发现与证据胶囊

对工具型 Domain Skill 或 MCP Provider，只在当前 Role 需要时发现能力和 schema。结果压缩为 delta-first 胶囊：`status`、`facts/findings`、`validation`、`gaps`、`risks`、`evidence_locators`。

验收：

- provider 缺失时保留原生 Direct fallback；
- 静态 Skill 文档不冒充运行时 schema；
- provider 输出不替代 Role 裁决或原始证据；
- 报告预算不隐藏 blocker、risk、unverified。

### C3. Source/mirror parity 能力

把“唯一权威源 + 派生镜像 check/sync + readback”抽象成可选部署验证能力，供存在多表面发布物的项目使用。

验收：

- 项目显式声明 source 与 mirror；
- sync 不扩大到未声明目录；
- parity 只证明内容一致，不证明运行时可发现或行为正确；
- 安装、refresh、发布继续需要适用授权。

### C4. 轻量健康检查

提供只读、显式触发的架构健康 Skill：读取项目事实，最多输出少量候选，不修改源码、不创建 PRD/issue/Spec，也不因为发现问题自动打开 Planner Gate。

验收：

- 每条候选都有事实 locator；
- 阈值只作调查信号，不自动授权重构；
- 实施仍回到当前合法 Executor/Planner 路线；
- 不创建第二套 backlog 或状态文件。

## 6. 不合入项

- cpTools 的 A/B/C 任务分档、固定 Skill 串联和“每次任务收尾”流程；
- `TodoWrite`、`AskUserQuestion`、具体 MCP/CLI 命令等表面工具名称；
- PySide6、cpui、ADB、EditorConnect、Lua Hotfix、PyInstaller 领域规则；
- 固定文件行数阈值、Mixin 拆分模板和测试 shim 方案；
- cpTools 自定义 Handoff、Review、Spec 或 commit 约定；
- 本机绝对路径、端口、设备、包名、线上版本状态；
- 自动安装、refresh、commit、push、发布或外部状态写入。

## 7. 后续规划前检查

- 先核对当时的 Workflow Contract、Artifact Protocol 和 Runtime Adapter；
- 判断候选属于 Core-neutral、Adapter-specific、Project Integration-owned 还是 Domain Skill-owned；
- 优先复用现有合同，避免增加新的 Role、Gate、Artifact 或状态机；
- 为 provider 缺失、部分完成、证据冲突和 schema 漂移定义 fallback；
- 使用真实消费项目验证，而不是只通过静态 validator；
- 保护 Sacha 当时进行中的 Scope 和用户改动。
