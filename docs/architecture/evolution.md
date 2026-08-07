# Sacha Orchestra 演进路线图

> 当前 release：`0.8.1` Flow-first design and Runtime owner convergence
> 当前 source candidate：未开始
> 当前主线：`0.8.1` 发布边界稳定，下一 candidate 尚未启动
> 发布边界：`0.8.1` 把完整流程骨架与 Role/Skill 职责抽离到仓库根 `PLUGIN_DESIGN.md` 开发控制面，且不随插件发布；Workflow/Core/Skill 自包含 Runtime 局部语义；主工作流直接入口收敛为三个生产 Role 与 Clarify，Manager/document-project 只接受内部路由；Feedback 由 Human 在另一真实任务显式调用，可提交具体流程问题、使用反馈或插件开发想法，调用即授权单向 owner transfer，目标任务回到普通流程；wait 收敛为有结果消费者的依赖屏障；不新增 Role、Gate、Artifact、Registry、Hook、MCP 或外部授权
> 本文只定义当前方向、版本和 breaking boundary，不授权实施、安装或发布

## 1. 权威边界

| 内容 | 权威来源 |
| --- | --- |
| 当前 release/source candidate、长期架构与 breaking boundary | 本文 |
| 顶层流程、产品入口、Role/Skill 职责与变更顺序 | 根目录 `PLUGIN_DESIGN.md`（开发控制面，不随插件发布） |
| Runtime Role、Gate 与节点/连线条件 | `plugins/sacha-orchestra/core/workflow-contract.md` |
| Human 可见提问、进度、结果顺序与必须披露的信息 | `plugins/sacha-orchestra/core/human-interaction-contract.md` |
| Review、Baseline、Outcome | `plugins/sacha-orchestra/core/assurance-contract.md` |
| Manager、dispatch、wait/return、identity/deviation | `plugins/sacha-orchestra/core/coordination-contract.md` |
| Artifact、Handoff 必要语义与扩展边界 | `plugins/sacha-orchestra/core/artifact-protocol.md` |
| 单 Runtime transport、模型与恢复映射 | `plugins/sacha-orchestra/adapters/<runtime>/runtime-adapter.md` |
| 当前任务批准 Scope | Human 明确目标或适用 Spec |
| 项目命令、领域证据与局部约束 | Project AGENTS / Domain Skill |

当前机制只由上述 owner 定义。已结束 release 的过程、验证数字和历史实现保留在 Git 与对应 Spec、Execution Report、Review，不在本文建立版本流水账；需要历史事实时按具名版本或文档查询，不从本文恢复旧操作规则。

## 2. 当前版本线

| 版本线 | 当前事实 | 证据边界 |
| --- | --- | --- |
| `0.8.1` release | 根目录 `PLUGIN_DESIGN.md` 先行定义顶层流程与职责；主工作流仅三个生产 Role 与 Clarify 可显式调用；Manager/document-project 由内部 owner 路由；Feedback 由 Human 在另一真实任务显式启动，可提交流程问题、使用反馈或开发想法并单向交付唯一目标任务；目标任务随后按普通任务处理；delegation 只在依赖屏障等待 | annotated tag 表示已发布源码；安装/cache/fresh discovery/Runtime 证据分别判断 |

两个 deployment manifest 表示当前源码版本，Git annotated tag 表示已发布版本，Core/Adapter 的 Contract Version 只表示 schema。README 只链接当前入口，不复制版本状态。

## 3. 长期架构边界

1. 生产 Role 只有 Planner、Executor、Reviewer；Manager 是控制面，不是第四个生产 Role。
2. `using-sacha` 是唯一默认入口；Planner、Executor、Reviewer 是高级直接入口，Clarify 只有显式窄授权；Manager 与 document-project 只接受图中的内部路由。Feedback 由 Human 在另一真实任务显式调用；调用授权来源任务调查与 owner transfer，目标任务的写入、安装、Git、发布或外部动作另行授权。
3. 普通清晰任务保持 Direct；复杂、耗时、多文件、多平台或想增加 Agent 本身不打开 Gate。
4. 根目录 `PLUGIN_DESIGN.md` 拥有完整顶层流程与 Role/Skill 职责，只供开发/评审且不随插件发布；Workflow 自包含唯一 Runtime 路由；Human Interaction 拥有 Human 可见交互规则；Coordination 拥有拆分、依赖、readiness、dispatch/wait/return 与 owner transfer；Adapter 只映射 Runtime；Skill 只实现已声明职责或主流程外功能，Runtime 不读取顶层设计。
5. 同一文件或共享可变输出只有一个活跃写入者；隔离候选由 integration owner 串行应用。
6. Spec 是批准 Scope 的持久权威；Artifact 按真实持久化/交接消费者渐进生成，简单任务不制造文档。
7. 原始文件、Diff、运行状态和命令输出决定事实；source/static、安装/cache、fresh discovery 与真实 Runtime 证据不得互相替代。
8. 不预建 Runtime Registry、数据库、后台服务、第四 Role、自动授权或跨项目特例；真实失败出现后再收紧现有 owner。
9. 所有任务优先复用同一通用 lifecycle；通过关闭无依据 Gate 与跳过无候选节点加速。新增特殊流程、专属 target 限制或隐藏旁路必须有通用流程无法覆盖的真实失败，并由 Human 明确批准后先改 `PLUGIN_DESIGN.md`。

