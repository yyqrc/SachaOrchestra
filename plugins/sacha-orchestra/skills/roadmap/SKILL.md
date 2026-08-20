---
name: roadmap
description: Human 显式要求生成、整理或更新跨阶段项目 Roadmap 时使用；单个可执行 Scope、Spec 起草或当前任务实施不用，不接受 Sacha、不进入生产 Role。
---

# Roadmap（项目路线图）

## 功能

作为主流程外独立规划环节，按需复用 Explore 补齐事实与 Human 决定，把项目长期目标组织为可独立理解的阶段、依赖、完成信号和 Spec 映射，再复用 document-project 写入 Project Integration 配置的 Roadmap root。

## 输入与首查

1. 只接受 Human 显式 Roadmap 请求；调用不接受 Sacha，不进入 Planner、Executor、Reviewer 或正常收尾候选。向 Human 提问、确认写入或报告结果前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
2. 先读项目规则、当前 Project Integration、项目事实、现有正式文档和相关 Spec。Project Integration 必须提供唯一 Roadmap root 与 Roadmap 文件模式；缺失时报告需要由 `setup-project` 配置的明确输入并停止，不自行调用 Setup，也不回退工作区默认目录。Project Integration 绑定 template catalog 时，按 `document_type=roadmap` 选择唯一最高相关 Profile；没有绑定时使用插件内 `canonical-roadmap-v1`。
3. 更新既有 Roadmap 时从 Human 输入或当前任务可达 reference 取得唯一文件 `path`，核对它位于 Roadmap root；不得扫描 root 按日期或名称猜测最新文件。新建时根据 Human 目标确定简短稳定 slug，按 Project Integration 的 Roadmap 文件模式生成文件名；日期使用首次创建日，后续更新保持 path 不变。
4. 事实、目标边界或实质决定不足时调用 `$sacha-orchestra:explore`；Roadmap 的显式请求只授权同一目标内的只读 Explore，结果返回 Roadmap。Explore 需要新写入、实施、Scope 或高影响授权时停止受影响部分并交 Human 决定。

## 动作顺序

1. 从项目来源和 Human 决定确定目标与完成形态、当前状态、适用范围、排除范围和稳定约束；Roadmap 不自行定义项目事实或改变 Scope。
2. 按需消费 Explore 返回的已核实事实、Human 决定、冲突、阻塞项、`Unknown` 和证据 reference。只把能够精确陈述且依赖可判断的内容组织为阶段或决策前沿；尚不能准确表述的内容留在 `Unknown`，不伪造阶段、日期或 Spec。
3. 每个阶段按项目语义写清名称、目标结果、包含/不包含范围、进入条件、关键工作面、依赖、完成信号、风险/`Unknown` 和 Spec 映射。阶段顺序由依赖与目标结果决定；没有真实排期来源时不得编造季度、月份、工期或承诺日期。
4. Roadmap 不强制阶段与 Spec 一一对应：一个阶段可对应一个 Spec，多个阶段也可按共同目标结果、Owner、验收和回退边界归入同一 Spec。只因阶段相邻不足以合并；已有 Spec 使用精确 path，尚未形成的分组明确标为候选，不创建 `spec.md` 或替 Planner 冻结实施方案。
5. 正文必须包含“目标与完成形态”“当前状态”“路线原则”“阶段路线”“Spec 映射”“决策前沿”“Unknown”“排除范围”“主要项目位置与依据”；没有对应事项时写明“当前无”，不得删除这些必需标题。其他扩展章节没有实质内容时不保留。一个事实只写一次，正文保留独立理解必需的项目语义，详细实现和证据通过可达 path/reference 指向 Owner。
6. Roadmap 面向项目 Human 与 Agent：移除 Sacha 上下文后仍须理解目标、阶段、依赖、完成信号和 Spec 分组。正文不得写 Sacha Role、Gate、Skill 调用、task/thread ID、Adapter、Handoff、内部路由或“返回某节点”等流程信息。
7. 读取选中的 Roadmap Profile/template 取得文风、章节组织和 generation policy；Profile 不得改变或省略第 5 步的必需语义。再读取 [Roadmap 文档输入](../document-project/assets/roadmap.json)，填充 `template_profile`、完整正文、document type `roadmap`、目标 path 和 create/update 意图后交给 `$sacha-orchestra:document-project`。document-project 按 Project Integration 的 Roadmap root 执行 dry-run、写入授权、Profile/template SHA-256、preimage、原子创建/更新、并发检查和回读验证；Roadmap 不绕过该 Skill 直接写文件。
8. document-project 返回后核对实际 path、transaction、验证、冲突和未验证项；写入失败时保留完整自包含正文及恢复条件，不把 draft 宣称为已持久化 Roadmap。

## 输出

- 返回 Roadmap 的目标、实际或计划 path、create/update、阶段摘要、Spec 映射、document-project transaction、验证、冲突、`Unknown` 与未验证边界。
- 成功写入时提供可直接打开的 Roadmap path；未写入时明确标记 draft 和恢复入口。

## 停止与禁止边界

- Roadmap 是项目文档，不是 Artifact、Spec、任务状态、实施授权或完成证据。
- 不创建或执行 Spec、阶段、Issue、Ticket、分支、发布或外部资源；后续实施由 Human 另行发起。
- 不从文件名、目录排序、旧任务记录或 Sacha 输出推断项目当前状态；当前状态只接受项目规则、源码、配置、正式项目文档、运行证据或 Human 决定。
- Roadmap root、文档 path 与写入授权分别沿用 Project Integration 和 document-project；root 外写入、Git、安装、发布和外部动作需要各自明确授权。
