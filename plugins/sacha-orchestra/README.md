# Sacha Orchestra

> 文档身份：插件发布使用；位于发布 `root` 内。

Sacha Orchestra 是一套跨宿主的项目工作流插件。这里列出安装后可用的入口，以及各项运行规则的位置。

## 默认入口

Codex 先根据 `$sacha-orchestra:using-sacha` 的简短说明判断任务是否适合 Sacha。任务符合条件、你明确要求使用，或有线索表明这项任务之前选用了 Sacha 时，才加载完整技能说明。在 DeepSeek Harness 中，可以直接说要用 Sacha，也可以调用 `using-sacha`。

继续已有任务时，先核对之前是否选择过 Sacha。原决定仍适用于本次请求时，按原流程继续。其他任务的目标、范围、授权和验收条件都清楚时，直接在当前任务处理。当关键决定、完整实施规格、让另一个对话接着做、正式协调或独立复核会改变做法时，才建议使用 Sacha。同一项建议只问一次。如何提问及等待时可以继续做哪些调查，见 [入口合同第 4 节](core/intake-contract.md#4-入口决定)。

## 显式入口

- 高级入口：`planner`、`executor`、`reviewer`；显式 `explore` 保持窄授权，目标项目生产源码、配置、资源与外部状态只读，可按 [Artifact Protocol](core/artifact-protocol.md) 写探索决定记录，以及制作、预览独立界面草稿。
- 明确调用 `roadmap` 可编写长期项目路线图，必要时用 `explore` 补齐事实。路线图应能独立阅读和使用，由 `document-project` 保存到项目配置指定的路线图目录。创建或实施规格由你另行发起。若建议另开任务写完整实施规格，会明确推荐 Sacha Planner 任务。你确认创建后，新任务从 `planner` 入口开始，本次路线图的授权仅适用于原任务。
- `document-project` 接受 Human 显式文档请求，或正常 Workflow 的收尾候选路由；显式发布文档目标的 path 即本次写入授权，可按模板新建或原位更新且不要求 Project Integration；其他请求继续服从项目策略。不接受 Sacha、不补走生产 Role。
- `closeout` 处理用户明确要求的「收口」「存档」或「收口并存档」。「收口」在满足完成条件后，把本次唯一获批的实施规格标为「已完成」，只更新原文件的状态行。「存档」通过 `document-project` 归档项目文档。「收口并存档」先标记完成，再归档。只讨论或引用这些词语时，不执行这些动作。
- `feedback` 只由 Human 在另一个真实任务手动调用，可提交流程问题、使用反馈或插件开发想法。来源任务交付唯一目标任务 reference 后结束，目标任务按普通任务重新判断。
- Manager 只接受内部 Gate 路由，不是用户入口。
- `setup-project`、`setup-agents` 是主流程外显式配置能力，不属于 workflow 入口。

入口不会扩大写入、安装、Git、发布、远程资源或高影响动作授权。

## 运行规则

- [Intake Contract](core/intake-contract.md)：入口接受/拒绝与重复抑制。
- [术语合同](core/terminology-contract.md)：流程与 Artifact 的提炼术语、定义与边界。
- [工作流合同](core/workflow-contract.md)规定任务何时进入规划、实施、评审和收尾。
- [交互合同](core/human-interaction-contract.md)规定怎样提问、报告进度和交付结果。
- [验收合同](core/assurance-contract.md)规定按哪个版本核对、怎样执行验收和作出裁决。
- [协调合同](core/coordination-contract.md)规定怎样安排依赖、派发、等待、接收结果和移交责任。
- [工作记录协议](core/artifact-protocol.md)规定何时保存记录、以什么为准，以及怎样接手和恢复任务。
- [Codex Adapter](adapters/codex/runtime-adapter.md)、[Claude Code Adapter](adapters/claudecode/runtime-adapter.md)与 [DeepSeek Harness Adapter](adapters/dsh/runtime-adapter.md)：各自 Runtime transport；DSH Adapter 另映射可选的 Sacha 可视化记录面。

源码和文档用于核对规则与实现。需要确认插件是否已安装、新会话能否发现它、子代理能否派发或实际运行行为时，分别用对应场景的直接证据判断。
