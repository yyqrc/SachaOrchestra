# Sacha Orchestra 项目上下文

> 文档身份：插件开发使用；不进入发布插件。

本文负责开发专用术语，并提供插件内共享术语的定义入口、使用方和核验方法，供 `PLUGIN_DESIGN.md` 及开发维护使用；发布插件不包含或读取本文。共享术语的完整定义只由[术语定义](../plugins/sacha-orchestra/core/terminology-contract.md)维护。

本文只保存术语定义、边界、开发侧使用方和核验方法，不复制入口、角色、批准、迁移或协调动作；开发侧完整流程读取 [`PLUGIN_DESIGN.md`](../PLUGIN_DESIGN.md)，安装后的动作读取插件内相应核心规则。

## 插件内共享术语

| 术语 | 插件内定义位置 | 使用方 | 核验方法 |
| --- | --- | --- | --- |
| 直接处理（Direct） | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 顶层设计、入口规则、工作流、入口技能、插件 README 和运行环境适配器 | 核对当前任务能否在已有授权内完成，以及是否仍执行适用的项目规则、领域技能和必要验证。 |
| 工作范围 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 根 `AGENTS.md`、入口规则、工作流规则、协调规则、角色技能 | 检查范围是否涵盖保留行为、排除项和适用条件，以及动作是否另有授权。直接推进时，核对硬性文件限制是否由用户或已批准规格明确指定。 |
| Owner | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 核心规则、角色技能、运行环境适配器、`PLUGIN_DESIGN.md` | 检查指的是负责文件还是负责任务，并核对局部负责人是否被误授主任务职责或额外授权。 |
| 工作单元 / 工作包 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 协调规则、Manager 技能、运行环境适配器 | 核对拆分是否基于独立交付结果。按实际前置条件核对能否开始，避免按代理、文件或 Spec 数量强拆。 |
| 主任务 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口规则、工作流规则、协调规则、角色技能、运行环境适配器 | 核对最终完成判断和派发权是否仍由主任务负责，以及迁移后是否已转给目标任务。 |
| 单层派发 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流规则、协调规则、Manager 技能、运行环境适配器 | 查宿主派发轨迹，核对委派代理是否创建下级代理或调用 Manager。 |
| 委派 Agent | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口规则、工作流规则、协调规则、角色技能、运行环境适配器 | 核对代理是否只完成并交回工作单元，有无接管整个流程、完成判断或派发权。 |
| 协调请求 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口规则、工作流规则、协调规则、角色技能、运行环境适配器 | 检查是否只用它向主任务返回需要协调的信息，以及有无把它当成新状态、必填数据格式或工作记录。 |
| 普通批准 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流规则、Planner 技能、运行环境适配器 | 核对用户未明确选择新任务时，是否在当前任务继续。 |
| 明确迁移批准 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流规则、协调规则、Planner 技能、运行环境适配器 | 核对用户是否明确选择新任务，以及是否另行核实迁移条件。 |
| 可靠迁移信号 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流规则、Planner 技能 | 核对提出迁移是否有具体收益，以及迁移是否仍取得用户明确批准。 |
| 执行任务迁移前提 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流规则、协调规则、运行环境适配器 | 核对实施任务迁移是否满足全部条件。Feedback 的负责人转移按它自己的条件判断。 |
| `base` | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | setup-project 技能或脚本、能力提供方指南、Planner 技能 | 核对它是否是直接提供的输入目录。 |
| `root` | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | setup-project、Planner、document-project 技能或脚本、插件 README | 核对它是否已从输入解析为实际生效的目录。 |
| `path` | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作记录规则、Planner、Explore、Reviewer、setup-project 或 document-project 技能和脚本 | 核对直接文件位置是否使用 `path`，以及非文件引用是否被误写为文件路径。 |
| `reference` | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 核心规则、角色或支持技能、运行环境适配器、工作记录与报告模板 | 核对非文件引用能否按其类型定位，以及是否混用文件 `path` 或引入 `locator` 别名。 |
| 显式发布文档目标 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口规则、工作流规则、document-project 技能、插件 README | 核对用户是否直接提供类型符合要求的项目内文件路径。由配置派生的输出按项目接入策略处理。 |
| Project Integration | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流规则、setup-project、角色技能、document-project、roadmap | 核对接入配置是否只提供接入信息，以及任务状态和动作授权是否另有依据。 |
| 规范技能 / canonical Skill | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流规则、setup-project 技能与生成器、能力提供方接入指南 | 核对技能身份能否按当前目录唯一定位，以及别名或内部工作单元是否被误作技能身份。 |
| 技能加载策略 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流规则、setup-project 技能、Planner、Explore、Executor、Reviewer 技能、能力提供方接入指南 | 核对实际使用方能否读取四种策略的条件，以及动作是否另有授权并满足技能前置。 |
| Project Context | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | setup-project、document-project 技能与生成器、工作流规则 | 检查是否只保存跨任务使用的项目术语和约束。任务进度、接入配置和 Spec 按各自位置维护。 |
| Artifact | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口规则、工作流规则、验收规则、协调规则、工作记录规则、角色或支持技能、运行环境适配器 | 核对是否仍能查到原始事实、用户授权和实际流程状态。 |
| Spec Artifact | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流规则、协调规则、工作记录规则、Planner、Executor、Reviewer 技能、运行环境适配器 | 核对同一份已批准的项目实施规格是否仍是实施与评审基线。 |
| 界面草稿 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作记录规则、入口规则、交互规则、协调规则、Planner、Explore 与 Roadmap 技能、验收规则、插件 README | 核对必要决定是否进入 Spec。检查草稿是否被误作独立批准状态或生产行为证据。 |
| Roadmap | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、setup-project、roadmap、document-project 技能和脚本、插件 README | 只看项目路线图能否理解计划。核对是否把它当成实施授权、实施规格、任务状态或流转指令。 |
| Spec 完成 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、工作流规则、工作记录规则、closeout 技能 | 核对是否到达合法完成状态，以及是否只在原规格内更新状态行。检查有无移动规格或另建完成记录。 |
| 探索决定记录 | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作记录规则、Explore 或 Planner 技能 | 核对记录是否只支持规划和恢复，以及有无被当成已批准规格或实施授权。 |
| Execution Report | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 工作流规则、工作记录规则、Executor、Reviewer、document-project 技能 | 核对报告能否指回原始证据，以及评审判断是否仍由评审者作出。 |
| Review Artifact | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | 验收规则、工作记录规则、Reviewer 技能 | 核对是否保存独立评审判断和下一步，以及有无被实施报告替代。 |
| Handoff | [术语定义](../plugins/sacha-orchestra/core/terminology-contract.md) | `PLUGIN_DESIGN.md`、入口规则、工作流规则、验收规则、协调规则、工作记录规则、角色或支持技能、运行环境适配器 | 核对是否只传递接手所需的信息，有无被当作流程节点、授权或完成证据。 |

## 开发文档专用术语

候选术语只有在存在多个现行开发文档使用方、且没有多个发布插件使用方时才由本文定义；在本节记录定义与边界、使用方和核验方法，不为了与术语定义集合相等而提升为安装后术语。

## 定义与引用维护

- 共享术语的含义与边界以[术语定义](../plugins/sacha-orchestra/core/terminology-contract.md)为准，流程动作以其引用的核心规则为准；本文不维护另一份完整定义。
- 修改共享术语或规则时，同次更新其负责文件和实际使用方；名称、位置或使用方变化时更新本文索引。
- 开发专用术语只在本文定义。开始被多个发布插件使用时，将定义提升到术语定义，开发侧改为引用并更新受影响映射。
- 发现使用方含义冲突时，按对应定义负责文件修正；实际使用方和引用未对齐前不声明该项完成。
