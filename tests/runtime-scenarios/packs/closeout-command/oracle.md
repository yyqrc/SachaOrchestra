# closeout-command 裁决标准

1. 执行者从正式入口识别 Human 的“收口”请求，读取 `closeout`、Workflow 与 Artifact Protocol 的必要现行来源；不把任务多文件或验证步骤当作 Planner/Manager 事实。
2. 执行者只使用明确的 `current/spec.md`，不扫描或选择其他 Spec；记录唯一状态行的当前完整文本，再使用带并发修改检查的局部编辑只替换该行。
3. `current/spec.md` 保持原 path，唯一头部状态变为“已完成”，Scope 正文不变。
4. 工作区没有 `docs/done`、项目文档、Spec 副本、移动或额外完成 Artifact。
5. `python -B verify.py` 返回 0 并输出 `closeout_command_status=pass`。
6. 本场景只证明源码 `source-scenario` 的自然语言路由、必要 Owner 读取和文件结果；不证明安装后 fresh discovery、组合命令或项目文档 Runtime 行为。
