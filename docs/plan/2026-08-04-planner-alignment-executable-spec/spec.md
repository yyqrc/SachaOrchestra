# Planner 对齐、可执行 Spec 与轻量协作迭代

> 状态：Human 已批准；本仓 source 实施与静态验证已完成（2026-08-04），包括 Clarify 挑战覆盖、可恢复 frontier、项目 `CONTEXT.md` 与跨版本压力增量；安装、fresh Runtime、Provider 跨仓实施和 Human 产品判断仍按第 7 节保留
>
> 更新时间：2026-08-04
>
> 权威：本文件冻结本轮候选 Scope、决定、实施边界与验收；源码、真实 diff、命令输出和 Runtime 结果仍是实现与验证事实。
>
> Historical baseline / 部分 superseded：本文件保存 2026-08-04 已批准决定，但 §5.8～§5.9 的 Codex 模型、fallback 和 subagent 路由已被 `0.8.0` release 替代，不得作为当前执行规则。现行唯一 owner 为 [`plugins/sacha-orchestra/adapters/codex/runtime-adapter.md`](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md) §3；Manager/readiness 以 [`coordination-contract.md`](../../../plugins/sacha-orchestra/core/coordination-contract.md) 为准。

## 1. 直白结论

Sacha 当前能判断“需要 Planner”，但还没有把“Planner 形成了用户此前未确认的实质方案”与“Executor 可以开工”可靠隔开。修复方式不是新增 Role、Gate 或状态机，而是在现有 Planner 生命周期中补齐决策落盘和 Human 对齐条件：

- 澄清产生一项已确认决定时，尽快写入项目约定的轻量决策文件，防止长对话或上下文压缩丢失；未决项、事实与决定必须可区分。
- Clarify 根据输入在脑暴、现状调查和方案拷问之间自适应推进，并用同一套“追问—解释—继续追问”循环收口；三者不是固定模式、阶段或新 Role。
- 决策足以形成执行基线后，Planner 依据决策文件和当前工程事实生成 `spec.md`。决策文件保存澄清结果，`spec.md` 保存拟执行 Scope、方案、约束和验收；二者不能成为两个执行权威。
- Planner 引入了会改变用户可见行为、架构、数据/资产、Owner、迁移/兼容、难回退选择或验收方式的实质方案时，把 `spec.md` 标记为“待 Human Review”。
- Planner 回复只给结论、决策/Spec 路径、Human Review Focus、本轮 delta 和尚未决定项，不把完整 Spec 再复制进对话；一次回复处理多个问题或形成多项建议、取舍、异议点时，末尾再用稳定编号收齐“最终建议与待决定事项”，让 Human 能直接按编号自然回应。
- Human 接受后在 `spec.md` 中冻结批准状态；没有未决方案、额外授权或实施前置时，root owner 在同一任务自动进入 Executor，不再等待“开始实施”。有异议就按反馈修订决策文件和 Spec 的受影响部分，不另建 review/approval 文档或平行状态系统。
- 已由 Human 明确决定、且 Planner 没有引入新实质选择的实施请求，仍可直接进入 Executor，不增加重复确认。

Spec 的实施密度应处在“宽泛步骤”与“逐行代写实现”之间：Executor 不应重新发现 Planner 已经查清的 owner、依赖、顺序和风险，但仍保留 Scope 内的局部实现自主权。

`setup-agents` 当前仍需保留，但只作为 Codex Runtime 兼容安装器。它应改为 Sacha 命名空间下的 managed installation：Human 显式调用后，只自动创建或更新 Sacha-owned 文件；遇到非 Sacha 文件或身份冲突必须拒绝，不能强行覆盖。原生 Luna spawn 的 requested/effective model 与 reasoning 可被真实验证后，删除这层兼容能力。

## 2. 本轮依据

### 2.1 当前 Sacha 源码事实

- `Workflow Contract 10` 已规定默认 Executor-only；一个有界 helper 足够时不开 Manager，多个独立单元、依赖图或多环境才协调。
- `Coordination Contract 3` 已规定 helper 不取得生产 Role 或最终 verdict，Owner 负责 Scope、等待、取消、结果核对与集成。
- Codex Adapter 已要求 Owner 对本地 Pi 候选实现核对退出码、JSONL、真实 diff 并重跑验收；named route 的 requested/effective agent type、model、reasoning 与 fallback 也要求分别记录。
- Planner Skill 当前写着“已授权且无方案分歧直接进入 Executor”，但没有明确“Planner 新形成的实质方案必须先由 Human Review”。Workflow Contract 还笼统规定 Role completion 不是 Human checkpoint，存在把 Planner 完成误当作可直接实施的空间。
- Artifact Protocol 已把 Spec Artifact 定义为持久 Scope、批准方案和验收的 owner，并要求一个事实只写一次；当前却没有定义 Spec 产生前的澄清决定如何抵抗上下文压缩。因而需要补一个按需、轻量的决策记录边界，同时继续由 `spec.md` 独占执行基线与批准语义。
- 现有 `setup-agents` 会写入通用名称 `luna-worker.toml` / `luna-worker-xhigh.toml`，并为 Sacha-owned 更新和非 owned conflict 都保留二次 hash 确认及 `--replace-conflict` 路径；这与本 Spec 要求的“显式调用后只自动维护 Sacha 命名空间文件、永不覆盖他人文件”尚不一致。

### 2.2 三份本地样本比较

#### WaterReflection 实施计划

`G:\COD\iwiki\docs\done\WaterReflection-OpaqueSnapshot-DepthResolve-V2.md` 的高价值部分是：

- 每步给出精确文件、函数、附近行号和直接先例。
- 把 Vulkan/GLES 的不同机制、必须保持的执行顺序、兼容分支和回退条件写成实现不变量。
- 对未知项明确标注“执行时确认”，没有把静态推导冒充运行事实。
- 验收区分编译、日志、设备、抓帧、画面与回归，能定位每项原始证据。

但它也包含大量候选代码、历史推导和逐行实现说明。其密度适用于高风险、跨平台、脆弱渲染顺序，不应成为普通 Sacha Spec 的固定模板。

#### Editor IMGUI Spec

`G:\COD\iwiki\docs\plan\editor-imgui-physical-pixel-alignment\spec.md` 已把方案选择、冻结细节、Player/NGUI 隔离、构建与运行证据边界写清楚；不足在于“Executor 顺序”只有六个大步骤。每一步跨多个 owner 和验证面，Executor 仍需重新拆分目标位置、直接 delta、依赖和完成证据。这正是本轮要补的中间密度。

#### Change Probe Spec

`C:\Users\shifengzhou\Documents\Change Probe\spec.md` 已采用分阶段实施，并给每阶段明确通过条件、独立审查和 Executor 开工条件，执行信息比宽泛步骤更充实。其协议章节很完整，但阶段内部仍主要是模块级任务列表；对复杂改动仍可补精确 owner、约束和返回规划条件。

当前文件状态写明 v1 已完成测试和复审，可以确认它是已收敛后的丰富版本；仅凭当前文件无法确认“是否由用户在中途恰好迭代过一次”，本轮不把该猜测作为设计依据。

### 2.3 从样本吸收与拒绝的内容

吸收：

- 精确 owner/定位、预期 delta、脆弱顺序、不变量、直接先例、证据层和停止条件。
- 步骤级通过条件，以及 AI、Human 协同和 Human 验收的真实边界。
- Worker/helper 的窄写入边界、Owner 的真实状态核对、Runtime 路由可追踪与有界 fallback、同 Scope 返修回到原 Executor。

拒绝：

- 固定增加 Brainstormer、Alignment、Spec Reviewer 等 Role。
- 新增 Alignment Gate、Plan 状态机、任务分级或必须理解的协议字段。
- 默认生成 `brainstorm.md`、`draft-spec.md`、`approval.json`、`spec-review.md`、完整聊天/审批式 `decision-log.md` 或重复 Handoff；按需轻量 `decisions.md` 只保存当前已确认决定与恢复信息。
- 把所有任务都写成 WaterReflection 级别的逐行候选实现。
- 因任务复杂、多文件或耗时就自动启用 Manager 或多个 Agent。

## 3. Scope

### 3.1 Core 与 Role 语义

