# Sacha Orchestra 迭代路线图提案

> 状态：提案，未经 Human 批准，不构成实施授权；放置位置沿用 CPTOOLS/CGAME 两份接入设计文档的先例（根目录设计输入）
> 日期：2026-07-24
> 输入：2026-07-24 全量评估会话；`CPTOOLS-CAPABILITY-INTEGRATION.md`、`CGAME-DOMAIN-CAPABILITY-INTEGRATION.md`；cgame-workflow / cgame-unity / cgame-engine / superpowers-brainstorming 实读证据；Codex 会话 `019f8437-460e-7a10-928d-b8fcd01a82d3` 真实使用痕迹
> 基线：`0.1.17` 已发布；`0.1.18` source/static 已 Accepted，未安装未发布；本路线图不阻塞 `0.1.18` 按既有授权单独完成安装与发布
> 状态更新（2026-07-24 Human 决策）：① ITER-02 路由入口改名确定为 `D0 Sacha Direct`；② ITER-04 采用「删除独立 L-Profile 表格」方向（§ITER-04 详解）；③ 批次 0 先行实施；④ ITER-06 clarify 改为**塞进 sacha `skills/clarify`**（非通用 provider、非 cgame-unity 专属；explicit-only，非生产 Role，小工具与引擎共用同一份机制，问题库靠 provider）
> 执行进度（2026-07-24，goal 驱动逐批次执行）：批次 0（ITER-01 已由另一会话先行完成且更优——CRLF hash 改为 `git diff HEAD`；ITER-02 D0）✅ commit `a04bd6c`；批次 1a（ITER-03 歧义区询问）✅ `a6710f1`；批次 1b（ITER-04 删 L-Profile，breaking）✅ `2b51e2f`+`5329b25`；批次 2（ITER-06 clarify + ITER-05 能力证据胶囊）✅ `ba6a633`+`8920909`；批次 3（ITER-08 caveman 密度原则 + ITER-11 ClaudeCode Adapter；ITER-07 真实并行仍为 Needs Evidence，见 §8.5）✅ `0f35d48`+`cca805d`；clarify 决策持久化（批次4/5/6）✅ `dd3bf17`/`cba68db`/`041bc2d`。2026-07-26 GPT5.6 review（`docs/plans/2026-07-24-roadmap-execution/review.md`）后：P0/文档矛盾/validator 退化修复 ✅ `0d1555a`，validator 内可执行模型探针 `9b4a068`（**测试内模型，非真实路由证据**；B1-01 真实路由仍 Open，需 Codex runtime 验证），review follow-up ✅ `07e9e63`，5 个拍板项（§8.3）落地 ✅ `9501b0a`+`53ba029`，B1-02/R-01/B1-04/B2-02 修复 ✅ `db74527`。每批次均经独立会话 review 后 commit+push。**注意：Contract Version 后经 §8.3-12 改判升 2（Workflow），早期批次的"维持 1"已被取代。**

## 1. 方向判断（三条主线）

1. **"过重"的解法不是砍能力，是砍默认路径上的分类仪式**：保持 `L0 Local Direct` 为唯一默认；歧义区一次轻量询问；三套验收坐标系瘦身。贵 Planner / 便宜 Executor 的模型分级（Adapter §2.1.1）保留且不再被套在全套仪式里。
2. **sacha + cgame-unity = 更强的 cgame-workflow**：cgame-unity 出领域能力（provider），Sacha 出 multiAgent / 模型分级 / 省上下文 / 跨 context 恢复（底座）。provider 不拥有 Role/Gate/Scope/verdict 的边界不变。
3. **Plan 零偏移的前提是 Planner 的输入质量**：以 clarify 能力（brainstorm / survey / grill 三模式）补足模糊需求的澄清，使贵模型 Planner 能产出可直接交接的 Plan。

## 2. 迭代清单总表

