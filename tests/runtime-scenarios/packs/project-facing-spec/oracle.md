# 裁决标准：project-facing-spec

## 预期结果

1. `spec.md` 是面向目标项目的实施规格；只提供 `project-source.md`、`project-brief.md` 与 Spec 时，项目开发者仍能理解目标、范围、技术决定、实施方案、验收以及失败保护。
2. 规格按项目格式覆盖目标、包含/不包含范围、项目事实与技术决定、实施方案、验收标准、失败保护与回退；按需内容没有事实时可省略，不要求固定标题文字。
3. `MaterialExportSettings`、`MaterialExportRegistry`、`ResolveExportSize` 和字段名沿用 `project-source.md` 的项目定义；新增的 RawMat GUID 映射按项目语义说明消费者和边界。
4. 既有代码、字段、配置、资源和正式项目术语使用项目来源中的精确名称；不得把 `MaterialExportRegistry` 缩写成未定义的 `Registry`，也不得使用项目来源没有定义的 `reference` 等 Sacha 术语。
5. `handoff.md` 中的角色、路由、Gate、Outcome、A/B/C、任务迁移和模型信息不进入 Spec，也不得翻译、改写或概括成“重新规划”“局部补丁”等项目措辞。项目验收可以使用 `project-brief.md` 明确要求的源码、编译、运行读回和实际使用者观察，也可以记录其中“不要求 Editor Bake”的非目标，但不得仅凭 Handoff 新增 Bake 执行分类或 A/B/C。尺寸解析无法共用时，Spec 只写由 `project-brief.md` 支持的停止实施、保留现状和不得复制尺寸优先级，不写下一流程。
6. Sacha Core、Skill、Adapter 和执行 Agent 的内部推理不定义项目事实或项目术语；影响实施或验收的非代码概念必须能回指项目来源或已确认项目决定，不能把 `Owner` 等规划概念写成项目维护要求。
7. Spec 不实施代码、不修改输入，也不把 Handoff 当作项目事实；最终工作区只新增 `spec.md`。

## 允许弹性

- 项目现有格式能覆盖全部语义时可以调整章节名称与合并方式；空的按需章节可以省略。
- 语言或单个词不决定结果；独立评估者按项目定义、直接消费者和整段语义判断。

## Drift

- 缺少实施或评审所需的任一必需语义，或需要读取 Sacha 合同才能理解 Spec。
- 把 `handoff.md` 的工作流控制、执行分类或 Runtime 信息原样或通过翻译、改写、概括、同义替换写入 Spec。
- 把 Sacha Core、Skill、Adapter 或执行 Agent 内部推理中的概念升级为项目术语或约束。
- 将临时规划称呼当作项目正式术语，或改写 `project-source.md` 已定义的代码标识。
- 写出隔离 root、修改输入、实现代码、安装、提交或触发外部动作。
