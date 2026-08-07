# Sacha Orchestra 项目规则

## Workspace 事实

- 本文件是 Project `AGENTS.md`；Global AGENTS 的安全/授权/证据/Git/用户改动保护仍生效。
- 本 workspace 是 repo-local marketplace，唯一 plugin 源码位于 `plugins/sacha-orchestra`。
- 当前 release/source candidate 与 breaking boundary 以 [`docs/architecture/evolution.md`](docs/architecture/evolution.md) 为权威；manifest=当前源码版本，tag=已发布版本；Core/Adapter 合同版本仅为 schema。
- Evolution 只给方向、版本和 breaking boundary，不授权实施。

## Owner 与直接入口

| 路径 | Owner 与用途 |
| --- | --- |
| `docs/architecture/evolution.md` | 当前 release/candidate、长期架构与 breaking change 权威；不保存版本流水账 |
| 两个 deployment manifest | 当前源码版本与部署接口元数据 |
| `plugins/sacha-orchestra/core/intake-contract.md` | 入口判断、接受/拒绝、重复抑制和授权边界的规范性 contract |
| `PLUGIN_DESIGN.md` | 与本文件并列的插件开发/评审顶层设计：完整流程骨架、Role/Skill 职责、Core owner 与自上而下变更顺序；不随插件发布，也不是 Runtime 依赖 |
| `plugins/sacha-orchestra/README.md` | 安装后入口、最小用法与 Runtime owner 导航；不保存顶层设计 |
| `plugins/sacha-orchestra/core/workflow-contract.md` | 唯一自包含 Runtime 路由：Role/Gate、节点进入/退出条件和 Human 路由；不定义 readiness、模型或宿主参数 |
| `plugins/sacha-orchestra/core/human-interaction-contract.md` | Human 可见提问、进度、结果顺序与必须披露信息的规范性 contract |
| `plugins/sacha-orchestra/core/assurance-contract.md` | Review、Baseline、Outcome 与 evidence 语义 |
| `plugins/sacha-orchestra/core/coordination-contract.md` | Manager 的 assessment、拆分、依赖、readiness、route requirement、dispatch/return、identity/dedup 与 deviation 的唯一 Core owner |
| `plugins/sacha-orchestra/core/artifact-protocol.md` | Artifact 与 Handoff 的规范性 contract |
| `plugins/sacha-orchestra/adapters/<runtime>/runtime-adapter.md` | 单 Runtime transport、自动模型/强度选择、精确调用参数、fallback、恢复与验证映射；不得反向定义 Gate/readiness |
| `plugins/sacha-orchestra/skills/*` | Runtime-neutral 的节点职责、局部工作流与边界；不增加流程节点，不复制 Core 判断或 Adapter 参数 |

## 读取路由

- 讨论或修改入口、高层流程、Role/Skill 职责时先读根目录 `PLUGIN_DESIGN.md`，再按受影响节点读取 Intake、Workflow、Human Interaction、Assurance、Coordination、Artifact 或目标 Skill；只查询 trigger/局部 procedure 时读取目标 `SKILL.md` 和 metadata。
- Runtime 局部任务只读目标 Adapter；Core 或跨 Runtime 审查按 Scope 比较。
- release、长期架构、Manager/并行、`1.0.0` 或 Core breaking：读取 Evolution；只有 Human 确认具体改动后才修改。
- Evolution 只读取当前 release/source candidate、当前 breaking boundary 与仍有效的长期决策；历史事实按具名版本、Spec/Report/Review 或 Git 查询，不从 Evolution 恢复旧机制。
- 普通实施不遍历历史计划目录寻找“更多规则”。active surface 与当前 owner 冲突时删除副本或改成 owner 引用；冻结历史文档仅在仍可能误导当前操作时添加最短 superseded 入口。
- Project Integration 和 Domain Skill 归各自项目所有。不得将项目特定命令或证据规则导入此 Core。

## Plugin Development Direct

- 普通 plugin `change`、`build`、`fix`、`sync` 或 `iterate` 请求默认在当前 task 执行；多文件、耗时或验证步骤多不单独打开任何 Gate。
- Direct Scope 以用户语义目标和明确约束为边界。预计文件列表不是穷尽 allowlist，只有用户或已批准 Spec 明确写出 exact file allowlist 时才是硬边界。
- 当前 Executor 可修改同一目标直接必需的源码、文档、断言和验证配置；同 Scope 漏改/失败直接修复重验，不创建额外流程。
- 出现实质新方案、breaking contract/schema、权限、安全、持久数据、验收改变、未授权外部动作或无法完整验证时，停止相关写入并按三个 Gate 路由。
- 每次只验证当前 Runtime 和交付层；除非 Human 明确要求跨 Runtime 验收，其他 Runtime 的安装、发现、行为或证据缺口只作后续反馈，不扩大或阻塞 source release。
- Review 只拦截会错误交付的关键问题；非 release-blocking 缺证据/改进项用 `Accepted with follow-up`。不追求全历史/全 Runtime，也不把“还能补证据”升级为 `Needs Fix`。

