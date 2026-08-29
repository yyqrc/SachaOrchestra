# Sacha Orchestra 项目上下文

> 文档身份：插件开发使用；不进入发布插件。

本文是开发文档侧提炼术语与规则的统一入口，并负责开发专用术语，供 `PLUGIN_DESIGN.md`、插件开发、维护和评审使用；发布插件不包含或读取本文。本文完整包含插件内共享术语的同步定义，也可以保存只供开发文档使用的术语；因此本文的术语集合必须包含[术语合同](../plugins/sacha-orchestra/core/terminology-contract.md)的术语集合。术语合同负责安装后使用的共享术语，只有两边共有的术语必须保持双向一致。

本文只保存术语定义、边界、开发侧使用方和核验方法，不复制入口、角色、批准、迁移或协调动作；开发侧完整流程读取 [`PLUGIN_DESIGN.md`](../PLUGIN_DESIGN.md)，安装后的动作读取插件内相应核心合同。

## 插件内共享术语

| 术语 | 插件内定义位置 | 定义与边界 | 使用方 | 核验方法 |
| --- | --- | --- | --- | --- |
| 入口候选 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 初次判断或需求发生实质转折时，已有事实表明进入 Sacha 可能改变执行方式，但用户尚未决定是否接受；只用于一次性提议和避免重复提议，不表示已经接受 Sacha、打开决策关口（Gate）或取得授权。 | `PLUGIN_DESIGN.md`、入口合同、using-sacha 技能、插件 README | 若该分类直接打开决策关口、取得授权或代表已经接受 Sacha，定义失效。 |
| Direct | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 当前主任务尚未进入 Sacha 的正式流程，在既有目标、范围、授权和验收内由当前上下文直接完成；仍须遵守适用的项目规则、使用领域能力并完成必要验证，需求发生实质转折并形成新的入口候选时重新判断。 | 根 `AGENTS.md`、`PLUGIN_DESIGN.md`、入口合同、工作流合同、using-sacha 技能、插件 README、运行环境适配器 | 若尚未接受 Sacha 却进入生产角色、决策关口或工作记录，或者把 Direct 解释为可以跳过项目规则、领域能力或必要验证，定义失效。 |
| Direct Scope | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 当前任务围绕同一目标直接推进时采用的实施范围，由用户目标、明确约束和已批准实施规格（Spec，若有）界定；预计文件列表只有在用户或已批准实施规格明确指定时才成为硬边界。 | 根 `AGENTS.md`、工作流合同 | 若没有用户或已批准实施规格的精确文件约束，却把预计文件列表作为硬边界，定义失效。 |
| 主任务 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 当前负责整个工作流程并推进最终完成状态的用户任务；迁移成功后改指承担该职责的新任务。 | `PLUGIN_DESIGN.md`、入口合同、工作流合同、协调合同、角色技能、运行环境适配器 | 若委派代理接管最终完成状态或派发权，或者迁移后来源任务仍负责整个流程，定义失效。 |
| 单层派发 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 主任务创建全部委派代理（Agent）；每个委派代理都是主任务的直接子级，不调用 Manager，也不创建下级代理；迁移成功后改由新主任务执行。 | `PLUGIN_DESIGN.md`、工作流合同、协调合同、Manager 技能、运行环境适配器 | 若任一委派代理创建下级代理或调用 Manager，定义失效。 |
| 委派 Agent | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 主任务为一个工作单元创建的代理；只完成该单元并返回，不接管整个工作流程或派发权。 | `PLUGIN_DESIGN.md`、入口合同、工作流合同、协调合同、角色技能、运行环境适配器 | 若其接管整个工作流程、最终完成状态或派发权，定义失效。 |
| 协调请求 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 委派代理需要继续拆分、协调依赖或增加代理时，向主任务返回重新评估所需的原因、候选单元、依赖或 `reference`；只定义返回含义，不新增状态、字段或工作记录（Artifact）。 | `PLUGIN_DESIGN.md`、入口合同、工作流合同、协调合同、角色技能、运行环境适配器 | 若它成为新状态、必填数据格式或工作记录，定义失效。 |
| 普通批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 用户批准实施规格（Spec），但未明确选择由新任务执行。 | `PLUGIN_DESIGN.md`、工作流合同、Planner 技能、运行环境适配器 | 若未明确选择新任务也触发任务迁移，定义失效。 |
| 明确迁移批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 用户批准实施规格，并通过选择项或同义表达明确选择由新任务执行；不表示执行任务迁移的前提已经满足。 | `PLUGIN_DESIGN.md`、工作流合同、协调合同、Planner 技能、运行环境适配器 | 若普通批准被视为该批准，或者该批准直接证明迁移前提，定义失效。 |
| 可靠迁移信号 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 实施规格已经持久化且可访问，并存在可核实的运行环境上下文占用较高或压缩事实，或者存在不依赖未落盘对话、可观察的多阶段长历史；只决定用户审阅选项的推荐顺序。 | `PLUGIN_DESIGN.md`、工作流合同、Planner 技能 | 若它替代用户批准或成为迁移授权，定义失效。 |
| 执行任务迁移前提 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 用户已经明确批准迁移，实施规格已经持久化、可访问且获批，进入条件（Entry Condition）已经满足，当前主任务是唯一负责整个流程的任务，并且同一范围内没有正在写入的执行者；只用于批准实施规格后迁到新任务执行，不适用于 Feedback 的负责位置转移，也不改变已批准的实施规格、范围或验收。 | `PLUGIN_DESIGN.md`、工作流合同、协调合同、运行环境适配器 | 若缺少任一条件仍迁移，或者 Feedback 使用该前提，定义失效。 |
| `base` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 用户或配置直接提供的目录；尚未表示解析、派生或验证后的实际生效目录。 | setup-project 技能或脚本、能力提供方指南、Planner 技能 | 若现行使用方把派生后的实际目录定义为 `base`，定义失效并须修正。 |
| `root` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 从 `base`、配置或发现结果解析、派生并实际生效的目录；不得代指任意输入目录。 | setup-project、Planner、document-project 技能或脚本、插件 README | 若现行使用方把未经解析的输入目录定义为 `root`，定义失效并须修正。 |
| `path` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 文件或目录在文件系统中的位置；用于可直接读取、写入或解析的文件系统目标。 | 工作记录协议、Planner、Explore、Reviewer、setup-project 或 document-project 技能和脚本 | 若目标不是文件系统对象却仍使用 `path`，或者文件位置只写为 `reference`，定义失效。 |
| `reference` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 非文件形式的证据、负责位置、运行环境标识或间接指向；不得代替本应明确的文件 `path`，也不得另建 `locator` 作为同义术语。 | 核心合同、角色或支持技能、运行环境适配器、工作记录与报告模板 | 若直接文件位置被称为 `reference`、非文件指向被要求作为文件读取，或者现行内容使用 `locator` 混称，定义失效。 |
| 显式发布文档目标 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 用户在明确的 `document-project` 请求中直接提供项目 `root` 内的 Markdown `path`，且文档类型为 `change-archive` 或 `system-guide`；不包括 Roadmap、Project Context、目录或 `root`，也不包括由项目接入（Project Integration）派生的目标。该术语只标识输入类别，授权、流转和写入动作仍归相应负责文件。 | `PLUGIN_DESIGN.md`、入口合同、工作流合同、document-project 技能、插件 README | 若未直接提供文件 `path`、类型不符或目标由配置派生却仍使用该术语，定义失效。 |
| 技能加载策略 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 项目接入中为规范技能确认的加载条件；只决定何时读取并采用技能，不表示已经获得授权、满足前置条件或执行动作。 | 工作流合同、setup-project 技能、Planner、Explore、Executor、Reviewer 技能、能力提供方接入指南 | 若策略直接授予动作、绕过技能前置条件，或者运行环境中的使用方无法取得四种策略的加载条件，定义失效。 |
| Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 供执行、恢复、复核或后续使用方继续工作的流程记录；不替代原始事实、用户授权或流程状态。 | `PLUGIN_DESIGN.md`、入口合同、工作流合同、保障合同、协调合同、工作记录协议、角色或支持技能、运行环境适配器 | 若 Artifact 替代原始事实、用户授权或流程状态，定义失效。 |
| Spec Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Planner 根据已核实的项目事实和用户决定形成、经用户批准后作为实施与评审基线的目标项目实施规格；内容格式与权威关系由工作记录协议（Artifact Protocol）定义。 | 工作流合同、协调合同、工作记录协议、Planner、Executor、Reviewer 技能、运行环境适配器 | 若其不是目标项目实施规格、不能作为实施与评审基线，或者被其他工作记录替代，定义失效。 |
| Roadmap | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 面向项目用户和代理的自包含长期路线文档，保存目标、当前状态、阶段、依赖、完成信号、实施规格映射、接下来需要作出的决定、`Unknown` 和排除范围；不是工作记录或实施规格，不授予实施，也不保存 Sacha 内部流转。 | `PLUGIN_DESIGN.md`、setup-project、roadmap、document-project 技能和脚本、插件 README | 若移除 Sacha 上下文后无法理解路线，或者 Roadmap 直接成为实施授权、实施规格、任务状态或工作流流转，定义失效。 |
| Spec 完成 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 当前任务进入 `goal_complete`，必需验证和适用评审均已满足后，把当前唯一已批准 Spec Artifact 的既有状态行原位标记为“已完成”；不移动、改名或生成新工作记录。 | `PLUGIN_DESIGN.md`、工作流合同、工作记录协议、closeout 技能 | 若未到合法完成状态即写入，或者移动实施规格、创建平行完成工作记录，定义失效。 |
| 探索决定记录 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 实施规格形成前，保存后续规划或恢复会使用的已确认决定、未决项和最小恢复信息的工作记录。 | 工作记录协议、Explore 或 Planner 技能 | 若它被当作获批实施规格或执行授权，定义失效。 |
| Execution Report | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 保存实际变更、验证、偏差、风险和证据 `reference` 的可恢复索引。 | 工作流合同、工作记录协议、Executor、Reviewer、document-project 技能 | 若它替代原始证据或评审者判断，定义失效。 |
| Review Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 保存评审者判断、证据缺口和下一步流转的工作记录。 | 保障合同、工作记录协议、Reviewer 技能 | 若它不含评审者判断和下一步流转，或者被实施报告替代，定义失效。 |
| Handoff | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 供跨角色工作或恢复时继续使用的最小信息；不是流程节点或完成证据。 | `PLUGIN_DESIGN.md`、入口合同、工作流合同、保障合同、协调合同、工作记录协议、角色或支持技能、运行环境适配器 | 若它成为流程节点、授权或完成证据，定义失效。 |

