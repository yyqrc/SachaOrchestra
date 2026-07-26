# Sacha Orchestra 项目规则

## 规则分层

- 本文件适用于 Sacha Orchestra workspace，并细化实际生效的 Global AGENTS 规则。
- 不得放宽 Global 的安全、授权、证据、用户改动保护、工程或验证要求。
- 本文件必须是 workspace 中唯一的 Project `AGENTS.md`；不得在 plugin 根目录下新增另一份。

## Workspace 事实

- 本 workspace 是 repo-local marketplace，其中只有一份 plugin 源码，位于 `plugins/sacha-orchestra`。
- 本 workspace 是 Git 仓库。commit 与发布须遵循 Global Git 规则。
- 当前 Git release、source candidate、manifest 与验证层级只以 [`docs/architecture/evolution.md`](docs/architecture/evolution.md) 为权威；manifest 表示当前源码 Scope 的精确版本，Git tag 表示已发布版本。Core 与 Adapter 的合同版本只表示各自 schema，不代表产品版本。
- `0.1.y` 保持为 `1.0.0` 前的 candidate line。只有 Lean Hybrid、Manager Gate、真实并行执行、运行时断言、自托管升级、安装后验证和独立验收同时满足，才具备发布 `1.0.0` 的资格。
- `docs/history/0.1.0/spec.md` 是 Foundation bootstrap 的冻结 execution contract。
- `docs/architecture/evolution.md` 是长期方向、当前主线、self-hosting Gate、版本策略和 Core breaking change 的权威来源，不构成未来能力的实施授权。

## Owner 与直接入口

| 路径 | Owner 与用途 |
| --- | --- |
| `docs/history/0.1.0/spec.md` | Foundation bootstrap 的 Scope、slice、Gate 和 acceptance contract；Executor 不得编辑 |
| `docs/plans/2026-07-14-stage3-lean-orchestration/spec.md` | 已冻结的 Stage 3 Lean Hybrid implementation Scope；Executor 不得编辑 |
| `docs/plans/2026-07-16-subagent-context-report-budget/spec.md` | Human 已批准的 `0.1.11` Subagent context/report budget Scope 与验收契约；Executor 不得编辑 |
| `docs/plans/2026-07-16-completion-return-routing/spec.md` | Human 已授权实施的 `0.1.12` Autonomous Goal Completion Scope 与验收契约；Executor 不得编辑 |
| `docs/plans/2026-07-16-workflow-feedback-intake/spec.md` | Human 已授权实施的 `0.1.13` Workflow Feedback Intake Scope 与验收契约；Executor 不得编辑 |
| `docs/plans/2026-07-16-project-binding-v2/spec.md` | Human 已授权实施的 Project Binding v2 Scope 与验收契约；Executor 不得编辑 |
| `docs/plans/2026-07-17-setup-capability-mapping-v3/spec.md` | Human 已授权实施的 Setup Project Capability Mapping v3 Scope 与验收契约；Executor 不得编辑 |
| `docs/plans/2026-07-17-self-hosting-workflow-hardening/spec.md` | Human 已授权并通过 R3 验收的 Workflow Hardening and Evidence Semantics Scope；Executor 不得编辑 |
| `docs/plans/2026-07-23-runtime-owner-restoration/spec.md` | Human 已批准的 Owner-Joined Terminal Return Scope；Executor 不得编辑 |
| `docs/architecture/evolution.md` | 长期架构与路线图权威；涉及版本、self-hosting、Manager、并行或 breaking change 的工作须读取 |
| `docs/history/0.1.0/execution-report.md` | Foundation bootstrap 的已完成 evidence index；不得编辑 |
| `docs/history/0.1.0/review.md` | Foundation bootstrap 的最终独立 Review；不得编辑 |
| `.agents/plugins/marketplace.json` | Repo-local 部署元数据；首次创建由 plugin-creator tooling 负责 |
| `plugins/sacha-orchestra/.codex-plugin/plugin.json` | 仅包含 plugin 部署与接口元数据 |
| `plugins/sacha-orchestra/core/workflow-contract.md` | Role、Gate、lifecycle、escalation 和 repair 的规范性 contract |
| `plugins/sacha-orchestra/core/artifact-protocol.md` | Artifact 与 Handoff 的规范性 contract |
| `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md` | Codex context、Skill、部署、恢复和 runtime verification 的映射 |
| `plugins/sacha-orchestra/adapters/claudecode/runtime-adapter.md` | Claude Code context、Agent、并行、恢复和 discovery 的映射 |
| `plugins/sacha-orchestra/skills/*` | 简洁且 Runtime-neutral 的 trigger 与 Role-local procedure；共享 contract 保留在 `core/` 中 |
| `plugins/sacha-orchestra/README.md` | 非规范性用户入口；必须链接到权威来源，不得复制其内容 |

