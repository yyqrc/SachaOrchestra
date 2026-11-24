# Runtime 场景测试

这里保存给独立 Agent 实际执行的任务包，不用正则、标记或固定句子证明流程正确。Markdown 只是任务输入，裁决标准只供独立评估者读取；只有真实派发、工作区结果、验证器输出与独立评估共同构成证据。

## 任务包结构

每个 `packs/<name>/` 包含：

- `task.md` 写清交给执行者的目标、授权、输入和验收要求。不得提前透露待验证的解法或预期的角色路线。单条任务直接交给执行者。需要连续用户消息时，文件应写明消息边界。运行者逐条发送，不提前暴露后续消息。
- `fixture/`：复制到本次隔离 root 的真实输入和验证器。
- `oracle.md`：只交给独立评估者，定义预期流程、允许弹性和偏移条件。执行 Agent 不得预读。

编写新任务包时，先写 `task.md`，再写独立的 `oracle.md`。一个任务包可以包含多个相关案例。

## 什么时候新增场景

- 场景优先记录实际使用中已经出现、修复后需要防止再次出现的问题。普通规则整理、措辞调整、新版本发布或之前未专门运行过某项行为，都不构成新增理由。
- 没有既有失败记录时，只有两种情况可以新增。权限、安全、删除或覆盖状态、不可逆外部动作等高风险变化，不宜等待日常使用暴露。用户明确要求实际运行验收时，也可以新增。
- 新增前确认现有案例无法覆盖该问题，且新案例能观察失败和成功结果。`oracle.md` 须写清问题来源和判定依据，有失败记录时说明实际发生的问题，需要防止高风险后果时说明要避免什么。
- 场景只回答对应问题。流程变化、角色、参数或状态枚举本身不构成新增理由，不为凑数量或组合覆盖拼接任务。某个未触发的场景没有执行，不自动形成后续验证清单。

## 通用运行流程

1. 在工作区 `.temp/runtime-scenarios/<run-id>/<case-id>/` 创建唯一隔离 root，把 `fixture/` 复制进去，并把 [`assets/workspace-AGENTS.md`](assets/workspace-AGENTS.md) 复制为该 root 的 `AGENTS.md`。单条消息的 `task.md` 另存为中性 `instructions.md`；连续 Human 消息按文件明确的边界逐条发送，不把后续消息提前复制进隔离 root。不得在包内原地执行，也不得把包名或 `oracle.md` 暴露给执行者。
2. 运行者按任务包验收选择执行上下文：不要求 Manager 派发时，以 `fork_turns="none"` 启动不携带父对话历史的委派 Agent；要求 Manager 派发、Root Session 或 continuable direct-child 身份时，由 Human 明确发起或授权创建全新主任务，不先创建承载整个流程的委派 Agent。两种上下文都只接收中性任务、隔离 root、工作区规则和正式入口 Skill；全新 Runtime 使用发现能力，`source-scenario` 才提供当前源码 `using-sacha/SKILL.md` path。执行者按入口 Skill 读取需要的 Core/Role/Adapter，不得读取仓库 `PLUGIN_DESIGN.md`、本 README、源任务包或 oracle。
3. 执行者需要 Human 澄清时，运行者只回答该问题，不补发预期 Role、Gate 或步骤。运行者保存 Human 问题/答复、真实工作区 delta、验证器原始输出，以及目标 Runtime 能提供的原生 Agent 创建、parent/depth、route、settlement/终态和工具轨迹。技能读取路径和原始输出从运行记录提取，不为取证要求执行者把明细写入用户可见答复。事后总结或 Agent 自报不能替代原生记录。
4. Manager 派发后，运行者必须能证明每个被裁决的 work unit 的首次创建标识和直接 parent。需要验证单层派发时，优先保存机器可读 parent/depth/descendant 证据；不可达时才保留实时树快照，再不可达则对应证据为 `blocked`。
5. 执行者结束后启动未参与实施的独立评估者；只给它 `oracle.md`、本次目标 Runtime Adapter、上述原始记录、最终工作区和验证器输出。独立评估者按 `pass | drift | blocked` 裁决，并指出第一处偏移与直接证据。
6. `pass` 必须同时满足任务验收和 oracle。源码阅读、Skill/Plugin validator、配置文件或执行者自报不能替代真实 Runtime 行为；安装后的全新发现只有在 Human 已授权安装并从全新任务启动时才能作为 Runtime 证据，其他运行标记为 `source-scenario`。

## 当前 19 个场景包

- `using-sacha-semantic-turn`：验证查询转为修改时只询问仍影响做法的实际问题，并保留只读边界。
- `using-sacha-spec-intake`：验证完整规格请求直接进入只读规划，在同一轮询问实际未决项，并沿用已有的规格写入授权。
- `using-sacha-method-consultation`：验证原型咨询只问实际取舍，反问不代替决定，待决期间继续可独立开展的只读工作。
- `explore-shared-context-loop`：验证 Human 不理解背景时先调查、解释、允许纠正，再进入真正 Human 决定。
- `roadmap-self-contained-document`：验证主流程外 Roadmap 与 document-project。
- `roadmap-spec-task-handoff`：验证 Roadmap 推荐独立完整 Spec 任务、Human 确认创建及 Codex 目标任务显式 Planner 入口。
- `closeout-command`：验证明确请求只把当前唯一 Spec 标为已完成。
- `implementation-completion`：验证实施完成后自动标记 Spec、阻塞证据或文档失败时保留状态，以及已确认具体文档写入时不重问。
- `project-facing-spec`：验证项目实施规格不混入工作流内部语义。
- `minimal-existing-flow`：以 TOD 材质简化返工为来源，验证方案与无原对话实施优先局部修改已有流程，不以新增准备结构搬运保存、清理；允许有实际必要性的小型关系数据。
- `interaction-spec`：验证从实际使用过程形成可操作草稿与精确 Spec、无原对话恢复，以及识别目标显示/处理、双侧选择和已要求比较方式的实现偏差。
- `workflow-language-boundary`：验证产品日志不得泄漏内部流程，同时放行项目已定义的代码标识。
- `reviewer-semantic-chain`：验证 Reviewer 对正式入口、边界和证据范围的真实追踪。
- `codex-skill-entry-visibility`：验证面向 Sacha 的普通修改直接沿用已有授权，产品名不触发额外询问或派发。
- `shared-compilation-input`：验证并行写入未完成时延后共享编译、实施者交回待验证项，以及稳定输入失败后的责任交接和补验；使用小型 Python 工程，不替代 Unity 运行验证。
- `delegation-context-cost`：验证共同接口未定时的工作块安排、同级事实与控制动作边界，以及连续/独立后续工作的复用判断和恢复信息；需要全新主任务，未运行不算基线通过。
- `delegation-serial-evidence`：验证调查派发后的责任边界、同文件串行实施归属、有效输入复用与实际发生的等待/状态查询；需要全新主任务，不推算成本节省比例。
- `dsh-continuable-review-isolation`：验证 DSH 正式 Reviewer 是新的 Root direct continuable child，输入来源独立、消费原始 evidence、没有下级创建，并且不依赖 Agent Teams。
- `dsh-companion-root-surface-routing`：在同一个 DSH 主会话中，先检查工具可见性，再按授权修改文件。核对工具集由 `bootstrap` 切到 `resident` 的会话事件，以及文件写入是否限于第二条消息的授权。需要恢复证据时只续查这一案例。
