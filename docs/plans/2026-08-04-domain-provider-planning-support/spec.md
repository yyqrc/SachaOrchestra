# Domain Provider 规划支持与接入指南迭代

> 状态：Human 已批准；Sacha Guide、canonical Skill 合同核查、术语 owner/冲突、Clarify 压力输入与 Guide 消费说明的本仓实施和静态验证已完成（2026-08-04）；真实任务输出和跨仓 Provider 实施仍需各仓独立授权
>
> 更新时间：2026-08-04
>
> 关联主 Spec：[`../2026-08-04-planner-alignment-executable-spec/spec.md`](../2026-08-04-planner-alignment-executable-spec/spec.md)
>
> 权威：本文件只冻结 Domain Provider 为 Planner/Clarify 提供领域事实和可执行规划输入的候选改造；不授权修改 provider 仓库、Sacha Core、安装状态、Git 或发布面。

## 1. 目标

让 cgame-unity、cgame-engine 及其他 Domain Provider 能为复杂任务提供足够具体的领域规划输入，使 Sacha Planner 不必凭通用知识重新推断 Unity、Engine、UE 等工程的 owner、数据边界、生命周期、平台约束和验证方式。

Provider 只负责“具体需要对齐什么”，Sacha 仍负责：

- 是否需要 Planner、Clarify、Human Review、Executor、Reviewer 或 Manager。
- 澄清决策记录、Spec storage、Scope、Non-goals、批准 revision 与执行许可。
- 外部动作授权、最终路由和 verdict。

## 2. 当前缺口

当前 [`capability-provider-guide.md`](../../integrations/capability-provider-guide.md) 已规定：

- Provider catalog、canonical Skill 与 Setup/Binding 的责任边界。
- Role 读取 confirmed Binding 和 canonical Skill。
- Provider 返回领域结果与 evidence locator，最终路由和 verdict 归 Sacha。

但 guide 尚未告诉 Provider：当 Planner 需要形成可执行 Spec 时，领域结果应具体到什么程度，也没有明确要求返回：

- 当前实现、owner、稳定 locator 与直接调用/数据链。
- 会改变方案的生命周期、数据/资产、序列化、线程、ABI、平台和兼容约束。
- 真正可行的候选方案、代价、推荐理由与无法由工程事实推出的 Human 选择。
- Executor 不需重新设计所需的实施地图。
- A/B/C 验收路线、Entry Condition、原始证据和领域停止条件。

结果是 Provider 虽然合规地返回了“领域结果”，Planner 仍可能只产出合同完整但实施宽泛的 Spec。

### 2.1 已核对的直接消费者

本轮实际读取了已安装的 cgame-unity `0.5.8` 与 cgame-engine `0.5.7` 中 `project-inspect`、`code-discovery`、`solution-comparison`、`change-guard`、`runtime-verify` 的 canonical `SKILL.md`。两者已经分别覆盖工程地图、owner/调用或数据链、方案比较、实施约束、最窄验证及人工检查步骤；因此当前没有依据新增 `planning` capability 或固定 Provider 输出协议。

仍缺的是一次真实复杂任务输出证据，用来确认这些能力组合后能否稳定给 Planner 提供实施地图与 A/B/C 输入。该缺口留给各 Provider 后续独立任务，不由本轮修改 cache 或 Provider 源码来伪造完成。

## 3. Scope

### 3.1 Sacha 仓库

- 迭代 `docs/integrations/capability-provider-guide.md` 的责任边界、Role 消费和 Provider 迭代章节。
- Guide 必须明确说明 Provider 如何按需提供现有领域术语 owner/locator、当前定义、冲突证据和领域压力场景，以及 Clarify 如何消费；不能只把这些内容留在本 Spec。
- 按需要补充 guide 的最小示例，但不新增固定输出 schema、catalog 字段或 Runtime 协议。
- 核对 `setup-project`、Planner/Clarify、Artifact、Adapter 与 validator 是否只是引用该边界；没有直接语义错误时不联动修改。

### 3.2 Domain Provider 仓库

