---
name: clarify
description: 显式澄清、脑暴、现状调查或方案打磨，或已接受 Sacha 且 Planner 仍缺目标、边界、验收/实质决定时使用；目标清晰时不用，不拥有 Scope、授权或裁决。
---

# Clarify（需求澄清）

## 功能

拥有 Planner 前的有界澄清节点：补齐会改变方案的事实与 Human 决定，再把事实、决定、冲突和未决项交回调用节点。Scope、授权、实施和裁决由对应 Role/Human 拥有。

## 输入与首查

1. 入口为 Human 显式调用，或活跃 Planner 发现目标结果、Scope/Non-goals、验收或实质决定未收口后的显式路由。
2. 先从代码、项目规则和已提供的 Domain/项目 Skill 核对事实。Project Integration 的已确认 Binding 可用时按 [Workflow Contract](../../core/workflow-contract.md) 的能力加载策略决定是否加载对应 Skill；加载后完整读取正文并另行核对只读边界、前置、副作用和授权，不满足时回退项目规则、可发现 Domain Skill 或原生路线并保留未验证项。Project Integration 给出 Project Context path 时，按当前术语、架构或跨任务约束查询相关 `CONTEXT.md`，不遍历历史任务目录。
3. 只把无法自行确认、会改变方案且决定权属于 Human 的内容列为问题。Planner/Executor 可依据已确认语义安全决定的局部实现选择直接进入方案。

## 动作顺序

1. 根据当前输入组合以下工作意图：
   - `brainstorm`：想法还模糊时，先收敛目标结果、Non-goals 和主要约束；存在实质不同的候选时比较取舍并给出推荐。
   - `survey`：方向已有但现状、内部先例或外部方案不清时，先用代码、项目资料、可用 Skill 或必要的一手资料形成可比较事实，再询问取舍。
   - `grill`：已有大致方案时，核对前提，使用反例和具体场景检查术语/Owner、状态/生命周期、失败/恢复、数据/迁移/兼容、环境差异、回退与可证伪验收；按风险选择零值/极值、重复/乱序、重入/中断、旧新数据互读等压力视角，不把抽象认可当作方案已打磨或把视角变成固定问卷。
2. 维护只覆盖实质分支的有界挑战图，标记可问项、上游依赖、待查事实、排除依据和未决项；按依赖顺序处理。
3. 向 Human 提问、解释或报告进度前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。对话按以下语义更新挑战图：
   - Human 拥有的业务事实与新增约束直接采纳；代码、运行状态或外部现状先核对。方案偏好先确认其事实前提和影响；猜想与推测记录为调查线索，已核实事实和 Human 决定进入决定记录。
   - Human 请求解释或调查时先核对真实来源，再回答并返回当前未决决策。
   - Human 输入明确选择或约束时记录决定；纠正前提或提出新方向时更新事实、锚点和未决分支；含义不清时只澄清该含义。
   - 同词多义、同义多名、两个概念被错误合并、模糊词或 Human/文档/代码定义冲突时，先查工程用法，再确认采用与排除的含义。输入与证据冲突时展示差异并询问真正需要 Human 决定的部分，不静默选边；`grill` 暴露的新边界可返回 `survey` 查证，调查结果也可触发新的方案比较。
4. 沿用[术语合同](../../core/terminology-contract.md)的主任务、委派 Agent 与协调请求。必要事实不可低成本取得时，向主任务请求一个有界只读研究委派 Agent，给出问题、查询范围、预期证据、停止条件和输入。主任务出现多个候选问题、依赖或恢复协调时，按 [Coordination Contract](../../core/coordination-contract.md) 调用 Manager 并消费其事实、冲突、未验证项和证据 reference；Clarify 委派 Agent 只返回研究结果或协调请求。
5. 已知后续会形成 Spec 或需要恢复时，第一个影响方案的决定确认后写入项目既有决定载体；多个未决项、分支打断或跨上下文风险出现时建立澄清锚点。无项目约定时在 Spec 任务目录使用最小 `decisions.md`。
6. 锚点只保存原始目标、已确认决定、当前关注点、阻塞性未决项、暂存思路、reference 和最小可恢复边界。恢复后先读锚点与当前证据，再重建挑战图。
7. 新思路用于解决当前未决项、增加阻塞性未决项或暂存为非阻塞候选。改变目标、Scope 或验收的新思路返回 Planner/Human。
8. 需供恢复或 Spec 消费的术语写入决定记录。具备任务外消费者或稳定接口的项目术语记录为项目上下文（`project-context`）候选，包含定义、排除含义、证据、边界、消费者与 `Unknown`。
9. 退出前扫描相关挑战面：影响方案的重要分支均已解决、明确暂缓、路由调查或保留为阻塞项；决定具备事实依据且关键歧义已消除。

## 输出

- 向调用节点返回已核实事实、Human 决定、冲突、阻塞性未决项、未验证项、证据 reference 和退出判断。
- 活跃 Planner 负责判断这些结果是否足以冻结 Spec。

## 停止与禁止边界

- 研究保持只读；Planner/Reviewer Gate、Scope、授权、Handoff、实施和验收由对应 Owner 处理。
- Project Context path、领域 Provider 和决定载体来自 Project Integration 与 [Artifact Protocol](../../core/artifact-protocol.md)。决定记录不替代批准后的 Spec，`project-context` 候选不授权项目文档写入。
- `brainstorm`、`survey`、`grill` 是同一 Clarify 节点内的工作意图。
- 无法澄清的实质决策作为阻塞项返回 Planner/Human。
