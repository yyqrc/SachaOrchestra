# Sacha Orchestra 项目规则

> 文档身份：插件开发使用；不进入发布插件。

## Workspace 事实

- 本文件是 Project `AGENTS.md`；Global AGENTS 的安全/授权/证据/Git/用户改动保护仍生效。
- 本文件、根目录 `README.md`、`PLUGIN_DESIGN.md`、`EVOLUTION.md`、`.agents/skills/**` 与 `docs/**` 供插件开发使用，不进入发布插件。
- 本 workspace 的 repo-local Agent Plugin marketplace 只有 `plugins/sacha-orchestra`；独立构建和安装的 DSH companion plugin 位于 `integrations/dsh/sacha-visualizer`，不进入三个 marketplace 或 Agent Plugin 发布 `root`。
- 当前 release、当前待发布源码版本、当前 breaking boundary、成熟度和尚未实施的长期方向以 [`EVOLUTION.md`](EVOLUTION.md) 为权威；现行架构和流程仍由 `PLUGIN_DESIGN.md` 及对应 Runtime Owner 定义。manifest 记录当前源码版本，tag 标记已经发布的版本。
- Evolution 只给版本、当前 breaking boundary、成熟度和尚未实施的方向，不授权实施。

## Owner 与直接入口

| 路径 | Owner 与用途 |
| --- | --- |
| `.agents/skills/*` | Sacha 插件自身开发、维护、评审和 Runtime 场景执行的仓库本地工作流；不进入发布插件，不拥有产品流程或 Runtime 合同 |
| `docs/AGENTS.md` | 插件开发文档子树的身份、放置、读取和历史 Artifact 处理规则；不定义 Runtime 流程 |
| `docs/CONTEXT.md` | 开发控制面提炼术语与规则的统一入口及开发专用术语 Owner；完整包含插件内共享术语的同步视图，并可额外拥有仅供插件开发、维护和评审消费的术语；`PLUGIN_DESIGN.md` 引用它，发布插件不读取它 |
| `docs/release.md` | Human 显式快速发版、普通发版或安装时读取的开发期操作指南；`scripts/release.py` 仍拥有机械执行 |
| `EVOLUTION.md` | 当前 release、当前待发布源码版本、当前 breaking boundary、成熟度与尚未实施的长期方向；不复制现行架构/流程或保存版本流水账 |
| 三个 deployment manifest | 当前源码版本与部署接口元数据；根 `plugin.json` 使用 Agent Plugins 开放标准供 Cursor 等兼容 Runtime 加载 |
| `.agents/plugins/marketplace.json`、`.claude-plugin/marketplace.json`、`.cursor-plugin/marketplace.json` | 各 Runtime 的 repo-local marketplace 入口；只保存部署路由，不拥有流程语义 |
| `plugins/sacha-orchestra/core/intake-contract.md` | 入口判断、接受/拒绝、重复抑制和授权边界的规范性 contract |
| `plugins/sacha-orchestra/core/terminology-contract.md` | 多个发布插件直接消费者共同使用且不属于单一 Runtime 的提炼术语唯一 Runtime Owner；与 `docs/CONTEXT.md` 中对应的共享术语强双向同步 |
| `PLUGIN_DESIGN.md` | 与本文件并列的插件开发/评审顶层设计：完整流程骨架、Role/Skill 职责、Core owner 与自上而下变更顺序；不随插件发布，也不是 Runtime 依赖 |
| `plugins/sacha-orchestra/README.md` | 发布插件入口、最小用法与 Runtime Owner 导航；不保存顶层设计 |
| `plugins/sacha-orchestra/core/workflow-contract.md` | 唯一 Runtime 路由：Role/Gate、节点进入/退出条件和 Human 路由；沿用插件内术语合同，不定义就绪判定、模型或宿主参数 |
| `plugins/sacha-orchestra/core/human-interaction-contract.md` | Human 可见提问、进度、结果顺序与必须披露信息的规范性 contract |
| `plugins/sacha-orchestra/core/assurance-contract.md` | Review、Baseline、Outcome 与 evidence 语义 |
| `plugins/sacha-orchestra/core/coordination-contract.md` | Manager 的 assessment、拆分、依赖、readiness、route requirement、dispatch/return、identity/dedup 与 deviation 的唯一 Core owner |
| `plugins/sacha-orchestra/core/artifact-protocol.md` | Artifact 生成条件、最小内容、Spec 完成、权威关系与恢复规则的规范性 contract；术语定义归插件内术语合同 |
| `plugins/sacha-orchestra/adapters/<runtime>/runtime-adapter.md` | 单一 Runtime 的传输、自动模型/强度选择、精确调用参数、回退、恢复与验证映射；不得反向定义 Gate/就绪条件 |
| `integrations/dsh/sacha-visualizer` | DSH companion plugin 的 Host/Client 源码、构建、状态投影与界面 Owner；只观察 DSH Root Session 的 continuable direct-child 状态与 Adapter 已记录的 Sacha phase/Gate/Manager DAG/delegation/Review/Evidence 事实，不拥有 Sacha 流程或发布插件 Runtime 语义 |
| `plugins/sacha-orchestra/skills/*` | 不绑定具体 Runtime 的节点职责、局部工作流与边界；不增加流程节点，不复制 Core 判断或 Adapter 参数 |

