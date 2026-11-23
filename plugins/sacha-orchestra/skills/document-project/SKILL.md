---
name: document-project
description: 用户明确要求新建或更新项目文档、Roadmap 交来完整正文，或工作流收尾的文档候选成立时使用。按目标、模板和项目策略安全写入项目文档。
---

# Project Documentation（项目存档）

## 功能

接收 Human 显式文档请求、Roadmap 文档请求或 [Workflow Contract](../../core/workflow-contract.md) 收尾候选路由。显式发布文档目标按明确模板原子新建或更新；其他请求按已确认的 Project Integration 和 Human 授权生成长期消费的项目文档、原子创建/更新 Roadmap 或维护项目上下文（Project Context）。

## 输入与首查

1. 先识别入口，再决定是否需要 Project Integration：
   - Human 显式调用并提供显式发布文档目标时，当前请求直接形成 `human-request` 输入；沿用 Intake Contract 的写入授权，不读取 Project Integration；调用方提供 `create | update`，update 时读取当前文件并提供 `expected_target_sha256`；
   - Human 显式调用但请求不符合「显式发布文档目标」的定义时，直接受理当前文档请求，并按已确认的 Project Integration 处理。只处理该文档目标，不接受 Sacha、不补走生产 Role，也不要求先存在收尾候选；
   - Roadmap 调用时只接受其已形成的完整自包含正文、唯一目标 path、`create | update` 与 update preimage。阶段、依赖和各阶段对应的实施规格由 Roadmap 确定。
   - `closeout` 把“存档”或组合动作的文档分支映射为 `human-request` 时，按同一显式请求处理；不读取、完成或替代 Spec；
   - Workflow 路由时，入口必须是收尾候选成立后的主任务；候选检查只使用当前任务最终事实；`disabled` 或无配置时静默跳过。
2. Artifact、Execution Report、Project Integration 与 Project Context 沿用[术语合同](../../core/terminology-contract.md)，再从当前任务最终事实选择生命周期和目标：
   - Execution Report 作为任务 Artifact/证据索引，留在 Spec/任务约定位置；
   - `change-archive`/完成文档记录已交付持久变化，`system-guide` 解释长期使用与维护；显式发布文档目标写入其 path，其他模式写入 Project Documentation root；
   - `roadmap` 只写 Project Integration 配置的 Roadmap root，文件名固定为 `<YYYY-MM-DD>-<short-slug>-roadmap.md`；
   - `project-context` 按 Project Context 的内容边界，写入 Project Context path 指定的 `CONTEXT.md` 受管区。