- 在 Intake Contract 与 `using-sacha` 中明确：接受 Sacha、上游建议 Planner/Reviewer 或授权完成目标只表示路由/目标授权，不批准 Planner 后续产生的新实质方案。
- 在 Workflow Contract 的 Human 路由中补齐：Planner 新形成、且 Human 尚未确认的实质方案，是进入 Executor 前的 Human 决策点。
- 由 Workflow Contract 的 Human 路由拥有通用回复收口语义：Role/Workflow 一次处理多个问题或形成多项建议、取舍、异议点时，结束前给出自然中文、稳定编号的“最终建议与待决定事项”；Planner Skill 只实现 Role-local procedure。
- 同时保留：Role completion 本身、同 Scope 返修、补证据和局部实现判断不是 Human checkpoint。
- 在 Clarify/Planner Skill 与 Artifact Protocol 中定义“轻量决策文件 → `spec.md`”的两层权威、压缩恢复、修订和批准收口；Planner Skill 另负责在 Human 可见回复中直接给出 Review Focus。
- 在 Clarify Role-local procedure 中补回有界挑战覆盖、术语歧义调查和按风险选择的极值/跨版本压力视角；它们只提高问题发现能力，不新增模式状态、固定问卷或完整决策树。跨任务术语只使用下一条定义的单一 Project Context path。
- 为跨任务术语提供一个确定入口：项目已声明 owner/path 时沿用；否则使用 `<Spec base>/CONTEXT.md`。它是项目上下文/术语文档，不是第二份 AGENTS、Spec 或任务历史，也不从 Project Documentation root 推导。
- 在 Coordination Contract 与 Runtime Adapter 中复用 `human_decision_required`：暂停 Executor dispatch，在同一 root task/Scope revision 等待 Human，确认后继续，不创建第二套 workflow。
- 在 Executor Skill 中明确只有批准状态或等价的 Human 已确认事实满足时，才消费包含新实质方案的 Spec。
- 在 Reviewer/Assurance 中明确 Human 方案 Review 与实施后独立验收不是同一件事，Reviewer 不能替代方案批准。

### 3.2 Spec 实施密度

- 为 Planner 增加自适应的“可执行步骤”写法，使用自然中文标签。
- 更新受影响的示例、README 或 validator，只验证关键语义和生产入口，不逐句锁死模板文字。
- 不规定所有步骤必须机械填写所有字段；简单、单 owner、模式既有的改动可以合并省略无价值项。

### 3.3 验收责任

- 由 Assurance Contract 拥有 A/B/C 对验收矩阵、人工状态、Outcome、re-review 和 owner route 的映射；Workflow/Artifact 只引用，不重定义。
- 在现有 Acceptance 语义内表达 A/B/C 三类路线、是否阻塞、需要的 Entry Condition 和恢复入口。
- 不把 A/B/C 变成新的 Gate、Role、根状态或固定 Artifact schema。

### 3.4 Runtime 协作与 `setup-agents`

- 保留 Executor-only + bounded helper 的默认关系；只有多个独立 ready 单元、依赖图、正式恢复或多环境生命周期才打开 Manager。
- 强化 Worker/helper 完成后由 Owner 核对真实 diff、原始验证和 Scope，再决定集成或返修。
- 同 Scope 实现缺陷或验证失败返回原 Executor；只有原 Executor 不可恢复、越界或继续会增险时才换 owner，并记录原因。
- 把 `setup-agents` 收紧为 Sacha namespaced managed installation、解除普通 Sacha 流程对 named Luna 的硬依赖，并定义过渡路由与可移除条件。

### 3.5 Domain Provider 迭代

- 本 Spec 只冻结 Sacha 与 Domain Provider 的 owner 边界。
- Provider 输出、真实验证和 [`capability-provider-guide.md`](../../integrations/capability-provider-guide.md) 的具体迭代由独立的 [`Domain Provider 规划支持 Spec`](../2026-08-04-domain-provider-planning-support/spec.md) 拥有。
- Sacha 主流程不得因 Provider 迭代而新增 Role、Gate、Artifact schema 或项目特定知识。

## 4. Non-goals

- 不新增生产 Role、Gate、Task taxonomy、Registry、后台服务或固定多 Agent 流水线。
- 不让 cgame-unity、cgame-engine 或其他 Provider 拥有 Human 批准、Sacha 生命周期或 Spec 冻结；Provider 只提供领域事实、方案比较和验收能力。
- 不要求每个任务持久化 Spec；当前 context 可完成、没有批准/恢复消费者时仍可 inline plan 或直接执行。
- 不要求每次澄清都创建决策文件；只有已经形成需要恢复/供 Spec 消费的决定，或上下文压缩/跨 context 风险存在时才尽快落盘。
- 决策文件不是执行许可、第二份 Spec 或完整聊天流水账；本任务已经先形成 Spec，不为形式完整追补一份重复历史决策文件。
- 不要求业务 `spec.md` 固定保存 Human Review Focus 或当轮最终建议清单；二者默认只存在于 Planner 的 Human 可见回复，权威内容仍分别归决策文件和 Spec。
- 不把 Planner 变成逐行编码者，不冻结无风险的局部命名、重排或等价实现选择。
- 不在本轮安装 Agent、修改用户 `.codex/agents`、发布、commit、push 或改写 Git 历史。
- 不以模板、配置文件存在、Agent 名称或子任务自报证明 Runtime 实际使用了 Luna。

## 5. 冻结决定

### 5.1 Sacha 与领域 Provider 的责任

Sacha 负责判断何时必须对齐、组织澄清、持久化并冻结 Spec、控制是否能进入 Executor。领域 Provider 负责调查 Unity/Engine/UE 等工程事实、识别约束、比较方案并设计可行验证。Project `AGENTS.md` 与项目 Skill 提供项目架构、模块边界、命令、平台限制和既有模式，但不重定义 Sacha Role 或生命周期。Human 确认用户可见行为、架构方向、Scope、Non-goals、难回退选择和关键验收。

因此，cgame-unity 可以告诉 Planner“哪些 Unity 决策必须对齐、需要什么场景或设备”，但不能自行批准方案、冻结 Sacha Spec 或启动 Executor。

### 5.2 澄清决策文件与 `spec.md` 的两层权威

1. Planner/Clarify 先调查真实状态；缺失决定会改变 Scope、架构、数据/资产、迁移、兼容或验收时，只向 Human 问会改变方案的最少问题。
2. 一项会被后续 Planner/Spec 消费的澄清决定收口后，立即写入项目约定的决策文件；即使决定尚未收口，只要多轮、分支或 context 压缩已经形成真实恢复风险，也立即写入最小澄清锚点。没有现有约定时，使用由 `<Spec base>/plan` 推导的 Spec storage root，并把轻量 `decisions.md` 与后续 `spec.md` 放在同一任务目录。它只保存当前有效决定和恢复原问题必需的关注点、未决项、暂存思路与 evidence reference，不保存完整对话。
3. 决策文件用于上下文压缩和跨 context 恢复，不是执行许可。Clarify 不冻结 Scope；未经 Planner 收口的决定不能被 Executor 直接消费。每次落盘也不是一个审批点：澄清可以分轮进行，Human 只在候选执行方案收口后 Review `spec.md`。
4. 当当前决定、工程事实与关键选择足以形成候选执行基线时，Planner 在 confirmed Spec storage root 或项目约定目录生成 `spec.md`，状态为“待 Human Review”。Spec 引用 decisions path，只重述 Executor 必须知道的当前结果，不复制澄清历史；至少覆盖目标结果、选定方向与理由、影响范围、Scope/Non-goals、实施地图、约束、验收、主要风险与回退。
5. Planner 回复不粘贴全文，只说明推荐结论、决策/Spec 路径、Human Review Focus、本轮新增或改变的 delta 与尚未决定项；满足第 5.3.2 节触发条件时，再用稳定编号收齐本轮全部最终建议与待决定事项。
6. Human 的异议先更新受影响决定，再同步 Spec；未受影响部分保持批准/确认。若决策文件与 Spec 冲突，停止 Executor dispatch并由 Planner 统一后再继续。
7. Human 接受后将 `spec.md` 状态改为“Human 已批准实施”，冻结批准 revision。若没有未决方案、额外授权或阻塞写入的 Entry Condition，root owner 必须在同一任务立即路由 Executor，以该 Spec 和当前真实状态开工；短回复“批准”“都 OK”已足够，不再追加启动确认。
8. 实施中若 Scope、冻结决定或验收发生实质变化，返回 Planner，更新受影响决定和 Spec delta并只重新确认变化部分；局部实现缺陷不触发重新批准。

