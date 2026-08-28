# Tool Surface Routing：Roadmap 输入

> Artifact 身份：开发期探索决定记录；不进入发布插件，也不是 Runtime 权威。
>
> 状态：Roadmap 输入。本文记录已确认方向、外部证据、候选技术路线与 Unknown；**不构成实施授权，也不是已批准实施 Spec**。
>
> 消费者：后续 Roadmap 任务。Roadmap 必须把本文与另一份独立输入一起合并；存在冲突时保留冲突与决策前沿，不静默选择本文方案。

## 1. Human 已确认方向

1. 目标不是固定“首轮两个工具”。“两工具”只是一种实验条件；真正要吸收的是**减少模型可见工具暴露面、按任务/阶段渐进披露能力**的设计思想。
2. `fastctx` 与 `cprobe` 继续作为全局执行工具存在，不改造成 Sacha 专属 Capability Provider：
   - `fastctx` 用于把高频文件读取、搜索、发现、机械替换与可选命令执行沉淀为稳定结构化操作，减少临时 `exec_command` 拼接与上下文开销；
   - `cprobe` 用于稳定处理 SVC diff 等高频专用检查；其精确 schema、副作用和实现来源尚未在本仓库复核，Roadmap 不得自行扩写能力。
3. `exec_command` / `apply_patch` 等 Codex 原生通用工具继续作为兼容与长尾 fallback，不因引入稳定工具而删除。
4. `using-sacha` 继续保持唯一默认入口和 Intake 控制面，不承担底层工具发现、工具注册或工具执行职责。
5. 本文先作为设计输入交给后续 Roadmap 消费，不直接修改 Sacha Core、Skill 或 Runtime Adapter 的现行语义。

## 2. 已确认的项目边界

### 2.1 Sacha 当前职责边界

当前仓库的 `using-sacha` 只决定 Direct 或进入 Sacha Workflow；接受后的 Role、Gate、实施、Review 与协调由现有 Owner 继续负责。Codex 的运行时传输、参数、回退、恢复与当前会话工具面证据属于 `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md` 的 Runtime 局部职责。

因此“模型此刻能看到哪些工具”如果进入 Sacha，优先应是 **Codex Runtime 层的 tool-surface policy**，而不是新增到 `using-sacha`、Workflow Contract 或 Capability Provider 的业务语义。

### 2.2 FastCtx 当前可核实能力

`yyqrc/fastctx` 当前公开为本地 Rust MCP runtime，核心工具包括：

- `inspect_local_file`：文件读取；
- `grep`：内容搜索；
- `glob`：文件发现；
- `replace`：机械批量替换；
- 可选 Bash/job 工具：`run`、`run_background`、`job_output`、`job_kill`、`job_list`。

它适合作为高频稳定执行原语，但 `replace` 与 `apply_patch` 不是完全同义：机械模式替换适合前者，语义性局部编辑仍需要通用编辑路径。

### 2.3 `cprobe` 边界

本文只采用 Human 当前给出的事实：`cprobe` 是全局工具，主要稳定处理 SVC diff 等高频专用检查。其仓库、schema、读写副作用、失败语义和回退路径均为 **Unknown**；Roadmap 若要把它写入具体阶段或验收，必须先取得当前实现证据。

## 3. 外部机制证据

### 3.1 `xiaobright/dsh-anchored-standard`

当前 `main`（检查日期：2026-08-28）已经从“首轮窄工具面后一次性恢复完整 Standard”继续演化为：

- 首次模型请求保持 Minimal 对齐的真实小工具面，并抑制自动注入 context；
- 首个 durable `tool/call` 或 `assistant/message` 后晋升；
- 晋升后只保留一个较小 resident catalog；
- `dev_tool_search` / Skill discovery 负责按需解锁更重的 Standard 工具；
- 仓库明确记录：晋升时重新灌入完整 Standard catalog 会把 trajectory 拉回 standard-like，因此当前实现避免一次性全量暴露；
- 独立复现对“trajectory 被首轮条件改变”有较强支持，但对最终 coding ability 的稳定提升仍未定论。

可吸收的工程结论不是“必须两个工具”，而是：

