# Runtime 场景测试

这里保存给独立 Agent 实际执行的任务包，不用正则、标记或固定句子证明流程正确。Markdown 只是任务输入，裁决标准只供独立评估者读取；只有真实派发、工作区结果、验证器输出与独立评估共同构成证据。

## 任务包结构

每个 `packs/<name>/` 包含：

- `task.md`：只交给执行 Agent 的目标、授权、输入和验收；不写期望 Role 路线。
- `fixture/`：复制到本次隔离 root 的真实输入和验证器。
- `oracle.md`：只交给独立评估者，定义预期流程、允许弹性和偏移条件；执行 Agent 不得预读。

## 通用运行流程

1. 在工作区 `.temp/runtime-scenarios/<run-id>/<case-id>/` 创建唯一隔离 root，把 `fixture/` 复制进去，把 `task.md` 另存为中性 `instructions.md`，并把 [`assets/workspace-AGENTS.md`](assets/workspace-AGENTS.md) 复制为该 root 的 `AGENTS.md`。不得在包内原地执行，也不得把包名或 `oracle.md` 暴露给执行者。
2. 运行者按任务包验收选择执行上下文：不要求 Manager 派发时，以 `fork_turns="none"` 启动不携带父对话历史的委派 Agent；要求 Manager 派发、Root Session 或 continuable direct-child 身份时，由 Human 明确发起或授权创建全新主任务，不先创建承载整个流程的委派 Agent。两种上下文都只接收中性任务、隔离 root、工作区规则和正式入口 Skill；全新 Runtime 使用发现能力，`source-scenario` 才提供当前源码 `using-sacha/SKILL.md` path。执行者按入口 Skill 读取需要的 Core/Role/Adapter，不得读取仓库 `PLUGIN_DESIGN.md`、本 README、源任务包或 oracle。
3. 执行者需要 Human 澄清时，运行者只回答该问题，不补发预期 Role、Gate 或步骤。运行者保存 Human 问题/答复、真实工作区 delta、验证器原始输出，以及目标 Runtime 能提供的原生 Agent 创建、parent/depth、route、settlement/终态和工具轨迹；事后总结或 Agent 自报不能替代这些原生记录。
4. Manager 派发后，运行者必须能证明每个被裁决的 work unit 的首次创建标识和直接 parent。需要验证单层派发时，优先保存机器可读 parent/depth/descendant 证据；不可达时才保留实时树快照，再不可达则对应证据为 `blocked`。
5. 执行者结束后启动未参与实施的独立评估者；只给它 `oracle.md`、本次目标 Runtime Adapter、上述原始记录、最终工作区和验证器输出。独立评估者按 `pass | drift | blocked` 裁决，并指出第一处偏移与直接证据。
6. `pass` 必须同时满足任务验收和 oracle。源码阅读、Skill/Plugin validator、配置文件或执行者自报不能替代真实 Runtime 行为；安装后的全新发现只有在 Human 已授权安装并从全新任务启动时才能作为 Runtime 证据，其他运行标记为 `source-scenario`。

## 当前基线包

- `executor-only`：清晰、低风险、单 Owner 的本地写入应直接完成。
- `using-sacha-semantic-turn`：验证查询/诊断转为修改时重新判断入口，Human 反问入口行为不被当成接受。
- `planner-explore-manager-reviewer`：验证 Planner/Explore、多个隔离单元协调和独立复核。
- `explore-shared-context-loop`：验证 Human 不理解背景时先调查、解释、允许纠正，再进入真正 Human 决定。
- `explore-handoff-continuation`：验证 Explore 的恢复与返回调用节点。
- `roadmap-self-contained-document`：验证主流程外 Roadmap 与 document-project。
- `closeout-command`：验证明确收口只完成当前唯一 Spec。
- `project-facing-spec`：验证项目实施规格不混入工作流内部语义。
- `workflow-language-boundary`：验证产品文本、运行日志、代码标识和 Handoff 边界。
- `reviewer-semantic-chain`：验证 Reviewer 对正式入口、边界和证据范围的真实追踪。
- `codex-code-mode-readonly-batch`：验证 Codex Code Mode 只读批量路线。
- `codex-skill-entry-visibility`：验证 `using-sacha` 自动入口、下游 Skill 隐式可见性、显式调用和 Human 可见输出。
- `codex-agent-capability-routing`：分别验证 Codex v1/v2 从真实 Capability Binding 到 child 首次工作单元的 canonical Skill path、无固定模型 Agent、Researcher/Reviewer/Executor 工具面与逐次模型路线。
- `codex-context-isolation-research`：验证 Manager Gate 关闭时，一个高噪声调查可以使用新的直接委派 Agent 并只返回压缩结果。
- `codex-context-isolation-execution`：验证多个独立实施单元由 Manager 统一派发，实施 Agent 吸收中间过程并返回压缩结果。
- `dsh-continuable-parallel-barrier`：验证 DSH Root 直接创建多个 continuable child、派发后继续推进 ready work、在 barrier 依赖 settlement 恢复，且部分结果不会导致提前完成。
- `dsh-continuable-review-isolation`：验证 DSH 正式 Reviewer 是新的 Root direct continuable child，输入来源独立、消费原始 evidence、没有下级创建，并且不依赖 Agent Teams。

新增包必须来自真实 failure mode 或待验证的流程变化；先写不带答案的 `task.md`，再把期望与允许弹性写进独立 `oracle.md`。不得为覆盖节点数量拼接不自然任务。

## 已取代证据

- `codex-code-mode-v1-batch`：只保存既有 v1 批量 Agent 生命周期的历史 source-scenario；当前 Sacha Code Mode 已排除 Agent 生命周期工具，不得作为现行验收。