Provider 维护者依据更新后的 guide，逐个核对已有 canonical Skill：

- 优先迭代已有的项目调查、代码定位、方案比较、修改前约束调查、构建/运行验证能力。
- 只有现有能力无法表达独立、可复用的领域目标，且至少有真实消费者时，才考虑新增 capability。
- Provider 自身的修改、验证、发布和 Binding refresh 由各 provider 仓库单独规划和授权；本 Spec 不直接修改它们。

## 4. Non-goals

- 不让 Provider 决定 Sacha Gate、Role、生命周期、Human Review、Spec 批准或 Executor 启动。
- 不让 Provider 写入或冻结 Sacha 的澄清决策文件、`spec.md`、Execution Report 或 Review Artifact。
- 不创建 `cgame-unity-workflow`、`cgame-engine-workflow` 或 Provider 内第二套 Planner/Executor/Reviewer。
- 不要求每个 Provider 新增 `plan`、`brainstorm`、`alignment` 或 `spec-review` capability。
- 不给 `capabilities.json` 增加输出格式、Human 决策、验证矩阵或 Spec locator 字段。
- 不规定固定字段表、固定方案数量或所有调用都返回完整实施地图；输出按当前消费者和风险自适应。
- 不把项目命令、Unity/Engine 特有知识或具体模型写进 Sacha Core。
- 不安装、refresh Binding、修改 cache、commit、push 或发布。

## 5. 冻结决定

### 5.1 Provider 给 Planner 的领域输入

当调用目的是形成或修订可执行 Spec，Provider 应按任务需要返回以下语义；没有消费者的项省略：

- `当前事实与定位`：真实 owner、入口、调用/数据链、资源或配置位置、当前行为和证据 locator。
- `领域约束`：生命周期、线程、坐标空间、数据/资产、序列化、ABI、平台、构建、兼容、性能和回退边界中会改变方案的部分。
- `候选与推荐`：只比较会产生不同实现或结果的可行方案，说明主要代价、推荐理由和已排除条件。
- `Human 选择`：仅列无法从工程事实推出、且会改变用户可见行为、架构、数据、迁移、兼容或验收的决定。
- `实施地图`：目标位置、预期变化、必须保持的不变量、脆弱顺序、直接先例、最窄检查和返回规划的领域触发条件。
- `验证路线`：AI 可直接验证、Human 准备后 AI 验证、Human 判断三类路线所需的 Entry Condition、预期证据与领域风险。
- `Unknown`：无法由当前证据确认的内容、影响和下一条最窄探针；不得把推测写成确定步骤。
- `术语与压力输入`：按消费者需要指出领域术语的当前定义、代码/文档冲突、真实用例，以及可能改变方案的极值、生命周期、迁移或跨版本压力场景；没有相关风险时省略。

这些名称是 guide 中的解释性语义，不是强制 JSON、表格或 Packet schema。

### 5.2 实施密度

Provider 输出只冻结会改变结果的领域事实：

> 实施结果对顺序、Owner、数据边界和领域约束越敏感，Provider 给 Planner 的实施输入越应接近可直接执行；当剩余选择只影响局部代码表达、不再改变行为、边界、风险或验收时停止继续细化。

简单、唯一既有路径或低风险局部修改可只返回 owner、直接入口、约束和验证；渲染阶段、资源状态、资产迁移、序列化、跨平台或脆弱生命周期应提供更完整的实施地图。

### 5.3 Human 决策与决策记录

- Provider 只能指出未决 Human 选择并给推荐/取舍，不能替 Human 决定。
- Provider 可以给出领域术语事实和项目既有术语 owner/locator，但不创建或拥有项目词典，不决定 Clarify 是否完成。
- Provider 没有既有术语 owner 时明确返回“无”，不得自行选择项目 `CONTEXT.md` 路径或写入；默认 locator、提升和写入授权仍归 Sacha Project Integration/Documentation owner。
- Planner/Human 确认后，由 Sacha owner 把决定尽快写入项目约定的澄清决策文件；Provider 不拥有该文件。
- Provider 返回的事实或建议不会因为被写入决策文件而取得执行授权。
- 形成 `spec.md` 时由 Planner 消费当前决定和 evidence locator；Provider 不直接生成 Sacha Spec。

