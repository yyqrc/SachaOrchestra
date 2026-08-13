# Sacha Orchestra 项目规则

> 文档身份：插件开发使用；不进入发布插件。

## Workspace 事实

- 本文件是 Project `AGENTS.md`；Global AGENTS 的安全/授权/证据/Git/用户改动保护仍生效。
- 本文件、根目录 `README.md`、`PLUGIN_DESIGN.md` 与 `docs/**` 供插件开发使用，不进入发布插件。
- 本 workspace 是 repo-local marketplace，唯一 plugin 源码位于 `plugins/sacha-orchestra`。
- 当前 release、当前待发布源码版本与 breaking boundary 以 [`docs/architecture/evolution.md`](docs/architecture/evolution.md) 为权威；manifest=当前源码版本，tag=已发布版本；Core/Adapter 合同版本仅为 schema。
- Evolution 只给方向、版本和 breaking boundary，不授权实施。

## Owner 与直接入口

| 路径 | Owner 与用途 |
| --- | --- |
| `docs/CONTEXT.md` | 开发控制面已提炼术语与规则的完整副本；`PLUGIN_DESIGN.md` 引用它，发布插件不读取它 |
| `docs/architecture/evolution.md` | 当前 release、当前待发布源码版本、长期架构与 breaking change 权威；不保存版本流水账 |
| 三个 deployment manifest | 当前源码版本与部署接口元数据；根 `plugin.json` 使用 Agent Plugins 开放标准供 Cursor 等兼容 Runtime 加载 |
| `.agents/plugins/marketplace.json`、`.claude-plugin/marketplace.json`、`.cursor-plugin/marketplace.json` | 各 Runtime 的 repo-local marketplace 入口；只保存部署路由，不拥有流程语义 |
| `plugins/sacha-orchestra/core/intake-contract.md` | 入口判断、接受/拒绝、重复抑制和授权边界的规范性 contract |
| `plugins/sacha-orchestra/core/terminology-contract.md` | 多个直接消费者共同使用且不属于单一 Runtime 的提炼术语唯一 Runtime Owner；与 `docs/CONTEXT.md` 强双向同步 |
| `PLUGIN_DESIGN.md` | 与本文件并列的插件开发/评审顶层设计：完整流程骨架、Role/Skill 职责、Core owner 与自上而下变更顺序；不随插件发布，也不是 Runtime 依赖 |
| `plugins/sacha-orchestra/README.md` | 发布插件入口、最小用法与 Runtime Owner 导航；不保存顶层设计 |
| `plugins/sacha-orchestra/core/workflow-contract.md` | 唯一 Runtime 路由：Role/Gate、节点进入/退出条件和 Human 路由；沿用插件内术语合同，不定义就绪判定、模型或宿主参数 |
| `plugins/sacha-orchestra/core/human-interaction-contract.md` | Human 可见提问、进度、结果顺序与必须披露信息的规范性 contract |
| `plugins/sacha-orchestra/core/assurance-contract.md` | Review、Baseline、Outcome 与 evidence 语义 |
| `plugins/sacha-orchestra/core/coordination-contract.md` | Manager 的 assessment、拆分、依赖、readiness、route requirement、dispatch/return、identity/dedup 与 deviation 的唯一 Core owner |
| `plugins/sacha-orchestra/core/artifact-protocol.md` | Artifact 生成条件、最小内容、权威关系与恢复规则的规范性 contract；术语定义归插件内术语合同 |
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

- 插件开发或评审者 → 涉及已提炼术语与规则 → 必须先读 `docs/CONTEXT.md`，再核对表中插件内定义 → 发布插件不得引用该文件。
- 插件开发或评审者 → 讨论或修改入口、高层流程、Role/Skill 职责 → 必须在完成适用的术语读取后读取根目录 `PLUGIN_DESIGN.md`，再按受影响节点读取 Intake、Workflow、Human Interaction、Assurance、Coordination、Artifact 或目标 Skill → 只查询触发条件或局部流程且不涉及已提炼术语时，只读目标 `SKILL.md` 和元数据。
- Runtime 局部任务只读目标 Adapter；Core 或跨运行环境审查按 Scope 比较。
- release、长期架构、Manager/并行、`1.0.0` 或 Core breaking：读取 Evolution；只有 Human 确认具体改动后才修改。
- Evolution 只读取当前 release、当前待发布源码版本、当前 breaking boundary 与仍有效的长期决策；历史事实按具名版本、Spec/Report/Review 或 Git 查询，不从 Evolution 恢复旧机制。
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

