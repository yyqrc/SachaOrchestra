# Sacha Orchestra 项目规则

> 文档身份：插件开发使用；不进入发布插件。

## Workspace 事实

- 本文件是 Project `AGENTS.md`；Global AGENTS 的安全/授权/证据/Git/用户改动保护仍生效。
- 本文件、根目录 `README.md`、`PLUGIN_DESIGN.md`、`EVOLUTION.md` 与 `docs/**` 供插件开发使用，不进入发布插件。
- 本 workspace 是 repo-local marketplace，唯一 plugin 源码位于 `plugins/sacha-orchestra`。
- 当前 release、当前待发布源码版本、当前 breaking boundary、成熟度与尚未实施的长期方向以 [`EVOLUTION.md`](EVOLUTION.md) 为权威；现行架构与流程仍归 `PLUGIN_DESIGN.md` 和对应 Runtime Owner，manifest=当前源码版本，tag=已发布版本。
- Evolution 只给版本、当前 breaking boundary、成熟度和尚未实施的方向，不授权实施。

## Owner 与直接入口

| 路径 | Owner 与用途 |
| --- | --- |
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
| `plugins/sacha-orchestra/skills/*` | 不绑定具体 Runtime 的节点职责、局部工作流与边界；不增加流程节点，不复制 Core 判断或 Adapter 参数 |

## 文档身份与发布可达边界

- 文档作者 → 新增或修改 Human 可读文档 → 必须先按 path 确定“插件开发使用”或“插件发布使用” → 一份文档只能属于一种身份。
- 仓库根 `AGENTS.md`、`README.md`、`PLUGIN_DESIGN.md`、`docs/**` 与 `tests/**` 内说明 → 供插件开发、维护或场景评估使用 → 不进入发布插件，不得成为安装后 Runtime 的依赖。
- `plugins/sacha-orchestra/**` 内 Human 可读文档 → 供发布插件使用 → 必须在发布 `root` 内自包含 Runtime 所需的规则、入口和恢复语义。
- 三个部署清单 → 解析 `plugins/sacha-orchestra` 为发布 `root` → 只发布该 `root` 内文件；仓库中可读、链接可打开或相对 path 在源码树成立，均不证明发布 `root` 外文件安装后可达。
- 插件发布文档 → 引用本地 path → 解析后的目标必须留在发布 `root` 内 → 不得引用根 `AGENTS.md`、根 `README.md`、`PLUGIN_DESIGN.md`、`docs/**`、`tests/**` 或其他发布 `root` 外文件承载运行语义。
- 修改者 → 把插件开发文档中的决定提供给安装后 Runtime → 必须写入插件内对应 Core、Skill 或 Adapter Owner，并同步直接消费者 → 不得用指向插件开发文档的链接替代插件内定义。
- Reviewer → 声明发布文档自包含 → 必须先从部署清单确认发布 `root`，再核对本次新增或修改的本地引用均在该 `root` 内可达，并运行插件校验 → 只能声明证据覆盖的源码/静态范围；安装后可达仍需安装证据或包一致性证据。

## 读取路由