## 文档身份与发布可达边界

- 文档作者新增或修改 Human 可读文档前，必须先根据 path 确定它供“插件开发使用”还是“插件发布使用”；一份文档只能有一种身份。
- 仓库根 `AGENTS.md`、`README.md`、`PLUGIN_DESIGN.md`、`.agents/skills/**`、`docs/**` 与 `tests/**` 内的说明只供插件开发、维护或场景评估使用，不进入发布插件，也不得成为安装后 Runtime 的依赖。
- `plugins/sacha-orchestra/**` 内的 Human 可读文档随插件发布，必须在发布 `root` 内完整提供 Runtime 所需的规则、入口和恢复语义。
- 三个部署清单都把 `plugins/sacha-orchestra` 解析为发布 `root`，因此只有该目录内的文件会随插件发布。在源码仓库中能够读取文件、打开链接或解析相对 path，并不能证明发布 `root` 外的文件在安装后仍然可达。
- 发布插件内的本地引用必须解析到发布 `root` 内，不能依赖根 `AGENTS.md`、根 `README.md`、`PLUGIN_DESIGN.md`、`docs/**`、`tests/**` 或其他发布 `root` 外文件承载运行语义。
- 如果安装后的 Runtime 需要使用插件开发文档中的决定，修改者必须把该决定写入插件内对应的 Core、Skill 或 Adapter Owner，并同步直接消费者；不得用指向插件开发文档的链接代替插件内定义。
- Reviewer 声明发布文档自包含前，必须根据部署清单确认发布 `root`，检查本次新增或修改的本地引用都在该 `root` 内可达，并运行插件校验。该校验只能证明所覆盖的源码和静态结构；安装后是否可达，还需要安装证据或包一致性证据。

## 读取路由

开发者或 Reviewer 讨论、调查或修改文档时，按以下规则选择读取范围：