- 当前执行者 → 遇到同词多义、同义多名、概念误合并或代码、合同、文档定义冲突 → 必须先只读核对现行 Owner、直接消费者、真实行为与冲突 → 事实足以消歧时在当前授权和 Scope 内统一；不同解释会改变产品面、Scope、验收、授权或破坏性边界时才交 Human 决定。该调查保持 Direct，不打开 Clarify、Planner Gate 或 Manager Gate。
- 当前执行者 → 流程判断被多个直接消费者重复、出现歧义或已造成真实失败 → 必须在插件内术语合同提炼术语；没有第二个现行消费者时，当前任务语义必须留在 Spec 或决定记录，存在跨任务项目消费者时才能列为 `project-context` 候选 → 术语合同必须只定义含义与边界，`docs/CONTEXT.md` 必须记录直接消费者和可证伪方式，具体进入条件与动作仍归相应 Core，其他下游只保留映射。术语提炼必须只命名既有判断；改变判断时必须按新增或扩展规则处理。没有机器消费者和实际判断需要时，不得升级为字段、状态、枚举、Artifact、必填格式或产品面。
- 修改者 → 新增、改名、改变语义/边界或删除已提炼术语与规则 → 必须同次更新 `docs/CONTEXT.md`、插件内术语合同、相应 Core 和受影响映射 → 两边不一致时以插件内术语合同恢复词义，以相应 Core 恢复流程；同步完成前不得使用受影响术语或声明完成。

## 内容归属与信息密度（必须遵守）

