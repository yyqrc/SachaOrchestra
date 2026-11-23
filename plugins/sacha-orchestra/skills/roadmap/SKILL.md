---
name: roadmap
description: 用户明确要求编写或更新跨阶段项目路线图时使用。路线图组织长期目标、阶段和依赖。单项实施或起草实施规格按对应入口处理。
---

# Roadmap（项目路线图）

## 功能

独立编写项目路线图。按需用 Explore 补齐事实和用户决定，说明长期目标、阶段、依赖、完成信号及各阶段对应的实施规格。通过 document-project 写入项目接入配置指定的路线图目录。

## 输入与首查

1. 只接受 Human 显式 Roadmap 请求；调用不接受 Sacha，不进入 Planner、Executor、Reviewer 或正常收尾候选。向 Human 提问、确认写入或报告结果前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
2. 先读项目规则、当前项目接入配置、项目事实、现有正式文档和相关 Spec。接入配置须给出唯一的路线图目录和文件模式。缺失时说明 `setup-project` 需要的具体输入，暂停当前工作，不自行配置或回退到工作区默认目录。已绑定模板目录时，按 `document_type=roadmap` 选择唯一最贴合的 Profile。否则使用内置 `canonical-roadmap-v1`。
3. 更新既有 Roadmap 时从 Human 输入或当前任务可达 reference 取得唯一文件 `path`，核对它位于 Roadmap root；不得扫描 root 按日期或名称猜测最新文件。新建时根据 Human 目标确定简短稳定 slug，按 Project Integration 的 Roadmap 文件模式生成文件名；日期使用首次创建日，后续更新保持 path 不变。
4. 事实、目标边界或实质决定不足时调用 `$sacha-orchestra:explore`；Roadmap 的显式请求只授权同一目标内的 Explore 读取目标项目源码、配置、资源与外部状态，并按 [Artifact Protocol](../../core/artifact-protocol.md) 创建或更新探索决定记录，以及制作、预览独立界面草稿，结果返回 Roadmap。Explore 需要除此以外的新写入、实施、Scope 或高影响授权时停止受影响部分并交 Human 决定。

## 动作顺序

1. 按[工作流合同的运行原则](../../core/workflow-contract.md#2-运行原则)划分阶段和主要工作。根据项目来源与用户决定明确目标、预期结果、当前状态、适用范围、排除范围和稳定约束。路线图不得自行定义项目事实或改变范围。
2. 使用 Explore 返回的已核实事实、用户决定、冲突、阻塞、未知问题和证据引用。内容能准确陈述且依赖可判断时，才组织成阶段，或将会改变路线、尚未作出的决定写入「待决定事项」。事实不足、暂时还说不清的问题，写入「待查明的问题」。不得据此编造阶段、日期或 Spec。
3. 每个阶段按项目语义写清名称、目标结果、范围、必要工作和完成信号。进入条件、依赖、风险、待查明的问题和对应的实施规格，只记录已有依据且影响阶段安排的内容。不得为填写这些内容扩大调查或设计。阶段顺序由依赖与目标结果决定。日期和工期须有实际排期依据。
4. Roadmap 不强制阶段与 Spec 一一对应：一个阶段可对应一个 Spec，多个阶段也可按共同目标结果、Owner、验收和回退边界归入同一 Spec。只因阶段相邻不足以合并；已有 Spec 使用精确 path，尚未形成的分组明确标为候选，不创建 `spec.md` 或替 Planner 冻结实施方案。
5. 正文必须包含「目标与预期结果」「当前状态」「路线原则」「阶段路线」「各阶段对应的实施规格」「待决定事项」「待查明的问题」「排除范围」「主要项目位置与依据」。没有事项的必需章节写「当前无」，有实质内容时再加其他章节。新建使用上述标题。更新旧路线图时，可以保留原有的「目标与完成形态」「Spec 映射」「决策前沿」或「Unknown」，并按获授权的编辑范围决定是否改名。同一主题只用一个标题。正文只写一次独立理解所需的项目事实，详细实现和证据给出可达引用。
6. Roadmap 面向项目 Human 与 Agent：移除 Sacha 上下文后仍须理解目标、阶段、依赖、完成信号和 Spec 分组。正文不得写 Sacha Role、Gate、Skill 调用、task/thread ID、Adapter、Handoff、内部路由或“返回某节点”等流程信息。
7. 读取选中的 Profile 和模板以确定文风、结构和生成规则，保留第 5 步的必需语义。按[路线图文档输入](../document-project/assets/roadmap.json)提供 `template_profile`、完整正文、类型 `roadmap`、目标路径和 `create | update`，更新时提供原文件哈希。把输入交给 [document-project](../document-project/SKILL.md) 处理授权、并发、写入和回读。路线图只通过该技能写入。
8. document-project 返回后核对实际 path、transaction、验证、冲突和未验证项；写入失败时保留完整自包含正文及恢复条件，不把 draft 宣称为已持久化 Roadmap。
9. 按[工作流合同第 4 节](../../core/workflow-contract.md#4-生命周期与-human-路由)判断是否推荐另开 Sacha Planner 任务，并按交互合同向用户说明。用户确认创建后，把路线图路径、目标和范围、已确认决定、未决项及明确的“使用 Sacha Planner”请求交给对应宿主的适配器。

## 输出

- 先给出路线图实际或计划路径，说明已创建、已更新或尚未写入，并概括目标、主要阶段和已有的 Spec 安排。把影响阶段安排、使用或恢复的未知项、冲突和验证结果放在对应内容旁。需要核对写入状态或排障时，引用 `document-project` 返回的 `transaction`。
- 成功写入时提供可直接打开的 Roadmap path；未写入时明确标记 draft 和恢复入口。
- 另开的 Planner 任务创建成功后，提供目标任务 reference 并结束当前路线图任务，无须等待完整 Spec。

## 停止与禁止边界

- Roadmap 是项目文档，不是 Artifact、Spec、任务状态、实施授权或完成证据。
- 不自动创建或执行 Spec、阶段、Issue、Ticket、分支、发布或外部资源。后续任务创建和实施的授权沿用[入口合同](../../core/intake-contract.md#4-入口决定)。
- 不从文件名、目录排序、旧任务记录或 Sacha 输出推断项目当前状态；当前状态只接受项目规则、源码、配置、正式项目文档、运行证据或 Human 决定。
- Roadmap root、文档 path 与写入授权分别沿用 Project Integration 和 document-project；root 外写入、Git、安装、发布和外部动作需要各自明确授权。
