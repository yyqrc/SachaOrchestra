# Sacha Orchestra

> 文档身份：插件发布使用；位于发布 `root` 内。

Sacha Orchestra 是一套跨宿主的项目工作流插件。这里列出安装后可用的入口，以及各项运行规则的位置。

## 默认入口

Codex 先根据 `$sacha-orchestra:using-sacha` 的简短说明判断当前任务是否需要专门的探索、规划、协调、评审或恢复。普通请求在当前任务直接处理。你也可以在 Codex 或 DeepSeek Harness 中主动调用入口。

日常按请求只读探索，或在已确认范围内实施和验证。继续已有任务时沿用仍有效的决定、授权和工作记录。需要规划、协调或独立评审时按任务实际情况安排。确实缺少决定或授权时，只问影响下一步的部分。另开任务、向指定任务发消息、安装和发布仍各自需要明确授权。 [入口规则](core/intake-contract.md#4-入口决定)

## 显式入口

- 高级入口：`planner`、`executor`、`reviewer`；显式 `explore` 保持窄授权，目标项目生产源码、配置、资源与外部状态只读，可按 [工作记录规则](core/artifact-protocol.md) 写探索决定记录，以及制作、预览独立界面草稿。
- 明确调用 `roadmap` 可编写长期项目路线图，必要时用 `explore` 补齐事实。路线图由 `document-project` 保存到配置指定的目录。需要另开任务编写 Spec 时，会说明新任务的目标并沿用已有创建授权。路线图的写入授权只适用于原任务。
- `document-project` 处理明确的文档请求，也按[工作流规则](core/workflow-contract.md#6-项目文档)为已完成的 Spec 保存值得留存的变更或必要的接手说明。明确指定的发布文档路径是本次写入授权，其他目标按项目接入配置处理。
- `closeout` 处理「把 Spec 标为已完成」和「存档」请求。完成条件满足时只更新原规格的状态行。两项一起请求时，先标记完成，再由 `document-project` 写入存档。
- `feedback` 只由 Human 在另一个真实任务手动调用，可提交流程问题、使用反馈或插件开发想法。来源任务交付唯一目标任务 reference 后结束，目标任务按普通任务重新判断。
- Manager 仅供主任务在需要协调时调用。
- `setup-project`、`setup-agents` 是主流程外显式配置能力，不属于 workflow 入口。

入口不会扩大写入、安装、Git、发布、远程资源或高影响动作授权。

## 运行规则

- [入口规则](core/intake-contract.md)：入口接受/拒绝与重复抑制。
- [术语定义](core/terminology-contract.md)：流程与 Artifact 的提炼术语、定义与边界。
- [工作流规则](core/workflow-contract.md)规定任务何时进入规划、实施、评审和收尾。
- [交互规则](core/human-interaction-contract.md)规定怎样提问、报告进度和交付结果。
- [验收规则](core/assurance-contract.md)规定按哪个版本核对、怎样执行验收和作出裁决。
- [协调规则](core/coordination-contract.md)规定怎样安排依赖、派发、等待、接收结果和移交责任。
- [工作记录规则](core/artifact-protocol.md)规定何时保存记录、以什么为准，以及怎样接手和恢复任务。
- [Codex Adapter](adapters/codex/runtime-adapter.md)、[Claude Code Adapter](adapters/claudecode/runtime-adapter.md)与 [DeepSeek Harness Adapter](adapters/dsh/runtime-adapter.md)：各自 Runtime transport；DSH Adapter 另映射可选的 Sacha 可视化记录面。

源码和文档用于核对规则与实现。需要确认插件是否已安装、新会话能否发现它、子代理能否派发或实际运行行为时，分别用对应场景的直接证据判断。
