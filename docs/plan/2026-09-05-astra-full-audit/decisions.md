# Astra 适配与全仓改进：接续记录

> 文档身份：插件开发使用，仅用于本任务的规划与恢复，不进入发布插件。
> 当前状态：用户已批准 [执行 Spec](spec.md)，源码交付完成；独立复核 Accepted with follow-up，详见 [实施记录](execution-report.md)。

## 目标与来源

用户要求全量评估 SachaOrchestra 的规则、脚本和接入，以适配 Astra，并判断既有检查与协调规则是否需要简化。模型路由与接入只是其中一部分，不能把范围缩成只改 Codex 适配器。

- 原任务：[核查Astra与仓库适配](https://chatgpt.com/c/6a9b2e1a-2b28-83e9-807d-ea43f354e2a8)。接手时会话读取接口返回 idle，网页末轮显示“已停止思考”。
- 原报告：[sacha-full-audit-2026-09-05.md](sacha-full-audit-2026-09-05.md)。包含 F01–F29、R01–R55 和 288 个跟踪文件清单。
- 当前任务：`01a0705c-cc57-7c11-9d00-fdea64e1edad`；用户在此明确要求把任务与文档接手过来。
- 报告从本任务已经读取的原文预览恢复为 Markdown。正文、表格、链接与附录已保存，排版不保证与原附件逐字节相同。报告中已有结论不因保存到仓库而升级为本地复测结果。

## 用户已确认的决定

以下取自原会话用户消息；报告中的建议与这些决定冲突时，以用户决定为准。

1. 范围是全仓规则与实现评估，接入、模型路由和简化都是其中的专题。
2. 参考 Astra 官方迁移指南和新的最佳实践；将 `astra_medium` 纳入方案，考虑大工程中需要联合理解多个模块的情况。
3. 对 `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md` 的要求原文是：“去掉v1的支持 只留下v2 不预设fallback方案 如果检测到codex不支持v2 则报错停止”。不得沿用原报告中预设兼容回退的建议来覆盖这一要求。
4. 发起独立任务验证新 API 能力是否支持，使用 `gpt-5.6-luna`、`xhigh`。需要核对的对象是异步工具调用、运行中纠正，以及 `configuration_update` 调整推理强度；官方 API、Work 与 Codex 桌面的实际暴露和行为分别取证。
5. 计费问题精确限定为“Sol 长输入收 2 倍、Astra 不加倍”的条件，继续查官方来源；不得仅用相同 token 数的基础单价回避这个问题，也不能混用 API Key 与订阅/积分的价格。
6. 原会话最后的明确指令：“不直接改 基于你刚才那份报告 using-sacha 生成一份可用的执行spec再开始动手”。本任务承接这一顺序。既有评估报告不是已批准实施规格。

### 2026-09-05 接续确认

- 用户补充要求：“也看看还有哪些需要澄清”。只向用户提出会改变行为、范围或验收且不能从源码确认的决定。
- 用户明确选择“全部取消自动回退”：Codex 接口或所选模型不支持时均报错停止。删除现有 Luna→Sol 自动回退；不采用报告中的 Astra→Sol 预设回退。不把创建失败、忙碌、超时或结果未知转换为新模型重放。
- 用户随后明确要求 Pi 完整移除、精简关键词测试与过度展开的 Runtime 包，并把 Astra 最高自动档由 xhigh 调整为 high。该决定取代先前“保留 Pi 兼容”和预设新增 Astra 场景的方案；Luna xhigh 与 Astra medium 不变。
- 用户以“更新”确认 DSH 跟随后续明确任务指令更新基础工具集。具体方案已写入 Spec 5.4：中性继续/进度消息保持当前，明确新任务指令重算并清空临时解锁，reset 回到最近明确指令，冷恢复按原生事件顺序重放且不接纳旧指令的晚到 control 结果。该确认不扩大执行权限。
- 用户提供的[官方计费例外](https://help.openai.com/en/articles/20001415-chatgpt-rate-card-enterprise-token-based-pricing#gpt-6-astra-codex-long-context-exception)已打开核实：Astra 在 Codex 中超过 272K 输入不增加长上下文倍率，Codex 不收缓存写入费用。该页一般长上下文表为输入/缓存 2 倍、输出 1.5 倍；按其美元价目，超过阈值时 Astra/Sol 输入为 10/8、输出为 50/30（每百万 token）。此处修正原报告第 2 节和 6.6 的“没有明确豁免声明/非对称前提未确认”，原报告保留为历史评估原文。该页声明美元费率适用于相应 Enterprise 协议；不将其费率外推为用户订阅额度的具体扣减。API Key 模式仍按 API 模型页的长上下文和缓存写入条款区分。
- 已请求创建用户原先指定的独立 Luna xhigh 能力验证任务，创建返回 `client-new-thread:179ad507-9712-4132-a23b-6210c46a6936`；工作树准备完成后再记录真实任务标识，不能将该临时标识传给任务读取或等待接口。

## 接手时核实的本地事实

- 工作目录：`C:/Users/shifengzhou/Documents/SachaOrchestra`。
- 当前 Git HEAD 为 `bf44b72`，提交标题为“备份全局 Codex 规则、Skills 和本地工具”。
- 原报告声明的评估基线为 `2054b78770fd25562677a28f52ca99bf0416689b`、版本 `0.14.2`。本地 Git 对该对象返回 `fatal: bad object`，尚不能通过修订差异证明两个基线一致；本次未 fetch、切分支或改写历史。
- 当前 `EVOLUTION.md` 仍声明 release 为 `0.14.2`，待发布源码版本未开始。
- `cprobe summary plugins/sacha-orchestra/adapters/codex --json` 返回 tracked_changed=0、untracked=0、conflicted=0、whitespace.errors=0、budget.complete=true。该证据只覆盖 Codex 适配器目录。
- 当前桌面会话的 `collaboration.spawn_agent` 实际提供 `agent_type`、`task_name`、`model`、`reasoning_effort` 和 `fork_turns`，并有 `send_message`、`followup_task`、`wait_agent`、`interrupt_agent`、`list_agents`。因此 F01 的“没有 agent_type”只保留其 Work 环境适用性；不能作为当前桌面不支持该字段的证据。
- 当前 `interrupt_agent` 的工具说明是中断当前回合，代理仍可继续接收消息；不能据此声明底层写入进程已经终止。F15 仍需按实际行为核对。
- 继续规划时按原报告附录逐个读取 288 个已知文件并比较 SHA-256 前 12 位：175 个字节相同，103 个仅 CRLF/LF 差异，10 个内容变化，0 个缺失。内容变化包括 `.gitattributes`、`.gitignore`、`AGENTS.md`、`EVOLUTION.md`、`docs/release.md`、DSH `tool-surface-policy.ts` 及其测试、`generate_project_integration.py`、`tests/runtime-scenarios/README.md`、`tests/test_skill_loading.py`。此比较只说明文件与原报告清单的对应情况，不替代语义复核。
- `cprobe` 当前还发现接手前已有的生产文件未提交改动：`generate_project_integration.py`（1 行增、1 行删）、DSH `tool-surface-policy.ts`（6 行增、2 行删）及其测试（8 行增）。规划会读取这些差异，实施不得覆盖；本任务未创建这些生产改动。

## 仍需继续的工作

首先以报告为问题索引，读取各问题的当前负责文件和直接使用方，区分仍然成立、已变化与原证据不足的项目，再形成自包含执行 Spec。原报告中的 29 项建议没有整体获得实施批准，不将建议直接写入运行规则。

| 工作内容 | 报告位置 | 接续要求 |
| --- | --- | --- |
| 正确性与跨平台缺陷 | F02–F08、F29 | 核对并发原像、测试选择器、工程根、YAML、预览授权、文案过滤和模板解析；按实际入口准备复现与验收，不以原环境 117 项测试替代本地结果。 |
| Codex v2、取消与技能读取 | F01、F15、F16 | 消费用户的 v2-only 与不预设回退要求；按当前宿主字段定义适用范围。Work 能力缺口不能直接当作桌面缺口。 |
| Astra 路由与失败影响 | F13、F14、报告第 6 节 | 纳入 Astra medium；保留用户精确选型、失败影响与独立性。未核实价格、固定窗口和压缩阈值不进入默认配置。 |
| 规则与职责简化 | F09–F12、F17–F21 | 对照现行项目规则逐项说明保留、修改、删除的含义及实际使用方；会改变入口、职责、协调或验收的方案先呈现给用户，不能以自然化文案名义削弱规则。 |
| DSH 缺口 | F23–F26 | 保留在全仓范围中，核对目录截断、任务分类、状态新鲜度、轮询和无使用方界面实现；源码、构建、安装及宿主界面证据分别记录。 |
| 兼容与其他环境 | F22、F27、F28 | Pi 去留按真实使用方决定；其他运行环境的预算和历史文档单独核对。未取得删除或配置变更授权前，不执行退役或用户配置改动。 |
| 新 API 能力验证 | 用户明确请求、报告 6.5 | 保留 Luna xhigh 的精确指定。原会话可读取消息未提供该独立任务的可恢复标识和最终原始证据；不能认定已验证，也不能宣称原任务从未派发。新验证应明确目标宿主并记录实际接口与结果。 |
| 长输入计费核查 | 用户明确请求、报告 6.6 | 查阅当前官方完整页面，分清适用模型、计费模式、阈值和倍率；未确认处继续标为未确认。 |

## 批准前的源码复核与处置依据

下表是形成 Spec 所需的规划事实与建议，不构成实施批准。源码行号只对应此次读取的工作区；实施前应核对仍有效的内容。

| 发现 | 当前判断与建议 | 直接负责位置 |
| --- | --- | --- |
| F01 | Work 的缺字段结论不能外推桌面。按当前 v2 工具结构验证组合，缺字段或能力类型时停止，不安排通用代理替代。当前固定模型 DeepSeek 角色禁止覆盖型号；包含强行覆盖要求的旧矩阵包按 Spec 5.9 整包删除。 | Codex `runtime-adapter.md:35-56,174-204`；当前 `collaboration.spawn_agent` 说明；Spec 5.9 |
| F02 | 批次统一原像检查后仍直接逐项替换，缺陷路径成立。每次替换前复查当前目标，保留既有补偿中“不覆盖再次改变的目标”规则；临时文件在替换成功前不能从清理集合移除。该修法不宣称跨进程原子 CAS。 | `setup_agents.py:466-486,499-543`；`tests/test_setup_agents.py` |
| F03 | `.js` 未进入机械文件集合，且生产 asset 未映射到已有测试。另补两个被实际消费的 Markdown 模板映射；不改 JS 本体。 | `scripts/release.py:218-284`；`tests/test_release.py` |
| F04 | 候选 root 无条件 casefold 仍会合并大小写不同的 POSIX 路径。使用宿主路径语义比较，原始候选值仍供消歧；单机证据不外推跨平台。 | `resolve_provider_queries.py:238-265`；`tests/test_skill_loading.py` |
| F05 | `_parse_skill_identity` 仍逐行正则提取，合法块标量会被读成 `|`。采用安全 YAML 解析并验证 mapping、字符串和身份；当前 Python 可发现 PyYAML，缺依赖时明确拒绝，不自动安装。 | `generate_project_integration.py:1101-1117`；setup-project Skill；`tests/test_skill_loading.py` |
| F06 | `_authorize` 把策略资格与写入确认混在一起，dry-run 也被拦截。保留始终适用的策略/触发检查，实际写入时才核对写授权；project-context 的覆盖确认同样移到写入处。 | `generate_project_document.py:991-1017,1675-1721`；`tests/test_document_project.py` |
| F07 | 普通 `spec.md`、cache 目录和 UUID 的词法禁用仍会误拒合法内容。删除这些已知误拒项，保留文件操作层的目标、原像和路径保护；不新增假装理解正文的正则。 | `generate_project_document.py:96-115,690-703,1043-1055`；`tests/test_document_project.py` |
| F08 | 两个实际生成器对同一模板目录采用深浅不同的解析，文档生成路径可能遇到缺键/错误类型。提取发布目录内的单一模板目录解析器并由两者使用；旧结构化正文输入仍有直接消费者，保留，不借此次修复退役。 | `generate_project_integration.py:304-454`；`generate_project_document.py:513-652`；现有两组入口测试 |
| F09 | 入口一次性选择具有明确产品依据；Spec 保留现行早期选择，不采用先完成领域调查再询问的建议。同一目标的明确接受继续有效，用户反问时先核对决定所需事实。 | `core/intake-contract.md:19-24,34-43`；using-sacha；专用入口场景 |
| F10 | Planner 固定三遍及失败全部重来确实存在。建议保留格式、来源、项目语境全部检查目标，取消固定轮次，修订后复查受影响部分。 | `skills/planner/SKILL.md:24-29` |
| F11 | 所有未收口项均需进入 Explore 的要求确实存在。建议可直接确认的小事实由 Planner 核对，需要持续探索或关键用户决定时才进入 Explore；须同步设计和工作流，不能先绕过现行规则。 | Planner `SKILL.md:16-17`；Workflow `:74,96`；`PLUGIN_DESIGN.md` |
| F12 | 首次等待前必须创建至少两个代理确实存在；当前合同要求九维评估，但没有要求向用户输出九列表格。建议取消数量硬约束与无收益的全套重评估，保留输入自足、依赖、写入隔离、独立性和完成检查。 | `core/coordination-contract.md:19-21,29-49`；设计中的并行/串行分支 |
| F13–F14 | 以具体破坏性后果判断失败影响，保留 Luna/Sol；新增 Astra medium 用于需要联合持有较大有效上下文的工作，Astra high 用于困难/关键推理。所有自动回退按用户新决定删除。 | Codex Adapter 第 3 节；模型路由专用场景；已核实官方计费与迁移资料 |
| F15 | 中断回合不等于代理或底层写入进程已终止。接管前分别核对；证据不足只暂停有双写风险部分，不重复创建替代写入者。 | Codex Adapter `:54,206-208`；当前 interrupt 工具说明 |
| F16 | 原报告的资源式 Skill 来自 Work，当前桌面仅有已确认的本地 Skill 路线。保留唯一身份及真实可读性；不为了未验证的资源提供方预建传输或 fallback。资源式 Skill 扩展列后续项。 | Codex Adapter `:167-172`；当前 Skill catalog |
| F17 | “方案阶段必须给精确行数”的强结论不成立：现行规则已明确允许估算及收敛条件。遵守现有表达要求即可，无需为此修改全局规则或删除信息。 | `core/human-interaction-contract.md:17`；全局规则中的方案表达要求 |
| F18 | 共享术语全文双向维护确实存在。建议改为插件内术语合同单一维护，开发侧保留链接、使用方及开发专用定义；术语含义不变，关联开发规则同次调整。 | `AGENTS.md:19,25,73-81,86-87`；`docs/CONTEXT.md`；`docs/AGENTS.md`；设计入口 |
| F19 | 不按文档字数安排全仓重写。只消除已确认的责任重复，并把“读取新的负责文件”与“新增职责/负责位置转移”分开；其余授权、安全、证据和发布边界保留。 | `AGENTS.md:85-100`；既有 sacha-doc-governance |
| F20 | Assurance 与 Reviewer 已要求只重跑能改变裁决的检查。对齐顶层设计中的宽泛措辞，复用仍有效的原始证据；行为变化仍需要真实场景，不能改成仅静态验收。 | Assurance `:12-20`；Reviewer `:20,26,38-40`；设计 `:177,209` |
| F21 | 已逐包核对 22 个场景，计划删除 10 个、收缩 3 个、保留 9 个；取消预设新增 Astra 场景及逐型号/角色/状态运行矩阵。明确路径和案例依据见 Spec 5.9；保留不等于每次都运行。 | `tests/runtime-scenarios/README.md`；各 pack 的 task/oracle；Spec 5.9 |
| F22 | 用户现已明确完整退役：删除 3 个生产文件、3 个专用测试、生成器字段/解析/渲染/结果/CLI 和现行说明；不留兼容路线。其他项目旧受管段只在将来正常获授权 setup 事务中移除，本次不批量改写。 | Spec 5.7 的精确文件与退役行为 |
| F23 | 256 项截断、忽略同名更新/删除、感叹句误判仍存在。用户已确认跟随后续明确任务指令更新基础工具集；初始与追加路径的总数截断都需移除，单次返回边界保留。完整动态目录刷新受宿主 API 限制，列为后续，不宣称本次全部解决。 | `tool-surface-policy.ts:215-245,313-375,719-725,973-985`；对应测试 |
| F24 | 保留仍有具体宿主依据的三层限制；删除 README 中“一次性授权 web Profile”的历史句。Codex 的无 fallback 决定不扩大为删除 DSH 的失败关闭保护。 | Companion README `:137`；`tool-surface-policy.ts:934-963` |
| F25 | 历史记录会永久触发热轮询，网络错误未标旧快照，新 Executor 阶段仍保留旧 accepted。建议按真实活跃/可见状态轮询，旧数据明确标记；复用已有 `scope_revision` 输入并在 review/evidence 归一化结果中保留关联，无法关联时不显示为当前通过。暂不增加无实测依据的增量缓存。 | `activity-monitor.ts:9-47`；`types.ts:46-100`；`normalize.ts:153-165`；`snapshot.ts:77-103` |
| F26 | move/resize 函数未接 UI，相关测试只验证函数，数个 CSS class 无使用方。建议清理孤立实现，不新增拖动/缩放产品能力。 | `panel-geometry.ts:142-169`；`panel-geometry.spec.ts`；`ActivityPanel.tsx`；对应 CSS |
| F27 | Cursor 内置具体套餐/价格/告警和降级假设；建议取消未经用户配置确认的预算默认，保留宿主本地参数与实际能力核对。Claude 按已有能力前置处理，不借 Astra 改写其生态。跨宿主实际行为仍分开验证。 | Cursor Adapter `:54-80`；Claude Adapter `:38-44,60-72` |
| F28 | 两份具名历史记录仍以进行中或现行实现描述旧 DSH 分包。仅增加最短历史/已取代入口，不重写冻结正文。 | `2026-08-28-runtime-capability-followup/feature.md`；`2026-08-28-runtime-surface-and-dsh-subagents/design.md` |
| F29 | 跨平台固定错误消息和 DSH `0.1.0` 固定断言仍需修正；保留不安全路径拒绝，分开原生/外来路径预期。只验证机器版本身份和实际打包结果，不解析 README 文字证明版本。 | `tests/test_document_project.py:1315-1331`；`tests/test_setup_project.py`；`tests/validate_dsh_companion.py:67-81` |

### DSH 目录刷新的宿主依赖

已读取本地 `C:/Users/shifengzhou/Documents/deepseek-harness/packages/core/tools/src/index.ts:1130-1192,1228-1236` 对应的调查片段：`schemas()` 是 global view；`schemas(agent)` 是经过 restriction 的当前有效 scoped view。公开 `tools/change` 事件没有 layer/change payload，注册、注销和 restriction 变化都会触发。原报告提出的完整动态刷新不能仅靠现有无参调用实现。

规划约束：不能拿 global view 替换整个 Root 目录，也不能为了刷新而在异步步骤中解除限制。Spec 只修复初始/追加路径的总数截断、中文判定和明确指令切换；同名更新、删除和任意 ancestor scoped 动态变化的完整一致性保留为后续。没有可靠来源时不新增多层缓存或猜测删除，宿主源码修改不在本任务授权中。

### 澄清与规格状态

已消费用户对 DSH 更新方式的明确选择；当前没有需要再次询问的同一行为歧义。其余实质方案集中在 Spec 中供整体审阅，不能把 DSH 单项确认当作整份 Spec 批准。

用户已经明确 Pi 全量退役，已纳入 Spec；修改宿主源码、自动安装依赖、修改全局配置或跨宿主部署仍不自行加入。新提出的具体测试清理清单见 Spec 5.8–5.9。

以上为批准前的规划记录。用户随后明确批准，实施事实与验证结果统一见 execution-report.md；未提交、发布、安装或修改用户全局配置。

## 当前交付与核对范围

已在本目录生成 [spec.md](spec.md)，按项目既有格式给出目标、范围、项目事实与技术决定、依赖、逐文件实施方案、验收、失败保护及未验证项，并覆盖 F01–F29 的处理、保留或后续处置。

初稿已完成格式、来源与项目语境回读，并解决共享解析器接口和 dry-run 新输出歧义。初稿的 52 个路径核查结果只属于当时版本；本次 Pi/测试精简修订另核对删除清单和引用，不复用旧计数声称已检查新范围。所有文档核对均不证明实现、测试或运行通过。

独立 API 验证请求仍只有创建队列标识，尚未取得真实任务标识或完成结果；不重复创建，不把排队视为已运行。该结果不构成本次未接入新 API 的 Spec 阻塞，也不被计入任何通过项。

## 测试精简修订的直接范围

- Pi：6 个文件整组删除，两个 setup-project Pi 测试方法删除；旧参数由标准 CLI 拒绝，旧项目文件不在本次仓库操作中被改写。不保留永久退役名单、兼容探针或新 Pi 测试。
- Runtime 场景：实施前确认 10 个整包为 56 个受管文件，另有 6 个多余 fixture；当时范围干净。批准后已精确删除这些 62 文件，现存 12 包，最终证据见实施记录。
- 关键词测试：静态调查预计删除或替换约 55–75 条固定文案断言；机器字段、实际命令 tuple、原始用户字节、原像/回滚和真实入口结果不归入普通关键词锁定。纯文本例外仅限极少数有实际生产消费者的重要控制标记，不建白名单机制。
- tests/test_runtime_scenario_verifiers.py 删除两个 bundled 接受/拒绝综合方法、自填 Runtime result 构造与专用 helpers；保留真实 CLI/UTF-8 缺陷探针的一个直接用例。
- 发布选测需消费真实暂存 D 状态，不能用 blob 解码失败或工作区缺文件猜删除；对仍存活的测试消费者继续选测，不为删除的 Pi 入口留下永久名字特判。
- 本次不新增 Runtime 包，不强制 A/B 成本对照或逐档模型验证。真实任务产生的参数与遥测可直接记录；没有明确案例的分支不为了覆盖率扩写。
- 原报告维持其评估当日的 288 文件、22 包和历史建议；当前处置以修订 Spec 为准，不改写原报告伪装成它当时已经得出新的决定。