- 先根据目标 path、文档身份和直接消费者选择主要工作面。根 `AGENTS.md`、根 `README.md`、`PLUGIN_DESIGN.md`、`EVOLUTION.md`、`docs/**` 与 `tests/**` 属于插件开发控制面，优先检查插件开发行为、维护归属、读取路线和开发证据；`plugins/sacha-orchestra/README.md`、`core/**`、`adapters/**` 与 `skills/**` 属于发布插件 Runtime，优先检查安装后的流程、Runtime Owner、直接消费者和行为证据。
- 同一任务同时涉及开发控制面和发布 Runtime 时，必须先分别说明开发决定以及需要同步到 Runtime 的内容；只有直接消费者、发布可达性或真实行为验证需要时才跨越两面。不得用开发文档对自身的描述评判 Runtime 文档，也不得用 Runtime 的局部流程扩大插件开发文档的 Scope。
- 新增、移动、审查或维护 `docs/**` 前，必须先读 `docs/AGENTS.md`，再根据目标文档的身份只读当前 Owner 或确切相关的历史 Artifact；不得遍历没有消费者的文档树。
- 任务涉及已提炼术语或规则时，必须先读 `docs/CONTEXT.md`，再核对其中列出的插件内定义。发布插件不得引用 `docs/CONTEXT.md`。
- 讨论或修改入口、高层流程或 Role/Skill 职责时，必须在读完适用的术语定义后读取根 `PLUGIN_DESIGN.md`，再读取受影响节点对应的 Intake、Workflow、Human Interaction、Assurance、Coordination、Artifact 或目标 Skill。只查询局部触发条件或流程且不涉及已提炼术语时，只需读取目标 `SKILL.md` 和元数据。
- 使用 `.agents/skills/*` 时，必须先按该 Skill 的 Scope 读取本文件和现行 Owner，并只把它作为插件开发工作流；开发 Skill 不得承载安装后 Runtime 语义，也不得扩大产品 Skill 的职责。
- Runtime 局部任务只读目标 Adapter；只有任务确实涉及 Core 或多个 Runtime 时，才在 Scope 内比较相应内容。
- 当前执行者在新 task 或协作界面继续同一 Runtime 的局部迭代时，必须先读目标 Adapter、已批准 Spec、专用 Runtime 场景和本次有界改动。只有这些现行来源不足以恢复状态时才查询 MEMORY 或 rollout；完整旧对话、完整 MEMORY 和冻结历史计划都不是默认输入。
- 处理 release、`1.0.0`、尚未实施的长期方向或 Core breaking boundary 时，必须读取 Evolution。显式快速发版、普通发版或安装还要读取 `docs/release.md`；处理现行架构、Manager/并行或产品流程时，必须先读 `PLUGIN_DESIGN.md`。只有改变 Evolution 独占的内容时才修改 Evolution。
- Evolution 只用于读取当前 release、当前待发布源码版本、当前 breaking boundary、成熟度和尚未实施的长期方向。历史事实必须按具名版本、Spec、Report、Review 或 Git 查询，不从 Evolution 恢复旧机制。
- 普通实施不遍历历史计划目录寻找额外规则。现行内容与当前 Owner 冲突时，删除副本或改成指向 Owner 的引用；冻结历史文档只有在仍会误导当前操作时，才增加最短的“已取代”入口。
- Project Integration 和 Domain Skill 归各自项目所有；不得把项目特定命令或证据规则导入此 Core。

## 普通插件开发（Direct）

- 普通 plugin `change`、`build`、`fix`、`sync` 或 `iterate` 请求默认在当前 task 直接完成；不得仅因为文件多、耗时长或验证步骤多而单独打开 Gate。
- Direct Scope 由用户的语义目标和明确约束决定。预计会修改的文件不是完整 allowlist；只有用户或已批准 Spec 明确给出 exact file allowlist 时，文件列表才构成硬边界。
- 当前 Executor 为完成同一目标，可以修改直接必需的源码、文档、断言和验证配置。同一 Scope 内发现漏改或任何失败时，直接修复并重新验证，不创建额外流程。
- 如果工作中出现实质新方案、breaking contract/schema、权限或安全变化、持久数据变化、验收变化、未授权外部动作，或者无法完整验证，必须停止受影响的写入并按三个 Gate 处理。
- 每次只验证当前 Runtime 和交付层。除非 Human 明确要求跨运行环境验收，否则其他 Runtime 在安装、发现、行为或证据上的缺口只作为后续反馈，不扩大或阻塞本次源码发布。
- Review 只拦截会导致错误交付的关键问题。不会阻塞发布的证据缺口或改进项使用 `Accepted with follow-up`；不追求覆盖全部历史或所有 Runtime，也不把“还可以补充证据”升级为 `Needs Fix`。

## 术语提炼与同步