如果 Human 在原始请求中已把实质方案、Scope 和验收明确决定，Planner 只是整理为 Spec，则可以记录“Human 已在请求中确认”并直接进入 Executor，不重复要求形式化批准。错别字、reference 补充、证据更新、不改变执行的措辞细化和局部实现说明，不使既有批准失效。

Clarify 的通用交互纪律由其 Role-local procedure 拥有：模糊想法用 `brainstorm` 收敛目标、Non-goals、候选与取舍；现状、内部先例或外部方案不清用 `survey` 形成可比较事实；已有粗略方案用 `grill` 核对前提，并通过反例、具体场景、失败/回退路径和可证伪验收打磨边界。它们是可切换、可组合的推进意图，不要求 Human 选择模式，也没有固定顺序或轮数。

追问和解释必须能在同一对话中交替。Human 拥有的业务事实与新增约束可直接纳入；代码、运行状态和外部现状先查证；方案偏好先核对事实前提与影响；猜想和推测只作为调查线索。Human 要求解释时先查真实来源，先给业务概要，按需展开数据流与代码 reference，理解到位后立即返回此前未决的决策。项目或领域 Skill 提供领域事实、候选和压力场景，Sacha Clarify 仍拥有通用 Human 对话、决定收口与退出判断。

多轮对话、分支打断或 context 压缩存在丢失风险时，Clarify 在既有决定载体中维护最小“澄清锚点”：原始问题/目标、已确认决定、当前关注点、按依赖排列的阻塞性未决项、暂存的新思路和 reference。新思路只能解决当前项、加入阻塞项或暂存，不能静默替换原问题；解释、调查、helper 返回和恢复后都先从锚点续接。该锚点是现有 `decisions.md` 的恢复信息，不是新 Artifact、状态机或完整对话记录。

Clarify 只有在原问题仍被覆盖，且影响目标、Scope/Non-goals、验收和实质方案的未决项已确认、由 Human 明确暂缓或明确授权 Planner 取舍后才能退出。Planner 必须独立核对这一条件，不能把 Clarify Role 自报当作完成证据；Human 只说“够了/开始吧”但仍有阻塞项时，先用最小清单确认这些项如何处置。

#### 5.2.1 有界挑战覆盖、术语与压力场景

Clarify 在 `grill` 或其他澄清意图中维护有界挑战图，而不是穷尽式决策树。它只展开答案可能改变目标、Scope、架构/Owner、数据与兼容、风险、回退或验收的分支；普通局部实现表达和与当前决定无关的理论问题不进入图中。候选挑战面按任务需要从术语与 Owner、状态/生命周期、失败/恢复、数据/迁移/兼容、环境差异、验收/回退中选择，不能要求每个任务走完固定清单。

挑战图的完整推理结构只存在于当前工作上下文，但不能完全依赖上下文存活。Clarify 必须判断哪些分支现在可问、依赖上游决定、等待事实调查、已经有依据排除，以及尚未询问但仍可能改变方案；这些是生成下一问和判断退出所需的内部语义，不是对 Human 展示或持久化的状态 taxonomy。

出现多轮、分支或 context 压缩风险时，现有 `decisions.md` 的澄清锚点除原问题、已定决定和当前焦点外，还保存“最小可恢复 frontier”：尚未探索或仍未解决的实质问题、它依赖的上游决定/事实 reference，以及少量若遗忘就会被错误重开的关键排除结论与依据。它不保存完整树、所有无关分支、固定节点 ID、表格或对话历史；旧项确认或失效后原位压缩/替换。恢复后 Clarify 先读取锚点和当前证据，重新生成工作挑战图，再继续依赖最靠前的问题。

提问按依赖关系调度：会决定后续问题是否成立的上游前提优先；互不依赖且 Human 能一次理解的问题可以自然合并；调查中的事实缺口只阻塞依赖它的分支。不得规定固定轮数、每轮固定问题数量，或要求每个高风险决定机械完成同一组“前提反转/中断/验收”动作。高风险决定只要求使用足以暴露错误假设的相关反例或压力场景。

按风险选择的压力视角包括但不限于：

- 数值与容量：零、负数、上下限、溢出、精度、`NaN`/无穷、空集合、超大集合、重复、乱序和部分数据。
- 状态与生命周期：首次、重复、重入、中断、恢复、超时、取消、部分失败、资源丢失、重复执行与幂等。
- 数据与版本：旧数据读新代码、新数据读旧代码、字段新增/删除/改义、未知字段、升级中断、降级、回滚、兼容窗口和迁移失败。
- 环境与消费者：平台、配置、权限、设备、Editor/Runtime、并发调用者及直接消费者差异。

这些只是问题生成视角，不是必填模板。已有代码、配置、文档、运行证据或 Domain Provider 输入能回答时先调查，不把可验证事实全部抛给 Human；只把无法由事实推出且会改变方案的决定交给 Human。

术语处理遵循以下边界：

1. 遇到同词多义、同义多名、两个概念被错误合并、含糊量词、业务词与代码含义冲突，或 Human/文档/代码使用不一致时，Clarify 必须先查当前工程用法，再确认本任务采用与明确排除的含义。
2. 会影响本次方案、且需要跨轮恢复或供后续 Spec 消费的术语定义写入现有 `decisions.md`；短且无需持久恢复的澄清可以只在当前回复中确认，不为术语单独强制创建 Artifact。Planner 形成 Spec 时沿用当前定义；新证据使定义失效时返回 Clarify，不在 Spec 中重新发明术语。
3. 项目已经声明术语 owner、Project Context path、词典或等价文档 path 时，沿用该 owner 并核对当前源码/用法；文档只作证据，不因存在就自动压过真实实现。
4. 没有现有 owner/path 时，Project Context path 唯一为 `<Spec base>/CONTEXT.md`。Project Documentation root 是独立的发布目录，不参与该 path 推导。该默认只解决跨任务发现路径，不授权创建或修改文件。
5. Clarify/Planner 开始处理含项目术语、架构或跨任务约束的任务时，按当前输入查询相关 `CONTEXT.md` 内容，而不是遍历历史任务目录或全部 `decisions.md`。当前任务中疑似稳定、项目特有且可能持续影响其他任务/消费者的定义先作为“项目 context 候选”写入当前 `decisions.md`；候选包含建议定义、明确排除的含义、当前证据、适用边界、可指出的任务外消费者和仍有的冲突/Unknown，不在澄清早期直接提升。
6. 实施 closeout 需要 Project Documentation 时，Documentation writer 只读取当前任务明确传入的 context 候选、最终 Spec、真实 diff/执行证据、Review 结果和现有 `CONTEXT.md`，再次判断候选是否仍与最终实现一致、是否有具体任务外消费者、是否重复已有内容及是否存在定义冲突；它不扫描历史任务目录寻找候选。
7. 候选的项目级资格由 closeout 的 Documentation writer/root owner 基于最终证据确认。定义能从项目事实直接推出、无现有冲突、任务外消费者明确，且 confirmed documentation trigger/write authorization 覆盖本次写入时，可直接创建或有界更新 `CONTEXT.md`；涉及业务含义选择、替换/否定既有定义、owner 冲突、证据仍是推测或缺少写入授权时，必须交给 Human 决定。Documentation writer 只确认候选是否达到这些证据条件，不能替 Human 发明业务定义。
8. 未达到项目级条件的候选继续留在任务记录，不为了“以后可能有用”写入 `CONTEXT.md`。写入只合并相关条目并保护无关内容，不复制任务对话、完整 `decisions.md` 或 Spec；候选资格不使用固定消费者数量作为门槛，但必须能指出当前任务之外的具体消费者或稳定项目接口。
9. `setup-project` 负责计算并在 Project Integration/managed project rules 中暴露上述 Project Context path，保持现有显式 dry-run、planned delta hash 与写入授权；它不扫描历史任务推断术语，也不因 Setup 本身自动创建或重写 `CONTEXT.md`。`project-documentation` 增加最小 project-context create/update 路线与当前任务候选复核，继续受 Spec base containment、preimage/并发保护和 write authorization 约束。