## 内容归属与信息密度

- 插件内的 Core、Adapter、Skill 与开发控制文档默认使用中文；Role、Skill、Runtime、API、字段名等只有保留英文才能避免歧义时才使用英文，不得用整段英文或未解释的英文缩写承载关键流程判断。
- 规则按“主体 → 进入条件 → 动作 → 结果/限制”陈述。只保留影响路由、授权、安全、恢复或验收的限制；删除背景解释、反向释义和同义补充。
- 一个事实一个 owner：项目事实归本文件，Runtime 机制归 Adapter，Role procedure 归 Skill，跨消费者稳定语义才进 Core；下游只引用 owner。
- 根目录 `PLUGIN_DESIGN.md` 是插件开发/评审顶层设计的唯一 owner，完整保存流程骨架和 Role/Skill 职责；它与 `AGENTS.md` 同属开发控制面，不进入 deployment manifest 所描述的插件包，也不是安装后 Runtime 依赖。只有维护者和 scenario evaluator 读取完整设计；Workflow Contract 自包含唯一 Runtime 路由，其他 Core 只定义局部判断，Skill 只携带自身职责/流程/边界，Adapter 只做 transport。Core、Skill、Adapter 不得要求消费者读取顶层设计，也不得复制整张流程骨架。
- 高层流程的节点、先后关系、分支、Role/Skill 职责或回路变化，按 `需求不变量 → PLUGIN_DESIGN.md → Workflow/对应 Core → 节点 Skill/Adapter 消费者 → Evolution（若改变长期或 breaking boundary）` 修改。节点内部判断或职责内 procedure 没有改变顶层设计时，直接修改唯一 Core/Adapter/Skill owner，不为“保持同步”改设计文档。
- Manager/路由分层固定为：`PLUGIN_DESIGN.md` 画出协调闭环；Workflow 只决定何时进入；Coordination 定义 assessment、依赖、readiness、dispatch/wait/return；Manager Skill 调用并消费；Adapter 组装 Runtime 参数。任一层越权时删除重复，不用补句解释。
- Codex 自动模型组合、选择条件、`agent_type/model/reasoning_effort/fork_turns` 与 fallback 只在 Codex Adapter 存在。顶层设计、Core、Skill、README 和通用历史说明不得复制当前型号表；Markdown 映射由 owner review 与 Runtime scenario 验证，不用正则或 marker 测试锁定文字。将来若有机器可读配置，测试配置消费者而不是说明文本。
- 当前机制替代旧机制时，active surface 删除旧副本并引用现行 owner；冻结历史文档只保留最短 superseded 入口，Evolution 不新增历史表格行或版本章节。
- Test/validator 不得读取顶层设计、README、Core、Adapter 或 `SKILL.md` 后用正则、marker、整句存在/缺失、段落顺序或字数断言来证明语义。生产脚本测试应调用真实入口，检查可解析状态、文件/副作用、幂等、失败恢复和禁止行为；生成 Markdown 只有在它本身是生产输出时才可作为结果核对，且不得借此证明 Role 路由或 Runtime 行为。Skill trigger、Role 路由、dispatch/return 与 Runtime 参数只用真实 scenario smoke 或明确标记未验证。
- 路径术语是硬约束：Human 或配置提供的目录用 `base`；解析、派生后实际生效的目录用 `root`；文件及其位置用 `path`；非文件的证据、owner、Runtime 标识或间接指向用 `reference`。不得使用 `locator`，也不得用 `reference` 代替本应明确的文件 `path`；修改既有内容时按该分类消除混用。
- `description` 只回答“何时用/何时不用”；正文才写首查位置、扩大条件、动作、交付和停止边界。metadata prompt 只给自然入口，不复述正文流程。
- Skill 正文默认按“职责/功能 → 输入与首查 → 动作顺序 → 输出 → 停止与禁止边界”组织；Adapter 默认按“实现的 Core 合同 → Runtime 能力映射 → 调用参数 → fallback/恢复 → Runtime 证据边界”组织。章节名称服从实际语义，不为套用结构重复内容。
- Adapter 单 Runtime；Skill Runtime-neutral；显式 setup 只管对应配置；README 只保留入口、最小用法和 Runtime owner 导航；完整流程与职责只在根目录 `PLUGIN_DESIGN.md`；历史/迁移归具名文档。
- Planner、Executor、Reviewer 三个 Role Skill 必须分别写清职责、工作流和边界。修改前先判断 delta 是否仍在该 Role 已声明的输入、输出和禁止边界内；如果新增职责、输出类型、调用 owner 或跨节点路线，先按高层流程变更处理，不能直接给 Skill 补一步。
- Manager、Clarify、Feedback、using-sacha、document-project 等控制/支持 Skill 只实现 `PLUGIN_DESIGN.md` 中的对应节点或闭环；setup-project、setup-agents 等主流程外 Skill 必须写清功能、概略工作流和副作用边界。迭代可改已声明功能内做法；新增功能、触发方式、外部副作用或跨节点接管属于顶层设计变化，不得以局部修复混入。
- 新增或扩展规则、Role、Gate、Artifact、状态、字段、模板或 validator 必须对应真实失败或重复低效，并明确唯一 owner、直接 consumer、改变的判断与可证伪方式；优先补强现有 owner，缺一项就不增加。“更完整/更规范”不是扩产品面的理由，示例、标签和局部做法不得自动升级为 Core 合同或必填格式。
- Hash 不是通用确认字段或展示信息。新增或保留 hash 前必须指出直接校验它的 consumer 和它防止的真实失败；仅在并发/覆盖保护、不可变产物身份或跨边界字节一致性确实依赖精确内容时使用。路径、稳定标识、版本、结构校验或直接内容比较已足够时不得再加 hash；不得要求 Human 手工读取、复制或复述可由工具传递和校验的 hash，也不得在结果中重复展示只供内部事务使用的 hash。修改相关流程时一并删除无消费者、重复或纯装饰性的旧 hash。
- 精简或压缩只提高表达密度，不得以语义模糊换字数：可删除铺垫、常识、历史、同义重复和无消费者说明；必须保留明确的主体、trigger/进入条件、动作及先后依赖、退出/停止/恢复条件、例外、Owner/Human 决策点、授权、安全、失败/未验证、Evidence、验收、Entry Condition 和 schema。压缩后若需要依赖上下文猜测、存在多种合理解释或无法证明语义等价，则保留原文；若会改变流程判断，停止该部分并把语义 delta 交给 Human 二次确认。
- 多种做法成立时写判断原则；稳定参数写配置；脆弱且重复的机械顺序写 script 并实跑。
- 主流程脱离 Sacha、固定 Gate、Scope/Handoff 仍能完成；编排只增强协调、恢复或独立验收。
- 默认复用 Workflow Contract 的同一套通用 Runtime 流程；提速应关闭没有事实依据的 Gate、跳过不成立的候选并避免加载无消费者 owner，不得为提速增加特殊 task、target 限制、隐藏旁路或第二套 lifecycle。确需特殊流程时，先向 Human 提交真实 failure mode、通用流程不足、拟新增节点/边/owner 与影响，取得明确批准后由维护者先修改 `PLUGIN_DESIGN.md`。