- 当前执行者发现同词多义、同义多名、概念误合并，或者代码、合同与文档定义冲突时，必须先只读核对现行 Owner、直接消费者、真实行为和冲突内容。事实足以消除歧义时，在当前授权和 Scope 内直接统一；只有不同解释会改变产品面、Scope、验收、授权或破坏性边界时，才交给 Human 决定。该调查保持 Direct，不打开 Explore、Planner Gate 或 Manager Gate。
- 同一术语或流程判断被多个发布插件直接消费者重复使用、已经产生歧义或造成真实失败时，当前执行者必须在插件内术语合同中提炼该术语，并在 `docs/CONTEXT.md` 保存开发侧同步视图、直接消费者和可证伪方式。术语合同只定义含义与边界，具体进入条件和动作仍由相应 Core 定义，其他发布插件下游只保留映射。
- 只有被多个开发控制面直接消费者共同使用的术语才由 `docs/CONTEXT.md` 拥有，不得为了让两边集合一致而把它写入术语合同。没有第二个现行消费者时，当前任务语义必须留在 Spec 或决定记录；只有存在跨任务项目消费者时，才能列为 `project-context` 候选。提炼术语只能命名已有判断；如果要改变判断，必须按新增或扩展规则处理。没有机器消费者和实际判断需要时，不得把术语升级为字段、状态、枚举、Artifact、必填格式或产品面。
- 修改者新增、改名、改变语义或边界，或者删除插件内共享术语与规则时，必须在同一次修改中更新 `docs/CONTEXT.md`、插件内术语合同、相应 Core 和受影响映射。两边不一致时，以插件内术语合同恢复 Runtime 词义，以相应 Core 恢复流程。
- 修改者处理只供开发控制面使用的术语时，只更新 `docs/CONTEXT.md` 和开发侧直接消费者；如果该术语开始被多个发布插件直接消费者使用，必须先提升到术语合同并完成共享同步。同步完成后才能使用受影响术语，本次修改也只有到这一步才算完成。

## 内容归属与信息密度（必须遵守）

### 内容放在哪里

- Core、Adapter、Skill 和开发控制文档都必须遵守 Global AGENTS 的【Human 表达与展示】；编写、迁移、精简或审查这些文本时使用仓库内 `$sacha-doc-governance`，不得给已定义的正式标识另加语言豁免。
- 每项事实只能有一个 Owner，以下归属均为硬性边界：项目事实写在本文件；完整顶层设计写在 `PLUGIN_DESIGN.md`；被多个发布插件直接消费者共同使用且不属于单一 Runtime 的提炼术语写在插件内术语合同；只被多个开发控制面直接消费者共同使用的提炼术语写在 `docs/CONTEXT.md`；流程判断写在相应 Core；Role 内部流程写在 Skill；单一 Runtime 的传输、模型和恢复写在 Adapter。
- `docs/CONTEXT.md` 必须完整保存插件内共享术语的开发侧同步视图，也可以拥有开发专用术语；`PLUGIN_DESIGN.md` 必须引用它。插件内下游只能引用插件内 Owner，或者保留自身需要的映射。
- `PLUGIN_DESIGN.md` 是插件开发和评审使用的唯一顶层设计 Owner，完整保存流程骨架和 Role/Skill 职责；它与根 `AGENTS.md` 同属开发控制面，不进入发布插件，也不能成为安装后 Runtime 的依赖，完整设计只能由插件开发者、Reviewer 和场景评估者读取。Workflow Contract 唯一且完整地定义 Runtime 路由，并沿用插件内术语合同；其他 Core 只定义各自的局部判断，Skill 只保存自身职责、流程和边界，Adapter 只负责传输；Core、Skill 和 Adapter 不得要求消费者读取或复制完整设计。
- Manager 协调闭环按层次分工：`PLUGIN_DESIGN.md` 必须画出完整闭环；Workflow 必须只决定何时进入闭环以及返回哪个调用节点；Coordination 必须定义评估、依赖、就绪判定、派发、等待和返回；Manager Skill 必须调用并消费这些规则；Adapter 必须组装 Runtime 参数。某一层越权时，必须删除越权副本，不得再补充解释维持重复。
- Codex Adapter 是自动模型组合、选择条件、`agent_type/model/reasoning_effort/fork_turns` 和回退的唯一 Owner。顶层设计、Core、Skill、README 和通用历史说明不得复制当前型号表。Markdown 中的映射必须由 Owner 复核并用 Runtime 场景验证，不得用正则或固定标记测试锁定文字；将来如果改为机器可读配置，必须测试真实配置消费者，而不是测试说明文本。
- 开发文档和发布插件使用 `base`、`root`、`path` 或 `reference` 时，必须分别沿用 `docs/CONTEXT.md` 中的开发定义和插件内术语合同中的 Runtime 定义。修改已有内容时必须消除混用，不得再创造 `locator` 作为同义术语。
- 显式 setup 必须只管理对应配置；根 `README.md` 必须只保留仓库导航，`plugins/sacha-orchestra/README.md` 必须只保留入口、最小用法和 Runtime Owner 导航，历史记录和版本迁移说明必须写入具名文档。Adapter、Skill、顶层设计和 Runtime 路由的归属沿用本文件的“Owner 与直接入口”表。
- Planner、Executor 和 Reviewer 三个 Role Skill 必须分别写清自己的职责、工作流和边界。修改这些 Skill 前，修改者必须先确认变化仍在对应 Role 已声明的输入、输出和禁止边界内；如果要新增职责、输出类型、调用 Owner 或跨节点路线，必须先按高层流程变化处理，不得直接给 Skill 增加一步。
- Manager、Explore、Feedback、using-sacha、document-project 等控制或支持 Skill 必须只实现 `PLUGIN_DESIGN.md` 中对应的节点或闭环。roadmap、setup-project、setup-agents 等主流程外 Skill 必须写清功能、概略工作流和副作用边界。迭代必须只修改已声明功能内的做法；新增功能、触发方式、外部副作用或跨节点接管时，必须按顶层设计变化处理，不得混入局部修复。