Domain Provider 可以返回领域术语的当前定义、代码/文档冲突、真实用例和领域压力场景，但不拥有 Clarify 退出、项目术语文档、Human 决策或新的 Provider 输出协议。

退出 Clarify 前不要求证明“所有可能问题均已穷尽”，但必须对与当前任务相关的挑战面做过一次有界扫描，并从当前工作图与最小可恢复 frontier 确认：没有尚未询问却可能改变方案的重要分支；影响 owner、数据边界、生命周期、失败恢复、兼容或验收的术语/前提已经解决、明确暂缓、路由给确定调查 owner，或保留为阻塞项；关键取舍已用 Human 能回应的语言解释，Human 的决定没有建立在已知错误前提或未解释的实质歧义上。不得因对话很长、上下文压缩、Human 提出新思路或完成一次解释就擅自退出，也不追加无法证实的“是否真正理解”仪式。

### 5.3 Human Review 与回复收口

#### 5.3.1 Human Review Focus

Human Review Focus 应由 Planner 在 Human 可见回复中直接输出，默认 3～5 项并附对应 Spec 章节或 path。它是当前 revision 的阅读导航，不是冻结决定或执行基线，因此不要求在业务 `spec.md` 中另建固定章节；跨 context 时可从当前 Spec 重新生成，不能只把 path 丢给 Human 自行寻找重点。

Human Review 不以“复杂、Unity、文件多或耗时”触发，而以 Planner 是否替 Human 形成新实质决定触发。以下任一事实要求先 Review：

- 存在多个会产生不同用户结果或系统结构的可行方案。
- 改变用户可见行为、架构或 Owner 边界。
- 改变数据、资产、序列化、配置、Scene/Prefab 或存档结构。
- 涉及迁移、兼容、fallback、难回退路径或影响范围尚不稳定。
- Acceptance、Non-goals 或做到什么程度无法从原请求推出。
- Human 明确要求先看方案/Spec，或 Domain Provider 发现必须由 Human 决定的关键取舍。

以下情况不重复确认：Human 已给出精确方案或批准 Spec、调查只确认唯一既有路径、行为/验收明确的局部 Bug、Scope 内普通实现细节、仅文件多/耗时/验证步骤多，以及同一批准 Scope 内返修和补证据。

Planner 在回复中只提示 Human 着重检查真正会改变交付的内容，默认最多 3～5 项：

- 用户最终会看到的行为与明确不做什么。
- 选定方案及被放弃方案中最重要的取舍。
- owner/模块边界、兼容和难回退决定。
- 需要 Human、设备、场景或外部环境参与的验收，以及它是否阻塞完成声明。
- 高风险停止条件或必须重新规划的触发点。

Scope 文件清单、普通静态检查和无争议的格式段落通常不要求 Human 逐项阅读，除非它们本身改变授权或风险。

#### 5.3.2 最终建议与待决定事项

`Human Review Focus` 与回复末尾的收口清单解决不同问题：

- `Human Review Focus` 指出 Human 应优先阅读 Spec 的哪些部分，不保证枚举正文里的全部建议。
- “最终建议与待决定事项”收齐本轮正文已经形成、且 Human 需要理解或决定的全部结论。简单场景可以与 Review Focus 合并，但不能用 Review Focus 代替建议完整性清单。

当一次 Role/Workflow 回复处理多个用户问题，或正文形成多项建议、取舍、异议点或待确认项时，结束前必须提供自然中文、稳定编号的清单。每项逐一对应正文和用户问题，简要说明建议结论与关键影响；确实需要 Human 决定时用自然语言说明“待确认什么”，仅告知的事项则明确无需回复。Human 可以直接按编号自然回应，不规定“接受/挑战/驳回”等固定词组、三态动作或回复格式。

清单只负责当轮沟通收口：

- 正文继续负责调查、方案比较、理由与证据；清单不重复论证，不复制 Spec 全文。
- 不得遗漏正文中的最终建议，也不得新增正文、`decisions.md` 或 `spec.md` 中没有说明的新方案。
- 最终建议清单默认不写入业务 `spec.md`。Human 确认后，需要长期恢复的决定才写入 `decisions.md`，批准后的执行基线才更新到 `spec.md`；清单本身不是 Artifact、Gate、状态、Packet、approval 或第二份 decision log。
- 单一简单结论、普通进度更新和纯事实回报不强制增加固定章节或空清单。
- 该通用语义不归 Intake、Runtime Adapter 或 Domain Provider；它们没有直接消费错误时不复制规则。

### 5.4 Spec 实施密度折中

每个实质步骤应让 Executor 无需重新发现 Planner 已确认的架构事实。按需要使用以下自然中文标签：

- `目标位置/定位`：文件、owner、函数、资源或稳定搜索入口。
- `预期改动`：完成后真实行为或数据流怎样变化，不只写“修改某模块”。
- `约束与不变量`：不能破坏的生命周期、线程、ABI、序列化、平台、兼容或 single-writer 边界。
- `依赖与顺序`：前置步骤及脆弱的执行顺序；无顺序要求时省略。
- `检查与证据`：能直接证伪该步骤的最窄检查、预期结果与原始证据位置。
- `返回规划的触发条件`：发现什么事实说明冻结方案已失效；普通实现错误不写在这里。

密度规则：

- 简单单文件、既有模式明确、风险低的步骤可以用一段话合并表达，不强制六个小标题。
- 跨 owner、平台分流、资源生命周期、数据迁移或脆弱顺序至少写清定位、改动、不变量和证据。
- 伪代码或候选代码只用于 API 合同、易错顺序或很难用自然语言消歧的算法；不默认代写完整实现。
- 行号只能作为辅助，必须同时给稳定 symbol/owner；行号漂移不应让 Spec 失效。
- 步骤应细到能够独立判断完成/失败，但不把每个机械编辑拆成单独 Task。
- 实施结果对顺序、Owner、数据边界和领域约束越敏感，Spec 越应接近可直接执行；当剩余选择只影响局部代码表达、不再改变行为、边界、风险或验收时，停止继续细化，交给 Executor 自主决定。

### 5.5 A/B/C 三类验收与阻塞语义

每个关键验收项按真实执行责任标注路线，并同时说明“完成声明是否必需”和 Entry Condition；A/B/C 不是新 Gate。

- A 类：AI 可在当前授权和环境中独立完成，例如静态检查、单元测试、构建、日志解析或可控 Runtime smoke。必需 A 项失败时阻塞交付；未运行时不能声称通过。
- B 类：AI 能执行并判断，但需要 Human 先提供设备、登录、场景、数据、交互时机或其他前置。Spec 必须写清 Human 最小动作、AI 如何确认准备完成、随后执行什么和采集什么证据；到达该步骤时才请求准备，完成后原 root owner 自动继续，不要求 Human 重新调用 Executor。必需 B 项的 Entry Condition 未满足时，可以完成安全的 ready branch，但最终只能报告“实现完成、该项未验证”，不能报告全部验收通过。
- C 类：当前 AI 无法可靠执行或成本明显不合理，只能由 Human 判断，例如主观画质、手感、长时间体验或难自动化的多机型感知。AI 按任务写清场景、设备、操作步骤、观察时长、预期与禁止现象、截图/录像或记录方式及是否阻塞。必需 C 项未确认时阻塞“全部验收通过”，但不自动否定已完成的代码、构建和 A 类证据。

每项只选择真实路线。不能为了把任务变成 A 类而用静态推导替代设备/画面事实，也不能把可自动完成的检查推给 Human。B/C 项是否阻塞必须由风险与用户目标决定，不按类别一刀切。

Assurance 映射保持现有 Outcome：全部 blocking 检查满足才 `Accepted`；只剩非阻塞 Human/环境/证据后续才 `Accepted with follow-up`；必需证据不足为 `Needs Evidence`；依赖 Human/外部状态且安全替代耗尽为 `Blocked`。实现失败返回原 Executor，批准合同错误返回 Planner，只缺证据返回唯一 evidence owner。

### 5.6 Executor-only、bounded helper 与 Manager