| ID | 动作 | 批次 | 成本 | 来源问题 |
| --- | --- | --- | --- | --- |
| ITER-01 | validator 去 CRLF 硬编码 hash | 0 止血 | 小 | 3 个历史 validator 在正确归一化的 checkout 上无条件失败（现状红灯） |
| ITER-02 | `S0` 一词三义消解（路由入口改名） | 0 止血 | 小 | `S0 Sacha Direct`（路由）vs `S0 No Setup`（setup 维度）vs stable Outcome 冲突 |
| ITER-03 | 歧义区主动询问入口 | 1 减重 | 中 | "过重"体感的最直接来源：默认就要穿越流程 |
| ITER-04 | 三套验收坐标系瘦身 | 1 减重 | 大（Core breaking） | Gate / L-Profile / 8 维并存，13 个分类决策点 |
| ITER-05 | CGAME I2：结构化能力消费 | 2 接入 | 中 | 会话 019f8437 证明能力是"嘴上遵守"，缺可核对轨迹 |
| ITER-06 | clarify 能力（brainstorm/survey/grill） | 2 接入 | 中 | Planner 不澄清模糊需求，Plan 无法零偏移 |
| ITER-07 | 第一次真实 Managed Parallel | 3 兑现 | 中-大 | 1.0.0 门槛 / SH3 僵局：并行从未真实跑通 |
| ITER-08 | caveman 密度原则 | 3 兑现 | 小 | 回复与 Artifact 冗余；输出密度是与流程正交的用户开关 |
| ITER-11 | ClaudeCode Adapter（第二 runtime 支持） | 3 兑现 | 大 | 当前正用 ClaudeCode 开发；evolution.md §7 Portability 首次落地 |
| ITER-09 | 测试从文本存在转向行为探针 | 4 按需 | 中 | F-02 证明文本测试会骗人 |
| ITER-10 | setup 生成器投入产出重估 | 4 按需 | 暂缓 | 1506 行服务低频操作 |
| 按需池 | cgame-unity 能力缺口 | 4 按需 | — | 真实任务踩到禁区才补 |

## 3. 批次详情

### 批次 0：止血（无依赖，可立即做）

#### ITER-01 validator 去 CRLF 硬编码 hash

- 历史改动点是三个 workflow 文本 validator；这些 validator 已在 2026-07-26 的最小测试收敛中删除，不再作为当前验证入口。
- 方案：把 `artifact-protocol.md` 的 CRLF 字节级 SHA-256 期望（`4F57…`）改为语义断言——文件含 `Contract Version: 1`；九字段名精确存在且顺序正确（Task ID → Entry Condition）；不含 runtime 传输词（`wait_threads`、`spawn_agent` 等）。内容完整性交还 Git。
- 验收：三个 validator 在当前 Windows 工作区通过；用 `git show HEAD:...`（LF 字节）输出到临时文件模拟，断言同样通过；其余 validator 不回退。

#### ITER-02 `S0` 一词三义消解（已定：改名 `D0 Sacha Direct`）

- 方案：路由入口 `S0 Sacha Direct` 改名为 `D0 Sacha Direct`，形成 `L0 Local Direct`（Sacha 外）/ `D0 Sacha Direct`（Sacha 内）的 Direct 系列；`S0`–`S4` 前缀独占 Project setup 维度。
- 同步点：Adapter §2.0.2/§2.6、executor/planner SKILL.md、两个 README、`AGENTS.md`、validator 文本断言、`generate_project_integration.py` 的 `render_workflow_rule` 模板（简明操作模板内含 `S0 Sacha Direct`）。
- 边界：已生成项目文件（如 `<client-root>\Docs\workflow-rule.md`）是项目所有的生成物，不在本 Scope；下次 reconciliation 自然跟进，不手工改。
- 验收：全仓 grep `S0` 只剩 setup 维度一种语义；validator 全绿。

### 批次 1：减重（"过重"体感的核心）

#### ITER-03 歧义区主动询问入口

- 方案：Adapter §2.0 入口判断增加三分类映射——明显琐碎（默认 `L0`，不问）；明显高风险（Reviewer Gate 事实成立，强制走，不问"要不要跳过"）；中间歧义区也不暴露“Sacha / 直接处理”内部编排选择，Route owner 默认采用满足目标的最轻路线。只有缺失的用户偏好会改变可见交付、持久化或跨 context 恢复时，才问一个带推荐、主要取舍和具体影响的问题。借鉴 cgame-workflow `unity-task-workflow` 的入口拦截，但不展开复杂度问卷；询问本身不产生 Artifact。
- 验收：三场景行为断言入 validator（琐碎不问、高风险不问、纯内部路线不问；缺失用户可见偏好时只问一次）；安装后真实任务验证。

#### ITER-04 三套验收坐标系瘦身（Core breaking change；已定方向：删除独立 L-Profile 表格）

**现状问题**：判断"验收做到什么程度"要同时穿越三套各自独立的体系——

