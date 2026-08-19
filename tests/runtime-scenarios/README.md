# Runtime 场景测试

这里保存给独立 Agent 实际执行的任务包，不用正则、标记或固定句子证明流程正确。Markdown 只是任务输入，裁决标准只供独立评估者读取；只有真实派发、工作区结果、验证器输出与独立评估共同构成证据。

## 任务包结构

每个 `packs/<name>/` 包含：

- `task.md`：只交给执行 Agent 的目标、授权、输入和验收；不写期望 Role 路线。
- `fixture/`：复制到本次隔离 root 的真实输入和验证器。
- `oracle.md`：只交给独立评估者，定义预期流程、允许弹性和偏移条件；执行 Agent 不得预读。

## 运行流程

1. 在工作区 `.temp/runtime-scenarios/<run-id>/<case-id>/` 创建唯一隔离 root，把该包 `fixture/` 的内容复制进去，把 `task.md` 另存为中性名称 `instructions.md`，并把 [`assets/workspace-AGENTS.md`](assets/workspace-AGENTS.md) 复制为该 root 的 `AGENTS.md`；不得在包内原地执行，也不得让源任务包名称向执行者泄露预期路线。
2. 运行者按任务包验收选择执行上下文：不要求 Manager 派发时，以 `fork_turns="none"` 启动一个不携带父对话历史的委派 Agent；要求 Manager 派发时，由 Human 明确发起或授权创建全新主任务，不先创建承载整个流程的委派 Agent。两种上下文都只接收中性 `instructions.md`、隔离 root、该 root 的 `AGENTS.md` 和正式入口 Skill；全新 Runtime 使用发现能力，`source-scenario` 才提供当前源码 `using-sacha/SKILL.md` path。执行者不使用 SachaOrchestra 仓库开发规则作为运行路线，只按入口 Skill 读取所需 Core/Skill/Adapter；不得读取根目录 `PLUGIN_DESIGN.md`、插件 README、源任务包 path 或 `oracle.md`。`PLUGIN_DESIGN.md` 只由维护者与独立评估者使用。
3. 执行者需要 Human 澄清时，运行者只回答该问题，不补发期望 Role、Gate 或步骤。其余过程由执行者自主完成。主任务发生 Manager 派发时，运行者从当前 Runtime 原生传输保存每次首次创建的原始调用参数、返回标识、委派 Agent 的直接启动/终态记录、执行者实际读取的当前 Runtime Adapter path，以及首次等待前可用的父任务/session/depth 元数据和子任务工具轨迹；主任务必须在首次等待前报告本波全部已成功创建的标识。机器调用图已证明全部实例是主任务直接子级且子任务没有下级创建时，不再要求 Human 手工查看 UI；当前 Runtime 不提供必要机器记录时，运行者才保存当时的实时 Agent 树快照，二者均不可达则把该证据判为 `blocked`。事后总结或已消失委派 Agent 的回忆不能替代这组原生证据。
4. 运行者还要保留 Human 问题与答复、工作区 `delta` 和验证器原始输出。执行者结束后，启动未参与实施的独立评估者；只给它 `oracle.md`、本次目标 Runtime 的 Adapter、上述直接记录、最终工作区和验证器输出。独立评估者按 `pass | drift | blocked` 裁决，并指出第一处偏移及直接证据；必要记录在评审前已不可达时必须判 `blocked`，不得按执行者自报放行。
5. `pass` 必须同时满足任务验收和裁决标准；静态阅读、执行者自报、Skill/Plugin validator 或 `fixture/` 字符串不能替代本步骤。安装后的全新发现只有在 Human 已授权安装并从全新任务启动时才能另记为 Runtime 证据，否则结果标为 `source-scenario`。

## 当前基线包

- `executor-only`：由不携带父对话历史的委派 Agent 执行；清晰、低风险、单 Owner 的本地写入应在该上下文直接完成。
- `planner-clarify-manager-reviewer`：由 Human 明确发起或授权创建的全新主任务执行；破坏性配置迁移先暴露真实 Human 决定，再由 Manager 派发两个可隔离单元，最后独立复核。
- `clarify-shared-context-loop`：由不携带父对话历史的执行上下文运行；验证 Human 明确不了解背景时，Clarify 先调查解释并接受反问/纠正，不把技术分析直接包装成选择题。
- `closeout-command`：由不携带父对话历史的执行上下文运行；验证 Human 明确请求“收口”时只原位完成当前唯一 Spec，不生成项目文档或 `docs/done`。
- `project-facing-spec`：由不携带父对话历史的显式 Planner 运行；从已确认项目事实与混合交付记录生成纯项目实施规格，验证 Spec 格式、项目语境和工作流信息外置。
- `workflow-language-boundary`：由不携带父对话历史的独立 Reviewer 运行；对真实候选差异区分产品文本、英文运行日志、项目正式代码标识和 Handoff，不使用粗暴关键词禁用。
- `codex-code-mode-readonly-batch`：由不携带父对话历史的执行上下文运行；对两个无共同原生批量入口的真实只读工具比较逐次基线与一个外层 Code Mode 调用，并验证 Runtime asset、嵌套 caller、输出边界和零重放。

新增包必须来自真实 failure mode 或待验证的流程变化；先写不带答案的 `task.md`，再把期望与允许弹性写入独立 `oracle.md`。不得为覆盖节点数量拼接不自然任务。

## 已取代证据

- `codex-code-mode-v1-batch`：保存既有 v1 Code Mode 批量 Agent 创建、等待和清理的 source-scenario 原始任务包；当前 Sacha Code Mode 已排除全部 Agent 生命周期工具，本包不得作为现行验收、改写或与 v2 证据混合。