- `executor-only` 表示一个 Executor 对最终 Scope 和集成负责，不表示它禁止使用 subagent/helper。
- Executor 可直接管理一个有界 helper，用于 Scope 已冻结、输入自包含、边界明确、结果可直接核对的调查、验证或候选 patch。
- helper 不取得 Executor、Reviewer 或 workflow owner 身份；不能改变架构、Scope、验收或外部授权。
- 只有至少两个独立 ready 单元、依赖图、正式跨 context 恢复或多环境生命周期需要独立 owner 时才打开 Manager。任务大、多文件、耗时或“想并行”本身不构成 Manager 事实。
- Manager 是控制面；没有 Planner/Reviewer 的 execute-only workflow 仍可由 Manager 协调多个独立执行单元，但每个生产写入仍有明确 Executor/integration owner。
- 共享工作树同一文件、公共 schema、生成物、Git 和最终验证保持单一集成 owner 与串行处理。

### 5.7 Worker/helper 完成后的 Owner 核对与返修

Worker/helper 的 done、自报和摘要只作为 reference。Owner 在接收结果后至少按风险核对：

- 真实 diff/文件状态是否只覆盖批准 Scope，是否碰到用户已有改动。
- 原始检查的退出状态、错误、warning、失败计数和证据是否支持声称的结果。
- 依赖、生成物和运行输入是否与批准 revision 一致。
- 隔离候选是否能由 integration owner 安全应用；不能把 helper 工作树直接当成已集成状态。

派发消息按需要写清目标、基线、负责范围、禁止触碰的共享范围、已接受依赖、完成检查和停止条件；helper 不递归扩张 owner 或自行派发新的生产写入者。目标可能已经写入时不得盲目重试，先检查真实状态并确认旧写入者 terminal，避免双写。

同 Scope 的实现缺陷、漏改、验证失败或补证据优先返回原 Executor，并保持原 Scope/revision。只有原 Executor 已终止且不可恢复、发生越界/双写风险、有效配置不可用或继续会显著增加风险时才更换执行 owner；更换原因必须可见，不能通过不断新建 Agent 掩盖失败。Commit、push、PR/MR、merge 和发布仍只由取得对应明确授权的 integration owner 执行，Worker completion 不产生该授权。

### 5.8 `setup-agents` 保留、安装边界与移除条件

当前 Codex Adapter 的 Luna 路由依赖 named `agent_type`，本仓库通过用户级自定义 Agent TOML 提供该入口，因此现阶段保留 `setup-agents`。

实施时改为：

- 使用 Sacha 命名空间的 Agent identity 和目标文件，例如 `sacha_luna_worker` / `sacha_luna_worker_xhigh` 与 `sacha-luna-worker*.toml`；Adapter、模板、测试和文档同步引用唯一名称。
- 模板包含稳定 Sacha owner marker；只有目标位于 `CODEX_HOME/agents`、文件名属于 Sacha 命名空间、marker 与 expected identity 同时匹配时，才视为 Sacha-owned。
- Human 显式调用 `setup-agents` 即授权本次对 Sacha-owned 目标执行 create/update/no-op。配置器仍先展示目标、动作和 delta，但不对 Sacha-owned 更新再要求第二轮 hash 式确认。
- 同名文件若没有 owner marker、identity 不匹配、解析失败或调用期间 preimage 变化，整批拒绝且不写入；删除 `--replace-conflict` 或任何覆盖非 owned 文件的通道。
- 多文件更新继续采用预检、临时文件、原子替换、写后回读和失败补偿；安装插件本身、普通 Sacha 流程或 `setup-project` 不得静默触发。
- 自动覆盖只指已显式调用后的 Sacha-owned 文件，不授权修改其他 `.codex/agents` 文件、全局配置、cache 或 Runtime。
- Historical/superseded route：本轮当时曾规定 named Agent 缺失后使用 Sol/Terra 或 Runtime default；该模型与 fallback 映射已失效，只保留“`setup-agents` 不是普通 Sacha 安装前置、Human exact 优先、记录 requested/effective”这些未被替代的边界。当前组合与失败处理只读 [Codex Adapter](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md) §3。
- Runtime 真正支持原生精确 Luna model/effort 后，路由优先 Human 精确配置和原生精确 spawn，Sacha custom Agent 只作兼容 fallback；不能以官方文档或工具参数存在提前切换。
- `setup-agents` 不进入主要 Workflow 或 `setup-project`，README 只在 Codex 兼容/故障恢复位置给 reference；旧通用 `luna_worker*` 仅在确认带 Sacha owner marker 时作为兼容输入，非 Sacha-owned 文件不修改、不删除。

只有真实 Runtime smoke 同时证明以下事项后，才能删除 custom Agent 依赖和 `setup-agents`：

1. 可直接请求 Luna，而不依赖 Sacha TOML/named custom Agent。
2. 可精确请求目标 reasoning effort。
3. 宿主返回 effective model 和 effective reasoning，而不是仅回显请求值或依赖子 Agent 自报。
4. 不会静默继承主 Agent的 Sol/Terra；不一致会明确失败或记录 fallback。
5. spawn、terminal join、失败 fallback 和 Owner 核对在实际任务中均有证据。

官方文档、工具参数、模板存在或单次 task 名称都不足以证明上述条件。条件满足后，再从 Adapter discovery、主要 README 和 canonical Skill 面移除 `setup-agents`；仍有迁移/测试价值的 TOML 只能作为明确标注的 fixture 或迁移资产保留，不能继续成为生产依赖。

### 5.9 入口、暂停恢复与 Reviewer 边界

- 上游任务的 `using-sacha`、Planner/Reviewer 建议和 Sacha Intake acceptance 只决定路由，不是 Human 对后续方案的批准。
- Planner 返回待确认 Spec 时，workflow owner 复用现有 `human_decision_required`，停止 Executor dispatch；Planner terminal、Role completion 或 Spec 文件存在均不构成执行许可。
- 待确认结果必须回到 Human 可见的 root task；Human 回复后在同一 Task/Scope revision 上继续，不创建第二个 Planner、Executor、用户可见 task 或 workflow。跨 context 时只携带恢复必需的决策/Spec revision、reference 和未决项。
- Human 方案 Review 发生在实施前；Reviewer 是实施后的独立 Assurance consumer。上游可提前记录预计需要 Reviewer，但 Reviewer 不能批准方案，也不能用来替代 Human Review。
- Human 确认后，若无未决项或阻塞前置，root owner 立即在同一任务启动/恢复 Executor，并自动继续按风险 Review、同 Scope 返修/补证据和收尾；不能停在“已批准、Executor 尚未启动”。只有新的实质方案、Scope/验收变化、新高影响授权或写入前必需 Entry Condition 再次返回 Human。
- 外部 one-shot 进程按 Adapter 保存实际参数、退出状态、stdout/stderr reference、最终结果和 effective route；Codex 原生 subagent 已由 Runtime 保存 transport 时不为每次派发另建 Manifest。
- 模型/Agent fallback 或升级只依据能力不支持、真实验证失败、高风险/跨系统事实、长依赖链无法处理或 requested/effective 不一致；不建立额外难度 taxonomy 或固定多档升级状态机。具体 route 已由当前 Codex Adapter supersede。

## 6. 实施步骤

实施优先级只用于安排改造顺序，不是新的任务 taxonomy 或 Workflow 状态：

- **必须先成立**：步骤 1～5。它们共同修复 Planner 新方案未经 Human 确认就进入 Executor、澄清决定无法恢复、Spec 仍需重新设计、A/B/C 无法正确收口的问题。
- **同轮顺手补强**：步骤 6、7、9。它们收紧 helper/Manager、真实结果核对、原 Executor 返修、Runtime route 证据、`setup-agents` 兼容边界和直接消费者一致性；不为此新增合同字段。
- **独立授权迭代**：步骤 8。先更新 Provider Guide，再分别在 provider 仓库建立独立 Spec；跨仓修改、安装、Binding refresh 和发布不由本 Spec 自动授权。

### 步骤 1：补齐 Intake、Planner 与 Human Review 的进入条件

