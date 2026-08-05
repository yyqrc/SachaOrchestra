# Sacha Orchestra 项目规则

## Workspace 事实

- 本文件是 Project `AGENTS.md`；Global AGENTS 的安全/授权/证据/Git/用户改动保护仍生效。
- 本 workspace 是 repo-local marketplace，唯一 plugin 源码位于 `plugins/sacha-orchestra`。
- Git release、candidate、manifest、验证只以 [`docs/architecture/evolution.md`](docs/architecture/evolution.md) 为权威；manifest=当前源码版本，tag=已发布版本；Core/Adapter 合同版本仅为 schema。
- Evolution 只给方向、版本和 breaking boundary，不授权实施。

## Owner 与直接入口

| 路径 | Owner 与用途 |
| --- | --- |
| `docs/architecture/evolution.md` | release、candidate、长期架构与 breaking change 权威 |
| 两个 deployment manifest | 当前源码版本与部署接口元数据 |
| `plugins/sacha-orchestra/core/intake-contract.md` | 入口判断、接受/拒绝、重复抑制和授权边界的规范性 contract |
| `plugins/sacha-orchestra/core/workflow-contract.md` | Workflow Kernel：不变量、Role/Gate 和 high-level lifecycle |
| `plugins/sacha-orchestra/core/assurance-contract.md` | Review、Baseline、Outcome 与 evidence 语义 |
| `plugins/sacha-orchestra/core/coordination-contract.md` | Manager、dispatch、return、identity/dedup 与 deviation |
| `plugins/sacha-orchestra/core/artifact-protocol.md` | Artifact 与 Handoff 的规范性 contract |
| `plugins/sacha-orchestra/adapters/<runtime>/runtime-adapter.md` | 单 Runtime discovery、transport、恢复与验证映射 |
| `plugins/sacha-orchestra/skills/*` | Runtime-neutral trigger 与 Role-local procedure |
| `plugins/sacha-orchestra/README.md` | 非规范性用户入口 |

## 读取路由

- 入口、Workflow、Assurance、Coordination、Artifact 只按当前 consumer 读取；只查询 trigger 时读取目标 `SKILL.md` 和 metadata。
- Runtime 局部任务只读目标 Adapter；Core 或跨 Runtime 审查按 Scope 比较。
- release、长期架构、Manager/并行、`1.0.0` 或 Core breaking：读取 Evolution；只有 Human 确认具体改动后才修改。
- Project Integration 和 Domain Skill 归各自项目所有。不得将项目特定命令或证据规则导入此 Core。

## Plugin Development Direct

- 普通 plugin `change`、`build`、`fix`、`sync` 或 `iterate` 请求默认在当前 task 执行；多文件、耗时或验证步骤多不单独打开任何 Gate。
- Direct Scope 以用户语义目标和明确约束为边界。预计文件列表不是穷尽 allowlist，只有用户或已批准 Spec 明确写出 exact file allowlist 时才是硬边界。
- 当前 Executor 可修改同一目标直接必需的源码、文档、断言和验证配置；同 Scope 漏改/失败直接修复重验，不创建额外流程。
- 出现实质新方案、breaking contract/schema、权限、安全、持久数据、验收改变、未授权外部动作或无法完整验证时，停止相关写入并按三个 Gate 路由。
- 每次只验证当前 Runtime 和交付层；除非 Human 明确要求跨 Runtime 验收，其他 Runtime 的安装、发现、行为或证据缺口只作后续反馈，不扩大或阻塞 source release。
- Review 只拦截会错误交付的关键问题；非 release-blocking 缺证据/改进项用 `Accepted with follow-up`。不追求全历史/全 Runtime，也不把“还能补证据”升级为 `Needs Fix`。

## 内容归属与信息密度