- Core、Adapter、Skill 与开发控制文档必须遵守全局【表达要求】；除全局定义的正式标识外，不得增加语言豁免。
- 规则必须按“主体 → 进入条件 → 动作 → 结果/限制”陈述；必须只保留影响内容归属、直接消费者、流程判断、授权、安全、恢复、验收、证据或维护动作的限制，并删除背景解释、反向释义和同义补充。
- 内容归属必须遵循一个事实一个 Owner：项目事实必须归本文件，完整顶层设计必须归 `PLUGIN_DESIGN.md`，多个直接消费者共同使用且不属于单一 Runtime 的提炼术语必须归插件内术语合同，流程判断必须归相应 Core，Role 内部流程必须归 Skill，单一 Runtime 的传输、模型与恢复必须归 Adapter；`docs/CONTEXT.md` 只能作为开发控制面的强同步副本，不取得规范性 Owner，`PLUGIN_DESIGN.md` 必须引用该副本，插件内下游必须只引用插件内 Owner 或保留自身映射。
- `PLUGIN_DESIGN.md` 必须作为插件开发/评审顶层设计的唯一 Owner，完整保存流程骨架和 Role/Skill 职责；必须与 `AGENTS.md` 同属开发控制面，不得进入发布插件或成为安装后 Runtime 依赖。完整设计只能由插件开发者、Reviewer 和场景评估者读取；Workflow Contract 必须唯一且完整定义 Runtime 路由并沿用插件内术语合同，其他 Core 必须只定义局部判断，Skill 必须只携带自身职责、流程与边界，Adapter 必须只负责传输。Core、Skill、Adapter 不得要求消费者读取顶层设计，也不得复制整张流程骨架。
- Human 明确确认高层流程的节点、先后关系、分支、Role/Skill 职责或回路变化后，必须按 `需求不变量 → PLUGIN_DESIGN.md → Workflow/对应 Core → 节点 Skill/Adapter 消费者 → Evolution（若改变长期或 breaking boundary）` 修改；节点内部判断或职责内流程未改变顶层设计时，必须直接修改唯一 Core、Adapter 或 Skill Owner，不得为“保持同步”修改设计文档。
- Manager/路由必须按以下层次归属：`PLUGIN_DESIGN.md` 必须画出协调闭环；Workflow 必须只决定何时进入 Manager 协调闭环及返回哪个调用节点；Coordination 必须定义评估、依赖、就绪判定、派发、等待和返回；Manager Skill 必须调用并消费；Adapter 必须组装 Runtime 参数。任一层越权时必须删除重复，不得补句解释。
- Codex 自动模型组合、选择条件、`agent_type/model/reasoning_effort/fork_turns` 与回退必须只存在于 Codex Adapter。顶层设计、Core、Skill、README 和通用历史说明不得复制当前型号表；Markdown 映射必须由 Owner 复核与 Runtime 场景验证，不得用正则或固定标记测试锁定文字。将来存在机器可读配置时，必须测试配置消费者，不得测试说明文本。
- 当前机制替代旧机制时，现行内容必须删除旧副本并引用现行 Owner；冻结历史文档必须只保留最短的“已取代”入口，Evolution 不得新增历史表格行或版本章节。
- 测试或校验器不得读取顶层设计、README、Core、Adapter 或 `SKILL.md` 后用正则、固定标记、整句存在/缺失、段落顺序或字数断言证明语义。生产脚本测试必须调用真实入口，检查可解析状态、文件/副作用、幂等、失败恢复和禁止行为；生成 Markdown 只有自身是生产输出时才能作为结果核对，且不得借此证明 Role 路由或 Runtime 行为。Skill 触发、Role 路由、派发/返回与 Runtime 参数必须使用真实场景冒烟验证，否则必须明确标记未验证。
- 路径术语必须遵循以下分类：Human 或配置提供的目录必须用 `base`；解析、派生后实际生效的目录必须用 `root`；文件及其位置必须用 `path`；非文件的证据、Owner、Runtime 标识或间接指向必须用 `reference`。不得使用 `locator`，不得用 `reference` 代替文件 `path`；修改既有内容时必须消除混用。
- `description` 必须只回答“何时用/何时不用”；正文必须写首查位置、扩大条件、动作、交付和停止边界；元数据提示词必须只给自然入口，不得复述正文流程。
- Skill 正文必须默认按“职责/功能 → 输入与首查 → 动作顺序 → 输出 → 停止与禁止边界”组织；Adapter 必须默认按“实现的 Core 合同 → Runtime 能力映射 → 调用参数 → 回退/恢复 → Runtime 证据边界”组织。章节名称必须服从实际语义，不得为套用结构重复内容。
- Adapter 必须只服务单一 Runtime；Skill 必须不绑定具体 Runtime；显式 setup 必须只管对应配置；根目录 `README.md` 必须只保留仓库导航，`plugins/sacha-orchestra/README.md` 必须只保留入口、最小用法和 Runtime Owner 导航；完整顶层流程骨架与 Role/Skill 职责必须只在根目录 `PLUGIN_DESIGN.md`，Runtime 路由必须由 Workflow Contract 唯一定义并沿用插件内术语合同；历史记录或版本迁移说明必须归具名文档。
- Planner、Executor、Reviewer 三个 Role Skill 必须分别写清职责、工作流和边界。修改前必须判断变化是否仍在该 Role 已声明的输入、输出和禁止边界内；新增职责、输出类型、调用 Owner 或跨节点路线时，必须先按高层流程变更处理，不得直接给 Skill 补一步。
- Manager、Clarify、Feedback、using-sacha、document-project 等控制/支持 Skill 必须只实现 `PLUGIN_DESIGN.md` 中的对应节点或闭环；setup-project、setup-agents 等主流程外 Skill 必须写清功能、概略工作流和副作用边界。迭代必须只修改已声明功能内的做法；新增功能、触发方式、外部副作用或跨节点接管必须按顶层设计变化处理，不得以局部修复混入。
- 新增或扩展规则、Role、Gate、Artifact、状态、字段、模板或校验器必须对应真实失败或重复低效，并明确唯一 Owner、直接消费者、改变的判断与可证伪方式；必须优先补强现有 Owner，缺一项就不得增加。“更完整/更规范”不得作为扩产品面的理由，示例、标签和局部做法不得自动升级为 Core 合同或必填格式。
- 精简或压缩必须只提高表达密度，不得以语义模糊换字数；可以删除铺垫、常识、历史、同义重复和无消费者说明，但必须保留明确的主体、触发条件/进入条件、动作及先后依赖、退出/停止/恢复条件、例外、Owner/Human 决策点、授权、安全、失败/未验证、Evidence、验收、Entry Condition 和 schema。压缩后需要依赖上下文猜测、存在多种合理解释或无法证明语义等价时，必须保留原文；会改变流程判断时，必须停止该部分并把语义变化交给 Human 二次确认。
- 多种做法成立时必须写判断原则；稳定参数必须写配置；脆弱且重复的机械顺序必须写 script 并实跑。
- 主流程必须在脱离 Sacha、固定 Gate、Scope/Handoff 后仍能完成；编排必须只增强协调、恢复或独立验收。
- 默认路线必须复用 Workflow Contract 的同一套通用 Runtime 流程；提速必须关闭没有事实依据的 Gate、跳过不成立的候选并避免加载无消费者 Owner，不得增加特殊任务、目标限制、隐藏旁路或第二套生命周期。确需特殊流程时，必须先向 Human 提交真实失败模式、通用流程不足、拟新增节点/边/Owner 与影响，并在取得明确批准后由维护者先修改 `PLUGIN_DESIGN.md`。