> **model-visible tool surface 本身是一等输入；常驻目录应尽量小，重能力可以按需发现，并且暴露阶段需要可恢复状态。**

来源：`xiaobright/dsh-anchored-standard` `README.md`，项目状态 2026-08-17，检查于 2026-08-28。

### 3.2 `yjh051108/dsh-routing-suite` / `dsh-router-standard`

名称需要消歧：另有 `dragonbaba/dsh-routing-suite`，该实现明确保持完整 Standard catalog、**不移除或限制工具**，不能作为“减少工具暴露”的证据。本文所指 Routing Suite 是 `yjh051108/dsh-routing-suite` 及其 `dsh-router-standard` 组件。

`yjh051108/dsh-router-standard` 当前研发线 `v1.19.1`（README 标记 2026-08-24，尚未发布）已经把相似思想推进到更完整的阶段模型：

- 首轮按真实用户任务进行分类；历史版本按 band 选择不同 first-turn core tool surface；
- 当前研发线使用严格阶段 workflow 与**渐进披露**；
- 阶段化解锁、两档预放、直达语义、交付阶段全量开放；
- 提供 `tools_catalog` 全量索引与 `tools_help` schema 查询；
- 删除 `all:true` 全量出口，未解锁工具不直接进入模型视野；
- 其历史与现行研究都把 persona / task routing 与 tool surface 视为外部 Harness 控制量，而不是让模型在完整目录里自行承担全部路由。

可吸收的核心不是其 DeepSeek-specific persona band，而是：

> **工具暴露面可以同时由任务类型、工作阶段和完成信号控制；“当前可见能力”与“系统实际拥有能力”不必相等。**

来源：`yjh051108/dsh-router-standard` `README.md`，检查于 2026-08-28。

### 3.3 Codex 已有原语

OpenAI Codex 当前源码已经提供可直接复用的底层机制：

- `ToolExposure::Direct`：进入初始 model-visible tool list；
- `Deferred`：不在初始列表，保留给后续 discovery；
- `Hidden` / `CodeModeOnly` 等其他暴露面；
- `tool_search`：对 Deferred tool metadata 做 BM25 搜索，并把匹配工具暴露给下一次模型调用。

这意味着 Sacha 不需要自己重新实现“工具仓库”或工具调用协议；如果 Codex 宿主暴露足够 seam，优先只需要决定**哪些工具 Direct、哪些 Deferred，以及何时改变 exposure**。

同时存在已公开的可靠性风险：Codex issue 中已有“工具全部 Deferred 后模型没有主动调用 `tool_search` 就结束”和 Code Mode 下 discovery surface 不一致的报告。因此 `tool_search` 应当是可测基础设施，不能在没有 fallback 和验收数据时被当成绝对可靠的唯一入口。

来源：`openai/codex` `codex-rs/tools/src/tool_executor.rs`、`codex-rs/core/src/tools/spec_plan.rs`、`codex-rs/core/src/tools/handlers/tool_search_spec.rs`，检查于 2026-08-28。

## 4. 候选目标架构（待 Roadmap 合并裁决）

建议用“**最小充分暴露面（minimal sufficient surface）**”替代“固定 N 个工具”。候选分层如下：

```text
用户目标
  │
  ├─ Direct
  │
  └─ using-sacha → 现有 Workflow / Role
                    │
                    ▼
          Runtime Tool Surface Policy
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Resident     Deferred    Fallback
   高频稳定原语   长尾能力      通用兜底
        │           │           │
  fastctx(read)   tool_search   exec_command
  cprobe*          GitHub       apply_patch
  必要交互工具      Web/MCP      其他原生通用工具
                  Plugins
```

`* cprobe` 的确切能力与副作用待验证。

### 4.1 Resident

只放**高频、稳定、跨大量任务都会复用**且 schema 成本值得常驻的工具。候选包括：

- `fastctx.inspect_local_file` / `grep` / `glob`；
- 经验证为只读且高频的 `cprobe` diff 能力；
- 当前阶段必需的人机交互或控制原语。

不要因为一个工具“可能有用”就常驻；Resident 的目标是稳定工作面，不是缩小版全量目录。

### 4.2 Role / Phase Direct Surface