- 开发者或 Reviewer → 讨论、调查或修改文档 → 先按目标 path、文档身份与直接消费者判定主工作面：根 `AGENTS.md`、根 `README.md`、`PLUGIN_DESIGN.md`、`EVOLUTION.md`、`docs/**` 与 `tests/**` 属于插件开发控制面，优先审查插件开发行为、维护归属、读取路线和开发证据；`plugins/sacha-orchestra/README.md`、`core/**`、`adapters/**` 与 `skills/**` 属于发布插件 Runtime，优先审查安装后流程、Runtime Owner、直接消费和行为证据。任务同时涉及两面时先分别声明开发决定与 Runtime 消费同步点，只为直接消费者、发布可达或真实行为验证跨界；不得用开发文档的自描述要求评判 Runtime 文档，也不得用 Runtime 局部流程扩大插件开发文档 Scope。
- 开发者或 Reviewer → 新增、移动、审查或维护 `docs/**` → 先读 `docs/AGENTS.md`，再按其身份路由只读目标当前 Owner 或精确历史 Artifact → 不遍历无消费者的文档树。
- 插件开发或评审者 → 涉及已提炼术语与规则 → 必须先读 `docs/CONTEXT.md`，再核对表中插件内定义 → 发布插件不得引用该文件。
- 插件开发或评审者 → 讨论或修改入口、高层流程、Role/Skill 职责 → 必须在完成适用的术语读取后读取根目录 `PLUGIN_DESIGN.md`，再按受影响节点读取 Intake、Workflow、Human Interaction、Assurance、Coordination、Artifact 或目标 Skill → 只查询触发条件或局部流程且不涉及已提炼术语时，只读目标 `SKILL.md` 和元数据。
- Runtime 局部任务只读目标 Adapter；Core 或跨运行环境审查按 Scope 比较。
- 当前执行者 → 在新 task 或新协作界面继续同一 Runtime 局部迭代 → 先读目标 Adapter、批准 Spec、专用 Runtime 场景和有界 delta；只有这些现行来源不足以恢复状态时才查询 MEMORY/rollout，完整旧对话、完整 MEMORY 和冻结历史计划不得作为默认输入。
- release、`1.0.0`、尚未实施的长期方向或 Core breaking boundary：读取 Evolution；显式快速发版、普通发版或安装另读 `docs/release.md`；现行架构、Manager/并行与产品流程先读 `PLUGIN_DESIGN.md`，只有改变上述 Evolution 独占内容时才修改 Evolution。
- Evolution 只读取当前 release、当前待发布源码版本、当前 breaking boundary、成熟度与尚未实施的长期方向；历史事实按具名版本、Spec/Report/Review 或 Git 查询，不从 Evolution 恢复旧机制。
- 普通实施不遍历历史计划目录寻找“更多规则”。现行内容与当前 Owner 冲突时删除副本或改成 Owner 引用；冻结历史文档仅在仍可能误导当前操作时添加最短的“已取代”入口。
- Project Integration 和 Domain Skill 归各自项目所有。不得将项目特定命令或证据规则导入此 Core。

## Plugin Development Direct

- 普通 plugin `change`、`build`、`fix`、`sync` 或 `iterate` 请求默认在当前 task 执行；多文件、耗时或验证步骤多不单独打开任何 Gate。
- Direct Scope 以用户语义目标和明确约束为边界。预计文件列表不是穷尽 allowlist，只有用户或已批准 Spec 明确写出 exact file allowlist 时才是硬边界。
- 当前 Executor 可修改同一目标直接必需的源码、文档、断言和验证配置；同 Scope 漏改/失败直接修复重验，不创建额外流程。
- 出现实质新方案、breaking contract/schema、权限、安全、持久数据、验收改变、未授权外部动作或无法完整验证时，停止相关写入并按三个 Gate 路由。
- 每次只验证当前 Runtime 和交付层；除非 Human 明确要求跨运行环境验收，其他 Runtime 的安装、发现、行为或证据缺口只作后续反馈，不扩大或阻塞源码发布。
- Review 只拦截会错误交付的关键问题；不阻塞发布的缺证据项或改进项用 `Accepted with follow-up`。不追求全历史或全部 Runtime，也不把“还能补证据”升级为 `Needs Fix`。

## 术语提炼与同步

- 当前执行者 → 遇到同词多义、同义多名、概念误合并或代码、合同、文档定义冲突 → 必须先只读核对现行 Owner、直接消费者、真实行为与冲突 → 事实足以消歧时在当前授权和 Scope 内统一；不同解释会改变产品面、Scope、验收、授权或破坏性边界时才交 Human 决定。该调查保持 Direct，不打开 Explore、Planner Gate 或 Manager Gate。
- 当前执行者 → 同一术语或流程判断被多个发布插件直接消费者重复、出现歧义或已造成真实失败 → 必须在插件内术语合同提炼术语，并在 `docs/CONTEXT.md` 保存开发侧同步视图、直接消费者和可证伪方式 → 术语合同只定义含义与边界，具体进入条件与动作仍归相应 Core，其他发布插件下游只保留映射。只有多个开发控制面直接消费者共同使用的术语归 `docs/CONTEXT.md`，不得为保持集合相等写入术语合同。没有第二个现行消费者时，当前任务语义必须留在 Spec 或决定记录，存在跨任务项目消费者时才能列为 `project-context` 候选。术语提炼必须只命名既有判断；改变判断时必须按新增或扩展规则处理。没有机器消费者和实际判断需要时，不得升级为字段、状态、枚举、Artifact、必填格式或产品面。
- 修改者 → 新增、改名、改变语义/边界或删除插件内共享术语与规则 → 必须同次更新 `docs/CONTEXT.md`、插件内术语合同、相应 Core 和受影响映射 → 两边不一致时以插件内术语合同恢复 Runtime 词义，以相应 Core 恢复流程。修改仅供开发控制面消费的术语时，只更新 `docs/CONTEXT.md` 与开发侧直接消费者；该术语新增多个发布插件直接消费者时，必须先提升到术语合同并完成共享同步。同步完成前不得使用受影响术语或声明完成。