| 体系 | 档位 | 回答 | 触发 |
| --- | --- | --- | --- |
| Reviewer Gate | 开/关 | 要不要**独立**判断 | §5.2 事实（安全/权限/持久数据/breaking/回退困难/验证不完整/证据冲突/Human 要求） |
| L-Profile（§2.2） | L0 直查 / L1 标准工程 / L2 独立风险 Review / L3 人工外部证据 | 由**谁**以多强保证判断 | 同 §5.2 事实（L2 写明"只由 Reviewer Gate 事实开启"） |
| V 强度（§2.1 八维之一） | V0 diff/解析 → V4 真机/Human | 执行**哪些**技术检查 | 按风险 |

**Reviewer Gate 与 L2 是同一事实的两次编码**：§2.2 的 L2 触发事实列表与 §5.2 Reviewer Gate 开启条件逐条重复；Core 被迫写至少 4 处消歧条款（"L2 独立 Review 不等于 V3"、"Profile 的 L0 不是入口 L0 Local Direct"、"L0/L1 不因文件数量自动升级"、"二者独立选择"）——这些条款的存在本身就证明两个体系在重叠。0.1.18 的 F-01（Executor 把 `V3 Full/Release Candidate` 偷换成 `Independent Risk Review`）正是这套混淆的实际受害者：执行者看到 V3/L2 都像"独立 Review"就真把它们合并了。

**收编映射**：

| 原 L 档 | 收编到 | 理由 |
| --- | --- | --- |
| `L0 Direct Check` | `V0` + Executor 自查 | 即"最轻验证"，V0 已覆盖 |
| `L1 Standard Engineering` | `V1` + Executor 自查并报告失败/warning/未验证项 | 即"与风险匹配的检查"，V1 已覆盖 |
| `L2 Independent Risk Review` | **就是 Reviewer Gate 开启** | 触发事实与 §5.2 逐字重复；留两个名字只会养出下一个 F-01 |
| `L3 Targeted Human/External Evidence` | **保留**，重命名 check-level **human overlay**（脱离 L 系列） | 唯一不可替代：把人工/真机/Editor 证据绑定到具体 `check_id` 而非升级整个任务；与 V4 正交（V4 是"跑真机检查"动作，overlay 是"此 check 须 Human 确认"的归属） |

**净效果**：验收判断从"三套同时分类"变两个正交判断——① Reviewer Gate（谁来判）＋ ② V 强度（做什么检查）；人工项由 human overlay 按 check_id 单独叠加。删掉的消歧条款比保留的 L 表格还多，Core 实际变薄。`Accepted with follow-up`（非 release-blocking 人工 pending 不阻塞交付）语义保留，搬到 Reviewer Gate 节。硬不变量（Reviewer provenance、原始证据权威、五态 human_assistance_state、`agent_observed ≠ human_confirmed`）全部保留——**没有任何行为语义真的消失，只删重复编码**。

**目标**：每任务分类决策点从 13 降到 ≤6——三个 Gate + 默认全最低强度（只在升级时记录触发事实，不再逐项分类）。

**并入项**（同属 Core 文本修订，一次做完）：
- Core §6 的 `no-polling` 条款挪到 Adapter §2.1（唯一真正越界的平台策略）；
- Entry Condition / evidence locator / 九字段过度触发审计：确认它们只在有真实交接消费者时生成（字段本身不砍——跨 context / 换模型 / 独立 task 时它们是刚需，是"贵 Planner→便宜 Executor"零偏移的载体）。

**程序约束**：按 `evolution.md` §8，这是 Core breaking change——Human 已确认方向（删除独立 L 表格）；落地时逐条列出改动供确认；需要独立 Review；评估 Contract Version 1→2。

**被否决的备选**：保留 L0–L3 名称但声明"L 只是 Reviewer Gate 开关 + human overlay 的简写"——改动小，但名字还在就会有人（和模型）继续琢磨"L 和 V 什么关系"，混淆的病根没除。

**验收**：Core 行数净减少；每个维度升级仍需记录触发事实；硬不变量逐条保留；validator 同步更新并通过。

### 批次 2：能力接入（sacha + cgame-unity 闭环）

#### ITER-05 CGAME I2：结构化能力消费

- 方案：在 `<client-root>`（或等价已接入项目）的真实任务中，Role 走完整可核对路径：读 confirmed Binding → 按 load policy 调用能力（如 `code.discover` on-demand、`compile.verify` risk-matched）→ 返回证据胶囊（status / facts_or_findings / validation / gaps / evidence_locators）进入 Execution Report 或最终回复。把会话 019f8437 式的"嘴上遵守"变成结构化消费。
- 证据胶囊格式：与 CPTOOLS C2 合并为单一规范，本次一并定义，避免两套胶囊。
- 前置：目标项目写入需该项目适用的授权（`<client-root>` 为 svn 项目）。
- 验收：至少一个真实任务留下可核对轨迹（capability id + load policy + 胶囊字段）；provider 缺失时 Direct 路线不受阻（回归断言）。

