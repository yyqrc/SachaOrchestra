# Artifact Protocol（产物协议）

> 状态：规范性 Core 合同

## 1. 范围与权威

本文是 Artifact 生成条件、最小内容、权威关系、Spec 完成和恢复规则的唯一权威。Artifact、Spec Artifact、Spec 完成、澄清决定记录、Execution Report、Review Artifact 与 Handoff 的定义见[术语合同](terminology-contract.md)；入口/Role/Gate 由 [Intake Contract](intake-contract.md) 与 [Workflow Contract](workflow-contract.md) 定义，Human 可见交互由 [Human Interaction Contract](human-interaction-contract.md) 定义。
Review 与返回分别由 [Assurance Contract](assurance-contract.md)、[Coordination Contract](coordination-contract.md) 定义。

保存路径由 Project Integration/Adapter 决定，不改变语义、字段或权威。真实文件、外部状态、文件差异（diff）和命令原始输出仍是实现与验证事实；Artifact 只索引或承载消费者需要的信息。

报告与原始事实冲突时以原始事实为准并记录冲突。改变批准 Scope 必须修订 Spec 并取得所需授权，不能由报告静默覆盖。

## 2. 渐进且最小

| Artifact | 生成条件 | 最小内容 |
| --- | --- | --- |
| 最终任务记录 | 同一上下文简单完成 | 修改、验证、失败/未验证与剩余风险 |
| 澄清决定记录 | Spec 形成前已有确定决定供规划消费，或多轮/分支/压缩恢复需要保留澄清锚点 | 已确认决定、依据/约束、未决项与 reference；恢复确需时增加原始问题、当前关注点、暂存思路，以及尚未探索/解决的实质分支、依赖与关键排除依据；疑似跨任务术语按需记录定义、排除含义、证据、边界、任务外消费者和 `Unknown` |
| Spec Artifact | 持久 Scope、批准方案或跨上下文恢复 | 目标项目实施规格；内容格式见第 2.1 节 |
| Execution Report | 续跑、证据索引或正式 Review | 实际变更（`delta`）、验证、偏差、风险、reference、恢复入口 |
| Review Artifact | 正式 Review | 问题、裁决结果（Outcome）、证据缺口、下一路由 |

### 2.1 Spec Artifact

Spec Artifact 面向目标项目的 Human、Executor 和 Reviewer。只给三者项目规则、项目事实和 Spec 时，必须仍能理解目标、边界、方案与验收；移除 Sacha 上下文不得改变其技术含义或可执行性。

项目已有实施规格格式且能完整承载下表语义时沿用项目格式；否则按以下顺序生成，必需内容不得省略，按需内容为空时不保留标题：

| 顺序 | 内容 | 要求 |
| --- | --- | --- |
| 1 | 目标 | 必需；说明项目问题、预期结果和可观察变化 |
| 2 | 范围 | 必需；分别说明本次包含与不包含的项目边界 |
| 3 | 项目事实与技术决定 | 必需；保存已确认事实、约束、技术决定与不变量 |
| 4 | 实施前提与依赖 | 按需；只记录项目环境、数据、工具和步骤依赖 |
| 5 | 实施方案 | 必需；说明项目位置、预期改动、顺序和完成结果 |
| 6 | 验收标准 | 必需；描述静态、构建、运行或人工可观察的项目结果，不写工作流执行分类 |
| 7 | 失败保护与回退 | 必需；说明停止实施的项目事实、禁止副作用、保留状态和恢复方式 |
| 8 | 风险与未验证项 | 按需；说明影响、验证方式和仍未知的项目事实 |
| 9 | 主要代码与资源位置 | 按需；列出实施和评审需要定位的项目文件、资源或配置 |

Planner → 写入既有项目概念 → 沿用项目当前定义。

Planner → 写入既有代码、字段、配置、资源或正式项目术语 → 使用项目来源中的精确名称 → 项目来源未定义简称或别名时不得自行新增。

Planner → 写入新增项目概念 → 按项目语义说明定义、直接消费者和边界 → 不得把临时规划抽象升级为项目术语。语言、单词或命名形式本身不决定是否合法；项目源码、规则、配置、正式文档和直接消费者决定语义。

Planner → 改写项目约束、验收或失败保护 → 保留项目来源中的主体、条件、动作、规范强度、边界与例外 → 不得用项目来源没有的概括性标签扩大或替代原意。

Planner → 确定 Spec 事实 → 只接受项目规则、源码、配置、正式项目文档或已确认项目决定 → 其他来源不得单独定义项目约束或项目术语。

Execution Report、Review Artifact、Handoff、其他工作流输出、运行时传输、Sacha Core 合同、Skill、Runtime Adapter 和 Planner 内部推理 → 只提供证据、流程状态或行为规则 → 不得原样或通过翻译、改写、概括、同义替换进入 Spec。输入同时包含项目事实和流程动作时，Planner 只写有独立项目来源的事实。

Planner → 遇到工作流角色、路由、协调、验证责任分类、迁移、裁决或运行时传输信息 → 分别交给 [Workflow Contract](workflow-contract.md)、[Assurance Contract](assurance-contract.md)、[Coordination Contract](coordination-contract.md)、Review Artifact、Handoff 或 Runtime Adapter → 不写入 Spec。

