# Intake Contract（入口合同）

> 状态：规范性 Core 合同

## 1. 范围

本文是 `using-sacha / 显式生产 Role / 显式 Explore / 显式 Roadmap / 显式 closeout / 显式 document-project` 入口、独立显式 Feedback 任务、接受/拒绝、重复抑制和授权边界的唯一 Runtime 权威。入口候选、主任务、委派 Agent 与协调请求的定义见[术语合同](terminology-contract.md)；接受后的生产路由及主流程外 Roadmap 跨 Skill 路由由 [Workflow Contract](workflow-contract.md) 定义，协调动作由 [Coordination Contract](coordination-contract.md) 定义；Human 可见提问与结果遵循 [Human Interaction Contract](human-interaction-contract.md)。

Intake 不依赖平台或项目。Runtime 发现归 Adapter；入口流程归 `using-sacha`；项目知识仍归 Project Integration 或 Domain Skill。

## 2. 最小加载

Runtime 常驻默认入口只需要 `using-sacha` 元数据；元数据匹配到入口候选、继续任务中的既有接受线索，或 Human 显式调用 `using-sacha` 时，必须加载入口 Skill 与本文。其他显式入口由各自元数据发现；Human 接受前不得仅为 Sacha 路由加载 Workflow Contract、Artifact Protocol、Project Integration 或生产 Role。

自动匹配路径的 Direct 只使用元数据完成筛选，不触发入口 Skill 或加载本文；保持当前任务直接执行，不生成 Goal、Artifact 或 Handoff。

## 3. 入口判断

- Human 只有明确要求由本工作流编排当前目标、选择接受，或直接调用 Planner、Executor、Reviewer 时才接受。Human 确认创建一个此前已明确说明使用 Sacha Planner 的独立 Spec 任务，属于对该新目标的选择接受；只确认创建普通任务不属于接受。显式调用 `using-sacha` 只触发入口判断；任务对象、产品名或正文术语不得推断为执行方式选择。
- Human 要求继续、迭代、返修或验收既有目标时，必须先核对当前上下文或正式恢复证据中的接受事实、适用 Scope 和当前要求；有效接受仍适用且未被撤销时，必须恢复已接受流程，按 Workflow Contract 判断当前 Role/Gate，不因方案已明确而退回 Direct，也不重复索取接受。Spec、任务链接或报告中的 Sacha 名称只提供核对线索；只读参考、独立咨询或新目标不继承原任务接受与写入授权。证据不足时只查具名来源的相关决定，再按本节普通入口判断，不推定接受。
- Direct：不存在仍适用的接受事实，且目标、Scope、关键决定、授权与验收足够明确，当前上下文可安全完成，没有下述实际规格交付或交接需求时，默认直接执行；跨文件、跨插件、规则或模型路由的行为变化本身不改变这一判断。
- 以下事实构成入口候选；本阶段只决定是否提出 Sacha 选择，不预判 Role Gate：
  - 持久 Owner、跨上下文恢复或正式编排会实质改变执行方式，且 Human 尚未选择是否进入 Sacha。
  - 会改变实施路线的关键方案需要比较与冻结；或 Human 要求完整 Spec，或实际后续消费者、难回退的跨 Owner 决策、破坏性迁移需要规格交付。
  - 局部缺失信息先通过最小查询或问题补齐，只暂停依赖答案的部分；不因一个局部问题自动进入正式规划。没有用户要求或实际规格消费者时，Agent 不得先自行决定写完整 Spec，再据此制造入口候选；可在当前任务内说明改动与验证。

- Planner、Executor、Reviewer 接受 Human 直接调用。
- Explore 接受 Human 显式窄授权，或由活跃 Planner / Roadmap 路由。
- Roadmap 只接受 Human 显式调用；该调用不接受 Sacha 或进入生产 Role。
- document-project 接受 Human 显式文档请求，或由 Workflow 收尾候选路由。
- Feedback 接受 Human 在另一个真实任务手动提交的流程问题、使用反馈、插件开发建议或能力想法。
- Manager 只接受内部主任务路由；Role Gate 与协调路由由 Workflow 判断，Explore 的合法调用不要求另行接受完整 Sacha。

复杂度、文件数量、耗时、多平台、持续验证、Skill/插件关键词或插件已安装不构成入口事实。

## 4. 入口决定

- 初次进入或目标、方案、交付、授权等事实发生实质变化并影响执行方式时，按第 3 节判断当前目标及准备推进的工作；普通步骤之间不重新评估入口。独立咨询按其窄目标判断，不能用“只读”或“前置验证”名称绕过实际已经出现的规格或编排需求。
- 入口候选成立且具备选择条件时，按 Human Interaction Contract 主动说明影响并询问一次是否进入 Sacha。只调查足以支持该选择的事实，不为提问先完成全套规划；等待期间继续与选择无关的已授权工作，依赖该选择的方案、派发与持久化等待答案。反问不算决定，无依据的推荐应纠正并保持 Direct。
- Human 接受或核实既有接受仍适用后，当前根 Owner 按需加载 Workflow Contract、当前 Adapter、已确认的 Project Integration 与目标 Role；只恢复当前请求对应的工作，验收请求不因此获得实施授权，任务创建和 Owner 迁移仍遵守原有条件。
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

通过显式 Explore、活跃 Planner 或活跃 Roadmap 进入 Explore 时，主任务可按 [Artifact Protocol](artifact-protocol.md) 创建或更新探索决定记录，以及制作、预览独立界面草稿；这些规划材料不授权修改目标项目生产源码、配置、资源或外部状态。

入口授权只作用于当前目标/Scope。上述规划材料只采用上一条边界；其他工作区写入、安装、Git、发布、远程资源、权限、高影响动作和 Planner 后续形成的实质方案分别取得对应授权；安全与工程规则持续生效。

Hook 可以由 Runtime 在另行授权后预加载环境信息，但不得接受 Sacha、替代 `using-sacha`、扩大授权或成为正确性与恢复前提。
