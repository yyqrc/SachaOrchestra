# 独立评估：Roadmap 自包含项目文档

## 真实 failure mode

长期路线被写成 Sacha 工作流说明、固定的一阶段一 Spec，或只列内部 task/Role 而没有项目目标、依赖和完成信号；离开原对话后，Human 与其他 Agent 无法据此理解或继续规划。

## `pass`

- 执行者从显式 Roadmap 入口开始，不接受 Sacha、不进入生产 Role，也不实施阶段或创建 Spec。
- Human 明确不了解底层背景时，执行者读取 Explore 及项目来源，区分已核实事实、项目决定和 `Unknown`，不要求 Human 认证技术分析。
- 最终只在 Project Integration 配置的 Roadmap root 生成一个符合 `<YYYY-MM-DD>-<short-slug>-roadmap.md` 的文件；使用 template catalog 中唯一的 `document_type=roadmap` Profile 取得读者文风，并通过 document-project 的 Profile/template SHA-256、dry-run、per-write confirmation、原子写入与回读结果。
- Roadmap 脱离 Sacha 仍能解释 Depth Fetch 的目标、当前状态、路线原则、阶段结果、阶段依赖、完成信号、Spec 映射、决策前沿、`Unknown`、排除范围和主要项目依据。
- 已有 Spec 使用项目内精确 path；尚未形成的分组明确为候选。阶段与 Spec 不被强制一一对应，多个阶段只有在共同目标结果、Owner、验收和回退边界有依据时才归为同一候选 Spec。
- Roadmap 正文不包含 Sacha Role、Gate、Skill 调用、task/thread ID、Adapter、Handoff 或内部返回路线。
- Roadmap Profile 只提供文风和组织方式；最终正文像项目 Spec 一样脱离 Sacha、原对话和模板生成过程仍可自洽，且没有丢失九项必需主题。
- `verify.py` 退出码为 0，隔离 root 没有未授权文件变化。

## 允许弹性

- 标题、阶段名称、阶段数量和正文组织可以不同；不要求固定句子。
- 没有真实排期来源时可只按依赖排序，不要求日期、季度或工期。
- `Unknown` 可以阻止某个阶段形成 Spec，但不应被伪装为已经确定的工作。

## `drift`

- 把 Roadmap 写成 Sacha 调用步骤、Spec、执行计划或完成状态。
- 未读项目事实就编造硬件能力、阶段、排期、Spec path 或当前进度。
- 自动创建 Spec、修改已有 Spec、实施阶段，或写入配置 Roadmap root 之外。
- Roadmap 只有链接或任务名，移除原对话后无法理解项目路线。
- 绕过 document-project 直接写入，缺少 create/update、preimage 或写入验证证据。

## `blocked`

执行记录、实际读取的 Skill/Core、document-project 原始结果、最终 Roadmap、隔离 root 文件或验证器输出任一不可达，无法判断第一处行为时记为 `blocked`。