项目运行所需环境和数据前提进入“实施前提与依赖”；授权、任务迁移、单写入者和恢复路由由主任务按 [Intake Contract](intake-contract.md)、[Workflow Contract](workflow-contract.md) 与 [Coordination Contract](coordination-contract.md) 判断，并在存在恢复消费者时通过 Handoff 交付，不写入 Spec。

批准后的 Spec 是唯一实施与评审基线。实施事实证明其中的范围、技术决定或验收失效时，Executor 只报告项目事实和证据，由 Workflow Contract 决定下一路由；Spec 不保存返回某个 Role、重新规划、进入评审或其他同义流程指令。

### 2.2 生成与消费

Artifact 只在存在消费者时创建。澄清决定记录优先使用项目既有载体；无约定且存在规划或恢复消费者时使用任务目录中的 `decisions.md`。它只保存已确认决定、未决项、必要 reference 和压缩后必须重建的最小恢复边界，旧项确认或失效后原位压缩。

Planner 读取决定记录形成 Spec 并沿用已确认术语。项目上下文候选在收尾时基于最终实现/Review 证据复核，并在文档授权覆盖后进入项目 `CONTEXT.md`。

一个事实只写一次：Spec 保存第 2.1 节定义的项目内容；工作流中的目标、Scope、验收与 Handoff 只引用对应 Spec 内容，不复制其定义；Execution Report 的 `delta` 专指表中的实际变更，Review Artifact 不定义 `delta`，只保存问题、裁决结果（Outcome）、证据缺口和下一路由，并引用 Baseline、Execution Report 与原始证据。Human 审查关注点（Review Focus）和当轮最终建议清单按 Human Interaction Contract 直接交付。
长度按风险和恢复需要自适应，不为格式拆文件。各 Artifact 的失败、未验证、授权、风险、证据与进入条件只由其直接消费者和本协议的内容边界决定，不得因压缩丢失，也不得为形式完整复制到无消费者的 Artifact。

Execution Report 在恢复、证据索引或正式 Review 存在消费者时随任务形成，并保存到 Spec/任务约定的 Artifact 位置。Project Documentation 的候选与授权由 Workflow 收尾和 `document-project` 决定，目标位置由 Project Integration 决定；Execution Report 继续留在任务 Artifact 位置。

## 3. Spec 完成

- 主任务 → 收到 Workflow Contract 路由的 Spec 完成动作 → 从当前任务、批准 Spec reference 或 Human 明确 path 取得当前 Spec → 不得扫描 Spec storage root 按时间或名称猜测当前任务。
- 当前 Spec 缺失、存在多个候选、不是可达的单一 `spec.md`、未批准或头部状态行不唯一 → 失败关闭且不写入。
- 当前任务尚未进入 `goal_complete`，或必需验证与适用 Review 尚未满足 → 保持 Spec 原状态并报告未满足条件 → `goal_partial`、`goal_cancelled`、`goal_superseded` 和其他非完成终态不得标记为已完成。
- 当前上下文可写且本次 Spec 状态写入已有明确 Human 授权 → 生成精确状态行编辑计划，再用 Runtime 的并发检查局部编辑把该行原位改为“已完成”并回读验证 → path、文件名、其余正文和 Artifact 身份保持不变；不得用整文件替换覆盖并发正文。
- Spec 已是“已完成” → 返回 `no_op`；状态行变化、只读上下文或局部编辑失败 → 不盲目重试、不移动文件、不创建替代 Artifact，报告原始缺口与恢复条件。
- Spec 完成只消费任务终态，不生成项目文档；项目文档继续由 `document-project` 按独立策略和授权处理。

## 4. Handoff

只有正式跨 Role 或恢复消费者无法从现有 Scope、Artifact 和原生传输安全继续时才写 Handoff。它按需提供：

- 路由标识：稳定的 Task/Scope 修订号，以及 Source/Target/Owner 中传输未携带但消歧必需的部分；
- 结果：已完成且可核实的结果；
- 范围：批准 Spec/用户目标的 reference；
- 产物/证据：恢复材料与真实状态 reference；
- 风险/进入条件：偏离、未验证、风险及开始前必须满足的授权、状态和验证。

名称、顺序和载体由消费者决定；空内容省略。Human 可见内容遵循 Human Interaction Contract。确有领域或 Runtime 消费方时可增加带命名空间的扩展；扩展沿用本协议的权威与授权边界。

## 5. 恢复规则

- Handoff 嵌入承载 Artifact/消息，不单建 Handoff 文件。
- reference 必须稳定、可达，可移植 Artifact 优先相对位置或环境中立标识。
- 同环境恢复确需绝对路径时标记 `non-portable`，可用时同时给出相对或环境中立 reference；Runtime 实例 ID、模型、界面状态和内部存储标识只进入仅供 Runtime 的传输。
- Outcome、报告或 Role 自报不能替代证据 reference 指向的原始证据。
- 返修/重规划保持 Task ID，除非 Human 建立新 Scope。
- Target 核对可用路由标识、Scope、Artifact/Evidence 和 Entry Condition；不满足时暂停或报告部分完成。
- 恢复继续使用 Spec、Execution Report 和 Review 作为权威状态。