### 5.4 A/B/C 领域验收输入

- A：Provider 给出 AI 可执行的领域检查、入口、预期结果和原始证据。
- B：Provider 写清 Human 最小准备、AI 如何确认 Entry Condition、随后执行的检查和证据；Human 不替 AI 判断 pass/fail。
- C：Provider 给出场景、设备、操作步骤、观察时长、预期/禁止现象、证据记录和是否可能阻塞；最终 Human 状态和 verdict 仍归 Sacha Assurance。

Provider 不得用静态检查替代设备/画面事实，也不得把本可自动完成的检查推给 Human。

### 5.5 Provider 与 Sacha 的返回边界

- Provider 返回领域结果、风险和 evidence locator；Sacha Planner 决定是否形成 Human Review proposal。
- Provider 仍只返回领域事实、候选方案、约束、验收输入及本次调用发现的 Human 待选项；跨问题的“最终建议与待决定事项”收口归 Sacha Workflow/Role，Provider 不拥有该通用语义，也不新增输出协议。
- Provider 提供的术语冲突和压力场景只是既有领域结果的一部分，不新增 `glossary`、`grill` 或 challenge-frontier 字段/schema。
- Capability Provider Guide 必须把上述能力写入 Role 消费与 Provider 迭代说明：优先迭代已有 code-discovery、project-inspect、solution-comparison、change-guard 等 canonical Skill 的自然语言结果；只有真实独立能力缺口和消费者成立时才新增 capability。
- Provider 发现需要新方案、Scope 或授权时返回事实，不自行改 Gate、Scope 或启动新任务。
- Reviewer 可以调用 Provider 补领域证据，但 Provider 不取得 Reviewer provenance 或 verdict。
- Provider 结果与真实代码、配置、产物或 Runtime 冲突时，以原始事实为准。

## 6. 实施步骤

### 步骤 1：迭代 Capability Provider Guide

- 目标位置/定位：`docs/integrations/capability-provider-guide.md` 的“责任边界”“Role 消费”“Provider 迭代”。
- 预期改动：补入第 5 节的领域规划输入、Human 决策、实施密度、A/B/C 和返回边界；明确 Provider 按需返回领域术语 owner/locator、定义冲突和领域压力场景，Clarify 负责 Human 对齐、项目 context 提升与退出；保持现有 Schema v2 与 Binding 格式不变。
- 约束与不变量：guide 是 provider 维护指南，不是 Runtime 强制加载面；不把解释性语义变成 catalog/schema 字段。
- 检查与证据：全文 owner/链接检查；确认 Sacha 与 Provider 的批准、Spec、verdict 权限没有交叉。
- 返回规划的触发条件：必须改变 capability catalog schema、Binding schema 或 Project Integration 才能表达该能力。

### 步骤 2：选择两个真实 Provider 做消费验证

- 目标位置/定位：优先 cgame-unity 与 cgame-engine 当前已存在的调查、方案比较和验证 Skills。
- 预期改动：只读评估现有输出能否覆盖第 5.1 节；形成每个 Provider 的最小迭代清单，不直接修改 provider 源码。
- 约束与不变量：不能因目录名或 capability id 推断能力；必须读取 canonical Skill 正文和真实任务输出。
- 检查与证据：至少一个 Unity/资源或生命周期任务，以及一个 Engine/渲染或 C++ owner 任务，证明 guide 能让 Planner 得到可执行输入而不转移 Sacha 权限。
- 返回规划的触发条件：现有 capability 无法承载且需要新增公开能力或跨仓库发布。

### 步骤 3：分别迭代 Provider