改变生产 Role、Gate、Handoff 必要语义、权威边界、外部授权或跨 Runtime contract 属于 Core breaking change，必须以批准 Spec 冻结决定并保留独立 Review。版本号、文案或内部 schema 单独变化不自动构成 breaking。

## 4. 当前 release：`0.8.1`

批准 Scope：[`Flow-first 与 Skill 职责边界 Spec`](../plan/2026-08-07-flow-first-skill-boundaries/spec.md)；[`Feedback 单向 owner transfer Spec`](../plan/2026-08-07-feedback-owner-transfer/spec.md)。

### 4.1 Flow-first 与 Skill 职责

- `PLUGIN_DESIGN.md` 先定义 Direct、Planner/Clarify/Human、Executor、Reviewer、Documentation、Feedback、Manager 协调闭环及 Role/Skill 职责；改变顶层设计先改该文件，再改 Runtime owner 与直接消费者。
- 主工作流的显式 surface 只保留 Planner、Executor、Reviewer 与 Clarify；Manager 由调用 owner 的 Gate 调用，document-project 由收尾候选路由。Feedback 是另一真实任务中由 Human 手动调用的独立支持入口，可承接流程问题、使用反馈或插件开发想法。
- Workflow Contract 19 定义图中 Role/Gate 和节点/连线条件；Human Interaction Contract 1 定义跨节点 Human 可见交互；Assurance、Coordination 与 Intake 分别实现自己的分支。
- Planner、Executor、Reviewer 明确职责、输入输出和禁止边界；支持/控制 Skill 映射图中节点，setup 等具体 Skill 在主流程外声明独立功能和副作用。
- 删除以产品 Markdown 为被测对象的正则、marker、句子存在性和段落顺序测试；release coherence 只核对机器可解析部署身份、生产入口、配置与 Git release identity。

### 4.2 Feedback 独立入口与 owner transfer

- Feedback 的输入是具体流程问题、使用反馈、插件开发建议或能力想法；Human 可提供原任务、项目或 evidence reference。
- 完整反馈身份由反馈 workspace、具体 objective、owner，以及 Human 已提供时的来源 reference 组成。
- 来源任务只复用身份精确匹配且仍 active/resumable 的唯一目标任务；无可复用匹配时在 Human 本次显式 Feedback 调用的授权内创建恰好一个目标任务，不再追加创建确认。
- 已 terminal 的同一反馈身份精确重复只返回既有 reference 并记为 `no_op`；其他 terminal/stale 候选不算匹配，无法消歧时停止。
- 来源任务交付原生目标任务 reference 后结束，不 join、不等待 terminal、不转述目标任务最终结果，也不取得目标任务写入权。
- 目标任务按 Intake Contract 作为普通任务重新判断，并使用通用的 Planner、Review、协调、验证和收尾规则。

### 4.3 Productive wait

- 派发不自动触发 wait。当前 owner 先重算依赖图并推进所有不依赖未完成结果、且不与活跃工作冲突的 ready 单元。
- 只有目标已启动、当前 owner 是 result consumer、下一 transition 依赖结果且没有其他 ready 工作时，才进入依赖屏障并等待。
- timeout 只接受新的 liveness 证据；不 busy polling、不重复读取相同进度、不因 timeout 重建 target。
- 安装后 fresh 验证只有在 Human 已授权安装与 fresh Runtime 验证时才由目标任务派发；目标任务完成其他已就绪工作后在验收依赖屏障消费结果，否则明确标记未验证。

### 4.4 Release 证据边界

- Core、Skill、Adapter 与 Runtime owner 导航按本 release 边界对齐；流程行为由任务包 scenario 验证，Markdown validator 不替代 Runtime 证据。
- annotated tag 只证明已发布源码；安装/cache/fresh discovery 与当前 Runtime 行为使用各自直接证据。

## 5. `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的 candidate line。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。

## 6. 变更方式

- 长期架构、`1.0.0`、生产 Role/Gate、Manager/并行或 Core breaking 的具体改动需要 Human 明确确认；需要冻结实质方案、Scope 或迁移时使用 Planner Spec。
- 普通 plugin change/fix/iterate 保持 Direct；同目标漏改与验证失败在原 Scope 修复。
- 顶层流程或 Role/Skill 职责变化先更新根目录 `PLUGIN_DESIGN.md`，再改 Core、Skill/Adapter 消费者和本文 breaking boundary；局部细节不改变顶层设计时不改该文件。
- Evolution 只更新当前 release/candidate、当前 breaking boundary 与仍有效的长期决策；结束过程不回填为版本章节或累计验证表。
- 安装、外部项目写入、commit、push、tag 与发布需要 Human 对具名动作明确授权。
- 路线图只在当前主线完成、Runtime 能力实质变化、开始 `1.0.0`、启动第二 Runtime/项目或提出 Core breaking change 时复审。