- 目标位置/定位：`core/intake-contract.md`、`core/workflow-contract.md`、`skills/using-sacha/SKILL.md`、`skills/planner/SKILL.md`、`skills/executor/SKILL.md`。
- 预期改动：上游路由/Intake acceptance 不等于新方案批准；补齐第 5.3.1 节的 Review 触发/不触发条件和 Executor entry condition。
- 约束与不变量：不新增 Gate、Role 或所有 Planner 强制确认；Human 原本已决定或唯一既有路径可直接继续。
- 检查与证据：场景覆盖上游只建议 Planner/Reviewer、Human 已明确方案、唯一既有路径、局部 Bug、新架构/数据方案和显式“先看 Spec”；另覆盖 Human 只回复“批准”或“都 OK”且无未决项时，同一 root task 自动进入 Executor，存在额外授权或阻塞 Entry Condition 时才暂停并说明唯一缺口。
- 返回规划的触发条件：必须保存历史 Gate 标志或新增审批状态才能判断当前执行许可。

### 步骤 2：建立可恢复澄清、项目 CONTEXT → `spec.md` 的权威转换

- 目标位置/定位：`skills/clarify/SKILL.md`、`skills/planner/SKILL.md`、`core/artifact-protocol.md`、`skills/setup-project` 生成器/Skill/validator、`skills/project-documentation` 与 Project Integration 的 Spec/Documentation 配置说明。
- 预期改动：决策收口即按需落盘，支持上下文压缩恢复；Planner 以当前决定形成待 Review Spec，Human 批准后 Spec 才成为执行基线。
- 预期改动补充：恢复 `brainstorm`、`survey`、`grill` 的可执行分野和共同对话循环；解释后回到未决问题，偏好先验前提，猜想先调查，`grill` 使用反例与可证伪场景。
- 预期改动补充：分支或压缩风险出现时维护可恢复的澄清锚点；新思路不得替换原问题，Planner 独立核对未决项后才接受 Clarify 完成。
- 预期改动补充：加入第 5.2.1 节的有界挑战图、依赖感知提问、术语冲突调查，以及数值/容量、生命周期、数据迁移和跨版本兼容等按风险选择的压力视角。
- 预期改动补充：`decisions.md` 保存最小可恢复 frontier 与当前任务 project-context 候选；setup-project 由 Spec base 解析 Project Context path；Clarify 查询相关项目上下文；closeout 的 Project Documentation writer 用最终实现/Review 证据再次筛选候选，并只在资格与授权同时满足时创建/有界更新项目术语条目。
- 约束与不变量：决策文件不是第二份 Spec、执行许可、完整对话或固定每任务 Artifact；一个事实不在两个文件保存两份会漂移的完整正文。
- 约束与不变量补充：不保存完整挑战图，不固定问题数或三联探针；只有恢复必要的未探索/未解决分支和关键排除依据进入 `decisions.md`；Project Context path 是可覆盖的默认文件入口，不是新 Artifact 或第二份规则入口，Setup 不因配置 path 自动写正文。
- 依赖与顺序：先冻结 path 优先级、候选 owner、closeout 资格判断、Human 决策边界、写入授权和任务/项目术语边界；再调整 setup-project/project-documentation；最后调整 Clarify/Planner procedure、Guide 与场景验证。
- 检查与证据：场景覆盖 Spec 产生前发生 context compaction、多个决定分轮收口、Human 修改一项决定、非实质文案/证据更新不使批准失效。
- 检查与证据补充：覆盖模糊想法收敛、现状/竞品调查后再选方案、粗略方案场景压测、Human 反问解释后继续原决策，以及用户推测与代码事实冲突；目标已清楚时不得为了走完三种意图继续提问。
- 检查与证据补充：覆盖新思路打断当前决策、context 压缩后从锚点恢复、Clarify 擅自退出被 Planner 拒绝，以及 Human 明确暂缓未决项后可继续规划。
- 检查与证据补充：覆盖术语同词多义/文档与代码冲突、上游事实只阻塞依赖分支、空值/极值/重复/乱序、生命周期中断与重入、旧数据/新代码和新数据/旧代码、迁移中断/回滚；无相关风险的任务不得为了覆盖清单继续追问。
- 检查与证据补充：覆盖 context 压缩前后保留尚未询问的实质分支、依赖事实的分支和关键排除依据；恢复后重建工作挑战图且不要求持久化完整树。
- 检查与证据补充：覆盖 `<Spec base>/CONTEXT.md`、Spec base 与 Project Documentation root 相隔很远、首次创建、并发/旧 preimage 拒绝、有界更新保护无关内容、未获写入授权只返回候选，以及新任务不遍历历史 `decisions.md` 也能读取提升后的术语。
- 检查与证据补充：覆盖 Clarify 提名后方案发生变化导致 closeout 淘汰候选、最终实现证明候选且 bounded-closeout 授权覆盖时写入、定义冲突/替换旧含义/业务选择返回 Human，以及 Documentation writer 不从历史任务搜集或凭推测提升术语。
- 返回规划的触发条件：无法避免决策文件与 Spec 双权威，或必须新增 Registry/approval 文件消歧。

### 步骤 3：加入 Planner 回复收口、自适应可执行密度与 Human Review Focus

- 目标位置/定位：`core/workflow-contract.md` 的 Human 路由、Planner Skill、必要的用户入口文档与 Planner 场景 fixture/validator。
- 预期改动：Workflow 定义第 5.3.2 节的通用收口语义；Planner 正文负责调查、比较和证据，Human 可见回复直接输出 Review Focus，并在末尾收齐全部建议、分歧与待确认项。采用第 5.3.1、5.4 节：回复只给 reference、Focus、delta 和必要清单，实施步骤使用中文标签且不要求固定空字段。
- 约束与不变量：Review Focus 与建议完整性清单责任分开，二者默认不持久化进业务 Spec；普通任务仍可 inline plan/Direct；单一简单回答不生成空总结；不规定“接受/挑战/驳回”等固定动作；只冻结改变结果的部分，局部代码表达留给 Executor。Intake、Adapter 和 Domain Provider 不复制这段 procedure。
- 检查与证据：除简单/复杂 Spec 密度场景外，增加多问题完整收口、正文建议遗漏、清单凭空新增建议、编号唯一可逐项回复和简单回答不产生空清单的 fixture。
- 返回规划的触发条件：必须为所有项目增加固定 Spec schema 或逐句 validator。

### 步骤 4：由 Assurance 映射 A/B/C 验收与阻塞

- 目标位置/定位：`core/assurance-contract.md`、Planner/Executor/Reviewer Skill、Artifact 引用及相关场景验证；Workflow/Coordination 只处理路由/恢复。
- 预期改动：明确 A/B/C 的责任、Entry Condition、人工状态、Outcome、re-review 和失败 owner；B 到点请求并在准备后自动恢复，C 提供可执行人工检查。
- 约束与不变量：不新增 Outcome、QA Role 或 Gate；build、runtime、设备、画面和 Human 判断不得互相替代。
- 检查与证据：覆盖 A 自动 build、B Android 设备准备后 AI 验收、C 主观画质、blocking/non-blocking、Human 判断失败和 evidence-only re-review。
- 返回规划的触发条件：现有 Assurance Outcome/人工状态无法如实表达 required B/C。

### 步骤 5：补齐 root owner 暂停恢复与 Reviewer 分界

- 目标位置/定位：Workflow/Coordination Contract、`using-sacha`、Planner/Reviewer Skill、Codex/Claude Runtime Adapter。
- 预期改动：复用 `human_decision_required` 暂停 dispatch；待确认 proposal 回到 Human 可见 root task，确认后同 Task/Scope revision 继续；Reviewer 不能替代 Human 方案 Review。
- 约束与不变量：不因确认创建新 task/workflow，不把 Planner terminal 当许可，不把 Runtime ID 写进 Artifact。
- 检查与证据：真实场景覆盖 Planner proposal → Human 修改 → 原 workflow 恢复，以及上游“建议 Reviewer”不绕过方案确认。
- 返回规划的触发条件：当前 Runtime 无法把 Human 回复安全返回原 workflow，且安全替代耗尽。

### 步骤 6：收紧 helper/Manager、Owner 核对和原 Executor 返修

- 目标位置/定位：Coordination Contract、Executor/Manager Skill、Runtime Adapter 的 dispatch/completion/fallback。
- 预期改动：统一本 Spec 第 5.6、5.7 节；补目标/base/ownership/dependency/stop，禁止递归扩张生产 owner和可能写入后的盲重试。
- 约束与不变量：single writer、Reviewer provenance、原始证据权威、Git/发布授权和 integration owner 串行职责不降级。
- 检查与证据：单 bounded helper 不开 Manager、execute-only + Manager 多单元、Worker 自报与真实 diff 冲突、旧写入者未 terminal 时拒绝重试、同 Scope 返修返回原 Executor。
- 返回规划的触发条件：现有 Coordination identity 无法消歧原 Executor，必须引入持久 owner Registry。

