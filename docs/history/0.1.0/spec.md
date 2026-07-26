# Sacha Orchestra 0.1.0 Foundation Bootstrap 执行规格

> 状态：草稿，待用户批准  
> Task ID：`SO-0.1.0-BOOTSTRAP-2026-07-12`  
> 方案角色：Planner / Sacha Orchestra Architecture Lead  
> 目标工作区：`C:\Users\<user>\Documents\MarketPlace\SachaOrchestra`  
> 唯一执行根：`<workspace-root>`，其值为上述目标工作区  
> 后续执行角色：Ultra Migration Executor  
> 规格修订：1

## 1. Executive Summary

本规格把现有的多上下文 Author / Executor / Reviewer 协作方式，迁移为跨项目、运行时解耦的 **Sacha Orchestra Multi-Agent Workflow Orchestration Framework**。迁移保留已有实践中真正有价值的部分：上下文隔离、模型可替换、Token 与成本控制、降低上下文污染、人工授权、独立审查，以及通过 `spec.md`、`execution-report.md`、`review.md` 进行持久交接。

迁移不模拟完整软件团队，也不建立固定流水线。稳定核心只包含 Planner、Executor、Reviewer 三个按认知边界、上下文边界和判断责任划分的生产 Role；Manager / Conductor 是按协调门控启用的可选控制面。默认路线从 Executor 开始，分别依据方案不确定性、后果与验证风险、协调复杂度决定是否增加 Planner、Reviewer 或 Manager。

本执行周期只完成 Sacha Orchestra 独立工作区的 **0.1.0 Foundation bootstrap**：创建 repo-local marketplace、可安装的 Codex Plugin、平台中立 Framework Core、Codex Runtime Adapter、三项正式 Role Skill、一个显式调用的兼容 alias，完成静态验证、官方 validator、经授权的安装，以及全新中立上下文中的 discovery、forward smoke test 和只读 self-hosting readiness smoke。RenderDocAnalysis 仅作为旧流程的只读事实来源，不在本周期内修改或清理。

本周期对应演进基线的 Stage 0，只建立后续迭代所需地基，不宣称框架已经达到生产可用或完整 Hybrid，也不得把 `0.1.0` 表述为 `1.0.0`。长期方向由 `docs/architecture/evolution.md` 单独冻结：Sacha Orchestra 的自托管能力按门槛渐进启用；能力尚未达到时允许外部流程补位并记录缺口，某一级能力通过验收后，后续同类 Framework 变更才默认使用 Sacha Orchestra 自身进行规划、执行、复核和升级。同时以 RenderDocAnalysis 作为唯一外部成熟度验证场，覆盖真实路线、返修、恢复与证据状态，直至 Hybrid 模式完整可用。只有完整 Hybrid 与完整自托管升级均通过验收后才发布 `1.0.0`；第二项目验证暂不作为可用门槛。

批准本规格表示批准 `<workspace-root>` 内本规格列明的文件创建与修改；安装 marketplace 或 plugin 会改变工作区外的 Codex 状态，执行到安装门控时仍须由 Human Conductor 单独授权。

## 2. 设计动机与目标

### 2.1 起点

现有流程以多个独立上下文承载 Author、Executor、Reviewer。它解决的不是“文档分工”，而是以下工程问题：

- 隔离方案、实现和验收的认知上下文；
- 允许不同运行实例使用不同模型，而不把模型写入工作流语义；
- 控制单一上下文的 Token、成本和污染；
- 让实现依据持久 Spec，而不是依赖会话记忆；
- 保留用户对目标、范围和高风险动作的最终授权；
- 让 Reviewer 能基于原始事实独立判断。

`Author` 容易把角色误解为“写文档的人”。正式名称改为 `Planner`，因为其产出是可执行契约，核心工作是调查事实、处理方案不确定性、冻结范围与验收，而不是文档写作本身。

### 2.2 产品目标

Sacha Orchestra 是跨项目 **Multi-Agent Workflow Orchestration Framework**，应适用于 Unity、Unreal、RenderDoc、C++、Python 和普通软件工程。项目差异由 Project AGENTS、Domain Skills、项目命令和证据规则补充。

它不是：

- Agent OS；
- RenderDocAnalysis 专属流程；
- Global AGENTS 的替代品；
- 单纯 Prompt 集合或 Skill 包；
- 某个 IDE 的自动化脚本；
- 固定的 Planner → Executor → Reviewer 流水线。

### 2.3 0.1.0 Foundation 成功定义

0.1.0 Foundation 成功必须同时证明：

1. 平台中立的 Role、门控、生命周期、Artifact 和 Handoff 语义有唯一权威来源；
2. Codex Plugin 只是当前打包与部署容器，Codex Adapter 只是 Runtime 映射，两者都没有反向定义 Core；
3. 三项正式 Role Skill 可被当前 Codex Runtime 发现和调用；
4. repo-local marketplace 与 plugin 通过本机官方创建器和 validator；
5. 经单独授权后，非默认 marketplace 和 plugin 可安装并在全新中立上下文中完成 forward smoke test；
6. 根 Project AGENTS 能把长期架构任务路由到 `docs/architecture/evolution.md`，同时本轮没有实现其中 Stage 1 及之后的能力；
7. 全新中立上下文能调用已安装的正式 Role，对 Sacha Orchestra 自身执行一次只读规划或复核 smoke，证明后续 self-hosting 入口可达；这不等于完整自托管已经通过；
8. 未修改 RenderDocAnalysis、Global AGENTS、系统 Skill、Codex cache 或其他项目。

## 3. 当前事实与证据来源

### 3.1 目标工作区

Planner 在 2026-07-12 已只读确认：

- `<workspace-root>` 存在；
- 生成本规格前目录为空；
- 该目录不是 Git 仓库；
- Planner 阶段只创建 `<workspace-root>/spec.md` 与 `<workspace-root>/docs/architecture/evolution.md`。

Executor 启动时必须重新列出工作区文件，并把上述两项 Planner Artifact 视为已知基线。若出现其他来源不明的文件，不得覆盖；先判断是否与本规格冲突，冲突时暂停并请求用户指示。

### 3.2 旧流程事实来源

旧资产位于：

`<legacy-source> = C:\Users\<user>\Documents\RenderDocAnalysis`

其中现有 Project AGENTS、workflow guide、Roadmap、`spec-author`、`spec-executor`、`spec-reviewer` 和历史计划只能只读参考。当前历史草稿：

`<legacy-source>/docs/plans/2026-07-12-sacha-orchestra-migration/spec.md`

不是本周期的执行规格，不得修改。Executor 只可从旧 Role Skill 提取跨项目、仍然有效且与本规格冻结决策一致的行为；RenderDoc、FrameGraph、RDC、发布边界、项目 Goal 或项目目录约定不得迁入 Framework Core。

### 3.3 当前 Codex Runtime 基线

已知基线事实：

- Windows 命令解析曾命中不可执行的商店桌面入口；不得据此修改 WindowsApps ACL 或系统 PATH；
- 真实 CLI 由 Codex 配置记录的 `CODEX_CLI_PATH` 指向，先前已验证为 `codex-cli 0.144.0-alpha.4`；
- `mcp list` 先前可运行，官方开发者文档 MCP 已启用并完成 HTTP 200 握手。

这些是方案输入，不替代执行时验证。Executor 必须定义符号 `<codex-cli>`：优先使用当前环境中存在且可执行的 `CODEX_CLI_PATH`；若未导出，则只读、安全地从当前 Codex Runtime 配置解析对应值，且不得输出无关配置或凭据。随后运行 `<codex-cli> --version` 和 `<codex-cli> plugin --help`，以当前实际输出决定可用命令。不得硬编码带构建 hash 的 CLI 路径。

### 3.4 创建器与规范来源

