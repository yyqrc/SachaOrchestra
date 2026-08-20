# Sacha Orchestra

> 文档身份：插件发布使用；位于发布 `root` 内。

跨运行环境的项目工作流插件。本文只保留安装后可用的入口、最小使用方式和 Runtime owner 导航。

## 默认入口

Codex 直接调用 `$sacha-orchestra:using-sacha`；Cursor 通过自然语言或 `/using-sacha` 调用。也可在任务初次接收及语义转折点重评估。目标、Scope、授权与验收清晰时保持当前 task Direct；只有执行方式会因探索未知事实、持久化批准 Spec、跨 context owner/恢复、正式协调或独立复核而改变时才建议进入 Sacha，同一入口候选只询问一次。

## 显式入口

- 高级入口：`planner`、`executor`、`reviewer`；显式 `explore` 只有只读窄授权。
- `roadmap` 是主流程外显式规划入口：按需复用 Explore，生成可脱离 Sacha 独立理解的长期项目路线图，并通过 `document-project` 写入 Project Integration 配置的 Roadmap root；不创建或执行 Spec。
- `document-project` 接受 Human 显式文档请求，或正常 Workflow 的收尾候选路由；显式调用只覆盖当前文档目标，不接受 Sacha、不补走生产 Role。
- `closeout` 接受 Human 明确提出的“收口”“存档”“收口并存档”请求：收口只原位完成当前唯一 Spec，存档只映射 `document-project`，组合动作先收口再存档；只讨论或引用这些词语不执行动作。
- `feedback` 只由 Human 在另一个真实任务手动调用，可提交流程问题、使用反馈或插件开发想法。来源任务交付唯一目标任务 reference 后结束，目标任务按普通任务重新判断。
- Manager 只接受内部 Gate 路由，不是用户入口。
- `setup-project`、`setup-agents` 是主流程外显式配置能力，不属于 workflow 入口。

入口不会扩大写入、安装、Git、发布、远程资源或高影响动作授权。

## Runtime owner

- [Intake Contract](core/intake-contract.md)：入口接受/拒绝与重复抑制。
- [术语合同](core/terminology-contract.md)：流程与 Artifact 的提炼术语、定义与边界。
- [Workflow Contract](core/workflow-contract.md)：唯一 Runtime 路由、Role/Gate 与 Human 路由。
- [Human Interaction Contract](core/human-interaction-contract.md)：Human 可见提问、进度、结果顺序与必须披露的信息。
- [Assurance Contract](core/assurance-contract.md)：Review、Baseline 与 Outcome。
- [Coordination Contract](core/coordination-contract.md)：Manager、readiness、dispatch/wait/return 与 owner transfer。
- [Artifact Protocol](core/artifact-protocol.md)：Artifact 生成条件、最小内容、权威关系与恢复规则。
- [Codex Adapter](adapters/codex/runtime-adapter.md)、[Claude Code Adapter](adapters/claudecode/runtime-adapter.md)与 [Cursor Adapter](adapters/cursor/runtime-adapter.md)：各自 Runtime transport。

静态源码与说明不证明安装、fresh discovery、dispatch 或真实 Runtime 行为；这些必须用对应 Runtime scenario 单独验证。
