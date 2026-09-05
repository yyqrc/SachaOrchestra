# Sacha Orchestra 项目上下文

> 文档身份：插件开发使用；不进入发布插件。

本文负责开发专用术语，并提供插件内共享术语的定义入口、使用方和核验方法，供 `PLUGIN_DESIGN.md` 及开发维护使用；发布插件不包含或读取本文。共享术语的完整定义只由[术语合同](../plugins/sacha-orchestra/core/terminology-contract.md)维护。

本文只保存术语定义、边界、开发侧使用方和核验方法，不复制入口、角色、批准、迁移或协调动作；开发侧完整流程读取 [`PLUGIN_DESIGN.md`](../PLUGIN_DESIGN.md)，安装后的动作读取插件内相应核心合同。

## 插件内共享术语

| 术语 | 插件内定义位置 | 使用方 | 核验方法 |
| --- | --- | --- | --- |
| 入口候选 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口合同、using-sacha 技能、插件 README | 若该分类直接打开决策关口、取得授权或代表已经接受 Sacha，定义失效。 |
| Direct | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 根 `AGENTS.md`、`PLUGIN_DESIGN.md`、入口合同、工作流合同、using-sacha 技能、插件 README、运行环境适配器 | 若尚未接受 Sacha 却进入生产角色、决策关口或工作记录，或者把 Direct 解释为可以跳过项目规则、领域能力或必要验证，定义失效。 |
| Direct Scope | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 根 `AGENTS.md`、工作流合同 | 若没有用户或已批准实施规格的精确文件约束，却把预计文件列表作为硬边界，定义失效。 |
| 主任务 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口合同、工作流合同、协调合同、角色技能、运行环境适配器 | 若委派代理接管最终完成状态或派发权，或者迁移后来源任务仍负责整个流程，定义失效。 |
| 单层派发 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流合同、协调合同、Manager 技能、运行环境适配器 | 若任一委派代理创建下级代理或调用 Manager，定义失效。 |
| 委派 Agent | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口合同、工作流合同、协调合同、角色技能、运行环境适配器 | 若其接管整个工作流程、最终完成状态或派发权，定义失效。 |
| 协调请求 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口合同、工作流合同、协调合同、角色技能、运行环境适配器 | 若它成为新状态、必填数据格式或工作记录，定义失效。 |
| 普通批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流合同、Planner 技能、运行环境适配器 | 若未明确选择新任务也触发任务迁移，定义失效。 |
| 明确迁移批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流合同、协调合同、Planner 技能、运行环境适配器 | 若普通批准被视为该批准，或者该批准直接证明迁移前提，定义失效。 |
| 可靠迁移信号 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流合同、Planner 技能 | 若它替代用户批准或成为迁移授权，定义失效。 |
| 执行任务迁移前提 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流合同、协调合同、运行环境适配器 | 若缺少任一条件仍迁移，或者 Feedback 使用该前提，定义失效。 |
| `base` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | setup-project 技能或脚本、能力提供方指南、Planner 技能 | 若现行使用方把派生后的实际目录定义为 `base`，定义失效并须修正。 |
| `root` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | setup-project、Planner、document-project 技能或脚本、插件 README | 若现行使用方把未经解析的输入目录定义为 `root`，定义失效并须修正。 |
| `path` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作记录协议、Planner、Explore、Reviewer、setup-project 或 document-project 技能和脚本 | 若目标不是文件系统对象却仍使用 `path`，或者文件位置只写为 `reference`，定义失效。 |
| `reference` | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 核心合同、角色或支持技能、运行环境适配器、工作记录与报告模板 | 若直接文件位置被称为 `reference`、非文件指向被要求作为文件读取，或者现行内容使用 `locator` 混称，定义失效。 |
| 显式发布文档目标 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口合同、工作流合同、document-project 技能、插件 README | 若未直接提供文件 `path`、类型不符或目标由配置派生却仍使用该术语，定义失效。 |
| 技能加载策略 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流合同、setup-project 技能、Planner、Explore、Executor、Reviewer 技能、能力提供方接入指南 | 若策略直接授予动作、绕过技能前置条件，或者运行环境中的使用方无法取得四种策略的加载条件，定义失效。 |
| Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口合同、工作流合同、保障合同、协调合同、工作记录协议、角色或支持技能、运行环境适配器 | 若 Artifact 替代原始事实、用户授权或流程状态，定义失效。 |
| Spec Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流合同、协调合同、工作记录协议、Planner、Executor、Reviewer 技能、运行环境适配器 | 若其不是目标项目实施规格、不能作为实施与评审基线，或者被其他工作记录替代，定义失效。 |
| Roadmap | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、setup-project、roadmap、document-project 技能和脚本、插件 README | 若移除 Sacha 上下文后无法理解路线，或者 Roadmap 直接成为实施授权、实施规格、任务状态或工作流流转，定义失效。 |
| Spec 完成 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流合同、工作记录协议、closeout 技能 | 若未到合法完成状态即写入，或者移动实施规格、创建平行完成工作记录，定义失效。 |
| 探索决定记录 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作记录协议、Explore 或 Planner 技能 | 若它被当作获批实施规格或执行授权，定义失效。 |
| Execution Report | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流合同、工作记录协议、Executor、Reviewer、document-project 技能 | 若它替代原始证据或评审者判断，定义失效。 |
| Review Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 保障合同、工作记录协议、Reviewer 技能 | 若它不含评审者判断和下一步流转，或者被实施报告替代，定义失效。 |
| Handoff | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口合同、工作流合同、保障合同、协调合同、工作记录协议、角色或支持技能、运行环境适配器 | 若它成为流程节点、授权或完成证据，定义失效。 |

## 开发文档专用术语

候选术语只有在存在多个现行开发文档使用方、且没有多个发布插件使用方时才由本文定义；在本节记录定义与边界、使用方和核验方法，不为了与术语合同集合相等而提升为安装后术语。

## 定义与引用维护

- 共享术语的含义与边界以[术语合同](../plugins/sacha-orchestra/core/terminology-contract.md)为准，流程动作以其引用的核心合同为准；本文不维护另一份完整定义。
- 修改共享术语或规则时，同次更新其负责文件和实际使用方；名称、位置或使用方变化时更新本文索引。
- 开发专用术语只在本文定义。开始被多个发布插件使用时，将定义提升到术语合同，开发侧改为引用并更新受影响映射。
- 发现使用方含义冲突时，按对应定义负责文件修正；实际使用方和引用未对齐前不声明该项完成。