## 开发文档专用术语

候选术语只有在存在多个现行开发文档使用方、且没有多个发布插件使用方时才由本文定义；在本节记录定义与边界、使用方和核验方法，不为了与术语合同集合相等而提升为安装后术语。

## 术语边界

- 普通批准与明确迁移批准按用户是否明确选择新任务执行区分；只批准实施规格或未明确选择新任务时属于普通批准。
- 可靠迁移信号只改变选项顺序，不构成用户批准，也不能替代明确迁移批准。
- 明确迁移批准只证明用户选择了迁移分支，不证明执行任务迁移前提已经满足。
- 执行任务迁移前提只用于批准实施规格后迁到新任务执行；Feedback 的负责位置转移不使用该前提。
- 工作记录（Artifact）只索引或承载使用方需要的信息；真实文件、外部状态、文件差异和命令原始输出仍决定实现与验证事实。
- Spec 完成只改变当前唯一 Spec Artifact 的状态，不改变其 `path` 或内容身份；Spec Artifact、探索决定记录、Execution Report、Review Artifact 与项目文档不得互相替代。

## 负责位置与同步边界

- 修改插件内共享术语或规则时，修改者必须同时更新术语合同、本文对应条目和实际使用方；受影响映射必须在同一次修改中更新。
- 修改开发文档专用术语或规则时，只更新本文与开发侧使用方；不得因为本文存在该术语就把它写入发布插件。
- 开发文档专用术语开始被多个发布插件使用时，先把定义与边界提升到术语合同，再同步本文及受影响映射；提升完成前发布插件不得使用该术语。
- 发现两边的共享术语不一致时，开发者或评审者按术语合同恢复安装后的词义并完成共有内容同步；发现开发专用术语与使用方不一致时按本文恢复。同步完成前不得使用受影响术语或声明完成。
- 使用已提炼术语的文件只保留自身映射；共享定义只在术语合同与本文对应条目保存，开发专用定义只在本文保存。