Sacha 已有 Planner / Explore / Executor / Reviewer 等任务职责，但工具面控制应与 Role 语义解耦，仅把 Role/阶段作为 Runtime policy 的输入之一。

候选示例，不是已批准矩阵：

| 工作态 | 候选 Direct surface |
| --- | --- |
| 普通只读调查 | `fastctx` read/search/glob、只读 `cprobe`、`tool_search` |
| Planner / Explore | 同上；默认不直接暴露写工具 |
| Reviewer | read/search/diff + `tool_search`；默认不直接暴露项目写工具 |
| Executor | read/search + `fastctx.replace` + `apply_patch` / `exec_command` fallback + `tool_search` |
| 交付/外部动作 | 只在当前 Scope、授权和阶段真正需要时展开对应能力 |

这里的价值是减少无关 schema 和错误工具选择，不是用工具面替代 Sacha 现有授权或 Gate。

### 4.3 Deferred Discovery

适合 Deferred 的是低频、任务相关性强、数量容易膨胀的能力，例如 GitHub、Web、部分 MCP、插件和外部服务。优先复用 Codex 原生 `tool_search`，而不是再造 `sacha_tool_search`。

如果后续证据证明纯模型主动 discovery 不稳定，可评估“Harness 预取 / route hint → 仍使用 Codex Deferred registry”的混合方式；不要第一步就新增第二套工具注册协议。

### 4.4 Fallback

`exec_command` / `apply_patch` 等通用能力保留，防止稳定专用工具覆盖不足或 Deferred discovery 失败后进入死路。它们究竟长期 Direct、按工作态 Direct，还是可快速解锁，需要通过 A/B 数据决定。

## 5. 不建议在第一阶段做的事

1. **不固定首轮两个工具。** 可把 narrow-bootstrap 当实验变量，但不写成产品不变量。
2. **不把 `fastctx` / `cprobe` 改造成 Sacha Capability Provider。** 它们当前是跨任务全局执行原语，不应与领域 capability routing 混为一层。
3. **不让 `using-sacha` 承担 tool routing。** Intake 只决定流程入口。
4. **不重新实现 Tool Registry / Tool Search。** Codex 已有 `Direct / Deferred / Hidden + tool_search` 原语，应先复用。
5. **不先做多 Runtime 对齐。** 初始验证优先 Codex；只有机制在真实任务中成立后，再判断哪些语义值得上升为跨 Runtime 抽象。
6. **不把 DeepSeek 的 trajectory 结论直接外推到 GPT-5.6。** 对 Codex 的收益必须独立测量。

## 6. Roadmap 候选阶段

以下只是供合并 Agent 组织 Roadmap 的候选，不是排期或实施授权。

### A. 建立基线与工具清单

- 记录当前 Codex session 的 model-visible tools、schema/token 成本和实际使用频率；
- 识别 `fastctx` / `cprobe` / 原生工具之间的重复面、fallback 和真实失败类型；
- 核对 `cprobe` 当前 schema、副作用和稳定入口；
- 建立 Direct / Deferred / Hidden 的可观测证据。

完成信号：可以回答“哪些工具值得常驻、哪些只是长尾、当前失败主要来自什么”，而不是按名称主观分类。

### B. Codex 原生 Deferred MVP

- 保持 Sacha Core 与 `using-sacha` 不变；
- 在 Codex Runtime 层使用现有 `ToolExposure` / `tool_search`，先把明确长尾工具移出初始 model-visible surface；
- `fastctx` 高频只读工具和已验证 `cprobe` 保持 Direct；
- 保留可验证 fallback。

完成信号：工具面明显缩小，同时任务成功率、fallback 和 discovery 失败不劣化到不可接受范围。

### C. Role / Phase Tool Profiles

- 让 Runtime 根据当前工作态选择不同 Direct surface；
- Planner / Explore / Reviewer 默认只读，Executor 才展开写能力；
- 不改变现有授权与流程判断 Owner。

完成信号：不同工作态的 surface 可预测、resume/恢复后不漂移，且不会因工具隐藏造成合法任务无法继续。

### D. 渐进披露与主动路由实验

在 B/C 有稳定数据后，再比较：

- 纯 `tool_search` model-driven discovery；
- task/phase hint 驱动的 Harness 预展开；
- 类 Router Standard 的阶段化解锁；
- 可选 first-turn narrow bootstrap。