#### ITER-06 clarify 能力（brainstorm / survey / grill 三模式；已定：塞进 sacha `skills/clarify`，explicit-only 非生产 Role）

- **分层定位**（关键）：clarify 拆为「机制」与「问题库」两半——
  - **澄清机制（domain-neutral）**：一次一问、HARD-GATE（设计未批准不实施）、2-3 方案带取舍、三模式分流、产出落入 Plan 输入证据。与领域无关——开发小工具和引擎开发用同一套"怎么澄清"。
  - **领域问题库（domain-specific）**：Unity 问 NGUI/AB/版本/平台矩阵；引擎问 C++/构建目标/bat；小工具问运行环境/输入输出。作为 clarify 的可选 reference（可消费 cgame-unity 的 project-inspect 结果来问对问题）。
- **承载**：**塞进 sacha `plugins/sacha-orchestra/skills/clarify`**（explicit-only，非生产 Role，与 setup-project/feedback 同款功能 Skill），Human 已就此改判（原方案"通用 provider 与 cgame-unity 平级"被否决，因 clarify 只被 sacha Planner 消费、无跨宿主复用需求，单造插件是过度工程）。澄清机制 domain-neutral，小工具与引擎共用同一份；领域问题库靠 provider。不是第 4 个生产 Role，不进 Core。
- 三模式分工：
  - `clarify.brainstorm`：模糊想法 → 展开成设计（回答"做什么"；借鉴 superpowers-brainstorming）；
  - `clarify.survey`：方向已有 → 现状事实与横向对比（回答"现在是什么样"；对应 cgame `unity-feature-survey`，可叠 `cgame-unity:code-discovery`）；
  - `clarify.grill`：想法已有 → 拷打边界细节（回答"具体怎么处理、验收怎么写"；对应 cgame `unity-grill`）。
- 从 superpowers-brainstorming 只吸收两条原则（不抄它的 9 步 checklist 和 Visual Companion）：HARD-GATE；提 2-3 方案带取舍和推荐。提问节奏后续经 mattpocock batch-grill-me 升级为 frontier 按轮（前置已决即可按轮并行问，前置未决归后轮；相互独立的决策同轮并列摆出）——见批次5/6。
- 验收：一个模糊需求真实走完 brainstorm → 产出被 Planner 采用的 Plan 输入；简单任务不被强制进 clarify；小工具场景（无 cgame provider）同样可用。

### 批次 3：multiAgent 兑现

#### ITER-07 第一次真实 Managed Parallel

- 方案：用 cgame-unity 只读能力当 Work Packet——同一引擎调查任务的两个独立 `code-discovery` 目标（只读、write scope 天然不重叠），跑通 `parallel_expected` → `parallel_started` → 去重聚合全链路。叠加 §2.1.1 模型分级与 `fork_turns=none` 最小上下文，一并验证"该贵则贵、该廉则廉 + 省上下文"。
- **ClaudeCode 侧已兑现（2026-07-24）**：在 ClaudeCode 环境，用同一条消息并发两个 `Agent` 调用（Work Packet A：cgame-unity 能力清单；Work Packet B：cgame-engine 能力清单 + 同构对照），两个独立只读调查并行启动并各自返回结构化结果，integration owner 去重聚合。结果：cgame-unity 6 项能力 / cgame-engine 5 项；前 4 轴（project.inspect / code.discover / change.guard / change.review）完全同构，验证轴命名分裂（`build.verify`↔`compile.verify`），unity 独有 `runtime.verify`。这兑现了 ClaudeCode Adapter §6 的并行映射（一条消息多 Agent 并发 = `parallel_started`）与 §10.3 待验证项。**Codex 侧 `spawn_agent` 并行仍需在 Codex runtime 另行验证**（当前环境无法直接跑）。
- 风险：0.1.11 前科（独立 Review Reject）；可能暴露 Runtime 真实问题——按既有 feedback 路由处理，不静默降级。
- 验收：真实记录 `parallel_started`（首次 wait/join 前 ≥2 实例）；聚合去重率与最小事实集完整；满足 `evolution.md` §5 中"至少一个真实开发任务实际启动并行并完成聚合"的 1.0.0 门槛条目（ClaudeCode 侧已满足）。