- 目标位置/定位：由每个 Provider 自己的项目规则、canonical Skill owner 和独立 Spec 决定。
- 预期改动：优先压实已有 Skill 的领域输出、证据和停止边界；只在真实能力缺口成立时新增 capability。
- 依赖与顺序：先接受本 Spec 和 guide 变更，再在 provider 仓库独立规划、实施、验证和发布；最后按授权执行 consumer Setup dry-run/Binding refresh。
- 检查与证据：provider schema、Skill/plugin validation、真实任务输出与消费项目 Planner 结果分层报告。
- 返回规划的触发条件：Provider 改动要求 Sacha 新 Role/Gate/Artifact，或需要改变 catalog/Binding schema。

### 步骤 4：用真实 Planner Spec 验证闭环

- 目标位置/定位：选择一项会受 owner、数据边界、领域约束和验证环境影响的真实任务。
- 预期改动：Planner 消费 Provider 结果，先记录已确认决策，再形成待 Human Review 的 `spec.md`；Provider 不写 Artifact。
- 检查与证据：Human 能看懂改什么和为何这样改；fresh Executor 不需重新做领域设计；Spec 没有逐行代写代码。
- 返回规划的触发条件：Planner 仍需重复调查 Provider 已声称提供的 owner、约束或验证事实。

## 7. 验收

### A 类：源码与场景验证

- [x] Guide 明确 Provider 可返回的领域规划输入，但没有新增固定 schema、Role、Gate 或 Artifact。
- [x] Guide 明确 Provider 不批准、不冻结 Spec、不启动 Executor、不拥有 verdict。
- [x] cgame-unity 与 cgame-engine 的 canonical Skill 合同已完成差距评估；真实任务输出仍需各 Provider 独立验证。
- [ ] 简单任务输出保持简短；领域敏感任务能提供可直接消费的实施地图。
- [x] A/B/C 输入能被 Planner/Reviewer 消费，Outcome 仍由 Assurance Contract 决定。
- [x] Provider 可按需返回领域术语冲突与极值/生命周期/迁移/跨版本压力场景，但没有新增固定字段、项目词典 owner 或 Clarify 生命周期责任。
- [x] Capability Provider Guide 的 Role 消费与 Provider 迭代章节已经实际包含术语 owner/定义/冲突、领域压力输入、无 owner 返回及 Sacha/Provider 边界；只更新本 Spec 或测试 fixture 不算完成。
- [x] guide、受影响文档链接、相关 validator 和 `git diff --check` 结果已读取并报告。

### B 类：跨仓 Provider 实施与消费环境

- [ ] Human 分别授权目标 Provider 仓库的 Spec、修改和验证。
- [ ] 需要刷新 Binding 时，Human 确认目标项目、provider 版本、load policy 和 planned delta。
- [ ] Runtime discovery 与真实任务输出在安装/refresh 后单独验证；不能由 source guide 或 Skill 文本推断。

### C 类：Human 产品判断

- [ ] Human 确认 Provider 输出使复杂 Unity/Engine Spec 更可读、可执行，同时没有复制一套 Sacha Workflow。
- [ ] Human 确认信息量按领域风险自适应，没有强制所有 Provider 返回长表格。

## 8. 明确拒绝

- Provider Brainstormer、Planner、Alignment、Spec Reviewer 或 Executor Role。
- Provider 自行创建、批准或冻结 Sacha 决策记录和 Spec。
- 新的 planning capability taxonomy、固定输出 Packet 或 catalog 字段扩张。
- Provider-owned 项目术语表、固定 Glossary 输出协议、完整决策树或每次调用必填的极值/跨版本问卷。
- 每个 Provider/任务强制候选方案数量、固定章节或完整实施手册。
- 仅为让测试通过而复制 Unity/Engine 项目知识到 Sacha Core。
- 把 Provider 自报、文档或模板当作安装、Runtime 或真实任务证据。
- 未经各仓库授权自动修改、发布 Provider 或 refresh 消费项目 Binding。

## 9. 开工条件

- Human 接受本 Spec，或异议已回写并重新冻结。
- 主 Spec 对决策记录、Human Review、A/B/C 和 Sacha/Provider owner 的语义已经确认。
- 本轮首先只修改 Sacha guide 与必要的本仓直接消费者；Provider 源码、安装、Binding、Git 和发布均需各自授权。
