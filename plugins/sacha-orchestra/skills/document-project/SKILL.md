---
name: document-project
description: Human 提供显式发布文档目标并要求按模板新建或更新、Roadmap 提交自包含路线文档，或 Workflow 收尾候选成立时，安全写入项目文档；不生成 Roadmap 内容，不替代 Artifact。
---

# Project Documentation（项目存档）

## 功能

接收 Human 显式文档请求、Roadmap 文档请求或 [Workflow Contract](../../core/workflow-contract.md) 收尾候选路由。显式发布文档目标按明确模板原子新建或更新；其他请求按已确认的 Project Integration 和 Human 授权生成长期消费的项目文档、原子创建/更新 Roadmap 或维护项目上下文（Project Context）。

## 输入与首查

1. 先识别入口，再决定是否需要 Project Integration：
   - Human 显式调用并提供显式发布文档目标时，当前请求直接形成 `human-request` 输入；沿用 Intake Contract 的写入授权，不读取 Project Integration；调用方提供 `create | update`，update 时读取当前文件并提供 `expected_target_sha256`；
   - Human 显式调用但未指定目标时，当前文档请求直接形成输入并读取已确认的 Project Integration；只处理该文档目标，不接受 Sacha、不补走生产 Role，也不要求先存在收尾候选；
   - Roadmap 调用时只接受其已形成的完整自包含正文、唯一目标 path、`create | update` 与 update preimage；不重新划分阶段、依赖或 Spec 映射；
   - `closeout` 把“存档”或组合动作的文档分支映射为 `human-request` 时，按同一显式请求处理；不读取、完成或替代 Spec；
   - Workflow 路由时，入口必须是收尾候选成立后的主任务；候选检查只使用当前任务最终事实；`disabled` 或无配置时静默跳过。
2. Artifact 与 Execution Report 沿用[术语合同](../../core/terminology-contract.md)，再从当前任务最终事实选择生命周期和目标：
   - Execution Report 作为任务 Artifact/证据索引，留在 Spec/任务约定位置；
   - `change-archive`/完成文档记录已交付持久变化，`system-guide` 解释长期使用与维护；显式发布文档目标写入其 path，其他模式写入 Project Documentation root；
   - `roadmap` 只写 Project Integration 配置的 Roadmap root，文件名固定为 `<YYYY-MM-DD>-<short-slug>-roadmap.md`；
   - `project-context` 只收有跨任务消费者的稳定术语/约束，写入 Project Context path 指定的 `CONTEXT.md` 受管区。
3. 显式调用已经形成当前文档请求；Workflow 路由中的 `on-request` 只在候选成立后询问一次，`required-at-closeout` 使用 `goal-closeout`。纯问答、无持久变更、仅任务报告或没有新增持久知识的局部修复只对 Workflow 候选检查静默跳过，不否定 Human 的显式文档请求。

## 动作顺序

1. `change-archive`、`system-guide` 或 `roadmap` 使用模板目录（template catalog）时读取当前 `profiles.json`；显式发布文档目标由调用方提供项目内 template catalog path，其他模式从 Project Integration 取得绑定：
   - 按 `document_type` 过滤，再用 `primary_purpose`、`primary_question`、`choose_when`、`avoid_when` 选择唯一最高相关 Profile。
   - 选定后只读取并校验该 Profile 的 `template`；正文覆盖 `required_topics`，可按 `generation_policy` 删除、合并、改名或重排可选章节。
   - Profile 并列或主要意图不清时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，向 Human 展示候选差异并请求选择。
   - 未绑定模板目录时按文档类型使用插件内 `canonical-change-archive-v1`、`canonical-system-guide-v1` 或 `canonical-roadmap-v1` 内置模板。
2. `project-context` 使用最终 Spec、真实证据、Review 和现有 `CONTEXT.md` 复核当前任务候选，不使用模板目录。
3. `roadmap` 读取并消费 [Roadmap 文档输入](assets/roadmap.json)，校验所选 Roadmap Profile/template、标题、九个必需语义章节、唯一文件名、Roadmap root 包含关系、`create | update` 与 `expected_target_sha256`；Profile 只提供文风和章节组织，正文语义仍由 Roadmap Skill 拥有。
4. 生成输入在试运行前完成语义复核：明确文档主题与长期直接消费者，一个事实只写在其 Owner，正文描述当前项目状态而不叙述任务过程、Review 编舞或 Sacha 路由；每条保留约束须保持项目来源中的主体、条件、动作、顺序、规范强度、例外、失败和影响。Profile 只控制文风与组织，不改变这些事实或省略恢复所需边界。
5. 运行 `python -B scripts/generate_project_document.py --project-root <root> --input-json <json>` 试运行（`dry-run`）。显式发布文档目标输入包含项目相对 `target_path`、`create | update`、update preimage、可选项目相对 template catalog path、Profile 与完整正文。
6. 显式发布文档目标试运行通过后增加 `--write`；`required-at-closeout + bounded-closeout` 覆盖当前持久变更时直接写入；其他显式调用、`on-request`、`per-write-confirmation` 或 Roadmap create/update 仍核对本次写入授权，满足后增加 `--per-write-confirmed --write`。目标、正文或计划 path 变化时重新确认。
7. 显式发布文档目标校验项目 root 包含关系、mode、结构、preimage 与 path；其他模式校验 Integration、授权和配置 root。模板目录模式校验当前 manifest、所选 Profile 的类型/版本/template path、选中模板的 SHA-256 与 `generation_policy`。正文必须清除占位符和模板作者说明，只保留有实质内容的标题。
8. 发布文档按明确 mode 原子新建或以 preimage 原位更新；Roadmap 同样按 mode 写入；Context 只写受管区。并发变化时停止写入，写后校验失败时恢复原内容。

## 输出

- 向 Human 提问、确认或报告结果时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)；报告文档类型、目标 path、`transaction`、验证与限制。
- SHA-256 只在并发 preimage、恢复或 Human 明确需要内容指纹时展示。
- 未满足事实、消费者或授权条件的候选，以及发生冲突的候选，保留在任务记录。

## 停止与禁止边界

- 显式发布文档目标只写其 project root 内 Markdown path；Roadmap、Project Context 与其他模式只写 Project Documentation root、Project Integration 配置的 Roadmap root 或 Project Context 受管区。任务 Artifact/Handoff 由 [Artifact Protocol](../../core/artifact-protocol.md) 管理。
- Roadmap 的目标、阶段、依赖、完成信号和 Spec 映射由 Roadmap Skill 拥有；本 Skill 只验证输入与安全持久化，不补写或改写路线语义。
- “存档”只是本 Skill 的 `human-request` 语义别名；Spec 完成与组合顺序由 `closeout` 和 Artifact Protocol 管理。
- 正文只使用可发布事实，不包含内部任务/线程 ID、缓存 path 或不可发布证据 reference。
- 所有发布项目文档的文风只读取所选 Profile；Roadmap 的目标、阶段、依赖和 Spec 映射语义仍由 Roadmap Skill 拥有，Profile 不得改变或省略这些内容。
- 生成器的证据范围为输入、授权、path 与静态结构；Runtime 触发、内容语义和外部副作用分别验证。
- 安装、Git、发布、外部消息及 root 外写入使用各自授权。
