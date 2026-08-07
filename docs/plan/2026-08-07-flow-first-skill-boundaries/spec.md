# Flow-first 与 Skill 职责边界 Spec

> 状态：Human 已批准实施
> 日期：2026-08-07

## 目标

停止用 Markdown 语句测试维持合同，把完整流程骨架与 Role/Skill 职责抽离到仓库根 `PLUGIN_DESIGN.md` 开发控制面；Runtime Core/Skill 只实现自己的局部 owner，使后续迭代自上而下，不再逐文件打补丁。

## Scope

- 删除读取 README、Core、Adapter 或 Skill 后做正则、marker、整句存在/缺失和段落顺序断言的测试。
- release coherence 只核对机器可解析部署身份、生产入口、可解析配置与 Git release identity。
- 先校对 `PLUGIN_DESIGN.md`，再使 Workflow、Intake、Assurance、Coordination、Role/支持 Skill 与直接 Adapter 映射一致。
- Planner、Executor、Reviewer 明确职责、工作流和边界；其他 Skill 明确功能、概略工作流和副作用边界。
- 由上述流程和职责重新整理 AGENTS 产品边界，不为现状硬凑消费者表或 validator 规则。

## Non-goals

- 不改变 Runtime transport、模型选择、安装状态或外部授权。
- 不新增 Role、Gate、Artifact、Hook、Registry、MCP、app 或外部服务。
- 不用静态 source test 声明 Runtime 路由已经验证。

## 决定

1. 根目录 `PLUGIN_DESIGN.md` 拥有完整流程节点、先后关系、分支、回路与 Role/Skill 职责；它与 `AGENTS.md` 并列、只供插件开发/评审且不随插件发布。改变顶层设计先改该文件，再改 Runtime Core/Skill 和消费者。
2. Runtime 节点条件与语义仍由对应 Core owner 自包含定义；顶层设计未变时不为同步而修改 `PLUGIN_DESIGN.md`。
3. Role Skill 只在已声明输入、输出和禁止边界内演进；新增职责、输出 owner 或跨节点路线先按流程变化处理。
4. 支持/控制 Skill 映射图中节点或闭环；setup 等具体 Skill 在主流程外声明独立功能、工作流和副作用。
5. 测试调用真实生产入口并检查行为或机器状态；Markdown 语义由 owner review 与真实 scenario/runtime 证据负责。
6. Human 于 2026-08-07 补充确认：主 workflow 的显式 surface 只保留 Planner、Executor、Reviewer 三个生产 Role 与 Clarify。Manager 只能由调用 owner 的 Gate 调用，document-project 只能由收尾候选路由；Feedback 是 Human 在另一个真实任务手动调用的独立支持入口，可承接流程问题、使用反馈或插件开发想法，调用本身即来源任务调查与 owner transfer 授权。setup 仍是主流程外显式配置能力。
7. Role/流程验证改用独立 task package：执行 Agent 不读取 oracle，真实完成隔离 workspace 任务；未参与实施的 evaluator 再对照 oracle、原生派发/return、workspace delta 和 verifier 输出裁决。静态 Markdown 测试不再充当流程行为证据。
8. Human 于 2026-08-07 补充确认：默认用同一通用 lifecycle 处理所有任务，通过关闭无事实 Gate 和跳过不成立候选缩短路径；不得为提速增加特殊流程。确需特殊节点、旁路或 target 限制时，先说明真实失败、通用流程不足与影响，并取得 Human 明确批准。
9. Human 于 2026-08-07 明确分层，并进一步要求抽离：仓库根 `PLUGIN_DESIGN.md` 与 `AGENTS.md` 并列，只供插件开发/评审，是唯一完整顶层设计，不随插件发布，也不是 Runtime 读取前提；README 只保留使用与导航。Workflow Contract 自包含唯一 Runtime 路由，其他 Core、Skill、Adapter 只携带各自局部语义，不得引用顶层设计或复制完整骨架。scenario 执行者只从入口 Skill/Core 运行，evaluator 才用顶层设计核对偏移。

## Acceptance

- 测试目录不存在以产品 Markdown 为被测对象的静态语义测试，release coherence 不使用正则或读取说明文档。
- `PLUGIN_DESIGN.md` 能完整表示 Direct、Planner/Clarify/Human、Executor、Reviewer、Documentation、Feedback、Manager 协调闭环及 Role/Skill 职责。
- 图和直接消费者不把 Manager 或 document-project 暴露为用户入口；三个生产 Role 与 Clarify 的主 workflow 直接入口仍可达，Feedback 只允许 Human 在另一真实 task 显式调用。
- Core 不新增图外 lifecycle；Runtime Adapter 映射声明与 Workflow schema 一致。
- 三个生产 Role Skill 都有清晰职责；其余 Skill 都能从正文直接看出功能与工作流。
- AGENTS 产品边界从流程和职责推导，明确 flow-first 次序、Skill 变更判定和测试边界。
- 生产脚本行为测试、官方 Skill/Plugin validator、candidate coherence 与有界变更审计通过；Runtime 行为仍明确为未验证。
- 至少提供 `executor-only` 与 `planner-clarify-manager-reviewer` 两个可实际运行的隔离任务包；是否通过只由真实 source-scenario 或 fresh Runtime 执行结果声明。