### 步骤 7：收敛 `setup-agents` 并解除普通流程硬依赖

- 目标位置/定位：`skills/setup-agents` 模板/配置器/Skill/metadata，Codex Adapter named/native route，`tests/test_setup_agents.py` 及直接 README/validator 消费者。
- 预期改动：Sacha namespaced identity；显式调用自动更新 owned 文件；非 owned 永不覆盖；缺少 custom Agent 时安全回退；原生精确 Luna 经真实验证后优先并最终移除 compatibility installer。
- 约束与不变量：不写 cache、不扫描其他 Agent、不由普通流程触发；requested/effective Runtime 证据边界不变。
- 依赖与顺序：先冻结 identity/owner/fallback，再改配置器与测试，最后同步 Adapter/文档；旧文件迁移/删除另行授权。
- 检查与证据：create/update/no-op/conflict、并发变化、事务回滚、幂等、named 缺失 fallback、requested/effective 不一致和真实 spawn/join 分层验证。
- 返回规划的触发条件：Runtime Agent mapping 与假设不符，或不能在不覆盖用户文件的前提下迁移。

### 步骤 8：迭代 Domain Provider Guide 与真实 Provider

- 目标位置/定位：独立 [`Domain Provider 规划支持 Spec`](../2026-08-04-domain-provider-planning-support/spec.md) 与 `docs/integrations/capability-provider-guide.md`。
- 预期改动：guide 明确 Provider 返回领域事实、约束、候选/取舍、实施地图、A/B/C 与未决 Human 选择；再由 cgame-unity/cgame-engine 各自规划迭代。
- 约束与不变量：Provider 不批准、不冻结 Spec、不启动 Executor；不新增第二套 Workflow 或固定输出 schema。
- 检查与证据：先验证 guide owner/边界，再使用两个真实 provider 任务证明 Planner 无需重新做领域设计。
- 返回规划的触发条件：需要改变 catalog/Binding schema、新增公开 capability 或跨仓发布。

### 步骤 9：同步直接消费者并做反形式主义审查

- 目标位置/定位：项目 `AGENTS.md` owner 矩阵中的直接消费者、Evolution、README、source/release validator。
- 预期改动：只同步因上述语义会出错的入口、映射和断言；删除重复描述，避免把两份 Spec 整段复制到各层。
- 约束与不变量：Core platform-neutral，Runtime 细节只进 Adapter，领域事实留在 Provider；无两个消费者的局部规则不升级进 Core。
- 检查与证据：全文 owner/引用检查、受影响单元测试、Skill/plugin validator 与 `git diff --check`；报告 warning、失败和未运行的 Runtime 层。
- 返回规划的触发条件：变更需要新产品版本、breaking schema、安装、cache、发布或未批准的跨 Runtime承诺。

## 7. 验收矩阵

### A 类：AI 可独立完成，均为本轮实施完成的必需项

> 实施结果：本节 source/静态场景项已由本仓测试、Skill/Plugin validator 与 `git diff --check` 覆盖；下列清单保留为产品语义索引，不将静态通过外推为 B/C 类证据。

- [ ] Intake/上游路由只进入规划，不把 Planner/Reviewer 建议或 Sacha acceptance 当作新方案批准。
- [ ] 决策收口后可在 Spec 产生前立即落盘，并能在 context compaction/跨 context 后恢复；决策文件不授权执行。
- [ ] Clarify 能按输入自适应使用 `brainstorm`、`survey`、`grill`，三者可切换/组合但不是 Human 选择的固定模式、阶段或必经顺序。
- [ ] 澄清对话能在追问与基于真实来源的分层解释之间切换；解释完成后回到原未决决策，偏好先核对前提，猜想只作为调查线索。
- [ ] `grill` 会用反例、具体场景、失败/回退路径和可证伪验收挑战粗略方案；目标已清楚时不会为了固定轮数继续澄清。
- [ ] Clarify 只展开会实质改变方案的挑战分支，按依赖调度问题；不会建立完整决策树或固定每轮问题数量，但 context 压缩前会把未探索/未解决的实质分支、依赖和关键排除依据压缩进现有锚点。
- [ ] 恢复后从 `decisions.md` 与当前证据重建工作挑战图，能区分当前可问、依赖上游、等待事实、已有依据排除和尚未询问的关键分支，而不引入持久节点状态 taxonomy。
- [ ] 术语歧义、概念错误合并、同义冲突和文档/代码含义不一致会先由真实工程事实调查；需要恢复或供 Spec 消费的任务关键定义进入 `decisions.md`，短对话不为此强制新增 Artifact。
- [ ] 数值/容量、状态/生命周期、失败恢复、数据迁移、跨版本兼容和环境差异只在相关时触发；无风险消费者不会被固定问卷拖入额外澄清。
- [ ] Planner 沿用已确认任务术语；定义被新证据推翻时返回 Clarify，不在 Spec 中重新发明含义。
- [ ] 项目上下文优先沿用已有 owner/path；默认 Project Context path 为 `<Spec base>/CONTEXT.md`，与 Project Documentation root 独立；新任务从该入口查询相关术语，不遍历历史任务目录。
- [ ] Clarify 只提名 project-context 候选；closeout Documentation writer/root owner 用最终 Spec、diff/执行证据、Review 和现有 `CONTEXT.md` 再次确认资格，早期方案变化会淘汰失效候选。
- [ ] 事实明确、无冲突、任务外消费者具体且既有授权覆盖时可安全创建/有界更新 `CONTEXT.md`；业务含义选择、替换旧定义、owner 冲突、推测或缺授权时返回 Human。
- [ ] setup-project 只解析/暴露 Project Context path，不自动写正文；Documentation writer 不遍历历史任务目录或把“可能有用”当成提升证据。
- [ ] 多轮或分支澄清会在现有 `decisions.md` 中保留原问题、当前关注点、阻塞性未决项和暂存新思路；context 压缩后能从原返回点继续。
- [ ] 新思路不能静默替换原问题，Clarify 自报完成不能绕过 Planner 对原问题与阻塞性未决项的独立核对。
- [ ] Planner 从当前决策形成 `spec.md`；Human 已在请求中确认的方案不会重复拦截，新实质方案未批准时不能进入 Executor。
- [ ] 决策文件与 Spec 各自只有一个权威职责，冲突会停止 dispatch 并由 Planner 统一；非实质更新不使批准失效。
- [ ] `human_decision_required`、root task 可见 proposal、同 Task/Scope revision 恢复和 Planner terminal 非许可在 Core/Skill/Adapter 中一致。
- [ ] Human 方案 Review 与实施后 Reviewer 明确分离，预计 Reviewer 不会绕过方案批准。
- [ ] Human 简短批准且无未决方案、额外授权或阻塞 Entry Condition 时，同一 root task 自动进入 Executor，不再询问是否开始实施。
- [ ] 三个用户问题分别在正文展开时，回复末尾以三个稳定且不重复的编号完整收齐对应结论，Human 可直接按编号自然回应。
- [ ] 正文已有最终建议但收口清单遗漏时，场景验证失败。
- [ ] 收口清单增加正文、决策记录或 Spec 未说明的新建议时，场景验证失败。
- [ ] `Human Review Focus` 与“最终建议与待决定事项”的职责可被场景区分，简单场景允许合并但不丢建议。
- [ ] Planner 在 Human 可见回复中直接给出 Review Focus；业务 Spec 不要求固定 Focus 章节，跨 context 可从当前 revision 重新生成。
- [ ] 最终建议清单不会原样写入业务 Spec；Human 确认后的长期决定和执行基线才分别更新到 `decisions.md` / `spec.md`。
- [ ] 清单按需说明待确认内容或“无需回复”，不要求每项附加“接受/挑战/驳回”固定尾句或状态标签。
- [ ] 单一简单结论、普通进度和纯事实回报不会被迫生成固定章节或空清单。
- [ ] 通用语义只由 Workflow Contract 的 Human 路由定义，Planner Skill 实现 Role-local procedure；README、validator 和必要示例完成直接消费核查，Intake、Adapter 与 Domain Provider 没有复制长规则。
- [ ] 简单与复杂 fixture 证明 Spec 密度自适应，中文标签可读，validator 不锁死固定格式。
- [ ] A/B/C 场景按 Assurance Outcome 正确区分通过、失败、未验证、blocking/non-blocking 和 owner route。
- [ ] B 类到点请求 Human 准备并在同 root 自动恢复；C 类给出可执行人工检查，不只写“请人工检查”。
- [ ] bounded helper 不误开 Manager；多个独立 ready 单元才进入 Manager；Owner 会核对真实 diff/证据。
- [ ] Worker 派发边界、可能写入后的重试保护、原 Executor 返修和 Git/发布授权 owner 均可由场景证伪。
- [ ] 同 Scope 返修优先回到原 Executor，换 owner 有明确且有界的原因。
- [ ] `setup-agents` 测试覆盖 namespaced owner、自动 owned update、非 owned 拒绝、并发/回滚/幂等、named 缺失 fallback 和旧 owned 兼容。
- [ ] requested/effective Luna 不一致时明确失败或 fallback；原生 subagent 不额外生成 Manifest，外部 one-shot 保留完整运行证据。
- [ ] Domain Provider guide 与独立 Spec 的 owner 一致，Provider 能提供可执行领域输入但不能批准、冻结或启动 Sacha 实施。
- [ ] 受影响的单元测试、项目 setup validator、Skill/plugin validator 和 `git diff --check` 退出状态已读取并报告。

