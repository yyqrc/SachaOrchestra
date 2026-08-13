# Sacha Orchestra 演进路线图

> 当前 release：`0.11.6` 统一候选类术语并保留机器接口
> 当前待发布源码版本：未开始
> 当前主线：主任务独占 Manager 并执行单层派发；Human 审阅 Spec 时明确区分普通批准、明确迁移批准与要求调整，Feedback 保持独立 Owner 转移
> 发布边界：`0.11.6` 不新增 Role、Gate、Artifact、Registry、Hook、MCP 或外部授权；只统一 Human 可读候选类术语、合同版本映射和脚本诊断，机器接口与 Runtime 路由不变
> 本文只定义当前方向、版本和 breaking boundary，不授权实施、安装或发布

## 1. 权威边界

| 内容 | 权威来源 |
| --- | --- |
| 当前 release、当前待发布源码版本、长期架构与 breaking boundary | 本文 |
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
| `0.11.6` release | 统一入口、发布和知识沉淀中的候选类术语，保留 `candidate` 机器接口与冻结历史 | 附注 tag 表示已发布源码；独立 Review、项目测试、Skill/Plugin validator、Pi 脚本与 metadata coherence 只证明 source/static 和脚本行为，未执行安装与 Runtime 验收 |

三个 deployment manifest 表示当前源码版本，Git annotated tag 表示已发布版本，Core/Adapter 的 Contract Version 只表示 schema。README 只链接当前入口，不复制版本状态。

## 3. 长期架构边界

1. 生产 Role 只有 Planner、Executor、Reviewer；Manager 是控制面，不是第四个生产 Role。
2. `using-sacha` 是唯一默认入口；Planner、Executor、Reviewer 是高级直接入口，Clarify 只有显式窄授权；Manager 与 document-project 只接受图中的内部路由。Feedback 由 Human 在另一真实任务显式调用；调用授权来源任务调查与 owner transfer，目标任务的写入、安装、Git、发布或外部动作另行授权。
3. 普通清晰任务保持 Direct；复杂、耗时、多文件、多平台或想增加 Agent 本身不打开 Gate。
4. 根目录 `PLUGIN_DESIGN.md` 拥有完整顶层流程与 Role/Skill 职责，只供开发/评审且不随插件发布；Workflow 自包含唯一 Runtime 路由；Human Interaction 拥有 Human 可见交互规则；Coordination 拥有拆分、依赖、readiness、dispatch/wait/return 与 owner transfer；Adapter 只映射 Runtime；Skill 只实现已声明职责或主流程外功能，Runtime 不读取顶层设计。
5. 主任务独占 Manager 并执行单层派发；委派 Agent 需要继续拆分或协调时返回协调请求。迁移后派发权随工作流 Owner 转移。
6. 同一文件或共享可变输出只有一个活跃写入者；隔离候选由 integration owner 串行应用。
7. Spec 是批准 Scope 的持久权威；Artifact 按真实持久化/交接消费者渐进生成，简单任务不制造文档。
8. 原始文件、Diff、运行状态和命令输出决定事实；source/static、安装/cache、fresh discovery 与真实 Runtime 证据不得互相替代。
9. 不预建 Runtime Registry、数据库、后台服务、第四 Role、自动授权或跨项目特例；真实失败出现后再收紧现有 owner。
10. 所有任务优先复用同一通用 lifecycle；通过关闭无依据 Gate 与跳过无候选节点加速。新增特殊流程、专属 target 限制或隐藏旁路必须有通用流程无法覆盖的真实失败，并由 Human 明确批准后先改 `PLUGIN_DESIGN.md`。

改变生产 Role、Gate、Handoff 必要语义、单层派发、权威边界、外部授权或跨 Runtime contract 属于 Core breaking change，必须以批准 Spec 冻结决定并保留独立 Review。版本号、文案或内部 schema 单独变化不自动构成 breaking。

## 4. 当前 release：`0.11.6`

实现 Scope：统一 Human 可读流程中的入口候选、当前待发布源码版本和领域/参考知识候选；同步术语与 Intake 合同版本映射并汉化相关脚本诊断。`--candidate-path`、`--phase candidate`、JSON 字段/状态、代码标识、Runtime 模型路由和 Manager 规则保持不变。

### 4.1 术语与机器接口

- 入口判断统一使用“入口候选”；发布流程使用“当前待发布源码版本”和“精确暂存发布内容”；知识沉淀使用“领域/参考知识候选”或“备选项”。
- `--candidate-path`、`--phase candidate`、JSON 字段/状态、代码标识与冻结历史保持不变；Runtime 模型路由和 Manager 规则不变。

### 4.2 发布证据边界

- 三个 deployment manifest、项目测试、Plugin validator 与待发布/发布阶段一致性检查构成 source/static 证据；附注 tag 与远端指向构成 Git 发布身份。
- Codex 安装、列表和源码/cache 一致性只证明本机安装版本；选项展示、Skill 触发、迁移、Owner 转移和恢复仍沿用 `0.11.4` 的独立 Runtime 证据边界。

## 5. `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。

## 6. 变更方式

- 长期架构、`1.0.0`、生产 Role/Gate、Manager/并行或 Core breaking 的具体改动需要 Human 明确确认；需要冻结实质方案、Scope 或迁移时使用 Planner Spec。
- 普通 plugin change/fix/iterate 保持 Direct；同目标漏改与验证失败在原 Scope 修复。
- 顶层流程或 Role/Skill 职责变化先更新根目录 `PLUGIN_DESIGN.md`，再改 Core、Skill/Adapter 消费者和本文 breaking boundary；局部细节不改变顶层设计时不改该文件。
- Evolution 只更新当前 release、当前待发布源码版本、当前 breaking boundary 与仍有效的长期决策；结束过程不回填为版本章节或累计验证表。
- 安装、外部项目写入、commit、push、tag 与发布需要 Human 对具名动作明确授权。
- 路线图只在当前主线完成、Runtime 能力实质变化、开始 `1.0.0`、启动第二 Runtime/项目或提出 Core breaking change 时复审。