## 读取路由

- 核查 Foundation bootstrap 历史时，先读取 `docs/history/0.1.0/spec.md`，并且只将同目录 `execution-report.md` 用作 evidence index。
- 实施或验收 Stage 3 Lean Hybrid 时，先读取 `docs/plans/2026-07-14-stage3-lean-orchestration/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 实施或验收 `0.1.11` Subagent context/report budget 时，先读取 `docs/plans/2026-07-16-subagent-context-report-budget/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 实施或验收 `0.1.12` Autonomous Goal Completion 时，先读取 `docs/plans/2026-07-16-completion-return-routing/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 实施或验收 `0.1.13` Workflow Feedback Intake 时，先读取 `docs/plans/2026-07-16-workflow-feedback-intake/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 实施或验收 Project Binding v2 时，先读取 `docs/plans/2026-07-16-project-binding-v2/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 实施或验收 Setup Project Capability Mapping v3 时，先读取 `docs/plans/2026-07-17-setup-capability-mapping-v3/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 实施或验收 Workflow Hardening and Evidence Semantics 时，先读取 `docs/plans/2026-07-17-self-hosting-workflow-hardening/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 实施或验收 Owner-Joined Terminal Return 时，先读取 `docs/plans/2026-07-23-runtime-owner-restoration/spec.md`，并且只将其本地 `execution-report.md` 用作 evidence index。
- 查询 Role、Gate、lifecycle、escalation 或 repair 语义时，读取 `plugins/sacha-orchestra/core/workflow-contract.md`。
- 查询 Artifact 权威边界或九字段 Handoff Envelope 时，读取 `plugins/sacha-orchestra/core/artifact-protocol.md`。
- 查询 Codex context、discovery、installation、refresh、removal、recovery 或 fresh-context 行为时，读取 `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md`。
- 查询 Role trigger 或最小 procedure 时，读取该 Role 的 `SKILL.md` 及其生成的 `agents/openai.yaml`。
- 涉及长期架构、成熟度 Stage、self-hosting level、`1.0.0`、Manager、并行、alias removal 或任何 Core breaking change 时，先读取 `docs/architecture/evolution.md`；只有 Human 明确确认具体改动后才可修改。该确认不要求额外 Planner Spec；需要冻结新实现 Scope、比较实质方案、跨 context 恢复或执行 breaking migration 时才创建 Spec。
- Project Integration 和 Domain Skill 归各自项目所有。不得将项目特定命令或证据规则导入此 Core。

## Plugin Development Direct

- 普通 plugin `change`、`build`、`fix`、`sync` 或 `iterate` 请求默认在当前 task 执行；多文件、耗时或验证步骤多不单独打开任何 Gate。
- Direct Scope 以用户语义目标和明确约束为边界。预计文件列表不是穷尽 allowlist，只有用户或已批准 Spec 明确写出 exact file allowlist 时才是硬边界。
- 当前 Executor 可修改同一目标直接必需的源码、非规范性文档、回归断言和本地验证配置；路径错误、漏改、格式/镜像差异和定向验证失败仍在同一目标内时直接修复并重验，不创建额外 Scope、Role、Goal、Report、Review 或 Handoff。
- 出现实质新方案、breaking contract/schema、权限、安全、持久数据、验收改变、未授权外部动作或无法完整验证时，停止相关写入并按三个 Gate 路由。
- 每次迭代只验证当前目标 Runtime 和交付层；除非 Human 明确要求跨 Runtime 验收，其他 Runtime 的安装、发现、行为或证据缺口只记录为后续使用反馈，不扩大当前 Scope，也不阻塞当前 Runtime 的 source release。
- Review 优先拦截会导致错误交付的关键问题：已知实现失败、安全/权限/持久数据风险、破坏性兼容问题、不可恢复写入、无效包、版本或发布一致性错误。小问题、改进建议和未被批准矩阵明确标为 release-blocking 的 `Needs Evidence` 使用 `Accepted with follow-up`，在实际使用中收集反馈，不为形式完整阻塞发布。
- Review 不追求全历史、全 Runtime 或全证据闭环；只读取能改变当前 verdict 的 locator，只重跑能发现致命回归的最小检查。不得把“还可以补更多证据”本身升级为 `Needs Fix`。

## 维护边界

- `plugins/sacha-orchestra/core/` 必须保持 platform-neutral 和 project-neutral。它可以定义稳定的协作语义，但不得定义 Codex 机制、项目命令或未来 Stage 的实现。
- `plugins/sacha-orchestra/adapters/<runtime>/` 必须保持为单一 Runtime 的映射层：只说明 Core 概念如何落到该 Runtime 当前正式能力，引用 Core 与 Artifact Protocol，不重定义 Role、Gate、lifecycle、Artifact 或 Handoff 语义。Adapter 不得引用、比较、解释或依赖其他 Runtime Adapter；Runtime 能力差异分别在各自 Adapter 内直接映射，不建立跨 Adapter 兼容关系。
- 规则进入 Core 必须同时满足 platform/project-neutral、至少两个独立 Role/组件消费、需要稳定互操作语义；仅跨 Runtime 不足以进入 Core。单 Runtime 的工具、identity、discovery、installation、notification、wait/join 或恢复机制属于对应 Adapter；单 Role 的最小执行步骤和单 Skill taxonomy 属于对应 `SKILL.md`。
- 新增字母分级、状态码或命名路线前，必须指出至少两个独立消费者或机器互操作需求；只有一个消费者时使用本地 procedure，不建立 Core taxonomy。
- Core、Artifact Protocol、Runtime Adapter、Role `SKILL.md` 和生成器产出的 Project Integration 只描述当前正式合同。旧版本、旧字段、旧 schema、旧 alias、迁移经过、能力演进、废弃提示和兼容兜底不得残留其中；历史事实只写入 README、Evolution、`docs/history/` 或具名 migration 文档。停止支持的入口直接拒绝，不保留 fallback、翻译层或静默迁移。
- 每份正式文档必须仅依赖其声明的当前上游并能独立解释自身职责；不得要求读者再加载旧文档、同级 Runtime 文档、发布记录或隐含会话历史才能确定当前行为。
- 下游文档只增加本层 procedure；引用上游即可确定行为时不得复述 schema、状态表、Gate、Outcome 或 transport。不得为了降低 active token 把重复内容转移到新的 reference；只有内容具有独立消费者且确实按需加载时才新增资源。
- README 只保留受众入口、最小用法、当前权威 locator 和必要迁移入口；不得复制正式合同、展开版本逐条流水账或成为第二份状态源。详细历史放入 Evolution、`docs/history/` 或具名 migration 文档，README 只链接。
- 生成的 Project Integration 只保存项目绑定、冲突、fallback 和 canonical locator；不得复制 Core 路由模板、Role procedure、Runtime transport 或发布说明。
- Role `SKILL.md` 必须保持简洁和 Runtime-neutral：仅包含 trigger 描述、最小 Role workflow、暂停/路由规则以及对 Core 的直接引用；Runtime API 名称和 transport 细节只出现在对应 Adapter。不得新增 Skill README、changelog、installation guide、空 resource 或重复 contract。
- 删除、重命名或改变正式概念时，必须检查 Core、Adapter、Skill、README、生成器模板和 validator 的直接消费者；不得只修改权威定义而留下仍会生成或展示旧合同的入口。
- 文档或 Skill 改动必须检查语义 diff。纯换行、编码、BOM、空白或格式噪音不得报告为内容修改，也不得为了制造改动而改写字符；若目标文件没有实质语义变化，应从任务交付范围移除。自动格式化不得掩盖或替代实际合同变更。
- 正式生产 Role 入口只有 `planner`、`executor`、`reviewer`；不得新增 Role alias 或兼容 Skill。`setup-project` 必须保持 explicit-only；重新生成其 `agents/openai.yaml` 后，须在验证前恢复并确认 `policy.allow_implicit_invocation: false`。
- Manager 必须保持控制面而非第四个生产 Role；只有 Human 批准的 Managed Parallel 实现 Scope 才能新增对应 Skill 或 Adapter 映射。不得创建 `spec-executor` 或 `spec-reviewer` Skill。
- 未经另行批准的 consumer 和 Scope，不得新增 hook、MCP server、app、asset、plugin script 或 manifest field。

## Scaffold 与生成器命令

执行命令前，先解析当前 `plugin-creator`、`skill-creator`，以及可导入 PyYAML 的 Python。不得在交付物中硬编码用户特定的 creator 路径。

已批准的初始 repo-local scaffold 形式如下：

```powershell
& <validator-python> <plugin-creator>/scripts/create_basic_plugin.py sacha-orchestra `
  --path <workspace-root>/plugins `
  --with-skills `
  --with-marketplace `
  --marketplace-path <workspace-root>/.agents/plugins/marketplace.json `
  --install-policy AVAILABLE `
  --auth-policy ON_INSTALL