## 产品边界

- 产品面以 `PLUGIN_DESIGN.md` 为准：`using-sacha` 是唯一默认入口；生产 Role 只有 Planner、Executor、Reviewer，三者可作为高级直接入口；Clarify 是主工作流唯一可显式调用的支持节点。Manager 只能由调用 owner 在 Gate 打开后调用，document-project 只能由收尾候选路由，二者都不是用户入口。Feedback 是独立显式支持入口：Human 只在另一个真实任务手动调用，可提交流程问题、使用反馈或插件开发想法；调用本身授权来源任务调查并转移 owner，但不授权目标任务写入或外部动作。setup-project、setup-agents 是主流程外显式配置能力，不进入主工作流。
- 任何新增 Role、Skill 功能、节点、连线、Outcome 去向或跨节点 owner transfer 都先改 `PLUGIN_DESIGN.md` 并取得 Human 对产品面变化的明确确认，再修改 Core 与直接消费者。现有职责内 procedure、提示词或证据细节不自动升级为顶层设计变化。
- Core 只容纳流程节点间被多个消费者共享的稳定判断；单 Skill 的 trigger、procedure、局部状态或格式留在 Skill，单 Runtime 的 transport/模型/恢复留在 Adapter，项目特例留在 Project Integration/Domain Skill。不能指出第二个真实消费者时，不新增 Core taxonomy 或必填字段。
- Hook 不得接受/替代 Sacha、扩大授权或参与恢复。新增 hook/MCP/app/外部服务/权限字段需明确批准；目标必需的 repo-local asset/script/manifest 元数据按 Scope 修改验证。