## 产品边界

- 产品面以 `PLUGIN_DESIGN.md` 为准：`using-sacha` 是唯一默认入口；生产 Role 只有 Planner、Executor、Reviewer，三者可作为高级直接入口；Clarify 是主工作流唯一可显式调用的支持节点。Manager 只能由主任务在 Gate 打开后调用，document-project 只能由收尾候选路由，二者都不是用户入口。Feedback 是独立显式支持入口：Human 只在另一个真实任务手动调用，可提交流程问题、使用反馈或插件开发想法；调用本身授权来源任务调查并转移 owner，但不授权目标任务写入或外部动作。setup-project、setup-agents 是主流程外显式配置能力，不进入主工作流。
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

普通 plugin 改动只运行风险对应的最小集合：

```powershell
python -B tests/validate_project_setup.py
python -B -m unittest discover -s tests -p 'test_*.py'
& <validator-python> -B <skill-creator>/scripts/quick_validate.py <affected-skill-root>
& <validator-python> -B <plugin-creator>/scripts/validate_plugin.py <plugin-root>
cprobe summary <affected-path-or-directory> --json
```

- Python 默认由 Codex 全局 `shell_environment_policy` 注入 `PYTHONUTF8=1`；生产脚本仍显式使用 `encoding="utf-8"`。不得给每条命令机械添加 `-X utf8`；只有实测 `sys.flags.utf8_mode != 1` 或出现解码错误时，才对受影响命令使用该 fallback。
- `cprobe` 返回 `budget.complete=true` 且 `whitespace.errors=0` 已构成该 Scope 的 whitespace 证据，不再重复执行 `git diff --check`。仅当 `cprobe` 缺失、结果不完整或不支持目标时，对同一 Scope 执行一次原生 Git fallback；暂存后内容未变化不重复取证。
- 源码校验器只核对 JSON/TOML/YAML 等机器可解析部署身份、实际文件结构、可执行入口和 Git 发布身份；Markdown 链接与语义由 Owner 复核及官方 Plugin/Skill 校验器负责，不写正则、固定标记、句子存在性、段落顺序或字数 Gate。
- 生产脚本用隔离临时目录的正反例、幂等、失败恢复和真实副作用测试；Skill 触发、Role 路由与 Runtime 调用用真实场景冒烟验证。前一层不得替代后一层。
- Role/流程场景使用 [`tests/runtime-scenarios/README.md`](tests/runtime-scenarios/README.md) 的任务包流程：执行者只看中性任务、隔离工作区规则与正式入口 Skill/Core，不读取插件 README 或场景裁决标准；独立评估者才用顶层图核对偏移。不要求 Manager 派发的场景使用不携带父对话历史的委派 Agent；要求 Manager 派发的场景从 Human 明确发起或授权创建的全新主任务运行，并遵守单层派发。运行者保存首次等待前的实时 Agent 树、首次创建参数和委派 Agent 的直接启动/终态记录，再核对验证器、原生派发/返回与工作区 `delta`；不得用执行者事后自报替代。未安装或不是全新任务时只能记为 `source-scenario`，不得宣称全新发现或 Runtime 已验证。
- 能力完成声明须定位生产入口；模板、fixture、字符串或自报只证明其自身，未运行的行为仍标记未验证。

`plugin-eval` 可用于结构、描述和令牌预算诊断，但不是必跑 Gate，也不能替代官方校验器、真实 schema、代码测试或 Runtime 冒烟验证。不得仅为提高评分添加无权威依据的 manifest 字段、英文触发词、reference 或其他产品内容；评估器输入兼容问题使用当前任务内的等价镜像并报告限制，不修改安装缓存或正式源码迁就工具。