## 内容归属与信息密度（必须遵守）

- Core、Adapter、Skill 与开发控制文档必须遵守全局【表达要求】；除全局定义的正式标识外，不得增加语言豁免。
- 规则必须按“主体 → 进入条件 → 动作 → 结果/限制”陈述；必须只保留影响内容归属、直接消费者、流程判断、授权、安全、恢复、验收、证据或维护动作的限制，并删除背景解释、反向释义和同义补充。
- 内容归属必须遵循一个事实一个 Owner：项目事实必须归本文件，完整顶层设计必须归 `PLUGIN_DESIGN.md`，多个发布插件直接消费者共同使用且不属于单一 Runtime 的提炼术语必须归插件内术语合同，只有多个开发控制面直接消费者共同使用的提炼术语必须归 `docs/CONTEXT.md`，流程判断必须归相应 Core，Role 内部流程必须归 Skill，单一 Runtime 的传输、模型与恢复必须归 Adapter；`docs/CONTEXT.md` 必须完整包含插件内共享术语的开发侧同步视图，并可拥有开发专用术语，`PLUGIN_DESIGN.md` 必须引用它，插件内下游必须只引用插件内 Owner 或保留自身映射。
- `PLUGIN_DESIGN.md` 必须作为插件开发/评审顶层设计的唯一 Owner，完整保存流程骨架和 Role/Skill 职责；必须与 `AGENTS.md` 同属开发控制面，不得进入发布插件或成为安装后 Runtime 依赖。完整设计只能由插件开发者、Reviewer 和场景评估者读取；Workflow Contract 必须唯一且完整定义 Runtime 路由并沿用插件内术语合同，其他 Core 必须只定义局部判断，Skill 必须只携带自身职责、流程与边界，Adapter 必须只负责传输。Core、Skill、Adapter 不得要求消费者读取顶层设计，也不得复制整张流程骨架。
- Human 明确确认高层流程的节点、先后关系、分支、Role/Skill 职责或回路变化后，必须按 `需求不变量 → PLUGIN_DESIGN.md → Workflow/对应 Core → 节点 Skill/Adapter 消费者 → Evolution（若改变长期或 breaking boundary）` 修改；节点内部判断或职责内流程未改变顶层设计时，必须直接修改唯一 Core、Adapter 或 Skill Owner，不得为“保持同步”修改设计文档。
- Manager/路由必须按以下层次归属：`PLUGIN_DESIGN.md` 必须画出协调闭环；Workflow 必须只决定何时进入 Manager 协调闭环及返回哪个调用节点；Coordination 必须定义评估、依赖、就绪判定、派发、等待和返回；Manager Skill 必须调用并消费；Adapter 必须组装 Runtime 参数。任一层越权时必须删除重复，不得补句解释。
- Codex 自动模型组合、选择条件、`agent_type/model/reasoning_effort/fork_turns` 与回退必须只存在于 Codex Adapter。顶层设计、Core、Skill、README 和通用历史说明不得复制当前型号表；Markdown 映射必须由 Owner 复核与 Runtime 场景验证，不得用正则或固定标记测试锁定文字。将来存在机器可读配置时，必须测试配置消费者，不得测试说明文本。
- 当前机制替代旧机制时，现行内容必须删除旧副本并引用现行 Owner；冻结历史文档必须只保留最短的“已取代”入口，Evolution 不得新增历史表格行或版本章节。
- 测试或校验器不得读取顶层设计、README、Core、Adapter 或 `SKILL.md` 后用正则、固定标记、整句存在/缺失、段落顺序或字数断言证明语义。生产脚本测试必须调用真实入口，检查可解析状态、文件/副作用、幂等、失败恢复和禁止行为；生成 Markdown 只有自身是生产输出时才能作为结果核对，且不得借此证明 Role 路由或 Runtime 行为。Skill 触发、Role 路由、派发/返回与 Runtime 参数必须使用真实场景冒烟验证，否则必须明确标记未验证。
- 开发者或发布插件消费者 → 使用 `base`、`root`、`path` 或 `reference` → 必须分别沿用 `docs/CONTEXT.md` 的开发定义与插件内术语合同的 Runtime 定义，修改既有内容时消除混用 → 不得另建 `locator` 作为同义术语。
- `description` 必须只回答“何时用/何时不用”；正文必须写首查位置、扩大条件、动作、交付和停止边界；元数据提示词必须只给自然入口，不得复述正文流程。
- Skill 正文必须默认按“职责/功能 → 输入与首查 → 动作顺序 → 输出 → 停止与禁止边界”组织；Adapter 必须默认按“实现的 Core 合同 → Runtime 能力映射 → 调用参数 → 回退/恢复 → Runtime 证据边界”组织。章节名称必须服从实际语义，不得为套用结构重复内容。
- Adapter 必须只服务单一 Runtime；Skill 必须不绑定具体 Runtime；显式 setup 必须只管对应配置；根目录 `README.md` 必须只保留仓库导航，`plugins/sacha-orchestra/README.md` 必须只保留入口、最小用法和 Runtime Owner 导航；完整顶层流程骨架与 Role/Skill 职责必须只在根目录 `PLUGIN_DESIGN.md`，Runtime 路由必须由 Workflow Contract 唯一定义并沿用插件内术语合同；历史记录或版本迁移说明必须归具名文档。
- Planner、Executor、Reviewer 三个 Role Skill 必须分别写清职责、工作流和边界。修改前必须判断变化是否仍在该 Role 已声明的输入、输出和禁止边界内；新增职责、输出类型、调用 Owner 或跨节点路线时，必须先按高层流程变更处理，不得直接给 Skill 补一步。
- Manager、Explore、Feedback、using-sacha、document-project 等控制/支持 Skill 必须只实现 `PLUGIN_DESIGN.md` 中的对应节点或闭环；roadmap、setup-project、setup-agents 等主流程外 Skill 必须写清功能、概略工作流和副作用边界。迭代必须只修改已声明功能内的做法；新增功能、触发方式、外部副作用或跨节点接管必须按顶层设计变化处理，不得以局部修复混入。
- 新增或扩展规则、Role、Gate、Artifact、状态、字段、模板或校验器必须对应真实失败或重复低效，并明确唯一 Owner、直接消费者、改变的判断与可证伪方式；必须优先补强现有 Owner，缺一项就不得增加。“更完整/更规范”不得作为扩产品面的理由，示例、标签和局部做法不得自动升级为 Core 合同或必填格式。
- 当前执行者 → 完成上述新增或扩展并同步直接消费者后 → 在交付前逐项复核真实失败或重复低效、唯一 Owner、直接消费者、改变的判断、可证伪方式、上位/相邻规则的语义强度与产品面边界；不符合时先修正并重新复核，无法证明合规时停止受影响交付 → 最终显式报告复核结论与未验证边界。
- 精简或压缩必须只提高表达密度，不得以语义模糊换字数；可以删除铺垫、常识、历史、同义重复和无消费者说明，但必须保留明确的主体、触发条件/进入条件、动作及先后依赖、退出/停止/恢复条件、例外、Owner/Human 决策点、授权、安全、失败/未验证、Evidence、验收、Entry Condition 和 schema。压缩后需要依赖上下文猜测、存在多种合理解释或无法证明语义等价时，必须保留原文；会改变流程判断时，必须停止该部分并把语义变化交给 Human 二次确认。
- 多种做法成立时必须写判断原则；稳定参数必须写配置；脆弱且重复的机械顺序必须写 script 并实跑。
- 主流程必须在脱离 Sacha、固定 Gate、Scope/Handoff 后仍能完成；编排必须只增强协调、恢复或独立验收。
- 默认路线必须复用 Workflow Contract 的同一套通用 Runtime 流程；提速必须关闭没有事实依据的 Gate、跳过不成立的候选并避免加载无消费者 Owner，不得增加特殊任务、目标限制、隐藏旁路或第二套生命周期。确需特殊流程时，必须先向 Human 提交真实失败模式、通用流程不足、拟新增节点/边/Owner 与影响，并在取得明确批准后由维护者先修改 `PLUGIN_DESIGN.md`。

