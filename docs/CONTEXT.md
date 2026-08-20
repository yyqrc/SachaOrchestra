# Sacha Orchestra 项目上下文

> 文档身份：插件开发使用；不进入发布插件。

本文是开发控制面提炼术语与规则的统一入口及开发专用术语 Owner，供 `PLUGIN_DESIGN.md`、插件开发、维护和评审使用；发布插件不包含或读取本文。本文完整包含插件内共享术语的同步视图，并可额外拥有仅供开发控制面消费的术语；因此本文的术语集合必须包含[术语合同](../plugins/sacha-orchestra/core/terminology-contract.md)的术语集合。术语合同是插件内共享术语的唯一 Runtime Owner，只有两边交集必须强双向同步。

本文只保存术语定义、边界、开发侧直接消费者和可证伪方式，不复制入口、Role、批准、迁移或协调动作；开发侧完整流程读取 [`PLUGIN_DESIGN.md`](../PLUGIN_DESIGN.md)，安装后 Runtime 动作读取插件内对应 Core Owner。

## 插件内共享术语

| 术语 | Runtime Owner | 定义与边界 | 直接消费者 | 可证伪方式 |
| --- | --- | --- | --- | --- |
| 入口候选 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 初次判断或语义转折中，已有事实表明进入 Sacha 可能改变执行方式，但 Human 尚未决定是否接受的入口分类；只用于一次性提议与重复抑制，不表示已接受 Sacha、打开 Gate 或取得授权。 | `PLUGIN_DESIGN.md`、Intake Contract、using-sacha Skill、插件 README | 若该分类直接打开 Gate、取得授权或代表已接受 Sacha，定义失效。 |
| 主任务 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 当前持有工作流 Owner 并负责推进根终态的用户任务；迁移成功后指新 Owner 所在的目标任务。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Coordination Contract、Role Skill、Runtime Adapter | 若委派 Agent 取得根终态或派发权，或迁移后来源任务仍为 Owner，定义被违反。 |
| 单层派发 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 主任务创建全部委派 Agent；每个委派 Agent 都是主任务的直接子级，不调用 Manager 或创建下级 Agent；迁移成功后改由新主任务执行。 | `PLUGIN_DESIGN.md`、Workflow Contract、Coordination Contract、Manager Skill、Runtime Adapter | 若任一委派 Agent 创建下级 Agent 或调用 Manager，定义被违反。 |
| 委派 Agent | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 主任务为一个工作单元创建的 Agent；只完成该单元并返回，不取得工作流 Owner 或派发权。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Coordination Contract、Role Skill、Runtime Adapter | 若其接管工作流 Owner、根终态或派发权，定义被违反。 |
| 协调请求 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 委派 Agent 需要继续拆分、依赖协调或额外 Agent 时，向主任务返回重新评估所需的原因、候选单元、依赖或 reference；只定义返回语义，不新增状态、字段或 Artifact。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Coordination Contract、Role Skill、Runtime Adapter | 若它成为新状态、必填 schema 或 Artifact，定义被违反。 |
| 普通批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Human 批准 Spec，且未明确选择新任务执行。 | `PLUGIN_DESIGN.md`、Workflow Contract、Planner Skill、Runtime Adapter | 若未明确选择新任务也触发任务迁移，定义被违反。 |
| 明确迁移批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Human 批准 Spec，并通过选择项或同义明确表达选择新任务执行；不表示执行任务迁移前提已经满足。 | `PLUGIN_DESIGN.md`、Workflow Contract、Coordination Contract、Planner Skill、Runtime Adapter | 若普通批准被视为该批准，或该批准直接证明迁移前提，定义被违反。 |
| 可靠迁移信号 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Spec 已持久化且可达，并有可核实的 Runtime 上下文占用高或压缩事实，或存在不依赖未落盘对话的可观察多阶段长历史；只决定 Human 审阅选项的推荐顺序。 | `PLUGIN_DESIGN.md`、Workflow Contract、Planner Skill | 若它替代 Human 批准或成为迁移授权，定义被违反。 |
| 执行任务迁移前提 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Human 已明确迁移批准，Spec 已持久化、可达且获批，Entry Condition 已满足，当前主任务是唯一工作流 Owner，且同一 Scope 没有活跃执行写入者；只用于批准 Spec 后迁到新任务执行，不适用于 Feedback Owner 转移，也不改变已批准的 Spec、Scope 或验收。 | `PLUGIN_DESIGN.md`、Workflow Contract、Coordination Contract、Runtime Adapter | 若缺少任一条件仍迁移，或 Feedback 使用该前提，定义被违反。 |
| `base` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Human 或配置直接提供的目录；尚未表示解析、派生或验证后的实际生效目录。 | setup-project Skill/脚本、Capability Provider Guide、Planner Skill | 若现行消费者把派生后的实际目录定义为 `base`，定义失效并须修正。 |
| `root` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 从 `base`、配置或发现结果解析、派生并实际生效的目录；不得代指任意输入目录。 | setup-project、Planner、document-project Skill/脚本、插件 README | 若现行消费者把未经解析的输入目录定义为 `root`，定义失效并须修正。 |
| `path` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 文件或目录在文件系统中的位置；用于可直接读取、写入或解析的文件系统目标。 | Artifact Protocol、Planner/Explore/Reviewer、setup-project/document-project Skill/脚本 | 若目标不是文件系统对象却仍使用 `path`，或文件位置只写为 `reference`，定义被违反。 |
| `reference` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 非文件的证据、Owner、Runtime 标识或间接指向；不得代替本应明确的文件 `path`，也不得另建 `locator` 作为同义术语。 | Core、Role/支持 Skill、Runtime Adapter、Artifact 与报告模板 | 若直接文件位置被称为 `reference`、非文件指向被要求作为文件读取，或现行内容使用 `locator` 混称，定义被违反。 |
| 能力加载策略 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Project Integration 的已确认 Capability Binding 对规范 Skill 的加载条件；只决定何时读取并采用 Skill，不表示授权、前置满足或动作已执行。 | Workflow Contract、setup-project Skill、Planner/Explore/Executor/Reviewer Skill、Capability Provider 接入指南 | 若策略直接授予动作、绕过 Skill 前置，或 Runtime 消费者无法取得四种策略的加载条件，定义被违反。 |
| Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 供执行、恢复、复核或返回消费者使用的工作流记录；不替代原始事实、Human 授权或流程状态。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Assurance Contract、Coordination Contract、Artifact Protocol、Role/支持 Skill、Runtime Adapter | 若 Artifact 替代原始事实、Human 授权或流程状态，定义被违反。 |
| Spec Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Planner 基于已核实项目事实和 Human 决定形成、经 Human 批准后作为实施与评审基线的目标项目实施规格；内容格式与权威关系由 Artifact Protocol 定义。 | Workflow Contract、Coordination Contract、Artifact Protocol、Planner/Executor/Reviewer Skill、Runtime Adapter | 若其不是目标项目实施规格、不能作为实施与评审基线，或被其他 Artifact 替代，定义被违反。 |
| Roadmap | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 面向项目 Human 与 Agent 的自包含长期路线文档，保存目标、当前状态、阶段、依赖、完成信号、Spec 映射、决策前沿、`Unknown` 与排除范围；不是 Artifact 或 Spec，不授予实施，也不保存 Sacha 内部路由。 | `PLUGIN_DESIGN.md`、setup-project/roadmap/document-project Skill 与脚本、插件 README | 若移除 Sacha 上下文后无法理解路线，或 Roadmap 直接成为实施授权、Spec、任务状态或工作流路由，定义被违反。 |
| Spec 完成 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 当前任务已进入 `goal_complete`，必需验证与适用 Review 已满足后，把当前唯一已批准 Spec Artifact 的既有状态行原位标记为“已完成”；不移动、改名或生成新 Artifact。 | `PLUGIN_DESIGN.md`、Workflow Contract、Artifact Protocol、closeout Skill | 若未到合法完成终态即写入，或移动 Spec、创建平行完成 Artifact，定义被违反。 |
| 探索决定记录 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Spec 形成前保存后续规划或恢复会消费的已确认决定、未决项和最小恢复边界的 Artifact。 | Artifact Protocol、Explore/Planner Skill | 若它被当作获批 Spec 或执行授权，定义被违反。 |
| Execution Report | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 保存实际变更、验证、偏差、风险和证据 reference 的可恢复索引。 | Workflow Contract、Artifact Protocol、Executor/Reviewer/document-project Skill | 若它替代原始证据或 Reviewer 判断，定义被违反。 |
| Review Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 保存 Reviewer 判断、证据缺口与下一路由的 Artifact。 | Assurance Contract、Artifact Protocol、Reviewer Skill | 若它不含 Reviewer 判断与下一路由，或被实施报告替代，定义被违反。 |
| Handoff | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 供既有跨 Role 或恢复消费者继续工作的最小信息；不是流程节点或完成证据。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Assurance Contract、Coordination Contract、Artifact Protocol、Role/支持 Skill、Runtime Adapter | 若它成为流程节点、授权或完成证据，定义被违反。 |