发布分两种模式：

- Human 说“快速发版”时，默认递增 patch 版本；只人工核对 Evolution 的当前 release 与当前待发布源码版本状态，并机器核对三个 deployment manifest、annotated tag 到 `HEAD` 的指向及 push 后远端分支/tag。跳过普通回归、Skill/Plugin validator、完整 release coherence、安装/cache parity、fresh discovery 和 runtime。
- Human 说“发版”时，运行风险对应的普通验证与完整 metadata coherence；安装和 runtime 仍按明确授权与发布目标决定。
- 普通发版执行者发现同一 Scope 已有仍有效的独立 Review，且精确暂存发布内容、验收输入和证据边界未超出该 Review 时复用原结论；发版本身不触发重审。任一项变化时只审原结论后的精确暂存变化及其影响，按风险选择最低充分模型与推理强度，不因发布动作默认提高强度。
- 普通发版执行者先精确暂存当前待发布源码版本对应的发布内容，再并行运行风险对应验证、待发布阶段一致性检查与确有必要的增量 Review；通过后才把 Evolution 从待发布状态切换为当前 release，并依次执行 commit、annotated tag、发布阶段一致性检查、原子 push 和远端核对。tag 建立前不得把当前待发布源码版本声明为当前 release，发布授权不得写入原实施 Scope。
- 普通发版执行者在 Scope、版本和 Review 结论稳定时优先使用 `scripts/release.py prepare|publish|install`；脚本只执行现有 Owner 已决定的机械步骤，失败后停止，不替代版本决定、Review、授权或 Runtime 验收。
- 普通发版实施收尾时若 Reviewer Gate 已有事实依据，当前 Owner 应完成必要 Review；发布阶段只核对精确暂存发布内容是否仍在该 Review 的 Scope、验收输入和证据边界内。发布脚本允许精确暂存发布范围外存在无关工作区改动，但 `--candidate-path` 指定文件暂存后又变化、存在冲突或 index 验证失败时必须停止。

普通发版先对当前待发布源码版本的精确暂存内容运行；`prepare` 从 Git index 导出隔离快照，验证不读取精确暂存发布范围外的 working/untracked 内容：

```powershell
python -B scripts/release.py prepare --version <version> --candidate-path <path> [--candidate-path <path> ...]
```

复用仍有效的 Review 或完成必要的增量 Review 后，维护者把 Evolution 从待发布状态切换为当前 release 并精确暂存；再运行：

```powershell
python -B scripts/release.py publish --version <version> --review reused|accepted --message <commit-message> --candidate-path <path> [--candidate-path <path> ...]
```

关闭本次发布创建且已终态的辅助 Agent 后，按安装授权运行：

```powershell
python -B scripts/release.py install --version <version>
```

脚本不可用时，待发布与发布两个机器阶段分别运行 metadata coherence：

```powershell
python -B tests/validate_release_coherence.py --version <version> --phase candidate
python -B tests/validate_release_coherence.py --version <version> --phase release
```

`candidate`（待发布阶段）只核对当前待发布源码版本的机器可解析部署身份和生产入口；`release`（发布阶段）在 commit、annotated tag 已建立且 Evolution 已人工切换为当前 release 后运行，并额外核对 annotated tag 精确指向 `HEAD`。该脚本不读取 README/Core/Adapter/Skill/Evolution 的说明文字。

## 安装授权 Gate

- Marketplace 注册、安装、refresh、removal/reinstall 需要 Human 明确授权；实施批准不隐含外部状态授权。
- 使用 `read_marketplace_name.py` 从 `.agents/plugins/marketplace.json` 读取 marketplace 名称；不得根据目录名猜测。
- 授权后按目标 Adapter 执行并验证 marketplace/plugin list；Scope、版本、目标、branch/remote 未变化时不重复询问。
- 安装执行者在调用安装 CLI 前关闭本次发布创建且已终态的辅助 Agent；安装返回拒绝访问或 cache 已创建但登记未完成时停止并报告，不删除、覆盖或手改 cache，待占用解除后再用同一 CLI 恢复并核对。
- manifest 使用批准的精确 semantic version，不加 cachebuster；不得编辑 cache、应用权限或系统 PATH。