### 修改顺序与产品边界

- Human 明确确认高层流程的节点、先后关系、分支、Role/Skill 职责或回路变化后，必须按 `需求不变量 → PLUGIN_DESIGN.md → Workflow/对应 Core → 节点 Skill/Adapter 消费者 → Evolution（若改变长期或 breaking boundary）` 的顺序修改。只改变节点内部判断或职责内流程而不影响顶层设计时，必须直接修改唯一 Core、Adapter 或 Skill Owner，不得为了“保持同步”修改设计文档。
- 新机制替代旧机制后，必须删除现行内容中的旧副本并引用当前 Owner。冻结历史文档必须只在仍会误导当前操作时保留最短的“已取代”入口；Evolution 不得新增历史表格行或版本章节。
- 新增或扩展规则、Role、Gate、Artifact、状态、字段、模板或校验器前，当前执行者必须指出真实失败或重复低效、唯一 Owner、直接消费者、会改变的判断和可证伪方式，并优先补强能够解决问题的现有 Owner；缺少任一条件都不能增加，“更完整”或“更规范”也不能作为扩大产品面的理由，示例、标签和局部做法不得自动升级为 Core 合同或必填格式。同步直接消费者后，交付前必须再次确认上述条件、上位或相邻规则的语义强度以及产品面边界仍然成立；条件不成立时先修正并重新检查，无法证明符合时不得交付受影响内容，最终结果必须说明检查结论和未验证边界。
- 默认路线必须复用 Workflow Contract 的同一套通用 Runtime 流程。需要提速时，必须关闭没有事实依据的 Gate、跳过不成立的候选，并避免加载没有消费者的 Owner；不得增加特殊任务、目标限制、隐藏旁路或第二套生命周期。确实需要特殊流程时，必须先向 Human 提交并说明真实失败模式、通用流程为什么不足、拟新增的节点、边和 Owner 及其影响；取得明确批准后，由维护者先修改 `PLUGIN_DESIGN.md`。

### 实现选择与主流程独立性

- 多种做法都成立时，必须写清选择原则；稳定参数必须写入配置；脆弱且会重复执行的机械顺序必须写成 script 并实际运行。
- 主流程必须在脱离 Sacha、固定 Gate、确定 Scope/Handoff 后仍能完成；编排必须只增强协调、恢复或独立验收，不能成为主流程成立的前提。

## 产品边界