```

- baseline scaffold 不得传入 `--marketplace-name`、`--category` 或 `--force`。
- 新建 Skill 使用 `init_skill.py`，生成其元数据使用 `generate_openai_yaml.py`。须显式传入 `display_name`、25～64 个字符的 `short_description`，以及明确写出 `$skill-name` 的 `default_prompt`。
- 不得以手工编辑现有 marketplace 的方式执行更新。须在另行批准的更新任务中，使用当前 plugin-creator 指南和 helper。

## 验证命令与声明

普通 plugin 改动只运行与风险直接对应的最小集合：

```powershell
# 修改了 setup-project 的 Python 实现时
python -B tests/validate_project_setup.py

# 修改了 Skill 时，只校验受影响的 Skill
& <validator-python> <skill-creator>/scripts/quick_validate.py <affected-skill-root>

# 修改了 plugin 内容或元数据时
& <validator-python> <plugin-creator>/scripts/validate_plugin.py <plugin-root>

# 所有源码改动
git diff --check
```

`tests/validate_project_setup.py` 只保留 dry-run/幂等、拒绝覆盖、路径逃逸、回滚、歧义不猜测和 capability reconciliation 等真实代码行为。Markdown、Skill 或 Adapter 中“是否出现某句话”不得作为 workflow 行为通过证据；涉及 Role 路由、lifecycle、并行、return 或 feedback 的改动，只在当前目标 Runtime 使用代表性真实 task 做最小 smoke，并明确报告未覆盖路径。其他 Runtime 和非 release-blocking 场景留到实际使用反馈。

`tests/validate_release_coherence.py` 同时执行正式文档维护边界检查：Adapter contract mapping、跨 Adapter 引用、Core/Skill 行数与总文本预算、Skill 复合长行、产品版本/历史兼容标记、单 Skill taxonomy 和 Runtime API 泄漏。新增 Runtime Adapter、正式字段或 Runtime API 时必须同步更新该检查；不得通过改写禁用词、扩大白名单或删除断言来绕过边界，除非 Human 明确批准对应合同变更。

`plugin-eval` 可用于结构、描述和 token budget 诊断，但不是必跑 Gate，也不能替代官方 validator、真实 schema、代码测试或 runtime smoke。不得仅为提高评分添加无权威依据的 manifest 字段、英文触发词、reference 或其他产品内容；评估器输入兼容问题使用 task-local 等价镜像并报告限制，不修改安装 cache 或正式源码迁就工具。

仅发布收尾运行 metadata coherence：

```powershell
python -B tests/validate_release_coherence.py --version <version> --phase candidate
python -B tests/validate_release_coherence.py --version <version> --phase release
```

`candidate` 在 source candidate 阶段运行；`release` 在 commit、annotated tag 已建立且 Evolution 已切换为 release 后运行，并额外核对 tag 精确指向 `HEAD`。

只报告本轮实际执行的 static check、official validator、installation/discovery、代码测试和 runtime smoke；未运行的类别标记为未验证。命令成功只能证明它直接检查的事项。

## 安装授权 Gate

- Marketplace 注册、plugin 安装、refresh、removal 或 reinstall 会改变 workspace 外部的 Codex 状态，因此需要 Human Conductor 明确授权；工具能力或实施批准不隐含该授权。
- 使用 `read_marketplace_name.py` 从 `.agents/plugins/marketplace.json` 读取 marketplace 名称；不得根据目录名猜测。
- 只有获得授权后，才可使用 Codex Adapter 中记录的当前受支持 CLI 形式，并验证 marketplace 与 plugin list 的输出。
- Human 的一次有边界请求可以明确授权多个具名动作，例如精确版本安装、commit 和 push。只要 Scope、版本、安装目标、branch、remote 和风险未变化，就不得重复询问；仅暂停边界发生变化的动作。
- 已经验收的实现，或 Gate 全部保持关闭且已完整验证的 Direct Scope，继续采用 Direct 的仅元数据发布收尾；不会仅因包含版本、安装、commit 或 push 就要求新的 Spec、Report、Review 或 Handoff。
- manifest 必须保持为当前 source/release Scope 所批准的精确 semantic version；当前已发布版本只从 Evolution 的 `当前 release` 读取。除非另行批准的 Scope 有此要求，semantic release 使用该精确版本且不添加 cachebuster。不得编辑 Codex cache、应用权限或系统 PATH。

## 临时文件与用户改动

- task-local validator environment 和 smoke fixture 放在 `.temp/` 下。
- 清理前，解析目标的绝对路径，并确认其仍位于本 workspace 内。
- 只删除当前任务创建的临时项；保留所有用户所有或来源不明的文件。
- 不得使用 stash、reset、checkout、强制覆盖或广泛清理来恢复本 workspace。
