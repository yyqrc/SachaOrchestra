---
name: document-project
description: 用户明确要求新建或更新项目文档、Roadmap 交来完整正文，或工作流收尾的文档候选成立时使用。按目标、模板和项目策略安全写入项目文档。
---

# Project Documentation（项目存档）

## 功能

处理用户明确请求的文档、Roadmap 和[符合工作流条件的自动存档](../../core/workflow-contract.md#6-项目文档)。显式发布文档目标按明确模板原子新建或更新。其他请求按已确认的项目接入配置和用户授权写入项目文档、Roadmap 或项目上下文（Project Context）。

## 输入与首查

1. 先识别入口，再决定是否需要 Project Integration：
   - 用户明确指定发布文档目标时，以 `human-request` 处理，沿用[入口授权](../../core/intake-contract.md#4-入口决定)。此情形无需读取项目接入配置。按请求选择 `create` 或 `update`，更新时读取原文件并提供 `expected_target_sha256`。
   - 用户明确请求文档但未指定发布文档目标时，按已确认的项目接入配置处理。只处理该文档请求。
   - Roadmap 调用时沿用其已选定的 `template_profile`、完整正文和写入参数。阶段、依赖和各阶段对应的实施规格由 Roadmap 确定。
   - `closeout` 把“存档”或组合动作的文档分支映射为 `human-request` 时，按同一显式请求处理；不读取、完成或替代 Spec；
   - 自动存档由主任务按[工作流规则第 6 节](../../core/workflow-contract.md#6-项目文档)判断，调用时使用 `goal-closeout` 和已完成 Spec 对应的最终事实。只有接手说明、没有持久产品变更时，使用 `change-archive` 并如实填写 `persistent_product_delta: false`。
2. 根据本次任务的实际结果及[术语定义](../../core/terminology-contract.md)选择文档类型和目标：
   - 实施报告和证据引用留在 Spec 或任务约定的工作记录位置。
   - `change-archive` 记录值得留存的变更或必要的接手说明，`system-guide` 解释长期使用与维护。显式发布文档目标写入其 `path`，其他模式写入配置的项目文档目录；
   - `roadmap` 只写 Project Integration 配置的 Roadmap root，文件名固定为 `<YYYY-MM-DD>-<short-slug>-roadmap.md`；
   - `project-context` 按 Project Context 的内容边界，写入 Project Context path 指定的 `CONTEXT.md` 受管区。

## 动作顺序

1. 准备 `change-archive`、`system-guide` 或 `roadmap` 正文时选一次模板。使用模板目录时读取 `profiles.json`。显式发布文档目标由调用方提供项目内模板目录路径，其他模式沿用项目接入配置：
   - 按 `document_type` 过滤，再依据 `primary_purpose`、`primary_question`、`choose_when`、`avoid_when` 和内容要求选模板配置。并列项只差排版时，更新沿用原样式，新建沿用项目同类文档的样式，优先选择与之匹配的配置。没有可核实的先例时，取清单中第一个等价项。
   - 先用当前请求和项目先例判断并列项。仍有会改变内容或用途的决定需要用户作出时，自动存档按[工作流规则](../../core/workflow-contract.md#6-项目文档)跳过。明确请求或验收要求的文档按 `tie_policy: ask-human` 只询问剩余的实质差异。
   - 选定后只读取该 Profile 的 `template`。正文覆盖 `required_topics`，可选结构按 `generation_policy` 和已有样式处理。局部更新时保留范围外的原文和结构。
   - 未绑定模板目录时按文档类型使用插件内 `canonical-change-archive-v1`、`canonical-system-guide-v1` 或 `canonical-roadmap-v1` 内置模板。
2. `project-context` 使用最终 Spec、真实证据、Review 和现有 `CONTEXT.md` 复核当前任务候选，不使用模板目录。
3. `roadmap` 直接把[路线图文档输入](assets/roadmap.json)交给生成器校验并写入。章节语义和旧标题兼容沿用 [Roadmap 技能](../roadmap/SKILL.md)。
4. 准备写入内容时，明确文档主题和使用方，保留项目要求的条件、约束与例外。正文说明项目当前状态，任务过程留在任务记录中。清除占位符和模板说明。局部更新遇到范围外的原文导致整篇校验失败时，保留原文并说明具体原因。
5. 目标、内容和写入授权清楚时，直接运行 `python -B scripts/generate_project_document.py --project-root <root> --input-json <json> --write`。用户要求预览，或确需只读核对目标、冲突或影响时，去掉 `--write` 试跑。生成器在写入时仍校验目标、模板、授权和文件原有状态。
   - 显式发布文档目标沿用该请求的授权。自动存档在项目策略为 `required-at-closeout` 且 `bounded-closeout` 覆盖本次写入时，直接使用 `--write`。
   - 项目要求逐次授权，或需要更新已有的项目上下文定义时，用 `--per-write-confirmed --write` 传递已有的具体写入授权。显式存档和 Roadmap 的原请求已覆盖目标和改动时也直接传入该参数。显式请求超出已有授权时，只核对缺少的部分。自动存档缺少具体授权时按工作流规则跳过。
6. 生成器按明确的 `mode` 写入显式发布文档目标和 Roadmap，Context 只更新受管区。新建只占用空缺路径。更新时由生成器保留并核对被替换的内容，系统不支持时停止更新。
   - 替换时发现并发保存，恢复并发保存的版本并报告冲突。
   - 写后验证失败时只撤回本次写入。恢复期间再遇变动或无法安全还原时，保留冲突版本，报告 `partial_write`、目标及可用的恢复位置。

## 输出

- 向 Human 提问、确认或报告结果时读取 [交互规则](../../core/human-interaction-contract.md)。先说明哪类文档已新建、已更新、无需改动或写入失败，并给出目标路径。只完成预检时说明尚未写入。把影响使用的验证结果和限制放在对应结果旁。发生冲突、回滚或部分写入时，说明文件的实际状态及可用的恢复入口。需要核对写入状态或排障时，引用工具返回的 `transaction`。
- 需要核对写入前的文件版本、恢复，或用户明确要求内容指纹时，才展示 SHA-256。
- 未满足事实、消费者或授权条件的候选，以及发生冲突的候选，保留在任务记录。

## 停止与禁止边界

- 明确指定的发布文档只写项目根目录内的 Markdown 路径。其他文档按类型限于配置的项目文档目录、路线图目录或项目上下文受管区。任务记录和交接信息按[工作记录规则](../../core/artifact-protocol.md)处理。
- 路线图的目标、阶段、依赖、完成信号和各阶段对应的实施规格由 Roadmap 技能确定。本技能只验证输入并安全写入，不补写或改写路线内容。
- 用户明确请求存档时使用 `human-request`。Spec 完成及与存档的先后顺序见 [`closeout`](../closeout/SKILL.md)。
- 正文只使用可发布事实，不包含私有任务/线程引用或不可发布证据。普通 `spec.md` 文件名、项目 `cache` 目录和业务 UUID 本身不说明内容私有；调用方仍须复核真实来源和正文语义。
- 生成器核对输入、授权、路径和文档结构。实际触发、正文含义和外部副作用各用对应证据判断。
- 安装、Git、发布、外部消息及 root 外写入使用各自授权。