- 产品入口、生产 Role、支持或控制 Skill、主流程外能力及其完整职责清单只由 `PLUGIN_DESIGN.md` 第 2、4、5 节拥有。当前改动不涉及入口、节点、连线、职责或 Owner 转移时，不复制或重新读取这份完整清单。
- 新增 Role、Skill 功能、节点、连线、Outcome 去向或跨节点 Owner 转移前，必须先向 Human 提交产品面变化说明并取得明确确认；确认后先修改 `PLUGIN_DESIGN.md`，再修改 Core 和直接消费者。现有职责内的流程、提示词或证据细节不得自动升级为顶层设计变化。
- Core 只保存流程节点之间被多个消费者共享且不属于单一 Runtime 的稳定判断。单个 Skill 的触发条件、内部流程、局部状态或格式留在 Skill；单一 Runtime 的传输、模型和恢复留在 Adapter；项目特例留在 Project Integration 或 Domain Skill。找不到第二个真实消费者时，不能新增 Core 分类或必填字段。
- Hook 不得接受或替代 Sacha，不得扩大授权，也不得参与恢复。新增 hook、MCP、app、外部服务或权限字段必须取得明确批准；完成目标直接必需的 repo-local asset、script 或 manifest 元数据，可以在当前 Scope 内修改并验证。

| 变化类型 | 修改与核查范围 |
| --- | --- |
| 高层流程节点、连线、Role/Skill 职责或 Owner 转移 | 取得 Human 明确确认后，先修改 `PLUGIN_DESIGN.md`，再修改 Workflow 或对应 Core、节点 Skill、受影响 Adapter 和 Evolution boundary；使用 scenario/runtime 证据验证，不增加 prose test |
| Core 节点内部判断 | 修改唯一 Core Owner，再检查直接调用或返回的 Skill 以及受影响 Adapter；顶层设计没有变化时不修改 `PLUGIN_DESIGN.md` |
| Role 或支持 Skill 的局部流程 | 修改必须留在已声明的职责或功能内，并同步元数据以及直接调用或返回方；超出边界时按高层流程变化处理 |
| 单一 Runtime 的传输、模型、安装或恢复 | 只修改目标 Adapter、相关元数据或 manifest，并运行真实 Runtime 验证；不联动其他 Runtime 或 Core |
| Setup、生成器或 Provider Binding | 修改具体 Skill 和生产脚本，检查 capability provider guide，并测试真实生成行为；不把生成格式提升为 Core 流程 |
| 产品版本、当前待发布源码版本或 release 状态 | 修改 Evolution、三个 deployment manifest 和 Git tag；release validator 只检查机器可解析的部署身份和可执行入口 |

## Creator 与生成器

- 运行生成器前，必须先找到当前 `plugin-creator`、`skill-creator` 和能够导入 PyYAML 的 Python；不得硬编码用户路径。
- 新建 Skill 使用 `init_skill.py`；生成 metadata 使用 `generate_openai_yaml.py`，并提供 `display_name`、25～64 字符的 `short_description`，以及包含 `$skill-name` 的 `default_prompt`。
- 更新 Marketplace 必须另行授权，并使用当前 creator helper；不得手工修改已经注册的 marketplace 或 cache。

## 按改动选择验证

当前执行者完成普通 plugin 改动后，必须根据实际改动从以下入口选择最小且充分的验证；这些命令不是默认全跑清单。报告结果时，只说明每项验证直接覆盖的范围：

```powershell
python -B -m unittest discover -s tests -p 'test_*.py'
& <validator-python> -B <skill-creator>/scripts/quick_validate.py <affected-skill-root>
& <validator-python> -B <plugin-creator>/scripts/validate_plugin.py <plugin-root>
cprobe summary <affected-path-or-directory> --json
```