## 产品边界

- 产品入口、生产 Role、支持/控制 Skill、主流程外能力及其完整职责清单只由 `PLUGIN_DESIGN.md` 第 2、4、5 节拥有；当前改动不触及入口、节点、连线、职责或 Owner 转移时不复制或重读该清单。
- 任何新增 Role、Skill 功能、节点、连线、Outcome 去向或跨节点 Owner 转移，都必须先向 Human 提交产品面变化并取得明确确认，再修改 `PLUGIN_DESIGN.md`，最后修改 Core 与直接消费者。现有职责内流程、提示词或证据细节不得自动升级为顶层设计变化。
- Core 只容纳流程节点间被多个消费者共享且不属于单一 Runtime 的稳定判断；单 Skill 的触发条件、内部流程、局部状态或格式留在 Skill，单一 Runtime 的传输、模型与恢复留在 Adapter，项目特例留在 Project Integration/Domain Skill。不能指出第二个真实消费者时，不新增 Core 分类或必填字段。
- Hook 不得接受/替代 Sacha、扩大授权或参与恢复。新增 hook/MCP/app/外部服务/权限字段需明确批准；目标必需的 repo-local asset/script/manifest 元数据按 Scope 修改验证。

| 变化类型 | 修改与核查范围 |
| --- | --- |
| 高层流程节点、连线、Role/Skill 职责或 Owner 转移 | Human 明确确认后由 `PLUGIN_DESIGN.md` 先行；再改 Workflow/对应 Core、节点 Skill、受影响 Adapter 与 Evolution boundary；以 scenario/runtime 证据验证，不增加 prose test |
| Core 节点内部判断 | 修改唯一 Core owner，再核查直接调用/返回 Skill 与受影响 Adapter；顶层设计没变就不改 `PLUGIN_DESIGN.md` |
| Role 或支持 Skill 的局部流程 | 必须落在已声明职责/功能内；同步元数据和直接调用/返回方，超界则升级为高层流程变化 |
| 单一 Runtime 的传输、模型、安装或恢复 | 只改目标 Adapter、相关元数据/manifest 与真实 Runtime 验证；不联动其他 Runtime 或 Core |
| Setup/生成器/Provider Binding | 修改具体 Skill 与生产脚本，核查 capability provider guide 和真实生成行为测试；不把生成格式提升为 Core 流程 |
| 产品版本、当前待发布源码版本或 release 状态 | Evolution、三个 deployment manifest 与 Git tag；release validator 只核对机器可解析部署身份和可执行入口 |