#### ITER-08 caveman 密度原则

- 方案：在 K 维度或 Core 增加一条原则——用户可见回复密度是与任务流程正交的显式开关（explicit-only），不改变任何授权/验证/裁决；Artifact 正文"压缩填充、不压缩事实"（evidence locator、Entry Condition、九字段、失败与未验证项必须保留）。
- 不做：不新增 Skill、不抄 caveman 的 7 条风格清单、不加触发关键词机制。
- 验收：一条原则入合同；validator 增加"最小事实集不因密度压缩缺失"断言。

#### ITER-11 ClaudeCode Adapter（第二 runtime 支持）

- **时机与定位**：当前正用 ClaudeCode 开发，这是 evolution.md §7 "Portability：第二 Agent Runtime 的 Adapter 审计"的首次落地，也印证了"不去 Codex 化"的判断——Core 三层断言是 runtime-neutral 正确性条件，ClaudeCode 用不同机制满足同一组断言。
- **前置**：排在 ITER-04（Core 瘦身）之后——Adapter 映射的是瘦身后干净的 Core，避免给 L-Profile/8 维两套语义各写一遍映射。"一次性弄完"指本项做透，不是跳过瘦身直接做。
- **runtime 机制映射**（ClaudeCode 与 Codex 模型根本不同，已查证）：

| Core 概念 | Codex 映射（现有） | ClaudeCode 映射（新增） |
| --- | --- | --- |
| 独立 Role context | `create_thread` 异步 task | `Agent` tool spawn subagent（独立 context） |
| completion 回传 | `wait_threads` join + `<codex_callback>` payload | subagent **同步 return**（Agent 调用本身阻塞等结果） |
| Transport：callback 恰一次 / dedup | 三层断言显式保证 | **被同步 return 平凡满足**（return 天然一次、无重复、无 idle root 要唤醒） |
| Identity：Task ID/Scope/revision 匹配 | 显式核对 | **仍保留**——subagent 返回内容仍要核对是否当前 transition 期望 |
| Progress：owner 续转 | root task 保持 phase + `wait_threads` | 主对话 loop 本身就是 owner，顺序执行天然续转 |
| 首次进展 / liveness 超时 | `60s`/`30s` 显式 bound | Agent 同步返回，无需（或映射为 timeout） |
| 模型分级（贵 Planner/便宜 Executor） | §2.1.1 task 配置参数 | **Agent `model` 参数直接指定**（sonnet/opus/haiku），比 Codex 更直接 |
| 并行 | `spawn_agent` + `wait_agent` | 一条消息里多个 Agent 调用并发 |
| 领域规则注入 | 读 AGENTS.md / workflow-rule | **SessionStart hook** 自动注入（cgame 已验证可行） |

- **关键设计决策**：
  - 承载形式：`adapters/claudecode/runtime-adapter.md` + 复用现有 `skills/`（ClaudeCode 插件同为 SKILL.md 结构，cgame `.claude-plugin/plugin.json` 已验证可行）；
  - Role context：生产 Role 用 `Agent` subagent 承载独立 provenance（满足 Reviewer 独立性）；轻路径直接主对话；
  - 模型分级：**ClaudeCode 反而更强**——Agent 的 `model` 参数直接指定贵/便宜模型，你要的"贵 Planner 便宜 Executor"在 ClaudeCode 更顺；
  - SessionStart hook：可选增强（像 cgame 自动注入 workflow-rule），但保守——hook 是 workspace 外状态，需单独授权；
  - **Core 改动：只加一段"runtime 映射注释"，不改规范性语义**；随本 Adapter 一起做 Core 三分类审计（自然映射 / 平凡满足 / 无意义），这是 evolution.md §7 三分类审计的首次兑现。
- **验收**：ClaudeCode 下一个真实任务走完 Planner(贵模型 subagent) → Executor(便宜模型 subagent) → 主对话 owner 续转的全链路；三层断言每条都有"本 runtime 如何满足/平凡满足"的映射记录；Core 规范性语义零改动。
- **风险**：ClaudeCode subagent 的 context/返回容量、Agent tool 的真实可用模型档位需以当前环境实测为准；hook 注入需单独授权，不作为默认路径。

### 批次 4：按需池（不预排期）