- 如果只修改 Core、Adapter、Skill 正文或开发文档，并且没有改变 frontmatter、metadata、资源或打包 path、manifest、机器合同和生产脚本，修改者必须检查唯一 Owner、直接消费者、链接和 diff，并对受影响 Scope 运行 `cprobe`。不得仅因文件位于 Skill 或 plugin 内就运行 Skill/Plugin validator。
- 如果修改 Skill frontmatter 或 `agents/openai.yaml`，必须对受影响 Skill 运行 `quick_validate.py`。该结果只证明 Skill 和 metadata 的结构正确；正文语义和实际行为仍需分别验证。
- 如果修改 plugin manifest、Skill 目录结构、Agent metadata、MCP/App、资源或打包 path，必须运行 `validate_plugin.py`。该结果只证明 plugin ingestion 和结构合同；纯正文改动不得运行该命令。
- 如果修改生产脚本、生成器、解析器或机器可读 schema/consumer，必须运行能够覆盖受影响入口的最窄测试；只有改动横跨完整测试面时才运行全量单元测试。测试结果不得外推到没有执行的 Runtime 行为。
- 如果修改 Skill 触发、Role 路由、派发或返回、Runtime 调用语义，必须使用真实场景冒烟验证。只检查了源码和 Owner 时，必须明确标记 Runtime 未验证；Skill/Plugin validator 和文本断言都不得代替场景证据。
- Python 默认由 Codex 全局 `shell_environment_policy` 注入 `PYTHONUTF8=1`；生产脚本仍显式使用 `encoding="utf-8"`。不得给每条命令机械添加 `-X utf8`；只有实测 `sys.flags.utf8_mode != 1` 或出现解码错误时，才对受影响命令使用该 fallback。
- 当 `cprobe` 返回 `budget.complete=true` 且 `whitespace.errors=0` 时，该结果已经提供当前 Scope 的 whitespace 证据，不再重复执行 `git diff --check`。只有 `cprobe` 缺失、结果不完整或不支持目标时，才对同一 Scope 执行一次原生 Git fallback；暂存后内容没有变化时也不重复取证。
- 测试或校验器不得通过读取顶层设计、README、Core、Adapter 或 `SKILL.md`，再检查正则、固定标记、整句存在或缺失、段落顺序或字数来证明语义。源码校验器必须只检查 JSON、TOML、YAML 等机器可解析的部署身份、实际文件结构、可执行入口和 Git 发布身份；Markdown 链接和语义由 Owner 及直接消费者检查，不得增加上述文本 Gate。只有生成 Markdown 本身是生产输出时，才能核对该 Markdown，且不得借此证明 Role 路由或 Runtime 行为。
- 测试生产脚本时，必须调用真实入口，并在隔离临时目录中覆盖正反例、可解析状态、文件或真实副作用、幂等、失败恢复和禁止行为。验证 Skill 触发、Role 路由、派发与返回以及 Runtime 调用时，必须运行真实场景冒烟；生产脚本测试不得代替 Runtime 场景。
- Role 或流程场景只能按照 [`tests/runtime-scenarios/README.md`](tests/runtime-scenarios/README.md) 中的任务包、执行者与评估者隔离以及原生证据流程运行。静态源码、validator、fixture、执行者自报和未安装的 `source-scenario` 都不得代替对应的 Runtime 证据。
- 只有运行生产入口后，相应能力才算经过验证。模板、fixture、字符串或自报只能证明其自身；没有运行的行为必须标记为未验证。

`plugin-eval` 可用于检查结构、描述和令牌预算，但不是必跑 Gate，也不得替代官方校验器、真实 schema、代码测试或 Runtime 冒烟验证。不得只为提高评分而增加没有权威依据的 manifest 字段、英文触发词、reference 或其他产品内容。如果评估器输入不兼容，必须在当前任务内使用等价镜像并说明限制；不得修改安装缓存或正式源码来迁就工具。

## 发布与安装入口

- Human 明确要求“快速发版”“发版”、安装、重装或 cache parity 验收时，执行者必须先读 [`docs/release.md`](docs/release.md)，再按其中的当前模式、授权和证据边界操作。普通实施批准不包含 commit、tag、push、Marketplace 或用户安装状态变更的授权。
- 发布和安装仍要遵守 Global AGENTS 中关于 Git、外部副作用、用户改动保护和完成证据的规则。操作指南和 `scripts/release.py` 不能代替 Human 的版本决定、Review、安装授权或 Runtime 验收。
- 没有进入显式发布或安装任务时，不加载发版操作指南，也不得因为源码版本、repo-local 直连或插件已启用就执行安装、refresh 或 cache 修改。