## Creator 与生成器

- 执行前解析当前 `plugin-creator`、`skill-creator` 和可导入 PyYAML 的 Python，不硬编码用户路径。
- 新建 Skill 用 `init_skill.py`；metadata 用 `generate_openai_yaml.py`，提供 `display_name`、25～64 字符的 `short_description` 和包含 `$skill-name` 的 `default_prompt`。
- Marketplace 更新须另行授权并使用当前 creator helper；不得手改已注册 marketplace 或 cache。

## 验证命令与声明

当前执行者 → 完成普通 plugin 改动后 → 按实际 `delta` 从以下入口选择最小充分证据，不得把命令列表当作默认全跑清单 → 每项只声明其直接覆盖范围：

```powershell
python -B -m unittest discover -s tests -p 'test_*.py'
& <validator-python> -B <skill-creator>/scripts/quick_validate.py <affected-skill-root>
& <validator-python> -B <plugin-creator>/scripts/validate_plugin.py <plugin-root>
cprobe summary <affected-path-or-directory> --json
```

- 改动只涉及 Core、Adapter、Skill 正文或开发文档，且未改变 frontmatter、metadata、资源/打包 path、manifest、机器合同或生产脚本 → 复核唯一 Owner、直接消费者、链接与 diff，并对受影响 Scope 运行 `cprobe` → 不得仅因文件位于 Skill 或 plugin 内运行 Skill/Plugin validator。
- 改动涉及 Skill frontmatter 或 `agents/openai.yaml` → 对受影响 Skill 运行 `quick_validate.py` → 该结果只证明 Skill/metadata 结构；正文语义和行为另行验证。
- 改动涉及 plugin manifest、Skill 目录结构、Agent metadata、MCP/App、资源或打包 path → 运行 `validate_plugin.py` → 该结果只证明 plugin ingestion 与结构合同；纯正文改动不得运行。
- 改动涉及生产脚本、生成器、解析器或机器可读 schema/consumer → 运行覆盖受影响入口的最窄测试；只有影响横跨完整测试面时才运行全量单元测试 → 结果不得外推到未执行的 Runtime 行为。
- 改动涉及 Skill 触发、Role 路由、派发/返回或 Runtime 调用语义 → 使用真实场景冒烟验证；只完成源码/Owner 复核时明确标记 Runtime 未验证 → Skill/Plugin validator 和文本断言不得替代场景证据。
- Python 默认由 Codex 全局 `shell_environment_policy` 注入 `PYTHONUTF8=1`；生产脚本仍显式使用 `encoding="utf-8"`。不得给每条命令机械添加 `-X utf8`；只有实测 `sys.flags.utf8_mode != 1` 或出现解码错误时，才对受影响命令使用该 fallback。
- `cprobe` 返回 `budget.complete=true` 且 `whitespace.errors=0` 已构成该 Scope 的 whitespace 证据，不再重复执行 `git diff --check`。仅当 `cprobe` 缺失、结果不完整或不支持目标时，对同一 Scope 执行一次原生 Git fallback；暂存后内容未变化不重复取证。
- 源码校验器只核对 JSON/TOML/YAML 等机器可解析部署身份、实际文件结构、可执行入口和 Git 发布身份；Markdown 链接与语义由 Owner 和直接消费者复核，不写正则、固定标记、句子存在性、段落顺序或字数 Gate。
- 生产脚本用隔离临时目录的正反例、幂等、失败恢复和真实副作用测试；Skill 触发、Role 路由与 Runtime 调用用真实场景冒烟验证。前一层不得替代后一层。
- Role/流程场景只按 [`tests/runtime-scenarios/README.md`](tests/runtime-scenarios/README.md) 的任务包、执行者/评估者隔离和原生证据流程运行；静态源码、validator、fixture、执行者自报及未安装的 `source-scenario` 不得替代对应 Runtime 证据。
- 能力完成声明须定位生产入口；模板、fixture、字符串或自报只证明其自身，未运行的行为仍标记未验证。

`plugin-eval` 可用于结构、描述和令牌预算诊断，但不是必跑 Gate，也不能替代官方校验器、真实 schema、代码测试或 Runtime 冒烟验证。不得仅为提高评分添加无权威依据的 manifest 字段、英文触发词、reference 或其他产品内容；评估器输入兼容问题使用当前任务内的等价镜像并报告限制，不修改安装缓存或正式源码迁就工具。

## 发布与安装入口

- Human 明确要求“快速发版”“发版”、安装、重装或 cache parity 验收时，执行者先读 [`docs/release.md`](docs/release.md)，再按其中当前模式、授权和证据边界操作；普通实施批准不授权 commit、tag、push、Marketplace 或用户安装状态变更。
- 发布和安装继续遵守 Global AGENTS 的 Git、外部副作用、用户改动保护与完成证据规则；操作指南和 `scripts/release.py` 不替代 Human 版本决定、Review、安装授权或 Runtime 验收。
- 未进入显式发布/安装任务时不加载发版操作指南，也不因源码版本、repo-local 直连或插件已启用而执行安装、refresh 或 cache 修改。