- 一个事实一个 owner：项目事实归本文件，Runtime 机制归 Adapter，Role procedure 归 Skill，跨消费者稳定语义才进 Core；下游只引用 owner。
- `description` 只回答“何时用/何时不用”；正文才写首查位置、扩大条件、动作、交付和停止边界。metadata prompt 只给自然入口，不复述正文流程。
- Adapter 单 Runtime；Role Skill Runtime-neutral；显式 setup 只管对应配置；README 只保留入口、最小用法和 locator；历史/迁移归具名文档。
- “不给 Sacha 注水”是项目验收条件：新增规则、Role、Gate、Artifact、状态、字段、模板或 validator 必须对应真实失败或重复低效，并能说清唯一 owner、直接 consumer、改变了什么判断和如何证伪；缺一项就不增加。
- 优先补强现有 owner 的 trigger、procedure 或 decision rule；“看起来更完整/更规范”不是扩产品面的理由。新增内容时先删铺垫、常识、历史和同义重复，示例、标签和局部做法不得自动升级为 Core 合同或必填格式。
- Caveman/精简只提高表达密度：可删除废话、同义重复和无消费者说明，不得删除或弱化有顺序依赖的步骤、trigger、进入/退出与恢复条件、Owner/Human 决策点、授权、安全、证据和验收。无法证明语义等价时保留原文；若会改变流程判断，停止该部分并把语义 delta 交给 Human 二次确认。
- 多种做法成立时写判断原则；稳定参数写配置；脆弱且重复的机械顺序写 script 并实跑。
- 主流程脱离 Sacha、固定 Gate、Scope/Handoff 仍能完成；编排只增强协调、恢复或独立验收。
- 不得为缩短文本删除授权、安全、失败、未验证、Evidence、Entry Condition、schema、恢复入口或脆弱顺序。

## 产品边界

- `using-sacha` 是唯一默认入口，不是 Role、Artifact、Hook 或授权层；自动建议只问一次，拒绝后同 Scope 不重复，接受不扩权。
- 无至少两个消费者时不向 Core 增加分级、状态码或 taxonomy。
- 生产 Role 只有 Planner/Executor/Reviewer；Manager 是控制面；直接 Role 是高级入口。Setup/Clarify explicit-only；不得新增 Role alias、`spec-executor` 或 `spec-reviewer`。
- Hook 不得接受/替代 Sacha、扩大授权或参与恢复。新增 hook/MCP/app/外部服务/权限字段需明确批准；目标必需的 repo-local asset/script/manifest 元数据按 Scope 修改验证。

| 变化 owner | 必须核查的直接消费者 |
| --- | --- |
| Intake 判断、接受/拒绝或入口授权 | `using-sacha`、Workflow、各 Adapter、Role/Feedback metadata、README、validator |
| Workflow Role、Gate、强度或 high-level lifecycle | Intake/Assurance/Coordination 边界、各 Adapter、受影响 Skill、README、generator、validator |
| Assurance Baseline、矩阵、Outcome 或 re-review | Workflow 引用、Reviewer/Executor、各 Adapter、Artifact、validator |
| Coordination Manager、dispatch、return、identity/dedup 或 deviation | Workflow、Manager/Feedback/Clarify、各 Adapter、Artifact、validator |
| Artifact 或 Handoff schema/权威边界 | Workflow 引用、各 Runtime Adapter、生产 Role/Manager/Feedback Skill、Project Integration 生成器、validator |
| 单 Runtime discovery、transport、identity、installation 或 recovery | 仅对应 Runtime Adapter、该 Runtime metadata/manifest、安装与 release validator；不得联动其他 Adapter |
| Skill trigger、local procedure 或 metadata | 对应 `SKILL.md`、生成的 metadata、直接调用/返回方、Adapter discovery 清单、README 入口与 plugin validator |
| Provider catalog/Binding 格式、resolver/generator 或 mapping 消费 | 必须同步 `docs/integrations/capability-provider-guide.md`；核查 `setup-project`、Role/Adapter、生成结果、测试/validator |
| `render_agents_block` 内容、managed_block 注入格式或 project-rules 模板契约 | 必须同步 `setup-project` SKILL.md 与生成器；核查 `capability-provider-guide.md`、`validate_project_setup.py`、provider `project-rules` skill 消费者 |
| 产品版本、source candidate 或 release 状态 | Evolution、两个 deployment manifest、README locator、release coherence validator、Git commit/tag identity |