- ITER-09 测试行为探针化：并行断言、callback 恰一次、`report_limited` 的运行时负向探针；依赖 ITER-07 有真实并行场景。
- ITER-10 setup 生成器投入产出重估：只记录问题，暂缓。
- cgame-unity 缺口池：`ngui-analysis` / `assetbundle-analysis` / `performance-gc` 只在真实任务踩到对应禁区时补；`xlua-hotfix` / `runtime-log-diagnosis` 经 Human 确认基本不用，最低优先。

## 4. 依赖与顺序

```text
批次 0（ITER-01, 02）          无依赖，可立即并行
  └─> 批次 1（ITER-03 → ITER-04）   03 小先做；04 是大改，含 Core breaking 程序
       └─> 批次 2（ITER-05 ‖ ITER-06） 两者可并行
            └─> 批次 3（ITER-07 依赖 05 的能力已被消费；
                          ITER-08 独立，可搭 ITER-04 的车；
                          ITER-11 依赖 04 的 Core 瘦身完成）
                 └─> 批次 4（ITER-09 依赖 07；其余按需）
```

建议 `0.1.18` 先按既有授权完成安装/发布收尾，批次 0 落在其后新 baseline 上，作为 `0.1.19` 的第一批内容。

## 5. 主要风险

| 风险 | 缓解 |
| --- | --- |
| ITER-04 是 Core breaking change，可能破坏已验证能力 | 严格走 evolution.md §8 程序；硬不变量逐条回归；独立 Review |
| ITER-02 改名跨文件同步点多，且触及生成器模板 | validator 先行（ITER-01 后全绿再改）；已生成项目文件明确不在 Scope |
| ITER-07 暴露 Runtime 真实问题（0.1.11 前科） | 预期之内；走 feedback 路由，不静默降级为串行成功 |
| ITER-05 需要目标项目授权（svn 项目写入） | 授权边界保持独立；无授权时只做到 read-only 消费证据 |
| clarify 被滥用成每单必问，加重而非减重 | HARD-GATE 只绑定"输入模糊"；简单任务明确不触发 |

## 6. Non-goals

- 不砍 Entry Condition / evidence locator / 九字段（跨 context 交接刚需）；只审计过度触发。
- 不做第 4 个生产 Role；clarify 是 Domain 能力。
- 不把 cgame 领域规则（Unity 版本、编译命令、NGUI/AB 禁区）上移进 Core。
- 不做"去 Codex 化"：Core 的 Codex 塑形在目标 runtime 仍是 Codex 期间无害；唯一越界的 `no-polling` 条款已并入 ITER-04 顺手处理。第二 Adapter 落地时再做 Core 三分类审计（自然映射 / 平凡满足 / 无意义）。
- 不抄 superpowers 的 9 步 checklist、Visual Companion、caveman 的风格清单与关键词机制。
- 不预排 xlua-hotfix / runtime-log-diagnosis。

## 7. 与 1.0.0 / SH3 的映射

| 1.0.0 门槛（evolution.md §5） | 本路线图对应 |
| --- | --- |
| Lean Hybrid 快速路径保持可用 | ITER-03 / ITER-04 强化默认轻路径 |
| 真实任务实际启动并行并完成聚合 | ITER-07 |
| 非 Direct objective 无 Human 搬运自动到 goal_complete | 已有（0.1.12/0.1.17）；ITER-03 不回退该能力 |
| SH3：自身使用 Managed Parallel 完成非平凡升级 | ITER-05 + ITER-06 + ITER-07 的组合是最近路径 |

## 8. Human 决策记录（决策索引）

> 本节汇总本次迭代的 Human 决策，作为**索引**帮助 Reviewer 快速定位"哪些方向是 Human 已批准的"。本节不覆盖各 owner 文件的权威：`docs/architecture/evolution.md` 是版本、当前主线与 breaking change 的权威；Core、Artifact Protocol、各 Adapter 各自拥有其规范边界；历史 Review 与 Git preimage 是事实记录。本节与上述文件冲突时，**以各 owner 文件与 Git 事实为准**，并把相应决策同步到对应 owner 文件；历史 finding 通过追加更正保留，不改写为"误报"。

### 8.1 路线方向决策（2026-07-24）