3. 显式调用直接形成当前请求。正常收尾只处理[工作流合同第 6 节](../../core/workflow-contract.md#6-项目文档)已确定的候选和触发方式，`required-at-closeout` 使用 `goal-closeout`。

## 动作顺序

1. `change-archive`、`system-guide` 或 `roadmap` 使用模板目录（template catalog）时读取当前 `profiles.json`；显式发布文档目标由调用方提供项目内 template catalog path，其他模式从 Project Integration 取得绑定：
   - 按 `document_type` 过滤，再用 `primary_purpose`、`primary_question`、`choose_when`、`avoid_when` 选择唯一最高相关 Profile。
   - 选定后只读取并校验该 Profile 的 `template`，文风按所选 Profile。正文覆盖 `required_topics`。在本次获授权的编辑范围内，可按 `generation_policy` 删除、合并、改名或重排可选章节。局部更新时，保留范围外的原文和结构。
   - Profile 并列或主要意图不清时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，向 Human 展示候选差异并请求选择。
   - 未绑定模板目录时按文档类型使用插件内 `canonical-change-archive-v1`、`canonical-system-guide-v1` 或 `canonical-roadmap-v1` 内置模板。
2. `project-context` 使用最终 Spec、真实证据、Review 和现有 `CONTEXT.md` 复核当前任务候选，不使用模板目录。
3. `roadmap` 使用 [路线图文档输入](assets/roadmap.json)。核对所选 Profile 和模板、标题、九个必需章节、唯一文件名、目标是否位于配置的路线图目录内，以及 `create | update` 和 `expected_target_sha256`。章节标题及旧标题兼容按 [Roadmap 技能](../roadmap/SKILL.md) 处理。Profile 只提供文风和章节组织。
4. 生成输入在试运行前完成语义复核：明确文档主题与长期直接消费者，一个事实只写在其 Owner。正文说明项目当前状态。任务执行过程、评审步骤和 Sacha 内部流转留在相应的任务记录中，是否保存按各自规则判断。每条保留约束须保持项目来源中的主体、条件、动作、顺序、规范强度、例外、失败和影响。Profile 只控制文风与组织，不改变这些事实或省略恢复所需边界。
5. 运行 `python -B scripts/generate_project_document.py --project-root <root> --input-json <json>` 试运行（`dry-run`）。预览核对策略、`trigger`、目标、写入前的原文件和结构，返回既有目标与摘要。具体写入授权和覆盖已有 Context 定义的确认由 `--write` 检查。显式发布文档目标需要项目相对 `target_path`、`create | update`、更新时的 preimage、可选的项目相对模板目录路径、Profile 和完整正文。
6. 按写入来源选择参数。
   - 显式发布文档目标试运行通过后，加 `--write`。
   - `required-at-closeout + bounded-closeout` 覆盖当前持久变更时直接写入。
   - 其他显式调用、`on-request`、`per-write-confirmation` 或 Roadmap 新建和更新，核对本次写入授权后加 `--per-write-confirmed --write`。目标、正文或计划路径超出已确认范围时重新确认。已有明确授权就直接使用。
7. 写入前完成目标和模板校验。
   - 显式发布文档目标核对路径是否在项目根目录内，以及 `mode`、结构、preimage 和目标路径。其他模式核对项目接入配置、授权和配置的根目录。
   - 使用模板目录时完整重验当前清单，再比较选中的 Profile 结构、模板 SHA-256 和 `generation_policy`。其他 Profile 的合法变化或 JSON 排版变化不构成选中模板冲突。
   - 正文清除占位符和模板作者说明，只保留有实质内容的标题。局部更新时，范围外原文或结构导致整篇校验不通过，就保留原文并暂停写入。说明具体位置和原因，由用户决定是否扩大范围。
8. 发布文档和 Roadmap 按明确的 `mode` 写入。Context 只更新受管区。新建只占用空缺路径。更新使用能保留被替换版本的系统操作，并核对实际被替换的内容。系统不支持时停止更新。
   - 替换时发现并发保存，恢复并发保存的版本并报告冲突。
   - 写后验证失败时只撤回本次写入。恢复期间再遇变动或无法安全还原时，保留冲突版本，报告 `partial_write`、目标及可用的恢复位置。

## 输出

- 向 Human 提问、确认或报告结果时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。先说明哪类文档已新建、已更新、无需改动或写入失败，并给出目标路径。只完成预检时说明尚未写入。把影响使用的验证结果和限制放在对应结果旁。发生冲突、回滚或部分写入时，说明文件的实际状态及可用的恢复入口。需要核对写入状态或排障时，引用工具返回的 `transaction`。
- SHA-256 只在并发 preimage、恢复或 Human 明确需要内容指纹时展示。
- 未满足事实、消费者或授权条件的候选，以及发生冲突的候选，保留在任务记录。

## 停止与禁止边界

- 显式发布文档目标只写其 project root 内 Markdown path；Roadmap、Project Context 与其他模式只写 Project Documentation root、Project Integration 配置的 Roadmap root 或 Project Context 受管区。任务 Artifact/Handoff 由 [Artifact Protocol](../../core/artifact-protocol.md) 管理。
- 路线图的目标、阶段、依赖、完成信号和各阶段对应的实施规格由 Roadmap 技能确定。本技能只验证输入并安全写入，不补写或改写路线内容。
- “存档”只是本 Skill 的 `human-request` 语义别名；Spec 完成与组合顺序由 `closeout` 和 Artifact Protocol 管理。
- 正文只使用可发布事实，不包含私有任务/线程引用或不可发布证据。普通 `spec.md` 文件名、项目 `cache` 目录和业务 UUID 本身不说明内容私有；调用方仍须复核真实来源和正文语义。
- 生成器的证据范围为输入、授权、path 与静态结构；Runtime 触发、内容语义和外部副作用分别验证。
- 安装、Git、发布、外部消息及 root 外写入使用各自授权。
