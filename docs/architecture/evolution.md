# Sacha Orchestra 演进路线图

> 当前 release：`0.9.0` 双协作界面适配与中文合同表达统一
> 当前 source candidate：未开始
> 当前主线：`0.9.0` 发布边界稳定；Codex Adapter 按当前工具面自适应 v1/v2 协作界面，Core、Adapter、Skill 与开发控制文档使用同一中文表达规则
> 发布边界：`0.9.0` 保持既有三个生产 Role、Gate、Artifact、Owner 与通用生命周期不变；Codex Adapter 分离 Runtime 路由与 v1/v2 传输编码，Claude Code Adapter 沿用同一内容归属和表达规则；不新增 Role、Gate、Artifact、Registry、Hook、MCP 或外部授权
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
| `0.9.0` release | 保持 `PLUGIN_DESIGN.md` 定义的产品面与三个生产 Role；Codex Adapter 根据当前会话参数结构唯一选择 v1/v2 协作界面并使用各自传输参数，Core/Skill 不复制 Runtime 映射；Core、Adapter、Skill 与开发控制文档的普通流程叙述统一使用中文 | 附注 tag 表示已发布源码；安装/缓存、新任务发现与 Runtime 证据分别判断；v1 已有当前会话冒烟验证，v2 复用未失效的既有 Runtime 验证 |

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

## 4. 当前 release：`0.9.0`

批准 Scope：Human 本轮明确要求迭代 Codex/Claude Adapter、统一 AGENTS/Core/Skill 表达，并授权发版、提交、push 与安装。

### 4.1 Codex v1/v2 协作界面

- Adapter 只依据当前会话实际暴露的命名空间、工具集和参数结构选择 v1 或 v2；模型目录、配置和父会话先例不能替代工具面证据。
- Runtime 路由先产生唯一 `route_id`，再按已选协作界面组装 `spawn_agent` 参数；v1 使用 `fork_context` 与 `send_input/wait_agent/close_agent`，v2 使用 `fork_turns` 与 `send_message/followup_task/wait_agent/interrupt_agent/list_agents`，两套字段不得混用。
- Luna 主路由尚未建立 Owner 时，可按当前协作界面的唯一映射回退到 Sol medium；精确 Human 路由、已启动实例、超时、结果失败或用户取消不自动回退。

### 4.2 内容归属与表达

- 插件内 Core、Adapter、Skill 与开发控制文档的普通流程叙述使用中文；产品、Role、Skill、Runtime、API、字段、枚举、状态、模型和已定义硬术语保留原标识。
- 六份 Core 合同与十份 Skill 只调整表达，不改变 Contract Version、触发条件、Role 职责、Gate、Owner、Outcome 或根终态；直接失配的 Skill metadata 同步更新。
- Claude Code Adapter 保持原传输和模型映射，只按同一规则清理普通英文流程叙述。

### 4.3 发布证据边界

- 当前 Codex 会话已验证 v1 的 Luna xhigh 创建、等待、结果消费和关闭；v2 的既有创建、消息、继续、等待、取消与标识查询语义未改变，本次只调整归属位置和中文表达，复用此前未失效的 Runtime 验证，不重复执行。
- 源码/静态、附注 tag、安装/缓存、新任务发现与真实 Runtime 行为分别判断；任一层不得替代另一层。

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
