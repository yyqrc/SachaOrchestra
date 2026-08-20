# 术语合同

> 状态：规范性 Core 术语合同

本文统一插件内提炼术语的定义。

## 术语

| 术语 | 定义 |
| --- | --- |
| 入口候选 | 初次判断或语义转折中，已有事实表明进入 Sacha 可能改变执行方式，但 Human 尚未决定是否接受的入口分类；只用于一次性提议与重复抑制，不表示已接受 Sacha、打开 Gate 或取得授权。 |
| 主任务 | 当前持有工作流 Owner 并负责推进根终态的用户任务；迁移成功后指新 Owner 所在的目标任务。 |
| 单层派发 | 主任务创建全部委派 Agent；每个委派 Agent 都是主任务的直接子级，不调用 Manager 或创建下级 Agent；迁移成功后改由新主任务执行。 |
| 委派 Agent | 主任务为一个工作单元创建的 Agent；只完成该单元并返回，不取得工作流 Owner 或派发权。 |
| 协调请求 | 委派 Agent 需要继续拆分、依赖协调或额外 Agent 时，向主任务返回重新评估所需的原因、候选单元、依赖或 reference；只定义返回语义，不新增状态、字段或 Artifact。 |
| 普通批准 | Human 批准 Spec，且未明确选择新任务执行。 |
| 明确迁移批准 | Human 批准 Spec，并通过选择项或同义明确表达选择新任务执行；不表示执行任务迁移前提已经满足。 |
| 可靠迁移信号 | Spec 已持久化且可达，并有可核实的 Runtime 上下文占用高或压缩事实，或存在不依赖未落盘对话的可观察多阶段长历史；只决定 Human 审阅选项的推荐顺序。 |
| 执行任务迁移前提 | Human 已明确迁移批准，Spec 已持久化、可达且获批，Entry Condition 已满足，当前主任务是唯一工作流 Owner，且同一 Scope 没有活跃执行写入者；只用于批准 Spec 后迁到新任务执行，不适用于 Feedback Owner 转移，也不改变已批准的 Spec、Scope 或验收。 |
| `base` | Human 或配置直接提供的目录；尚未表示解析、派生或验证后的实际生效目录。 |
| `root` | 从 `base`、配置或发现结果解析、派生并实际生效的目录；不得代指任意输入目录。 |
| `path` | 文件或目录在文件系统中的位置；用于可直接读取、写入或解析的文件系统目标。 |
| `reference` | 非文件的证据、Owner、Runtime 标识或间接指向；不得代替本应明确的文件 `path`，也不得另建 `locator` 作为同义术语。 |
| 能力加载策略 | Project Integration 的已确认 Capability Binding 对规范 Skill 的加载条件；只决定何时读取并采用 Skill，不表示授权、前置满足或动作已执行。 |
| Artifact | 供执行、恢复、复核或返回消费者使用的工作流记录；不替代原始事实、Human 授权或流程状态。 |
| Spec Artifact | Planner 基于已核实项目事实和 Human 决定形成、经 Human 批准后作为实施与评审基线的目标项目实施规格；内容格式与权威关系由 Artifact Protocol 定义。 |
| Roadmap | 面向项目 Human 与 Agent 的自包含长期路线文档，保存目标、当前状态、阶段、依赖、完成信号、Spec 映射、决策前沿、`Unknown` 与排除范围；不是 Artifact 或 Spec，不授予实施，也不保存 Sacha 内部路由。 |
| Spec 完成 | 当前任务已进入 `goal_complete`，必需验证与适用 Review 已满足后，把当前唯一已批准 Spec Artifact 的既有状态行原位标记为“已完成”；不移动、改名或生成新 Artifact。 |
| 探索决定记录 | Spec 形成前保存后续规划或恢复会消费的已确认决定、未决项和最小恢复边界的 Artifact。 |
| Execution Report | 保存实际变更、验证、偏差、风险和证据 reference 的可恢复索引。 |
| Review Artifact | 保存 Reviewer 判断、证据缺口与下一路由的 Artifact。 |
| Handoff | 供既有跨 Role 或恢复消费者继续工作的最小信息；不是流程节点或完成证据。 |