实现时的 schema 与命令权威顺序为：

1. 本机当前 `plugin-creator`、`skill-creator` 的完整 `SKILL.md`、引用文档和脚本 `--help`；
2. 当前官方 Codex 文档；
3. scaffold 实际生成结果与官方 validator。

已核对的本机入口为：

- `plugin-creator/scripts/create_basic_plugin.py`
- `plugin-creator/scripts/validate_plugin.py`
- `plugin-creator/scripts/read_marketplace_name.py`
- `plugin-creator/scripts/update_plugin_cachebuster.py`
- `skill-creator/scripts/init_skill.py`
- `skill-creator/scripts/generate_openai_yaml.py`
- `skill-creator/scripts/quick_validate.py`

不得把脚本所在用户目录硬编码到产物；Executor 在执行报告中记录本轮解析到的实际路径。官方参考：

- [Build plugins](https://developers.openai.com/codex/plugins/build)
- [Build skills](https://learn.chatgpt.com/docs/build-skills)

当前默认 Python 与 Codex bundled Python 均未提供 `yaml` 模块，因此 validator 前置条件不是假设已满足。Executor 应先寻找已有且可导入 PyYAML 的 Python；若没有，在 `<workspace-root>/.temp/validator-venv` 创建临时虚拟环境并仅安装 validator 所需的 PyYAML，记录版本和安装结果。该临时环境不是交付物，完成后只清理本轮创建的临时项。若依赖无法获得，静态 scaffold 可继续，但 validator 状态必须报告为未验证，且不能进入“完整通过”。

## 4. 冻结架构决策

以下决策已收敛，Ultra Executor 不得重新选择或扩大：

| 决策 | 0.1.0 Foundation 结论 | 理由 |
| --- | --- | --- |
| 产品定位 | Multi-Agent Workflow Orchestration Framework | 抽象协作语义，不绑定单项目或单平台 |
| 核心生产 Role | Planner、Executor、Reviewer | 按认知、上下文和判断责任划分的最小集合 |
| Author | 正式废弃并迁移为 Planner | 强调可执行方案，不强调写文档 |
| Manager | 可选编排控制面；0.1.0 不创建 Manager Skill | 只有协调成本成为问题时才有价值 |
| 默认路线 | Executor-only | 保持简单任务的低成本快速路径 |
| 复杂度判断 | Planner、Reviewer、Manager 三个独立门控 | 方案不确定性、风险、协调复杂度不能压成单一分数 |
| Artifact | 渐进生成 | 同上下文小任务不被文档成本拖累 |
| Handoff | 嵌入 Artifact 或交接消息的九字段 Envelope | 提供最小可恢复上下文，不引入状态机 |
| 当前部署 | repo-local marketplace 中的 Codex Plugin | 独立可维护，且不把用户级默认 marketplace 当源码仓库 |
| Core 与 Plugin | 可同仓物理部署，保持语义与引用边界 | Plugin 是容器，不是 Core，也不等于 Adapter |
| 正式 Skill 名 | `planner`、`executor`、`reviewer` | 安装后由 plugin namespace 消除冲突 |
| 兼容入口 | 保留 explicit-only、deprecated 的 `spec-author` alias | 为已知 Author 调用提供低成本过渡，并可验证弃用路径 |
| 其他旧 alias | 不创建 `spec-executor`、`spec-reviewer` | 正式名称未发生语义迁移，无兼容收益 |
| Git | 不初始化、不作为 bootstrap 前置条件 | 当前工作区不是 Git；文件和运行时证据足以验收 bootstrap |
| 成熟度路线 | 在 RenderDocAnalysis 内迭代至 Hybrid 完整可用；第二项目验证暂缓 | 先用多类真实任务验证全部路由和返修闭环，避免为证明通用而制造接入任务 |
| 正式版本 | `1.0.0` 只在 RenderDocAnalysis 完整 Hybrid 与 Sacha Orchestra 自托管升级同时验收后发布 | `1.0.0` 表示可用产品，不表示第一份合同或首次 scaffold |
| Self-hosting | 按能力门槛渐进启用；未达门槛时允许外部流程补位并记录缺口，已验收能力覆盖的后续同类变更默认由 Sacha Orchestra 自身驱动 | 不提前假装具备能力，同时用自身开发自身持续暴露路由、交接、恢复和升级缺陷 |

## 5. Target Architecture

### 5.1 分层模型

#### Layer 1：Framework Core

负责：

- Role Contract；
- Planner、Reviewer、Manager 三门控；
- Workflow 生命周期；
- 动态升级、返修和停止路由；
- Artifact 语义；
- Handoff Envelope。

Core 必须保持项目无关、平台无关，不包含 Codex、窗口、任务线程、Subagent、模型、Goal、UI、安装、存储 ID，也不包含 RenderDoc、Unity、Unreal 或任何项目规则。

#### Layer 2：Runtime Adapter

负责把稳定抽象映射到具体平台能力：

- 如何创建、恢复、隔离和去重 Agent context；
- 如何把 Role 映射到运行实例；
- 如何装载 Skill；
- 如何选择模型和控制预算；
- 如何保存 Artifact 与恢复任务；
- 如何映射串行、并行和单一写入者约束；
- 如何安装和发现当前部署包。

Adapter 不定义 Workflow 语义。例如 Core 只要求 Planner 具备独立执行上下文；Codex Adapter 才说明当前平台可如何用 task、subagent 或其他受支持运行实例满足该要求。

#### Layer 3：Project Integration

由接入项目拥有：

- Project AGENTS；
- Domain Skills；
- 项目架构、模块边界和命令；
- 项目证据等级、验证方式和发布约束；
- Artifact 的项目内保存位置。

项目不得重定义核心 Role、门控、生命周期或 Handoff，也不得放宽 Global AGENTS 的安全、授权、证据和工程纪律。

### 5.2 Codex Plugin 的准确定位

Codex Plugin 是 Sacha Orchestra 在当前平台上的打包与部署容器。一个独立 plugin 源目录可以同时包含平台中立 Core 文档、Codex Adapter 和 Role Skills，但依赖方向必须保持：

`Framework Core → 被 Adapter 与 Skills 引用`，而不是 `Skills / Plugin manifest → 定义 Core`。

Codex Plugin 不等于 Framework Core，也不等于 Runtime Adapter。未来增加其他 Adapter 时，稳定 Role、门控、Artifact 与 Handoff 语义不应修改。

### 5.3 唯一权威来源

为避免三个 Skill 复制同一套规则，0.1.0 Foundation 固定以下 ownership：

- `core/workflow-contract.md`：Role、三门控、生命周期、升级与返修路由的唯一权威；
- `core/artifact-protocol.md`：Artifact 和九字段 Handoff Envelope 的唯一权威；
- `adapters/codex/runtime-adapter.md`：Codex context、Skill、安装、恢复与运行实例映射的唯一权威；
- `skills/*/SKILL.md`：触发条件、当前 Role 的最小执行步骤，以及对上述权威文档的直接引用；
- `<workspace-root>/docs/architecture/evolution.md`：长期方向、不变量、RenderDoc 成熟度阶段、完整 Hybrid 目标、阶段门槛与兼容规则的唯一权威；它不是本轮执行授权，也不进入安装包；
- `<workspace-root>/AGENTS.md`：Sacha Orchestra 的 Project AGENTS，定义本 workspace 作为 repo-local marketplace 加单 plugin 源码仓库的项目事实、目录 owner、直接入口、读取路由、Core / Codex Adapter / Role Skills 维护边界、scaffold / validator / 安装门控与验证命令、当前非 Git 事实和临时文件规则，并把长期架构任务路由到 `docs/architecture/evolution.md`；它不得放宽 Global AGENTS 的安全、授权和证据纪律，也不得复制 Role Contract、三门控、Artifact 或 Handoff 正文；
- plugin 根 `README.md`：面向使用者的非规范性入口，不成为第二套合同；
- `.codex-plugin/plugin.json` 与 marketplace entry：只定义部署 metadata，不定义 Workflow 语义。

### 5.4 精确目录树

Executor 只创建有实际消费者的文件和目录。目标结构为：

```text
<workspace-root>/
├── AGENTS.md                          # Sacha Orchestra Project AGENTS
├── spec.md
├── docs/
│   └── architecture/
│       └── evolution.md               # Planner 冻结；本轮 Executor 只读
├── execution-report.md                 # 执行时渐进写入
├── review.md                           # 仅独立 Reviewer 执行后创建
├── .agents/
│   └── plugins/
│       └── marketplace.json
└── plugins/
    └── sacha-orchestra/
        ├── .codex-plugin/
        │   └── plugin.json
        ├── README.md
        ├── core/
        │   ├── workflow-contract.md
        │   └── artifact-protocol.md
        ├── adapters/
        │   └── codex/
        │       └── runtime-adapter.md
        └── skills/
            ├── planner/
            │   ├── SKILL.md
            │   └── agents/openai.yaml
            ├── executor/
            │   ├── SKILL.md
            │   └── agents/openai.yaml
            ├── reviewer/
            │   ├── SKILL.md
            │   └── agents/openai.yaml
            └── spec-author/
                ├── SKILL.md
                └── agents/openai.yaml
```

约束：

- 工作区目录 `SachaOrchestra` 不是 plugin 根；规范化 plugin 根必须是 `plugins/sacha-orchestra`；
- 目标树只有一份 `AGENTS.md`，固定为 `<workspace-root>/AGENTS.md`；不得在 plugin 根再创建第二份 Project AGENTS；
- `docs/architecture/evolution.md` 属于仓库级方向性 Artifact，不复制到 plugin Core，不随 plugin 安装，也不得把未来阶段变成本轮待办；
- plugin directory 与 manifest `name` 均为 `sacha-orchestra`；
- manifest 基础版本为 `0.1.0`；若安装后必须刷新缓存，只允许 helper 生成 `0.1.0+codex.<cachebuster>`；`1.0.0` 保留给完整 Hybrid 与自托管升级通过后的正式可用版本；
- 不创建空目录、未使用的 `templates/`、README 于各 Skill 内、Changelog、独立状态文件，或 manifest 中指向不存在文件的字段；
- 若 scaffold 创建了无消费者 placeholder，填充为本规格要求的文件或安全删除该 placeholder；不得保留空壳；
- `.temp/` 仅可承载 Executor 本轮临时验证环境和 smoke fixture，不属于交付树，只清理本轮创建的项。

## 6. Role Contract

### 6.1 Planner

**目的**：把用户目标和已验证事实转化为可执行契约。

**必须负责**：

- 调查现状、owner、调用链和约束；
- 识别实质不同的候选方案及取舍；
- 记录冻结决策与理由；
- 定义 Scope、Non-goals、允许与禁止修改范围；
- 定义依赖、切片顺序、暂停条件和回退；
- 定义可证实的验收标准和 Reviewer Gate；
- 生成或更新 `spec.md`，并提供进入 Executor 的 Handoff Envelope。

**不得负责**：

- 在仅获方案授权时实施迁移；
- 用未经验证的假设冒充代码或运行时事实；
- 把平台实例 ID、模型或 UI 流程写成 Core 合同；
- 为理论完整增加常驻 Role。

### 6.2 Executor

**目的**：在已批准契约或明确用户目标内完成修改，并产生可复核证据。

**必须负责**：

- 启动前核对工作目录、Spec、允许范围、入口条件和现有文件；
- 按依赖顺序实施，保持单一写入者；
- 运行与风险匹配的验证，完整读取退出码、错误、warning 和失败数；
- 维护 `execution-report.md`，索引真实命令、文件、哈希、运行状态和偏离；
- 遇到 Scope、架构、授权或高风险分歧时暂停并升级；
- 完成后提供进入 Reviewer 的 Handoff Envelope。

**不得负责**：

- 静默扩大或缩小 Scope；
- 重新选择本规格已冻结的 Role、目录、marketplace 或兼容策略；
- 用 execution report 代替真实文件和原始输出；
- 声称未执行的安装、discovery 或 smoke test 已通过。

### 6.3 Reviewer

**目的**：独立判断实现是否满足已批准契约及真实风险边界。

**必须负责**：

- 读取 Spec、execution report、真实文件、validator 输出、安装状态和 smoke 证据；
- 独立重跑关键检查，而不是复述 Executor 结论；
- 区分 blocker、非阻塞问题、已验证、未验证和范围外事项；
- 检查 Core / Adapter / Project Integration 是否泄漏；
- 将判断写入 `review.md`，给出 Accept、Accept with follow-up 或 Reject。

**不得负责**：

- 默认修复发现的问题；
- 重写 Spec 来迁就实现；
- 承担 Manager 调度；
- 把报告索引当作原始证据。

### 6.4 Optional Manager / Conductor

Manager 是可选控制面，不是第四个生产 Role。0.1.0 Foundation 只在 Core 和 Adapter 接口中定义其边界，不创建 `manager` Skill。

当前由 Human Conductor 负责：

- 目标与 Scope 的最终确认；
- 高风险、破坏性、权限与工作区外安装动作授权；
- 在 Planner / Executor / Reviewer 之间调度和决定是否继续。

未来 Agent Manager 可负责：

- 路由和门控评估；
- Agent context 的创建、恢复、去重和回收；
- Work Packet 依赖、串并行、预算和资源；
- 单一写入者与返修路由；
- Artifact 与 Handoff 的可达性检查。

Manager 不得代替 Planner 做技术设计、代替 Executor 修改、代替 Reviewer 验收，也不得越过 Human Conductor 的授权边界。

### 6.5 不新增常驻 Role 的原则

Architect、Researcher、Tester、QA、Security、Performance 默认表现为某个核心 Role 加 Domain Skill。只有同时具备独立上下文、独立工具或数据来源、独立判断责任，并且合并到现有 Role 会损害独立性时，才可在未来版本评估新增 Role；新增必须通过独立规格，不属于本周期。

## 7. 三门控与动态路由

三个门控独立判断，不使用“简单 / 中等 / 复杂”总分替代。

### 7.1 Planner Gate：方案不确定性

以下任一项成立时前置 Planner：

- 目标、验收或 owner 不清；
- 存在实质不同方案或关键取舍；
- 跨模块、跨公共契约、迁移或兼容性决策；
- 涉及不可逆决定或返工成本高；
- Executor 无法在既有约束内唯一确定路径。

目标明确、修改局部可逆、路径唯一且验收直接时，Planner Gate 关闭，保留 Executor-only。

### 7.2 Reviewer Gate：后果与验证风险

以下任一项成立时后置独立 Reviewer：

- 安全、权限、持久数据、公共契约或发布边界；
- 回滚困难或影响范围广；
- 关键验证无法完整执行；
- 实现存在偏离、残余风险或证据冲突；
- 用户明确要求独立视角。

本 bootstrap 涉及跨项目公共合同、plugin 安装和弃用兼容，因此 Reviewer Gate 固定开启。

### 7.3 Manager Gate：协调复杂度

仅当存在以下协调问题且人工调度本身成为显著成本或风险时启用：

- 多个可独立执行的 Work Packet；
- 明确依赖图或可安全并行分支；
- 多个仓库、环境或运行实例；
- 反复恢复、去重、返修或预算管理；
- 需要强制单一写入者。

本 0.1.0 Foundation bootstrap 是单工作区、顺序依赖的一个执行周期，Manager Gate 默认关闭，由 Human Conductor 调度。Ultra Executor 不得为了“演示 Multi-Agent”自行创建 Manager。

### 7.4 路由、升级与返修

基础路由为：

```text
Executor
  ├─ Planner Gate 开启：Planner → Executor
  ├─ Reviewer Gate 开启：Executor → Reviewer
  └─ Manager Gate 开启：Manager 包裹已选择的路线
```

运行时动态规则：

- Executor 发现新方案分歧、Scope 变化或验收不再成立：暂停写入，返回 Planner / Human Conductor；
- Reviewer 发现实现缺陷但 Spec 仍有效：返回 Executor，保持同一 Task ID；
- Reviewer 发现 Spec 本身缺失或错误：返回 Planner，不得由 Reviewer 暗改合同；
- 安装授权未获得：完成 workspace-local 工作后标为部分完成，不进入安装与 runtime smoke；
- 依赖或平台能力不可用：记录未验证范围和恢复入口，不伪造通过；
- 简单返修不得创建新的 Spec、Task ID 或并行状态系统。

## 8. Artifact Protocol

### 8.1 渐进生成

Artifact 是否落盘由持久化和交接需要决定：

- 简单、同上下文任务：最终回复记录修改与验证即可；
- 需要持久方案或跨上下文交接：创建 `spec.md`；
- 正式执行续跑或需要 Reviewer：创建 `execution-report.md`；
- 正式独立审查：创建 `review.md`。

Core 不硬编码 Artifact 保存目录。本 Sacha Orchestra bootstrap 作为 Project Integration 决策，选择工作区根的 `spec.md`、`execution-report.md`、`review.md`；其他项目可选择自己的计划目录。

### 8.2 权威边界

- `spec.md`：目标、Scope、决策、暂停条件和验收契约；
- 真实文件、Diff（若存在）、系统状态和命令原始输出：实现与验证事实；
- `execution-report.md`：事实和证据索引，不替代原始证据；
- `review.md`：独立判断，不重写 Spec 或 report。

当前工作区无 Git，故不得要求 Git 状态、Diff 或 release-boundary 命令作为 bootstrap 前置证据。使用执行前后文件清单、逐文件重读、SHA-256、官方 validator、定向语义检查、安装状态和 fresh-context smoke 作为证据。若用户之后独立初始化 Git，可补充 Git 检查，但不能改变本规格的完成条件。

### 8.3 Handoff Envelope

Envelope 是嵌入 Artifact 或交接消息的最小协议，不是独立业务文件。每次正式跨 Role 交接必须包含以下九个字段，字段无内容时写 `None`：

1. `Task ID`
2. `Source Role`
3. `Target Role`
4. `Outcome`
5. `Scope Reference`
6. `Artifact References`
7. `Evidence References`
8. `Deviations and Open Risks`
9. `Entry Condition`

字段语义：

- `Outcome`：Source Role 已完成的可核实结果，而不是下一角色的目标；
- `Scope Reference`：指向 Spec 或明确用户目标的稳定引用；
- `Artifact References`：交接产物的可访问相对引用；
- `Evidence References`：原始文件、命令输出或报告证据索引；
- `Deviations and Open Risks`：合并记录已批准偏离、未解决问题和风险；
- `Entry Condition`：Target Role 开始前必须满足的授权、文件和验证条件。

Envelope 不包含 Window ID、Thread ID、Subagent ID、Model、Goal、UI 状态、Runtime storage ID 或本机绝对路径。不得创建 `handoff.md`、`state.md`、`context-summary.md` 或 `artifact-manifest.md`。

## 9. Plugin、Marketplace 与 Skill 契约

### 9.1 Repo-local marketplace

marketplace 固定为：

- 文件：`<workspace-root>/.agents/plugins/marketplace.json`
- marketplace name：由 scaffold helper 生成后用 `read_marketplace_name.py --marketplace-path <workspace-root>/.agents/plugins/marketplace.json` 读取；当前基线预期为默认值 `personal`
- marketplace display name：由 helper 根据实际 marketplace name 生成；当前基线预期为 `Personal`
- plugin source：`./plugins/sacha-orchestra`
- installation policy：`AVAILABLE`
- authentication policy：`ON_INSTALL`
- category：`Productivity`

初建必须使用 `plugin-creator/scripts/create_basic_plugin.py`，不得手写 marketplace schema。固定 scaffold 语义如下；Executor 先通过 `--help` 核对当前参数仍受支持：

```powershell
& <validator-python> <plugin-creator>/scripts/create_basic_plugin.py sacha-orchestra `
  --path <workspace-root>/plugins `
  --with-skills `
  --with-marketplace `
  --marketplace-path <workspace-root>/.agents/plugins/marketplace.json `
  --install-policy AVAILABLE `
  --auth-policy ON_INSTALL
```

基线初建不得传入 `--marketplace-name`：本机 helper 只允许在默认 `personal` identity 已被占用或安装、确需另建名称时使用该参数。当前已核对的已安装 marketplace 不含 `personal`，且用户级默认 marketplace 文件不存在，因此当前执行预期生成 name `personal`、display name `Personal`。Executor 必须在 scaffold 前重新检查；若执行时 `personal` 已被其他 marketplace 占用或安装，停止并请求用户决定，再按 `plugin-creator` 的例外规则选择名称，不得自动改名。

基线初建同样不传入 `--category`，使用 helper 当前默认值 `Productivity`。生成后必须用 `read_marketplace_name.py` 读取实际 name，并用 JSON parser 验证 display name、source、policy 与 category；安装命令只能使用读取结果。

不得对初建使用 `--force`。若 workspace-local marketplace 文件已存在，先用 `read_marketplace_name.py --marketplace-path <workspace-root>/.agents/plugins/marketplace.json` 和完整 JSON 检查确认 ownership；其 name 必须与当前基线或用户批准的例外一致。后续版本刷新使用 `update_plugin_cachebuster.py` 与受支持的 reinstall 流程，不手工修改已有 marketplace。

### 9.2 Plugin manifest

`.codex-plugin/plugin.json` 以 scaffold 结果为 schema 基线，并按本机 `plugin-json-spec.md` 与官方文档做最小 metadata 更新。语义必须满足：

- `name`：`sacha-orchestra`
- 基础 `version`：`0.1.0`
- `description`：明确为跨项目 Multi-Agent Workflow Orchestration Framework 的 Codex 部署包；
- `author.name`：`Sacha Orchestra`
- `skills`：指向实际存在的 `./skills/`；
- `interface.displayName`：`Sacha Orchestra`
- `interface.shortDescription`：简洁说明动态 Role 路由；
- `interface.longDescription`：说明 Core、Codex Adapter、三 Role 与渐进 Artifact；
- `interface.developerName`：`Sacha Orchestra`
- `interface.category`：`Productivity`；
- `interface.capabilities`：`["Interactive", "Write"]`；
- `interface.defaultPrompt`：使用 scaffold 当前支持的类型，提供一个触发动态 Role 路由的简短 starter prompt。

0.1.0 Foundation 不提供 hooks、MCP server、apps、assets 或 plugin-level scripts，因此 manifest 不得出现指向这些不存在组件的字段。不得在 `.codex-plugin/` 内放置 `plugin.json` 之外的文件。任何字段名和类型以执行时本机 schema 与 validator 为准；若 validator 明确拒绝上述 category 或 capabilities 的当前 schema 表达，只允许做保持 `Productivity`、`Interactive` 和 `Write` 语义的纯 schema 适配，并在 execution report 记录，不得改变产品架构或让 Executor 重新选择 capability。

### 9.3 Role Skill progressive disclosure

正式 Skill 内部名称固定为：

- `planner`
- `executor`
- `reviewer`

安装后由 plugin namespace 暴露为：

- `sacha-orchestra:planner`
- `sacha-orchestra:executor`
- `sacha-orchestra:reviewer`

每个 Skill 必须由 `skill-creator/scripts/init_skill.py` 初始化，并使用 `generate_openai_yaml.py` 生成或更新 `agents/openai.yaml`。不得手写一套与 SKILL frontmatter 不一致的 metadata。每个 Skill：

- `SKILL.md` 只包含可触发描述、当前 Role 的最小步骤、暂停与交接要求；
- 直接引用 `../../core/workflow-contract.md` 和 `../../core/artifact-protocol.md`；
- 需要平台操作时再直接引用 `../../adapters/codex/runtime-adapter.md`；
- 不复制完整 Role Contract、九字段协议或安装流程；
- 不创建 Skill 内 README、安装指南、Changelog、无消费者模板或冗余 references；
- `agents/openai.yaml` 的 `display_name`、`short_description`、`default_prompt` 与 Skill 语义一致；
- 正式 Skill 允许当前默认的 implicit discovery，触发描述必须能区分方案、执行和验收意图。

正式 Skill 的最小行为：

- `planner`：先查事实和约束，评估 Planner / Reviewer / Manager Gate，产出可执行 Spec 或轻量计划；仅获方案授权时不实施；
- `executor`：确认 Scope 与 Entry Condition，实施、验证、报告偏离，必要时升级；
- `reviewer`：读取真实状态与原始证据，独立判断，默认不修复。

### 9.4 `spec-author` 兼容 alias

0.1.0 Foundation 保留 `spec-author`，理由是 `Author → Planner` 是已知且真实的公开迁移缝；一个极小、显式调用的 alias 能让旧提示在项目正式接入前获得清晰弃用引导，并验证兼容路径，而无需复制旧项目流程。

alias 必须：

- 仅位于 Codex 部署适配面，不进入 Framework Core 的正式 Role 列表；
- 在 `SKILL.md` 与 `agents/openai.yaml` 明确标记 deprecated，并转交 `planner`；
- 设置 `policy.allow_implicit_invocation: false`；
- 只包含弃用提示、转发入口和对 Planner / Core 权威文档的引用，不复制 Planner 全文；
- 不读取或携带 RenderDoc 项目约束；
- 不创建 `spec-executor` 或 `spec-reviewer` alias。

移除条件：所有已知接入项目和持久提示均已改用 Planner，后续 Project Integration 验收不再依赖 `spec-author`，并由单独版本规格批准移除。当前 Stage 0 内不得提前删除。

## 10. 精确范围与授权边界

### 10.1 Executor 允许修改

仅允许创建或修改：

- `<workspace-root>/AGENTS.md`
- `<workspace-root>/.agents/plugins/marketplace.json`
- `<workspace-root>/plugins/sacha-orchestra/**`
- `<workspace-root>/execution-report.md`
- 独立 Reviewer 后续创建的 `<workspace-root>/review.md`
- `<workspace-root>/.temp/**` 中本周期明确创建的临时验证环境与 smoke fixture

`<workspace-root>/spec.md` 与 `<workspace-root>/docs/architecture/evolution.md` 是 Planner 已冻结的 Artifact。Executor 只可在用户明确批准对应 Planner 修订后修改；执行中不得为适配实现静默改写，也不得把演进阶段改写成已完成能力。

### 10.2 只读范围

- `<workspace-root>/docs/architecture/evolution.md`；
- `<legacy-source>` 中与旧 Role 通用行为直接相关的 AGENTS、Skill 和 workflow 文档；
- 本机 `plugin-creator`、`skill-creator` 与引用文档；
- 当前 Codex CLI help、配置中的 CLI 路径项和安装状态；
- 当前官方 Codex 文档。

### 10.3 明确禁止

本周期不得：

- 修改或删除 RenderDocAnalysis 的 AGENTS、Guide、Roadmap、Skill、计划、报告或代码；
- 删除旧 `spec-author`、`spec-executor`、`spec-reviewer`；
- 执行 RenderDoc release-boundary 或项目组合 smoke test；
- 修改 Global AGENTS、系统 Skill、Codex plugin cache、WindowsApps ACL、系统 PATH 或其他项目；
- 初始化 Git、创建 commit、发布或把 Git 当作完成前置条件；
- 创建 Manager Skill、额外常驻 Role、固定流水线或第二套任务状态；
- 创建独立 `handoff.md`、`state.md`、`context-summary.md` 或 `artifact-manifest.md`；
- 修改演进基线，或实现其中 Stage 1 及之后的 RenderDoc 接入、完整 Hybrid、Manager、Work Packet、并行或其他 Runtime 能力；
- 未经单独授权注册 marketplace、安装、卸载或重装 plugin；
- 清理非本轮创建的临时文件。

## 11. Ultra Executor 实施切片

切片严格顺序执行。每个切片完成条件满足后才进入下一切片；发现暂停条件时先更新 `execution-report.md`，不得绕过。

### Slice 0：启动、边界复核与工具预检

动作：

1. 将工作目录设为 `<workspace-root>`；先读取本文件全文，再读取 `docs/architecture/evolution.md` 的不变量与阶段边界；不从 RenderDocAnalysis 工作目录执行；
2. 列出工作区现有文件并计算 `spec.md` 与 `docs/architecture/evolution.md` 的 SHA-256；确认没有来源不明的冲突文件；
3. 解析本机 `plugin-creator`、`skill-creator` 根及上述脚本，读取完整 Skill 和必需 references；
4. 对创建器脚本运行 `--help`，确认参数；
5. 解析 `<codex-cli>`，运行 `--version`、`plugin --help`、`plugin marketplace --help` 和受支持的 marketplace list；确认默认 `personal` identity 在执行时是否仍可用于初建；
6. 找到可导入 PyYAML 的 `<validator-python>`；若不存在，建立 workspace-local 临时 venv；
7. 创建 `execution-report.md`，记录启动快照、版本、授权状态和后续检查表。

完成条件：

- 工作目录、Spec / Evolution hash、允许范围和现有文件清单已记录；
- 创建器、validator 和 CLI 的实际入口已确认；
- 没有修改工作区外状态；
- 若工具接口与本规格有实质冲突，已暂停而非猜测。

### Slice 1：Scaffold repo-local marketplace 与 plugin

动作：

1. 确认 Slice 0 的 marketplace list 中默认 `personal` identity 未被其他 marketplace 占用或安装；若已占用，暂停并取得用户对例外名称的决定；
2. 使用 9.1 的 scaffold helper 和固定参数创建 plugin parent、plugin manifest、`skills/` 与 repo-local marketplace；基线路径不传 `--marketplace-name` 或 `--category`；
3. 不使用 `--force`，不手写 marketplace；
4. 立即读取生成的完整 `plugin.json` 与 `marketplace.json`；
5. 用 `read_marketplace_name.py` 读取 name，并验证当前基线为 `personal`（或用户批准的例外）；同时验证 source 为 `./plugins/sacha-orchestra`、policy 与 category `Productivity`；
6. 记录 scaffold 命令、读取到的 marketplace name、退出码和初始文件清单。

完成条件：

- `.codex-plugin/plugin.json` 与 `.agents/plugins/marketplace.json` 均由 helper 生成并可解析；
- plugin name 与目录均为 `sacha-orchestra`；
- marketplace name 来自 helper 输出并由读取脚本复核；当前基线为 `personal`，任何例外均有用户决定；
- marketplace source 精确指向 workspace-local plugin；
- marketplace entry category 为 `Productivity`；
- 未创建未请求的 hooks、MCP、apps、assets、scripts 或模板目录。

### Slice 2：建立 Framework Core

动作：

1. 创建 `core/workflow-contract.md`，声明 `Contract Version: 1`，完整定义三 Role、Optional Manager、三门控、生命周期、升级与返修路由；
2. 创建 `core/artifact-protocol.md`，声明 `Contract Version: 1`，定义渐进 Artifact、权威边界和九字段 Handoff Envelope；
3. 读取 `docs/architecture/evolution.md` 的不变量，只落实当前 Stage 0 合同；不得把 RenderDoc 成熟度路线、完整 Hybrid、Manager 实现或并行阶段复制进 Core 当作当前能力；
4. 仅从旧 Role Skill 只读提取跨项目且仍有效的证据、Scope、验证和交接纪律；
5. 对 Core 做平台、项目和未来阶段泄漏检查。

完成条件：

- 两个 Core 文件各自有单一、互不重复的 ownership；
- 两个 Core 文件都声明合同版本 1；
- Handoff 的定义精确为本规格九字段；
- Core 不出现 Codex Runtime 细节、项目命令或项目术语；
- Author 只作为迁移历史出现，不是正式 Role。

### Slice 3：建立 Codex Runtime Adapter

动作：

1. 创建 `adapters/codex/runtime-adapter.md`；
2. 映射 Role 到独立 context、Skill discovery、Artifact 可达性、任务恢复、模型可替换、预算、单一写入者、未来 subagent / parallel agent 和 Manager 接口；
3. 记录 repo-local marketplace 注册、plugin 安装、刷新、卸载边界和 fresh-context 验证方法；
4. 明确所有工作区外变更均受 Human Conductor 授权。

完成条件：

- Adapter 引用 Core 而不复制或改写 Core 语义；
- Codex 特有概念只存在于 Adapter、Skill metadata、部署文档或 marketplace/manifest；
- 不包含 RenderDoc 或其他项目规则；
- 不把特定模型、运行实例 ID 或 UI 点击路径写成稳定合同。

### Slice 4：建立 Role Skills 与兼容 alias

动作：

1. 用 `init_skill.py` 分别初始化 `planner`、`executor`、`reviewer`、`spec-author`；
2. 按 9.3 精简三个正式 `SKILL.md`，加入对 Core 和需要时对 Adapter 的直接相对引用；
3. 按 9.4 实现 minimal deprecated alias；
4. 使用 `generate_openai_yaml.py` 生成或更新每个 `agents/openai.yaml`；
5. 核对名称、描述、default prompt 与 implicit policy。

完成条件：

- 三个正式 Skill 能从描述清楚区分方案、执行和验收意图；
- 每个 Skill 的 `SKILL.md` 与 `agents/openai.yaml` 一致；
- `spec-author` 显式调用关闭 implicit，且不复制 Planner 合同；
- 不存在 Manager、spec-executor、spec-reviewer Skill；
- 不存在 Skill 内 README、空 resources 或无消费者模板。

### Slice 5：完成 Project AGENTS、plugin 文档与 metadata

动作：

1. 创建 `<workspace-root>/AGENTS.md` 作为 Sacha Orchestra Project AGENTS，明确 workspace 是 repo-local marketplace 加单 plugin 源码仓库，并记录目录 owner、直接入口与按任务读取路由；长期架构、阶段或兼容问题必须读取 `docs/architecture/evolution.md`；
2. 在 root AGENTS 中定义 Core / Codex Adapter / Role Skills 的维护边界，列出本规格确认的 scaffold、validator、安装授权门控与验证命令，并记录当前非 Git 事实和 `.temp/` 只清理本轮创建项的规则；
3. root AGENTS 必须声明 Global AGENTS 的安全、授权、证据和工程纪律不得放宽；只引用 plugin `core/*`，不得复制 Role Contract、三门控、Artifact 或 Handoff 正文；
4. 创建 plugin 根 `README.md`，说明定位、快速路由、安装后的正式 Skill 名、兼容 alias 和 Core / Adapter / Project Integration 边界；
5. 按 9.2 在 scaffold schema 内最小更新 manifest metadata；
6. 重读所有文档，删除重复合同和失效引用，确认 plugin 根不存在 `AGENTS.md`，并确认 README / Core 没有把 Evolution 的未来阶段描述为当前可用能力。

完成条件：

- README 是入口而不是第二权威；
- workspace root 只有一份 Project AGENTS，且覆盖项目事实、owner、读取路由、维护边界、命令、授权门控、非 Git 与临时文件规则；
- root AGENTS 能把长期方向和 breaking-change 任务路由到 `docs/architecture/evolution.md`；
- root AGENTS 不重定义或复制 Core 语义，并明确不得放宽 Global 规则；
- plugin 根不存在第二份 `AGENTS.md`；
- manifest 只声明实际存在的组件；
- 所有相对引用从其所属文件出发均能解析。

### Slice 6：静态与官方 validator 验证

动作：

1. 对四个 Skill 分别运行 `skill-creator/scripts/quick_validate.py <skill-dir>`；
2. 运行 `plugin-creator/scripts/validate_plugin.py <workspace-root>/plugins/sacha-orchestra`；
3. 用 JSON parser 完整读取 manifest 与 marketplace，做 9.1、9.2 的定向字段断言，包括 marketplace 当前基线 name `personal`、entry category `Productivity`，以及 manifest category `Productivity`、capabilities `Interactive` / `Write`；
4. 检查每个 manifest 路径和 Skill 引用实际存在；
5. 检查 `spec-author` 的 `policy.allow_implicit_invocation` 精确为 `false`；
6. 对 `core/` 做平台和项目泄漏扫描，对整个 plugin 做本机绝对路径和 RenderDoc 项目规则扫描；
7. 检查整个 workspace 只有 `<workspace-root>/AGENTS.md` 一份 AGENTS；核对其 Project AGENTS 职责完整、指向 `core/*` 与 `docs/architecture/evolution.md` 的引用有效，且没有复制 Role Contract、三门控、Artifact / Handoff 正文；
8. 重新计算 Evolution hash，确认 Executor 未修改该文件；检查本轮交付树没有实现 Stage 1 及之后的 RenderDoc 接入、Hybrid Manager、Work Packet、并行或其他 Runtime 能力；
9. 检查无空目录、无未消费模板、无额外状态文件、无禁止 alias 或 Manager Skill；
10. 生成交付文件清单和 SHA-256，逐文件重读 Markdown，检查 code fence、标题层级和内部路径；
11. 将完整命令、退出码、warning、失败数和结果写入 execution report。

Core 泄漏扫描至少覆盖以下术语类别，而不是只依赖固定大小写字符串：Codex 平台名、窗口或任务线程、subagent、模型、Goal、UI、Runtime storage ID，以及 RenderDoc、Unity、Unreal 等项目名。出现命中时必须逐项判断；稳定 Core 中的实质命中为失败。

完成条件：

- 四个 Skill quick validator 全部退出 0；
- plugin validator 退出 0；
- manifest、marketplace、引用、alias policy 定向断言全部通过；
- workspace AGENTS 唯一性、Project AGENTS 职责和 Global / Project / Core 权威边界检查通过；
- Evolution hash 未变化，root AGENTS 路由有效，未来阶段未被误实现；
- Core / Adapter / Project Integration 边界检查无未处理命中；
- 文件清单与 hash 已记录；
- validator 未运行或仅人工检查时，不得标记本 Slice 通过。

### Slice 7：安装授权门控与安装

前置条件：Slice 0–6 全部通过，且用户在执行时明确授权修改 Codex marketplace / plugin 安装状态。

动作：

1. 再次确认 `<codex-cli>` 指向可执行 CLI，而非商店桌面入口；
2. 用当前 `plugin marketplace --help` 已证实的受支持语法注册 `<workspace-root>` 作为非默认 marketplace；当前已核对语义为：

   ```powershell
   & <codex-cli> plugin marketplace add <workspace-root>
   ```

3. 用 `read_marketplace_name.py --marketplace-path <workspace-root>/.agents/plugins/marketplace.json` 读取实际 name，并将结果绑定为 `<marketplace-name-from-marketplace-json>`；当前规格基线下该值应为 `personal`，若不是且没有 Slice 1 记录的用户批准例外，停止；
4. 用当前 `plugin --help` 已证实的受支持语法安装：

   ```powershell
   & <codex-cli> plugin add "sacha-orchestra@<marketplace-name-from-marketplace-json>"
   ```

5. 运行受支持的 marketplace list / plugin list 检查，确认 plugin 来源与 `<marketplace-name-from-marketplace-json>` 一致；
6. 不读取或修改 plugin cache；不修改系统 PATH 或 ACL。

若当前 CLI 与上述命令不一致，必须先以当前 help 和官方文档核实等价受支持入口；只有参数层适配可继续。若没有可验证的 CLI 安装入口，可使用当前 Codex App 提供的受支持安装入口，但必须记录操作和可验证状态；两者都不可用时，将状态标为“workspace-local 完成，安装未验证”，不得声称 plugin 可用。

完成条件：

- 单独授权证据已记录；
- repo-local marketplace 已注册且 identity / source 正确；
- plugin list 显示 `sacha-orchestra` 来自读取到的 marketplace name；当前基线预期为 `personal`，或为已记录的用户批准例外；
- 未触碰禁止的系统或 cache 边界。

### Slice 8：Fresh-context discovery 与 forward smoke test

前置条件：安装状态已验证。测试必须使用新的中立 Codex context，不继承本规格会话的隐藏上下文；Runtime 如何创建该 context 属于 Codex Adapter，不写入 Core。

测试 fixture：

- 路径：`<workspace-root>/.temp/sacha-orchestra-smoke/neutral-project`
- 固定 Task ID：`SO-0.1.0-SMOKE-001`
- 中立目标：在临时目录内创建一个最小文本产物，其内容和验收由 smoke Planner 明确给出；不得使用 RenderDoc、Unity、Unreal 或 Sacha 源码作为测试对象。

测试顺序：

1. **Discovery**：在全新 context 中检查已安装 plugin 和三项正式 Skill 可见；确认显示命名空间为 `sacha-orchestra:*`；
2. **Planner forward**：显式调用 namespaced Planner，只允许规划，不实施；要求输出 Scope、Non-goals、验收和九字段 Planner → Executor Envelope；
3. **Executor forward**：在另一个全新 context 中只给 smoke Spec / Handoff，调用 namespaced Executor，在 fixture 内实施并产生原始验证证据及九字段 Executor → Reviewer Envelope；
4. **Reviewer forward**：在另一个全新 context 中只给 Spec、report 索引和 fixture，调用 namespaced Reviewer；要求独立重跑关键检查、默认不修复并给出判断；
5. **Implicit routing spot check**：使用不点名 Skill 的中立“只制定方案”提示，确认 Planner 可被描述发现；不得把一次隐式未命中掩盖为通过；
6. **Deprecated alias check**：显式调用 `sacha-orchestra:spec-author`，确认显示弃用并路由 Planner；使用普通规划提示时确认 alias 不会被 implicit 调用；
7. **SH1 readiness smoke**：另建全新 context，以 `<workspace-root>` 为只读目标，显式调用 namespaced Planner 或 Reviewer 检查 Core / Adapter / Project Integration 边界，并为一个后续有界改进生成只读方案或复核结果；固定 Task ID 为 `SO-0.1.0-SELFHOST-READ-001`。不得修改 workspace、不得生成 Stage 1 执行 Spec、不得声称达到 SH2 或完整 self-hosting；
8. 记录各 context 的最小输入、Role 命中证据、输出、Artifact 与验证结果；完成后只清理本轮 smoke fixture，保留 execution report 中的 hash 和证据索引。

完成条件：

- 三项正式 Role 均在 fresh context 可发现并执行其合同；
- forward handoff 使用完全一致的九字段；
- Executor 只修改临时 fixture，Reviewer 独立验证且未默认修复；
- implicit Planner spot check 通过；
- deprecated alias 仅显式生效；
- SH1 readiness smoke 能使用已安装 Role 只读理解 Sacha Orchestra 自身边界，且没有产生写入或夸大能力；
- 失败、路由偏差或未验证项均如实记录。

### Slice 9：执行收尾与 Reviewer Handoff

动作：

1. 完整重读交付树和 `execution-report.md`；
2. 再跑高价值 validator 与定向语义检查；
3. 记录最终文件清单、hash、安装状态、smoke 状态、偏离和风险；
4. 清理仅由本轮创建且不再需要的 `.temp` 项；
5. 在 `execution-report.md` 末尾写九字段 Executor → Reviewer Handoff；
6. 由 Human Conductor 在独立 Reviewer context 启动 `sacha-orchestra:reviewer`；Reviewer 后续将正式判断写入 `<workspace-root>/review.md`。

完成条件：

- execution report 自包含且所有声明均有本轮证据；
- Reviewer 可仅凭 Spec、report 索引和真实工作区恢复验收；
- 未创建重复计划、Goal 或状态系统；
- 未把 RenderDoc Project Integration 混入本周期。

## 12. 验证矩阵与最终验收

| Claim | 直接证据 | Pass 条件 |
| --- | --- | --- |
| Workspace bootstrap 正确 | 最终文件清单、逐文件重读、SHA-256 | 只有本规格允许的交付文件；无空壳和禁止项 |
| 演进方向未漂移 | Evolution 前后 SHA-256、root AGENTS 引用、交付树检查 | 文件未被 Executor 修改；Stage 1+ 未进入本轮实现；RenderDoc 至 Hybrid 完整的方向仍可发现 |
| Project AGENTS 分层正确 | workspace AGENTS 文件枚举、全文与引用检查 | 仅根目录存在一份 `AGENTS.md`；职责完整，不复制 Core 合同，不放宽 Global 规则 |
| Plugin schema 有效 | `validate_plugin.py` 完整输出 | 退出 0，无未处理错误 |
| Skill schema 有效 | 四次 `quick_validate.py` 完整输出 | 每次退出 0 |
| Metadata 一致 | manifest、YAML frontmatter、`agents/openai.yaml`、定向断言 | Skill 名称、描述、default prompt、policy 一致；manifest category 为 `Productivity`，capabilities 为 `Interactive` / `Write` |
| Marketplace 正确 | JSON parser、helper 读 name | 当前基线 name 为 `personal`（或有用户批准例外）；source、policy 精确匹配，entry category 为 `Productivity` |
| Core 平台中立 | 术语扫描和人工逐项判定 | 无实质平台、运行实例或项目语义泄漏 |
| Adapter 不定义 Core | 文档 ownership / 引用检查 | Adapter 只映射，不改写 Role、Gate、Artifact、Handoff |
| 正式 Role 最小 | 目录与 manifest / discovery | 仅 Planner、Executor、Reviewer 为正式 Role |
| Alias 安全 | YAML policy 与 fresh-context 测试 | `spec-author` 仅显式、deprecated、转 Planner |
| 安装可用 | CLI/App 受支持入口、marketplace list、plugin list | 来源为 repo-local marketplace，plugin 已安装 |
| Runtime 可用 | fresh-context discovery 与 forward smoke | 三 Role、九字段 handoff、独立 review 行为均通过 |
| 边界未越权 | 前后外部路径 hash / 状态与执行清单 | 未修改 RenderDoc、Global、系统 Skill、cache、ACL、其他项目 |

最终状态分级：

- **完整完成**：Slice 0–9 的所有适用检查通过，安装与 fresh-context smoke 已验证，Reviewer Handoff 已生成；
- **workspace-local 完成 / 安装未验证**：本地 scaffold 与 validator 通过，但未获得安装授权或没有受支持安装入口；不得称 plugin 可用；
- **部分完成**：validator、metadata、安装或 smoke 任一关键检查失败或未执行；报告恢复入口；
- **失败**：Core 语义、Scope、来源或安全边界被破坏，或无法在不重新设计的情况下继续。

Lint、validator、安装和 smoke 分别验证、分别报告，不得合并成一个“全部通过”。

## 13. `execution-report.md` 契约

Executor 必须渐进维护一个报告，至少包含：

1. Task ID、执行角色、起止时间、Spec hash 和 Evolution hash；
2. 启动文件清单、工具与 CLI 解析结果；
3. 每个 Slice 的动作、完成条件和状态；
4. 实际创建或修改的文件清单；
5. 所有 validator、定向检查、安装和 smoke 命令的完整命令、退出码、错误、warning 与失败数；
6. manifest、marketplace 和 Skill metadata 的定向断言结果；
7. 安装授权、marketplace identity、plugin source 和安装状态；
8. fresh-context discovery / forward smoke 的最小输入、Role 命中与结果；
9. 最终 SHA-256 清单；
10. 已批准偏离、未验证项、开放风险和恢复入口；
11. 九字段 Executor → Reviewer Handoff Envelope。

报告不得包含凭据、无关配置值、Runtime storage ID 或本机 cache 内容。原始输出过长时可在报告中保留完整失败上下文和可定位摘要，但必须记录原始证据位置；不得只写“通过”。

## 14. 风险、暂停条件与安全回退

| 条件 | 必须动作 | 禁止动作 |
| --- | --- | --- |
| 工作区出现来源不明且冲突的文件 | 暂停并请求用户确认 ownership | 覆盖、`--force`、批量清理 |
| 本机 creator / schema 与规格实质冲突 | 查当前本机 reference 与官方文档；报告差异 | 手写猜测 schema 或改架构 |
| PyYAML 不可用 | 建 workspace-local 临时 venv；失败则标未验证 | 向系统 Python 做未经授权的全局安装 |
| CLI 命中商店入口 | 解析真实 `CODEX_CLI_PATH` 并验证 | 修改 WindowsApps ACL 或系统 PATH |
| 默认 `personal` marketplace name 在执行前已被占用或安装 | 暂停，请 Human Conductor 决定是否按 creator 例外规则使用其他 identity | 自动传入替代名称、静默改名或覆盖其他 marketplace |
| 已存在同名安装且来源不同 | 记录来源并请求卸载 / 切换授权 | 擅自卸载或复用错误来源 |
| 未取得安装授权 | 停在 workspace-local 完成状态 | 注册 marketplace、安装或重装 |
| 安装后内容疑似陈旧 | 先证实 cache mismatch；经授权使用 cachebuster helper 和 reinstall | 直接编辑 Codex cache |
| Core 出现平台 / 项目泄漏 | 在安装前修正并重跑全部边界检查 | 以“当前只有 Codex”作为保留理由 |
| Smoke Role 行为不符合合同 | 保留失败证据，定位 Skill / Adapter，最小修正后重验 | 修改 Core 来迁就错误行为 |
| 需要修改 RenderDoc 或 Global 规则 | 停止，移入后续独立规格 | 在当前周期顺手迁移 |
| 需要改变冻结 Role、Gate、目录或 alias 决策 | 返回 Planner / Human Conductor | Executor 自行重新设计 |
| 当前 Spec 与 Evolution 方向出现冲突 | 停止并返回 Planner，明确修订哪一项及其影响 | Executor 自行调和、修改 Evolution 或实现未来阶段 |

所有回退只处理本轮创建的 workspace-local 文件或经明确授权的安装状态。不得用 Git reset、清理用户文件或系统权限修改作为回退手段。

## 15. 后续 RenderDocAnalysis Project Integration

RenderDocAnalysis 是未来首个 Project Integration 示例，但必须使用独立、后续 Spec。进入条件：

1. Sacha Orchestra workspace-local validator 全部通过；
2. plugin 安装、正式 Role discovery 与 forward smoke 已通过；
3. Stage 0 的 `Contract Version: 1` Role、Gate、Artifact、Handoff 合同经独立 Reviewer 接受；
4. 用户明确批准修改 RenderDocAnalysis。

后续规格才可规划：

- RenderDocAnalysis Project AGENTS 与 workflow guide 对接；
- 项目 Artifact 保存策略映射；
- 旧 `spec-author/spec-executor/spec-reviewer` 的迁移、兼容期和删除；
- RenderDoc Domain Skill 与 Role Skill 的组合；
- 项目验证、Roadmap、release-boundary 与组合 smoke test。

这些均不是当前 bootstrap 的未完成项，不得写入当前 execution report 的实现清单，也不得为了兼容测试修改旧项目。

RenderDocAnalysis 接入后的成熟度迭代、完整 Hybrid 路由和可用退出条件由 `docs/architecture/evolution.md` 的 Stage 1–3 规定。第二项目验证暂不作为 Sacha Orchestra 在 RenderDoc 范围内达到可用的前置条件；未来只有出现真实需求时才进行可移植性审计。

## 16. Ultra Migration Executor 启动说明

Ultra Executor 必须：

1. 将工作目录设为 `C:\Users\<user>\Documents\MarketPlace\SachaOrchestra`；
2. 读取该目录内 `spec.md` 作为唯一执行规格，并读取 `docs/architecture/evolution.md` 作为不变量与未来阶段护栏；Evolution 不是本轮 Scope；
3. 不从 RenderDocAnalysis 工作目录执行，不修改其历史草稿；
4. 不创建 Goal、子 Spec、第二套计划、ticket 或状态文件；
5. 不重新设计 Role、门控、目录或 alias；marketplace name 必须来自 workspace-local JSON 的读取结果，默认 `personal` 发生冲突时按 9.1 暂停，不得自动选择例外 identity；
6. 不实现 Evolution Stage 1 及之后的 RenderDoc 接入、完整 Hybrid、Manager、Work Packet、并行或其他 Runtime；
7. 按 Slice 0–9 顺序执行，在授权门控前停止工作区外安装动作；
8. 用 `execution-report.md` 累积事实和证据；
9. 遇到暂停条件时保留现场、记录恢复入口并向 Human Conductor 报告。

Executor 的启动 Entry Condition：本规格已由用户明确批准；`<workspace-root>` 可写；所有工作区外安装动作仍待独立授权。

## 17. Planner → Executor Handoff Envelope

- **Task ID**: `SO-0.1.0-BOOTSTRAP-2026-07-12`
- **Source Role**: `Planner`
- **Target Role**: `Executor`
- **Outcome**: Sacha Orchestra 0.1.0 Foundation 的产品定位、三层边界、三核心 Role、三门控、渐进 Artifact、九字段 Handoff、repo-local marketplace、Codex Plugin 布局、兼容 alias、实施切片与验收已冻结为 Stage 0 可执行契约；`1.0.0` 只在 RenderDoc 完整 Hybrid 与 Sacha Orchestra 自托管升级均通过后发布，该方向已由 Evolution Artifact 冻结。
- **Scope Reference**: 本规格第 1–16 节，尤其第 10 节允许 / 禁止范围与第 11 节 Slice 0–9。
- **Artifact References**: `spec.md`; `docs/architecture/evolution.md`
- **Evidence References**: 本规格第 3 节当前事实与规范来源；执行时重新验证并写入 `execution-report.md`。
- **Deviations and Open Risks**: 当前系统 Python 与 bundled Python 均缺少 PyYAML；安装动作尚未获得执行时单独授权；CLI 与官方 schema 必须在执行时按当前 help / validator 复核。
- **Entry Condition**: 用户批准本规格；Executor 从 `<workspace-root>` 启动；先完成 Slice 0，且在 Slice 7 前取得工作区外安装授权。

---

本规格在用户批准前保持“草稿，待用户批准”。本轮不执行迁移、不创建 Goal、不安装 plugin、不修改 RenderDocAnalysis。
