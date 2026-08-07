# Runtime scenario 测试

这里保存给独立 Agent 实际执行的任务包，不用正则、marker 或固定句子证明流程正确。Markdown 只是任务输入和评审 oracle；只有真实 dispatch、workspace 结果、verifier 输出与独立 evaluator 共同构成证据。

## 任务包结构

每个 `packs/<name>/` 包含：

- `task.md`：只交给执行 Agent 的目标、授权、输入和验收；不写期望 Role 路线。
- `fixture/`：复制到本次隔离 work root 的真实输入和 verifier。
- `oracle.md`：只交给独立 evaluator，定义预期流程、允许弹性和 drift 条件；执行 Agent 不得预读。

## 运行流程

1. 在 workspace `.temp/runtime-scenarios/<run-id>/<case-id>/` 创建唯一隔离 work root，把该包 `fixture/` 的内容复制进去，把 `task.md` 另存为中性名称 `instructions.md`，并把 [`assets/workspace-AGENTS.md`](assets/workspace-AGENTS.md) 复制为该 root 的 `AGENTS.md`；不得在包内原地执行，也不得让 source pack 名称向执行者泄露预期路线。
2. 以 `fork_turns="none"` 启动一个新 subagent，只提供中性 `instructions.md`、隔离 work root、该 root 的 `AGENTS.md`、正式入口 Skill（fresh Runtime 用 discovery；`source-scenario` 才给当前源码 `using-sacha/SKILL.md` path）和本次 evidence recipient。执行 Agent 不使用 SachaOrchestra 仓库开发规则作为运行路线，只按入口 Skill 读取所需 Core/Skill/Adapter；不得读取根目录 `PLUGIN_DESIGN.md`、插件 README、source pack path 或 `oracle.md`。`PLUGIN_DESIGN.md` 只由维护者与独立 evaluator 使用。
3. Agent 出现 Human clarification 时，运行者只回答该问题，不补发期望 Role、Gate 或步骤。其余过程由 Agent 自主完成。若发生嵌套 dispatch，每个 target 在开始与结束时直接向 evidence recipient 报告 canonical id、owned scope 和 terminal；invoking owner 必须在首次 wait 前报告本波全部已成功创建的 id，运行者立即保存当时的 live agent-tree snapshot。事后总结或已消失 target 的回忆不能替代这组原生证据。
4. 运行者还要保留 Human 问题与答复、workspace delta 和 verifier 原始输出。执行者结束后，启动未参与实施的独立 evaluator；只给它 `oracle.md`、上述直接记录、最终 workspace 和 verifier 输出。evaluator 按 `pass | drift | blocked` 裁决，并指出第一处偏移及直接证据；必要记录在评审前已不可达时必须判 `blocked`，不得按执行者自报放行。
5. `pass` 必须同时满足任务验收和 oracle；静态阅读、执行者自报、Skill/Plugin validator 或 fixture 字符串不能替代本步骤。安装后 fresh discovery 只有在 Human 已授权安装并从 fresh task 启动时才能另记为 Runtime 证据，否则结果标为 `source-scenario`。

## 当前基线包

- `executor-only`：清晰、低风险、单 owner 的本地写入，应在当前 context 直接完成。
- `planner-clarify-manager-reviewer`：breaking 配置迁移先暴露真实 Human 决定，再处理两个可隔离单元，最后独立复核。

新增包必须来自真实 failure mode 或待验证的流程变化；先写不带答案的 `task.md`，再把期望与允许弹性写入独立 `oracle.md`。不得为覆盖节点数量拼接不自然任务。
