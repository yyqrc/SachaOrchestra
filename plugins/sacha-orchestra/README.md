# Sacha Orchestra

这是 Sacha Orchestra 的 Codex 部署包。Git release、source candidate 和验证层级以 [Evolution](../../docs/architecture/evolution.md) 为唯一权威。

## 使用入口

- 目标明确并已授权实施：`sacha-orchestra:executor`。
- 方案、边界或验收存在实质不确定性：`sacha-orchestra:planner`。
- Human 明确要求独立验收，或 Reviewer Gate 已开启：`sacha-orchestra:reviewer`。
- Manager Gate 已开启且存在可安全并发的 ready 工作单元：`sacha-orchestra:manager`。
- 调查 Sacha 流程或 plugin 偏差：`sacha-orchestra:feedback`。
- `sacha-orchestra:clarify` 与 `sacha-orchestra:setup-project` 仅显式调用。

普通局部任务不因 plugin 存在而强制进入 Sacha。Role、Gate 和生命周期以 [Workflow Contract](core/workflow-contract.md) 为准；Artifact 与 Handoff 以 [Artifact Protocol](core/artifact-protocol.md) 为准。

## Project setup

`sacha-orchestra:setup-project` 通过 dry-run、候选确认、expected hash 和回滚保护生成当前 Project Integration。生成物只保存项目绑定和 canonical locator；项目命令、领域知识与验证规则仍由 Project AGENTS 或 Domain Skill 所有。

## Codex Runtime

[Codex Runtime Adapter](adapters/codex/runtime-adapter.md) 定义 context、Skill discovery、dispatch/join、安装、恢复和 fresh-context 映射。

Marketplace 注册、plugin 安装、refresh、removal 或 reinstall 会修改 workspace 外部状态，必须获得 Human 明确授权。完成安装或刷新后，只有新的 Codex task 才能验证 fresh-context discovery。

## 历史入口

版本策略和当前状态见 [Evolution](../../docs/architecture/evolution.md)；冻结证据见 [history](../../docs/history/)；迁移经过见 [migrations](../../docs/migrations/)。