1. ~~`S0 Sacha Direct` 的新名称~~ → **已定：`D0 Sacha Direct`**。
2. ~~ITER-04 的 L-Profile 瘦身方向~~ → **已定：删除独立 L-Profile 表格**，L0/L1→V0/V1+Executor 自查，L2→Reviewer Gate，L3→check-level human overlay（脱离 L 系列）。
3. ~~批次 0 是否作为 `0.1.19` 第一批启动~~ → **已定：批次 0 先行实施**。
4. ~~clarify 的承载位置~~ → **已定：塞进 sacha `skills/clarify`**（explicit-only 非生产 Role；原"通用 provider"方向经 Human 改判否决）。
5. ~~批次 0+1 打包还是分开~~ → **已定：批次 0 一起 → ITER-03 → ITER-04 单独**（breaking change 单飞）。
6. ~~Spec 还是 Plan 作跨 context 交接文档~~ → **已定：Spec 语义**——权威段（目标/Scope/Non-goals/冻结决策/验收/Entry Condition，偏移需重新授权）+ 推荐段（实现步骤建议，可被实施事实修正，冲突以权威段为准）；术语统一叫 Spec。
7. ~~Claude Code Adapter 是否加入迭代~~ → **已定：加入（ITER-11）**，当前正用 Claude Code 开发，是 evolution §7 Portability 首次落地；排在 ITER-04 Core 瘦身后。

### 8.2 clarify 与决策持久化决策（2026-07-24，对齐 grill/brainstorm 后）

8. ~~clarify 要不要独立 decisions 文件~~ → **已定：要**——时序上 clarify 阶段 spec.md 尚未诞生，已锁定决策必须先落在先于 spec 的载体。术语→`docs/CONTEXT.md`（纯 glossary，项目级）；普通决策→`docs/plans/<需求>/decisions.md`（需求级，与 spec.md 同处）；难逆决策→`docs/adr/`（项目级永久）。
9. ~~决策摘要/决策文件分级~~ → **已定：决策一锁定即原子落盘，不分轮数轻重**——Codex 窗口小易压缩，"轻量只给摘要"在易压缩环境会丢，任何锁定决策都立即落盘。
10. ~~提问节奏~~ → **已定：frontier 按轮**——前置已决的问题当轮可并列摆出（不是问卷轰炸），前置未决归后轮；先 breadth-first 铺开再深问（吸收 mattpocock batch-grill-me，取代旧"一次只问一个"）。
11. ~~no-fog 早退~~ → **已定：breadth-first 扫完无实质迷雾（无"无法精确表述的开放问题"）即停止拷打**，不为走完流程继续问。

### 8.3 GPT5.6 review 拍板项（2026-07-26）

12. ~~B1-02 Contract Version~~ → **已定：升 2，不写 migration 对照**——目前无消费方用到旧 L0～L3，为不存在的迁移对象写对照是过度复杂。Workflow Contract 升 2（删 L-Profile 是 breaking）；Artifact Protocol 维持 1（九字段未动）；两个 Adapter 头部 `Core Contract Version` 同步升 2。
13. ~~B2-02 clarify 入口~~ → **已定：双入口**——Human 显式调用 + Planner Gate 开启且输入模糊时 Planner 触发。Planner Gate 由当前承载 Intake/Route 的生产 Role（默认 Executor）按 §5.1 事实判断。`allow_implicit_invocation: false` 只禁止"看到词就自动触发"，不禁止这两个明确入口。
14. ~~B2-03 clarify 写入边界~~ → **已定：写 decisions/CONTEXT/ADR 不逐条询问**——是 clarify 职责内的澄清产出，非扩大授权、非第二权威；spec.md 才是最终拍板权威，decisions.md 是 spec 的输入证据。
15. ~~C-01 decisions.md 状态~~ → **已定：只放已确认决策**——待澄清项不落盘，交 Planner 记入 spec 待澄清/未决段或直接问用户（澄清产出多，不形式主义全落盘）。
16. ~~C-03 fact subagent~~ → **已定：保留**——配只读/查完即弃/谁启动谁收的简化规则；stale/冲突结果丢弃（Codex 上下文小，clarify 当前 context 直查更快撑满）。

### 8.4 归属澄清

- codex adapter 的歧义区改"只问用户偏好"（B1-05）与 spawn_agent 模型能力更正（B3-03）是 **Human 授意 Codex 修复**，非 GPT5.6 reviewer 所改；早期 commit message 误写为 reviewer 修复，以本节为准。
- B3-03 经核对 adapter §2.1.1 早已写对（spawn_agent 支持 model/reasoning_effort），review 该条属误报。

### 8.5 仍 Open（需真实运行时证据，非本节能关闭）

- B2-05 真实 capability capsule 消费；
- B3-05 真实并行（Claude Code / Codex 各侧）；
- G-01 各批次 review 结论落成可审计 Artifact（现为 subagent 会话 + commit message）。