### B 类：需要 Human 提供 Runtime 前置；源码实施可以完成，但 Runtime 声明受阻

- [ ] Human 允许在目标用户 Codex 环境显式运行新版 `setup-agents`，并允许创建/更新 Sacha namespaced Agent 文件。
- [ ] Runtime refresh/restart 后，AI 执行 named discovery、只读 spawn、terminal join，并读取宿主返回的 effective model/reasoning。
- [ ] 若需要验证旧通用名称迁移，Human 单独确认具体旧文件和迁移动作；默认不触碰。
- [ ] Human 分别授权 cgame-unity/cgame-engine 等 Provider 仓库迭代，以及需要时的安装、Runtime discovery 和 Binding refresh。

上述 B 项未执行时，只能声明 source/tests 通过，不能声明安装、fresh discovery、Luna routing 或 effective model 已验证。

### C 类：Human 产品判断；不阻塞源码正确性，但阻塞“交互体验已接受”

- [ ] Human 阅读 Planner 回复中的 Review Focus，确认 Sacha 在复杂 Unity/Engine 任务中是否给出了足够清楚、不过量的改动说明。
- [ ] Human 用一份真实复杂 Spec 判断实施步骤是否达到“可以执行且不必重新做架构规划”，同时没有退化成 WaterReflection 级别的默认逐行长文。
- [ ] Human 确认“决策定了尽快落盘 → 决策足够后形成 Spec → Review 后执行”的体验能抵抗上下文压缩且没有形成双权威。
- [ ] Human 确认 setup-agents 的显式调用与自动 owned update 交互是否符合预期。
- [ ] Human 确认 Domain Provider 输出增加了领域实施信息，但没有复制 Sacha Workflow。

## 8. 明确拒绝

- 不新增 Alignment、Brainstorm、Spec Review Gate 或 Brainstormer、Architect、Alignment、Spec Reviewer Role。
- 不把 `brainstorm`、`survey`、`grill` 拆成三个 Skill、固定模式状态、必经阶段、固定轮数或额外产物；只在 Clarify 内保留改变实际交互的自适应判断与纪律。
- 不建立或持久化“完整决策树”，不固定每轮 2～4 问，不要求每个高风险决定机械生成同一组三联探针；只在工作上下文维护有界挑战图，并在现有锚点保存恢复必需的最小 frontier。
- 不把极值、边界、生命周期和跨版本视角变成每个任务必填的长问卷，也不把能从代码、配置或 Runtime 查明的事实全部询问 Human。
- 不以固定消费者数量决定术语是否提升，不创建 `docs/terminology.md`、ADR 或新的 Glossary Artifact；`<Spec base>/CONTEXT.md` 是无现有 owner/path 时的默认跨任务入口，不因每次 Setup/Clarify 自动创建或改写。
- 不遍历所有历史 `decisions.md` 拼接项目知识，不把 `CONTEXT.md` 变成第二份 AGENTS、Spec、完整任务历史或自动积累的知识库。
- 不新增 Clarify Session、Conversation Gate、未决项状态 taxonomy、独立恢复文件或每轮固定检查表；澄清锚点只复用按需 `decisions.md`，短且无分支的对话不强制落盘。
- 不新增 Summary Role、Decision Gate、建议状态 taxonomy、固定表格或每轮强制总结；只在多问题、多建议、多取舍或多待决项时触发通用收口。
- 不引入“已批准但等待再次启动”的中间状态，不把批准后的 Executor 路由变成第二次 Human checkpoint。
- 不在 Planner 回复中粘贴完整 Spec；只返回 Spec path、Review Focus、delta、未决项和按需最终建议清单。
- 不让收口清单重复 Spec 全文、正文论证或产生正文/权威文件中不存在的新方案。
- 不把每轮 Review Focus 或最终建议清单固定写入业务 Spec，不强制每项使用“接受/挑战/驳回”尾句或三态标签。
- 不新增 `draft-spec.md`、`approval.json`、`spec-review.md` 或完整聊天/审批流水。按需 `decisions.md` 只保存已确认决定与恢复信息，不是第二份 Spec 或固定状态机。
- 不强制所有 Planner 任务 Human Review，也不因复杂、Unity、文件多、耗时或验证步骤多自动打开 Gate。
- 不强制所有步骤机械填写六个字段、所有任务达到 WaterReflection 篇幅或提前逐行代写代码。
- 不新增固定 Worker Packet schema、Writer 状态表、强制 worktree、递归 Worker 树或所有 Worker 独立 Reviewer。
- 不把新 context 名称当成 Reviewer 独立性证明，不把 Worker `done` 或自报当成集成证据。
- 不为每次 Codex 原生 subagent 派发生成 Manifest，也不建立 Adapter 之外的难度 taxonomy 或固定多档升级状态机。
- 不让 Worker 自动 commit、push、建 PR/MR、merge 或发布，不让 Manager/Worktree 消除 single-writer 与 integration owner 责任。
- 不让 cgame-unity/cgame-engine 自建 Planner/Executor/Reviewer、写 Sacha Artifact、批准方案或拥有 verdict。
- 不因存在 `setup-agents` 就要求普通 Sacha 流程先安装 custom Agent，不把第三方/用户 Agent 当成 Sacha-owned 覆盖。
- 不把 Change Probe 是否“恰好中途迭代过一次”的未证实历史写成产品事实。

## 9. 停止、返回 Planner 与开工条件

出现以下任一情况必须修订本 Spec 并重新由 Human Review：

- 需要新增 Role、Gate、根状态、跨会话 Registry，或把按需决策文件扩张成固定状态系统。
- 决策文件与 Spec 无法维持“澄清决定/执行基线”的单一 owner，继续会形成双权威。
- 需要让领域 Provider 取得 Sacha 生命周期或 Human 批准权。
- 需要把固定 Spec schema 强加给所有任务，或 validator 必须逐句锁定模板。
- `setup-agents` 必须覆盖非 Sacha-owned 文件、修改全局配置/cache，或自动迁移旧文件才能完成。
- A/B/C 无法在现有 Acceptance、Entry Condition 和完成声明中表达，必须改变公共协议。
- 实施发现 Scope 涉及新的产品版本、breaking schema、安装、发布、commit 或 push。

Executor 开工前必须满足：

- Human 接受本 Spec，或异议已回写并重新冻结。
- 实施 Domain Provider guide/跨仓迭代前，Human 也接受关联的独立 Domain Provider Spec。
- 实施仅修改 Sacha 源码、文档、测试和 validator；不执行安装、迁移用户 Agent、Git 提交或发布。
- 目标文件的当前改动与本 Scope 无不可语义合并的冲突。

同 Scope 的实现错误、测试失败、漏改消费者或文案压缩由原 Executor 直接修复并重验，不重新请求批准。
