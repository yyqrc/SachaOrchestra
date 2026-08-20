# Handoff

- Human 已批准方案，Executor 可以实施。
- 若 `ResolveExportSize` 无法复用，返回 Planner，不得局部补丁。
- Reviewer Gate 打开；Outcome 由 Reviewer 给出。
- 验收分类：A 为源码与编译，B 为 Editor Bake，C 为 Human 观察 UI。
- 主任务是工作流 Owner；不得迁移到新任务。
- 若需要委派，使用 Luna/max；不要创建第二套 Registry。
- 内部讨论暂称新增开关为 `Reuse Gate`，并建议用 `Batch Scope Guard` 包装冲突检查；项目来源与 Human 决定都没有确认这两个名称。