## Creator 与生成器

- 执行前解析当前 `plugin-creator`、`skill-creator` 和可导入 PyYAML 的 Python，不硬编码用户路径。
- 新建 Skill 用 `init_skill.py`；metadata 用 `generate_openai_yaml.py`，提供 `display_name`、25～64 字符的 `short_description` 和包含 `$skill-name` 的 `default_prompt`。
- Marketplace 更新须另行授权并使用当前 creator helper；不得手改已注册 marketplace 或 cache。

## 验证命令与声明

普通 plugin 改动只运行风险对应的最小集合：

```powershell
python -B tests/validate_project_setup.py
python -B -m unittest discover -s tests -p 'test_*.py'
& <validator-python> -B <skill-creator>/scripts/quick_validate.py <affected-skill-root>
& <validator-python> -B <plugin-creator>/scripts/validate_plugin.py <plugin-root>
cprobe summary <affected-path-or-directory> --json
```

- Python 默认由 Codex 全局 `shell_environment_policy` 注入 `PYTHONUTF8=1`；生产脚本仍显式使用 `encoding="utf-8"`。不得给每条命令机械添加 `-X utf8`；只有实测 `sys.flags.utf8_mode != 1` 或出现解码错误时，才对受影响命令使用该 fallback。
- `cprobe` 返回 `budget.complete=true` 且 `whitespace.errors=0` 已构成该 Scope 的 whitespace 证据，不再重复执行 `git diff --check`。仅当 `cprobe` 缺失、结果不完整或不支持目标时，对同一 Scope 执行一次原生 Git fallback；暂存后内容未变化不重复取证。
- Source validator 只检查可解析结构、稳定标识、owner/link、真实 consumer 预算和禁止边界；不得逐句锁定可等价改写的说明文字。按需加载的 Skill 正文不以总字数、行数或单行长度作为 release blocker；压缩不得删除流程判断。
- 生产脚本用隔离临时目录的正反例/幂等/失败恢复测试；Skill trigger、Role 路由与 Runtime 调用用真实 scenario smoke。前一层不得替代后一层。
- 能力完成声明须定位生产入口；模板、fixture、字符串或自报只证明其自身，未运行的行为仍标记未验证。

`plugin-eval` 可用于结构、描述和 token budget 诊断，但不是必跑 Gate，也不能替代官方 validator、真实 schema、代码测试或 runtime smoke。不得仅为提高评分添加无权威依据的 manifest 字段、英文触发词、reference 或其他产品内容；评估器输入兼容问题使用 task-local 等价镜像并报告限制，不修改安装 cache 或正式源码迁就工具。

发布分两种模式：

- Human 说“快速发版”时，默认递增 patch 版本；只核对两个 deployment manifest、Evolution 的 release/candidate 版本、annotated tag 到 `HEAD` 的指向及 push 后远端分支/tag。跳过普通回归、Skill/Plugin validator、完整 release coherence、安装/cache parity、fresh discovery 和 runtime。
- Human 说“发版”时，运行风险对应的普通验证与完整 metadata coherence；安装和 runtime 仍按明确授权与发布目标决定。

普通发版收尾运行 metadata coherence：

```powershell
python -B tests/validate_release_coherence.py --version <version> --phase candidate
python -B tests/validate_release_coherence.py --version <version> --phase release
```

`candidate` 在 source candidate 阶段运行；`release` 在 commit、annotated tag 已建立且 Evolution 已切换为 release 后运行，并额外核对 tag 精确指向 `HEAD`。

## 安装授权 Gate

- Marketplace 注册、安装、refresh、removal/reinstall 需要 Human 明确授权；实施批准不隐含外部状态授权。
- 使用 `read_marketplace_name.py` 从 `.agents/plugins/marketplace.json` 读取 marketplace 名称；不得根据目录名猜测。
- 授权后按目标 Adapter 执行并验证 marketplace/plugin list；Scope、版本、目标、branch/remote 未变化时不重复询问。
- manifest 使用批准的精确 semantic version，不加 cachebuster；不得编辑 cache、应用权限或系统 PATH。