---

## 附录 A：关键证据——Codex 会话 `019f8437-460e-7a10-928d-b8fcd01a82d3`

> 用途：本附录记录 ITER-05（结构化能力消费）的核心证据，供后续 Codex 独立核查时无需重新翻会话原文即可理解。

### A.1 会话基本信息

| 项 | 值 |
| --- | --- |
| Session ID | `019f8437-460e-7a10-928d-b8fcd01a82d3` |
| 日期 | 2026-07-21（rollout 起于 18:27:30） |
| rollout 文件 | `C:\Users\<user>\.codex\sessions\2026\07\21\rollout-2026-07-21T18-27-30-019f8437-460e-7a10-928d-b8fcd01a82d3.jsonl` |
| 规模 | 1907 行 JSONL；261 个工具调用 |
| 工作区 | `E:\MagicDawn\CGameEditorProject\LookDevProject`（引擎编辑器项目） |

### A.2 用户任务（引擎渲染源码调查）

同一用户连续提出三个只读调查问题，均为魔改 Unity 引擎的渲染/光照烘焙源码：

1. Dawn 烘焙后 **LightProbe 数据存在哪**、`DAWN_CODM` 宏控制的分支在做什么、数据怎么读；
2. `RebuildLightingDataAsset` 的**完整调用顺序**（从烘焙内部状态还原调用链）；
3. 函数 `static bool ConvertLightProbetAsset(Scene, DawnBakeResultAsset, LightProbes, bool)` 是否被某个提交**在 `DAWN_CODM` 分支内改动过**（查提交历史与当前生效路径是否一致）。

这三个问题的共同点：**纯调查、不改代码、需要先定位源码与宏分支的真实流向**——正是 `code-discovery` 类能力的典型适用场景。

### A.3 观察到的行为

助手在每一轮调查前都以自然语言声明要先走 cgame-unity 能力，例如（原文摘录）：

> "先调用 `cgame-unity:code-discovery` 只读定位 Dawn 烘焙后与 LightProbe 存储相关的源码，再逐步追查 `DAWN_CODM` 宏的分支与数据流路径；**全程只读，不修改代码**。先确认项目规则与 Skill 约束。"

并在后续轮次继续使用 `code-discovery` 只读核对 `RebuildLightingDataAsset` 调用点、`DAWN_CODM` 分支的可用性、提交历史的真实生效路径。

### A.4 关键数据：能力"被提及"与"被结构化调用"的落差

| 指标 | 数值 | 说明 |
| --- | --- | --- |
| 助手**自然语言提及** `cgame-unity:*` 能力 | code-discovery ×27、project-inspect ×12、change-guard ×12、change-review ×12、build-verify ×12 | 以"先调用 … 只读定位"形式出现的**意图声明** |
| 工具调用总数 | 261 | 全部为实际执行的工具 |
| 其中可识别的 **Skill 形式化调用** | 0 | 工具分布为 `manage_editor`×14、`eval_cs`×10、`refresh`×4、`get_compile_errors`×3、`read_thread`×3、`shell_command`×3、`ping`×2、`wait`×1、`view_image`×1，**无一条是 `cgame-unity:*` 的 Skill/能力调用** |

（注：实际执行的工具是会话环境提供的编辑器/构建工具；`build-verify` 是 cgame-**engine** 侧的构建能力，本会话属 cgame-**unity** 消费场景，出现的是 `get_compile_errors` 等环境工具而非 cgame-engine 能力调用。）

### A.5 结论与对 ITER-05 的意义

- **正向证据**：`code-discovery` 的**领域纪律被真实遵循**了——助手确实"先只读定位、不改代码、先确认项目规则"。说明 cgame-unity 能力的**价值主张成立**，方向正确。
- **暴露的缺口**：这种遵循**只靠"环境注入 + 模型自觉声明"**，没有任何"读 confirmed Binding → 按 load policy 调用 → 返回证据胶囊（status / facts_or_findings / validation / gaps / evidence_locators）"的**可核对结构化轨迹**。27 次提及、0 次形式化调用，证明"能力被使用"目前不可独立核查。
- **ITER-05 的目标**正是把 A.3 那种"嘴上说要遵守 code-discovery"变成可核对消费：Planner/Executor/Reviewer 调用能力时，留下 capability id + load policy + 结构化证据胶囊的轨迹，使"用了哪个能力、按什么策略、产出了什么证据"可被独立复核，而不是依赖助手自述。
