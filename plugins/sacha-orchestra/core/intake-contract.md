# Intake Contract（入口合同）

> 状态：规范性 Core 合同

## 1. 范围

本文是 `using-sacha / 显式生产 Role / 显式 Explore / 显式 Roadmap / 显式 closeout / 显式 document-project` 入口、独立显式 Feedback 任务、接受/拒绝、重复抑制和授权边界的唯一 Runtime 权威。入口候选、主任务、委派 Agent 与协调请求的定义见[术语合同](terminology-contract.md)；接受后的生产路由及主流程外 Roadmap 跨 Skill 路由由 [Workflow Contract](workflow-contract.md) 定义，协调动作由 [Coordination Contract](coordination-contract.md) 定义；Human 可见提问与结果遵循 [Human Interaction Contract](human-interaction-contract.md)。

Intake 不依赖平台或项目。Runtime 发现归 Adapter；入口流程归 `using-sacha`；项目知识仍归 Project Integration 或 Domain Skill。

## 2. 最小加载

Runtime 常驻默认入口只需要 `using-sacha` 元数据；元数据匹配到入口候选或 Human 显式调用 `using-sacha` 时，才加载入口 Skill 与本文。其他显式入口由各自元数据发现；Human 接受前不得仅为 Sacha 路由加载 Workflow Contract、Artifact Protocol、Project Integration 或生产 Role。

自动匹配路径的 Direct 只使用元数据完成筛选，不触发入口 Skill 或加载本文；保持当前任务直接执行，不生成 Goal、Artifact 或 Handoff。

## 3. 入口判断

- Human 只有明确要求由本工作流编排当前目标、选择接受，或直接调用 Planner、Executor、Reviewer 时才接受。Human 确认创建一个此前已明确说明使用 Sacha Planner 的独立 Spec 任务，属于对该新目标的选择接受；只确认创建普通任务不属于接受。显式调用 `using-sacha` 只触发入口判断；任务对象、产品名或正文术语不得推断为执行方式选择。
- Direct：目标、Scope、授权与验收足够明确，当前上下文可安全完成，且没有入口候选；无论复杂度、文件数和耗时，默认直接执行。
- 入口候选按 Planner Gate 事实处理：
  - 尚无 Planner Gate 事实时，持久 Owner、跨上下文恢复或正式编排会实质改变执行方式，且 Human 尚未选择是否进入 Sacha。
  - 已有 Planner Gate 事实时，目标、Scope、Acceptance、Owner 或路径存在实质不确定性；实施前需要关键 Human 澄清、需要起草/冻结供后续实施或验收使用的完整可执行 Spec，或存在实质方案、难回退的跨 Owner 决策、破坏性迁移。是否已经出现“持久化”或“落盘”字样不改变这个判断。

- Planner、Executor、Reviewer 接受 Human 直接调用。
- Explore 接受 Human 显式窄授权，或由活跃 Planner 路由。
- Roadmap 只接受 Human 显式调用；该调用不接受 Sacha 或进入生产 Role。
- document-project 接受 Human 显式文档请求，或由 Workflow 收尾候选路由。
- Feedback 接受 Human 在另一个真实任务手动提交的流程问题、使用反馈、插件开发建议或能力想法。
- Manager 只接受内部 Owner 路由；Reviewer Gate 与 Manager Gate 由 Workflow 在接受后判断。

复杂度、文件数量、耗时、多平台、持续验证、Skill/插件关键词或插件已安装不构成入口事实。

## 4. 入口决定