## 开发控制面专用术语

候选术语只有在存在多个现行开发控制面直接消费者、且没有多个发布插件直接消费者时才由本文定义；在本节记录定义与边界、直接消费者和可证伪方式，不为保持与术语合同集合相等而提升到 Runtime。

## 术语边界

- 普通批准与明确迁移批准按 Human 是否明确选择新任务执行区分；只批准 Spec 或未明确选择新任务时属于普通批准。
- 可靠迁移信号只改变选项顺序，不构成 Human 批准，也不能替代明确迁移批准。
- 明确迁移批准只证明 Human 选择了迁移分支，不证明执行任务迁移前提已经满足。
- 执行任务迁移前提只用于批准 Spec 后迁到新任务执行；Feedback Owner 转移不使用该前提。
- Artifact 只索引或承载消费者需要的信息；真实文件、外部状态、文件差异和命令原始输出仍决定实现与验证事实。
- Spec 完成只改变当前唯一 Spec Artifact 的状态，不改变其 path 或内容身份；Spec Artifact、探索决定记录、Execution Report、Review Artifact 与项目文档不得互相替代。

## Owner 与同步边界

- 修改者 → 修改插件内共享术语或规则 → 同次更新术语合同、本文对应条目并核查直接消费者 → 受影响映射必须同次更新。
- 修改者 → 修改开发控制面专用术语或规则 → 只更新本文与开发侧直接消费者 → 不得因本文存在该术语就写入发布插件。
- 修改者 → 开发控制面专用术语新增多个发布插件直接消费者 → 先将定义与边界提升到术语合同，再同步本文及受影响映射 → 提升完成前发布插件不得消费该术语。
- 开发者或 Reviewer → 发现共享术语两边不一致 → 按术语合同恢复 Runtime 词义并完成交集同步；发现开发专用术语与消费者不一致时按本文恢复 → 同步完成前不得使用受影响术语或声明完成。
- 下游消费者 → 使用已提炼术语 → 只保留自身映射 → 共享定义只在术语合同与本文对应条目保存，开发专用定义只在本文保存。