| 变化类型 | 修改与核查范围 |
| --- | --- |
| 高层流程节点、连线、Role/Skill 职责或 owner transfer | `PLUGIN_DESIGN.md` 先行；再改 Workflow/对应 Core、节点 Skill、受影响 Adapter 与 Evolution boundary；以 scenario/runtime 证据验证，不增加 prose test |
| Core 节点内部判断 | 修改唯一 Core owner，再核查直接调用/返回 Skill 与受影响 Adapter；顶层设计没变就不改 `PLUGIN_DESIGN.md` |
| Role 或支持 Skill 的局部 procedure | 必须落在已声明职责/功能内；同步 metadata 和直接调用/返回方，超界则升级为高层流程变化 |
| 单 Runtime transport、模型、安装或恢复 | 只改目标 Adapter、相关 metadata/manifest 与真实 Runtime 验证；不联动其他 Runtime 或 Core |
| Setup/生成器/Provider Binding | 修改具体 Skill 与生产脚本，核查 capability provider guide 和真实生成行为测试；不把生成格式提升为 Core 流程 |
| 产品版本、source candidate 或 release 状态 | Evolution、两个 deployment manifest 与 Git tag；release validator 只核对机器可解析部署身份和可执行入口 |

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
- Source validator 只核对 JSON/TOML/YAML 等机器可解析部署身份、实际文件结构、可执行入口和 Git release identity；Markdown 链接与语义由 owner review/官方 Plugin/Skill validator 负责，不写正则、marker、句子存在性、段落顺序或字数 Gate。
- 生产脚本用隔离临时目录的正反例、幂等、失败恢复和真实副作用测试；Skill trigger、Role 路由与 Runtime 调用用真实 scenario smoke。前一层不得替代后一层。
- Role/流程 scenario 使用 [`tests/runtime-scenarios/README.md`](tests/runtime-scenarios/README.md) 的任务包流程：执行 Agent 只看中性 task、隔离 workspace 规则与正式入口 Skill/Core，不读取插件 README 或 scenario oracle；独立 evaluator 才用顶层图核对偏移。必须真实发起 clean-context subagent、运行 verifier 并检查原生派发/return 与 workspace delta。嵌套 target 消失前由 evidence recipient 保存首次 wait 前的 live tree 和 target 直接 start/terminal，不得用执行者事后自报替代。未安装或不是 fresh task 时只能记为 `source-scenario`，不得宣称 fresh discovery/Runtime 已验证。
- 能力完成声明须定位生产入口；模板、fixture、字符串或自报只证明其自身，未运行的行为仍标记未验证。

`plugin-eval` 可用于结构、描述和 token budget 诊断，但不是必跑 Gate，也不能替代官方 validator、真实 schema、代码测试或 runtime smoke。不得仅为提高评分添加无权威依据的 manifest 字段、英文触发词、reference 或其他产品内容；评估器输入兼容问题使用 task-local 等价镜像并报告限制，不修改安装 cache 或正式源码迁就工具。

发布分两种模式：

- Human 说“快速发版”时，默认递增 patch 版本；只人工核对 Evolution 的 release/candidate 状态，并机器核对两个 deployment manifest、annotated tag 到 `HEAD` 的指向及 push 后远端分支/tag。跳过普通回归、Skill/Plugin validator、完整 release coherence、安装/cache parity、fresh discovery 和 runtime。
- Human 说“发版”时，运行风险对应的普通验证与完整 metadata coherence；安装和 runtime 仍按明确授权与发布目标决定。

普通发版收尾运行 metadata coherence：

```powershell
python -B tests/validate_release_coherence.py --version <version> --phase candidate
python -B tests/validate_release_coherence.py --version <version> --phase release
```

`candidate` 在 source candidate 阶段运行，只核对机器可解析部署身份和生产入口；`release` 在 commit、annotated tag 已建立且 Evolution 已人工切换为 release 后运行，并额外核对 annotated tag 精确指向 `HEAD`。该脚本不读取 README/Core/Adapter/Skill/Evolution 的说明文字。

## 安装授权 Gate

- Marketplace 注册、安装、refresh、removal/reinstall 需要 Human 明确授权；实施批准不隐含外部状态授权。
- 使用 `read_marketplace_name.py` 从 `.agents/plugins/marketplace.json` 读取 marketplace 名称；不得根据目录名猜测。
- 授权后按目标 Adapter 执行并验证 marketplace/plugin list；Scope、版本、目标、branch/remote 未变化时不重复询问。
- manifest 使用批准的精确 semantic version，不加 cachebuster；不得编辑 cache、应用权限或系统 PATH。