- 初次判断及 Direct 执行期间，主任务必须在继续形成实质方案、实施或持久化前检查语义转折。诊断演变为设计/修改、授权扩到新 Owner/平台，或新增 API 形态、Owner、回退/行为模式决策、Spec 消费者、跨上下文恢复需求，且这些事实会改变执行方式时，必须停止当前 Direct 推进并重新执行入口判断；完成入口决定前不得继续形成单一路线的实施方案。
- 元数据已经匹配入口候选时，只能先读取确认该候选是否成立所需的最小事实。当前输入或最小核对已经证明候选成立后，必须在继续领域调查、加载实施或规划 Domain Skill、形成方案、实施或持久化前完成入口决定；不得把完整项目调查解释为入口判断所需的核对。
- 同一目标或表面 Scope 名称未变，不得压过已改变的 Acceptance、风险、授权、Owner、实现边界或交付模型。没有第 3 节入口候选时保持 Direct。
- 自动识别到入口候选时，只询问一次是否进入 Sacha，并按 Human Interaction Contract 说明新增能力、成本、执行影响与推荐。
- Human 接受后，当前根 Owner 按需加载 Workflow Contract、当前 Adapter、已确认的 Project Integration 与目标 Role。
- Human 拒绝后按当时事实保持 Direct；同一入口候选不得重复推销或创建 Sacha Artifact。实质变化形成新入口候选时可再推荐一次。
- reference、日志、进度、非语义文案或仅估算变化不触发重问。
- 重复抑制只依赖当前上下文或正式恢复证据；不得新增跨会话注册表（Registry）。

| Human 输入 | 授权范围与下一路由 |
| --- | --- |
| 显式调用 `using-sacha` 评估入口 | 执行本合同的入口判断；只有 Human 随后明确选择接受才进入 Sacha 路由 |
| 明确要求用 Sacha 编排当前目标、选择接受，或直接调用 Planner、Executor、Reviewer | 接受当前目标/Scope 的 Sacha 路由；主任务按 Workflow Contract 推进 |
| 确认创建此前已明确推荐为 Sacha Planner 的独立 Spec 任务 | 接受新任务目标/Scope 的 Sacha 路由并授权创建该用户任务；目标任务从显式 Planner 入口开始，不继承 Roadmap 的写入、实施或其他高影响授权 |
| 显式 Explore | 授权主任务在窄 Scope 内探索并管理一个有界只读研究委派 Agent；Explore 委派 Agent 只返回研究结果或协调请求，多个研究就绪单元由主任务按 Manager Gate 协调 |
| 活跃 Planner 路由 Explore | 沿用既有 Sacha 接受状态与 Owner，结果返回 Planner |
| 显式 Roadmap | 只授权当前 Roadmap 目标内读取项目事实、按需调用 Explore 做有界只读探索，并把自包含正文交给 document-project 按 Project Integration 写入；不接受 Sacha、不进入生产 Role、不创建或执行 Spec |
| 显式 document-project | 直接路由当前文档目标到 document-project；显式发布文档目标的 path 构成本次写入授权，不要求 Project Integration；其他请求继续服从项目策略和写入授权；不接受 Sacha、不补走生产 Role，也不替代正常 Workflow 的收尾候选检查 |
| `closeout` 请求 | 只授权当前 closeout 目标，不接受 Sacha；具体动作、顺序与失败路由由 Workflow Contract 决定，Spec 与项目文档写入继续服从各自 Owner |
| 显式 Setup Project | 只授权本次项目配置 Scope；后续开发目标重新判断入口 |
| 在另一个真实任务显式调用 Feedback | 授权来源任务围绕具体反馈目标有界只读调查，并查询、复用或创建唯一反馈目标任务；Human 可提供原任务、项目或证据 reference；目标任务另行核对写入与外部动作授权 |
| 直接调用 Manager | 返回当前目标给 `using-sacha` 或主任务，由 Manager Gate 路由 |

通过显式 Explore、活跃 Planner 或活跃 Roadmap 进入 Explore 时，主任务可按 [Artifact Protocol](artifact-protocol.md) 创建或更新探索决定记录；该工作流 Artifact 写入不授权修改目标项目源码、配置、资源或外部状态。

入口授权只作用于当前目标/Scope。探索决定记录写入只采用上一条边界；其他工作区写入、安装、Git、发布、远程资源、权限、高影响动作和 Planner 后续形成的实质方案分别取得对应授权；安全与工程规则持续生效。

Hook 可以由 Runtime 在另行授权后预加载环境信息，但不得接受 Sacha、替代 `using-sacha`、扩大授权或成为正确性与恢复前提。