完成信号：有 A/B 证据证明额外路由复杂度带来的收益超过额外 round-trip、cache 破坏与恢复复杂度。

### E. 决定是否上升为跨 Runtime 概念

只有 Codex 机制稳定且出现第二 Runtime 的真实消费者后，才决定是否抽象“Tool Surface Policy”到平台中立层；否则继续留在 Codex Runtime 局部实现。

## 7. 建议验收指标

后续 Spec 不应只验证“工具数量变少”，至少同时看：

- 首次请求与稳态的 model-visible tool 数量和 schema token；
- 任务成功 / 验收结果，而不是只看 reasoning 风格；
- `tool_search` 调用率、命中率、未调用导致的失败率和额外 round-trip；
- FastCtx / cprobe 首选命中与 fallback 比例；
- 错误工具选择、重复搜索、重复读取和命令构造失败；
- prefix/cache 变化与工具面切换成本；
- resume、compaction、subagent 下的 exposure 状态一致性；
- 授权、只读/写入边界和高影响动作是否保持现有安全语义。

## 8. Unknown / 决策前沿

1. `cprobe` 的正式仓库、当前工具名/schema、只读/写入副作用和失败语义尚未核实。
2. 当前 Codex App/CLI 对 `ToolExposure` 的哪些控制面可通过插件/配置实现，哪些仍需要 Codex core patch，需按实际目标版本验证。
3. `tool_search` 在当前 GPT-5.6 Sol + Code Mode / Direct Tool Mode 组合下的真实可靠性需要单独测试；公开 issue 不能替代本项目证据。
4. `fastctx` 哪些工具应该始终 Direct：只读三件套较可信，`replace` / Bash/job 是否常驻应按频率、副作用和 schema 成本决定。
5. 是否需要 first-turn bootstrap、任务分类或严格阶段 workflow，必须在静态 Resident + Deferred MVP 之后用 A/B 结果决定。
6. subagent 是否继承父任务 surface、独立计算 surface，或保持原生 Codex 行为，需要先核对当前协作界面和模型工具面证据。
7. compaction 是否需要重新收窄 surface 尚无 Codex 本地证据；不能直接照搬 DSH 的 re-anchor 机制。

## 9. 给 Roadmap 合并 Agent 的消费规则

1. 把第 1 节 Human 已确认方向作为固定输入；不要把“固定两个工具”重新写成目标。
2. 第 2、3 节是当前事实/外部证据；其中外部实验只能说明设计可行性和风险，不能单独定义 Sacha 产品事实。
3. 第 4、6、7 节是候选架构、阶段和验收输入；与另一份文档冲突时列入“决策前沿”，不得静默以本文覆盖另一来源。
4. Roadmap 应表达项目目标、阶段结果、依赖、完成信号、Unknown 与未来 Spec 分组；不要把 Sacha 内部流程调用、Agent 交接或本次会话状态写进 Roadmap 正文。
5. 真正实施前应形成独立 Spec；如果要修改 Codex Runtime surface，优先从 Runtime 局部 Owner 和真实 Codex 版本证据开始，不从本文直接复制成 Runtime 合同。

## 10. 主要来源

### Sacha Orchestra

- `AGENTS.md`
- `docs/AGENTS.md`
- `PLUGIN_DESIGN.md`
- `plugins/sacha-orchestra/skills/using-sacha/SKILL.md`
- `plugins/sacha-orchestra/skills/roadmap/SKILL.md`
- `plugins/sacha-orchestra/core/artifact-protocol.md`
- `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md`

### 外部项目（检查于 2026-08-28）

- `xiaobright/dsh-anchored-standard` — `README.md`
- `yjh051108/dsh-routing-suite` / `yjh051108/dsh-router-standard` — `README.md`
- `dragonbaba/dsh-routing-suite` — `README.md`，仅用于同名实现消歧
- `openai/codex` — `codex-rs/tools/src/tool_executor.rs`、`codex-rs/core/src/tools/spec_plan.rs`、`codex-rs/core/src/tools/handlers/tool_search_spec.rs`
- `yyqrc/fastctx` — `README.md`
