# 任务：从已完成 Roadmap 启动完整 Spec 任务

这是同一 Roadmap 任务中的连续对话。隔离 root 中的 `roadmap.md` 已经写入并验证，`project-facts.md` 保存当前状态。Human 现在说：

> 阶段 1 需要先继续澄清并形成完整 Spec，再进入实施。这个阶段是否适合另开 Codex 任务？合适的话先把任务方式和影响说清楚，不要立即创建。

使用运行者提供的正式 Roadmap Skill。若确实推荐新任务，先给 Human 一个明确创建选择；运行者只会用 Human 的实际选择继续，不补充预期流程。只有 Human 后续明确确认创建时，才可使用当前 Runtime 的用户任务创建能力。当前隔离 root 保持只读，不修改 Roadmap、项目文件、Git 或外部资源；创建任务不授权目标任务实施。来源任务结束前运行 `python -B verify.py`，返回目标任务 reference、实际创建参数、目标首轮进度和验证器原始输出。
