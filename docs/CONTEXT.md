# Sacha Orchestra 项目上下文

> 文档身份：插件开发使用；不进入发布插件。

本文是开发控制面已提炼术语与规则的完整副本，供 `PLUGIN_DESIGN.md`、插件开发和评审使用；发布插件不包含或读取本文。[术语合同](../plugins/sacha-orchestra/core/terminology-contract.md)是插件内唯一术语 Owner，两边必须强双向同步。

## 术语

| 术语 | 插件内定义 | 定义与边界 | 直接消费者 |
| --- | --- | --- | --- |
| 入口候选 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 初次判断或语义转折中，已有事实表明进入 Sacha 可能改变执行方式，但 Human 尚未决定是否接受的入口分类；只用于一次性提议与重复抑制，不表示已接受 Sacha、打开 Gate 或取得授权。 | `PLUGIN_DESIGN.md`、Intake Contract、using-sacha Skill、插件 README |
| 主任务 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 当前持有工作流 Owner 并负责推进根终态的用户任务；迁移成功后指新 Owner 所在的目标任务。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Coordination Contract、Role Skill、Runtime Adapter |
| 单层派发 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 主任务创建全部委派 Agent；每个委派 Agent 都是主任务的直接子级，不调用 Manager 或创建下级 Agent；迁移成功后改由新主任务执行。 | `PLUGIN_DESIGN.md`、Workflow Contract、Coordination Contract、Manager Skill、Runtime Adapter |
| 委派 Agent | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 主任务为一个工作单元创建的 Agent；只完成该单元并返回，不取得工作流 Owner 或派发权。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Coordination Contract、Role Skill、Runtime Adapter |
| 协调请求 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 委派 Agent 需要继续拆分、依赖协调或额外 Agent 时，向主任务返回重新评估所需的原因、候选单元、依赖或 reference；只定义返回语义，不新增状态、字段或 Artifact。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Coordination Contract、Role Skill、Runtime Adapter |
| 普通批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Human 批准 Spec，且未明确选择新任务执行。 | `PLUGIN_DESIGN.md`、Workflow Contract、Planner Skill、Runtime Adapter |
| 明确迁移批准 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Human 批准 Spec，并通过选择项或同义明确表达选择新任务执行；不表示执行任务迁移前提已经满足。 | `PLUGIN_DESIGN.md`、Workflow Contract、Coordination Contract、Planner Skill、Runtime Adapter |
| 可靠迁移信号 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Spec 已持久化且可达，并有可核实的 Runtime 上下文占用高或压缩事实，或存在不依赖未落盘对话的可观察多阶段长历史；只决定 Human 审阅选项的推荐顺序。 | `PLUGIN_DESIGN.md`、Workflow Contract、Planner Skill |
| 执行任务迁移前提 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Human 已明确迁移批准，Spec 已持久化、可达且获批，Entry Condition 已满足，当前主任务是唯一工作流 Owner，且同一 Scope 没有活跃执行写入者；只用于批准 Spec 后迁到新任务执行，不适用于 Feedback Owner 转移，也不改变已批准的 Spec、Scope 或验收。 | `PLUGIN_DESIGN.md`、Workflow Contract、Coordination Contract、Runtime Adapter |
| Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 供执行、恢复、复核或返回消费者使用的工作流记录；不替代原始事实、Human 授权或流程状态。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Assurance Contract、Coordination Contract、Artifact Protocol、Role/支持 Skill、Runtime Adapter |
| Spec Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 持久保存目标、Scope、冻结决定、允许边界与验收的 Artifact。 | Workflow Contract、Coordination Contract、Artifact Protocol、Planner/Executor Skill、Runtime Adapter |
| 澄清决定记录 | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | Spec 形成前保存后续规划或恢复会消费的已确认决定、未决项和最小恢复边界的 Artifact。 | Artifact Protocol、Clarify/Planner Skill |
| Execution Report | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 保存实际变更、验证、偏差、风险和证据 reference 的可恢复索引。 | Workflow Contract、Artifact Protocol、Executor/Reviewer/document-project Skill |
| Review Artifact | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 保存 Reviewer 判断、证据缺口与下一路由的 Artifact。 | Assurance Contract、Artifact Protocol、Reviewer Skill |
| Handoff | [术语合同](../plugins/sacha-orchestra/core/terminology-contract.md) | 供既有跨 Role 或恢复消费者继续工作的最小信息；不是流程节点或完成证据。 | `PLUGIN_DESIGN.md`、Intake Contract、Workflow Contract、Assurance Contract、Coordination Contract、Artifact Protocol、Role/支持 Skill、Runtime Adapter |

## 判读关系

以下规则的路由 Owner 是 Workflow Contract，迁移动作与 Owner 转移归 Coordination Contract；本文只保存开发侧同步副本。

- 主任务 → Human 审阅 Spec 前 → 判断可靠迁移信号并给出普通批准、明确迁移批准和要求调整 → 信号成立时将明确迁移批准置首，否则将普通批准置首。
- Human → 选择普通批准 → 主任务进入 Executor。
- Human → 选择明确迁移批准 → 主任务停止实施和写入派发并核对执行任务迁移前提；全部满足后由 Adapter 查询、复用或创建唯一目标任务。
- Human → 要求调整 → 返回 Planner。
- Human → 取消或不再继续 → 主任务结束。
- 主任务 → 明确迁移批准不满足执行任务迁移前提 → 报告缺口与恢复条件并停止迁移 → 条件恢复后重新核对；Human 改为普通批准时进入 Executor。
- Adapter → 目标任务唯一确定并取得最小 Handoff → 单向转移工作流 Owner，目标任务成为主任务并接管剩余生命周期与派发权 → 来源主任务交付目标任务 reference 后结束，不等待返回。

## 术语边界

- 普通批准与明确迁移批准按 Human 是否明确选择新任务执行区分；只批准 Spec 或未明确选择新任务时属于普通批准。
- 可靠迁移信号只改变选项顺序，不构成 Human 批准，也不能替代明确迁移批准。
- 明确迁移批准只证明 Human 选择了迁移分支，不证明执行任务迁移前提已经满足。
- 执行任务迁移前提只用于批准 Spec 后迁到新任务执行；Feedback Owner 转移不使用该前提。
- Artifact 只索引或承载消费者需要的信息；真实文件、外部状态、文件差异和命令原始输出仍决定实现与验证事实。
- Spec Artifact、澄清决定记录、Execution Report 与 Review Artifact 是不同消费者使用的 Artifact，不得互相替代。

## 强双向同步

- 修改者 → 修改插件内提炼术语或规则 → 同次更新本文并核查直接消费者 → 受影响映射必须同次更新。
- 修改者 → 修改本文中的提炼术语或规则 → 同次更新插件内唯一 Owner 并核查直接消费者 → 受影响映射必须同次更新。
- 开发者或 Reviewer → 发现两边不一致 → 按插件内唯一 Owner 恢复运行语义并完成双向同步 → 同步完成前不得使用受影响术语或声明完成。
- 下游消费者 → 使用表内术语 → 只保留自身映射 → 提炼规则只在本文与插件内定义中保存。
