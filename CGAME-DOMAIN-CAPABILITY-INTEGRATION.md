# CGame 领域能力接入设计

> 状态：合入设计输入，不是已批准的实施 Spec  
> 目标：供 Sacha Orchestra 后续迭代使用  
> 能力提供方：`cgame-unity`、`cgame-engine`

## 1. 目的

定义 Sacha Orchestra 如何消费外部 CGame 领域能力，同时不把 Unity/C#/C++ 项目知识吸收到 Core，也不创建第二套工作流生命周期。本文档是后续规划和实施的稳定输入，不授权修改 Sacha Core、Adapter、Project Integration、setup 工具或发布状态。

## 2. 当前能力提供方

| 能力 | Unity 提供方 | Engine 提供方 | 提供方负责的结果 |
|---|---|---|---|
| 检查项目事实 | `cgame-unity:project-inspect` | `cgame-engine:project-inspect` | 已验证项目事实、缺口、下一验证入口 |
| 定位 owner/调用链 | `cgame-unity:code-discovery` | `cgame-engine:code-discovery` | 发现、证据锚点、未知项 |
| 约束已授权改动 | `cgame-unity:change-guard` | `cgame-engine:change-guard` | 适用约束与必需验证 |
| 技术 diff 审查 | `cgame-unity:change-review` | `cgame-engine:change-review` | 领域发现与证据缺口 |
| 编译/构建证据 | `cgame-unity:compile-verify` | `cgame-engine:build-verify` | 命令结果、诊断与覆盖缺口 |

这些能力可以独立调用。它们不选择 Workflow Gate，不授予权限，不拥有 Scope，不创建 Goal/Plan/Review/Handoff Artifact，也不作 Sacha 验收裁决。

## 3. 冻结的接入边界

Sacha 继续负责：

- Planner、Executor、Reviewer 路由；
- Workflow Gate 决策；
- Scope、授权与 single-writer 约束；
- Artifact 与 Handoff 权威；
- workflow owner 的推进、返修、补证据与 re-review transition。

领域能力提供方继续负责：

- 条件式 Unity/C#/C++ 技术知识；
- 多工程根规则接入、CGame 默认相对路由与有界源码调查；
- Unity 目标 DLL 元数据/反编译与匹配 revision 源码证据、Editor 有界查询与行为保持、跨工程 `.meta`/GUID 迁移、离线编译或经 M0 身份门槛的 MCP 编译，以及 Engine 根目录 Bee bat 构建；
- 为已授权改动提供实现约束；
- 技术审查发现；
- 编译/构建证据与覆盖缺口。

消费项目的 Project Integration 继续负责绝对源码根、项目到魔改引擎 revision 的关联、项目覆盖规则、目标矩阵、warning 策略、产品宏和项目专属禁令。领域插件可以提供稳定相对目录、排除项、搜索预算、Unity 行为/资产保护与离线/MCP M0 合同，以及 Engine Windows Editor Bee bat 默认值，但不得覆盖项目证据。

不得把 CGame reference、源码索引、构建机设置、插件名或产品常量复制进 `core/`。只有未来批准的 Scope 证明有必要时，Core 才能定义与提供方无关的稳定协作语义。

## 4. Role 消费模型

| Sacha Role | 可选能力调用 | 返回后仍由 Role 负责 |
|---|---|---|
| Planner | `project-inspect`、`code-discovery` | 判断事实是否充分、比较真实方案并冻结 Scope |
| Executor | `project-inspect`、`code-discovery`、`change-guard`、编译/构建验证 | 保持授权与写入 Scope、实施、验证和报告偏离 |
| Reviewer | `project-inspect`、`change-review`、编译/构建验证 | 独立核对证据并作 Sacha 裁决 |
| Manager | 仅在有界 Work Packet 内调用 | 保持 Packet 依赖、报告预算与 single-writer 约束 |

提供方结果只是证据输入，不能替代当前 Role，也不能改变合法的下一 transition。

## 5. 与提供方无关的证据胶囊

未来接入只在传输边界规范化提供方输出。最小胶囊为：

```text
provider: <可用时记录 Skill namespace 与版本>
task_surface: <项目事实 | 调查 | 约束 | 审查 | 验证>
status: <completed | partial | blocked>
facts_or_findings: <新增且有证据的结果>
constraints: <适用实现限制或 None>
validation: <实际执行的命令/检查、退出码、错误、warning>
gaps: <未验证输入与跳过范围>
evidence_locators: <file:line、命令来源、Artifact 路径>
```

胶囊必须保持 delta-first，并保留失败、Scope 相关风险、缺失验证和证据 locator。它不是新的 Artifact、Handoff、Goal、Registry 或授权格式。

## 6. 能力发现与 fallback

未来接入遵循：

1. 优先使用消费项目 Project Integration 声明的能力映射。
2. 把命名 Skill 视为可用前，先确认其在当前 Codex context 中可发现。
3. 任务新增源码、目标或参考工程根时，让提供方在该根上搜索或验证前先完成根规则接入；当前工作区规则不能自动覆盖新根。
4. 只调用当前 Role 和任务表面需要的最窄能力。
5. 提供方不存在时，继续使用适用 Project `AGENTS.md`、仓库证据与原生 Role 行为；不得阻塞原本合法的 Direct 路线。
6. 提供方输出与项目证据冲突时，以项目事实和一手证据为准，并记录冲突。
7. 普通 Role 路由不得主动执行安装、refresh 或 marketplace 变更；这些仍是需要明确授权的外部状态动作。

## 7. 候选合入切片

### I1. Project Integration 能力映射

新增可选的项目自有映射，把领域任务表面关联到 Skill namespace。不使用领域插件的项目可以省略。

验收：

- 现有 Project Integration 无修改仍然有效；
- 提供方缺失不破坏 Direct 执行；
- 精确插件 namespace 保持由项目拥有；
- 提供方调用不授予写入或外部状态权限。

### I2. Role 局部能力路由

Planner、Executor、Reviewer 只在当前任务确实需要领域证据时查询可选能力映射。Role Skill 保持简洁，Codex discovery 行为留在 Adapter 或 Project Integration 层。

验收：

- Planner 把提供方发现当作事实，不当作规划权威；
- Executor 只在授权已经成立后调用 `change-guard`；
- Reviewer 保留最终裁决，不委派验收；
- 不引入统一领域工作流或固定调用序列。

### I3. setup-project 可选生成

只有单独批准 Scope 后才扩展 `setup-project`。生成器可以在 dry-run 探测后提供可选领域能力块，但不得安装插件、猜测 namespace 或覆盖未管理内容。

验收：

- 生成保持幂等且受 marker 边界保护；
- 用户可以选择 Unity、Engine 或不使用提供方；
- 生成内容只含能力映射与 fallback 语义，不复制领域规则；
- 并发变化继续使用当前事务与恢复边界。

### I4. Conformance 测试

增加提供方存在、缺失、部分完成、证据冲突和错误 Role 调用的 fixture。

必需断言：

- Core 保持 project-neutral；
- 提供方缺失时 Executor-only 路线仍可达；
- `change-guard` 不能授权写入；
- `change-review` 不能作 Sacha 裁决；
- 报告预算不得丢失提供方失败和缺口；
- 不把安装 discovery 与源码声明混为一谈。

## 8. 推荐实施顺序

1. 以本文档为设计输入，为 I1、I2 冻结一份批准 Spec。
2. 实现与提供方无关的映射和 Role 路由，不改 setup 工具。
3. 使用安装/未安装提供方的合成 Unity、Engine Project Integration 验证。
4. 每个提供方各运行一个代表性真实消费任务。
5. 独立审查所有权、fallback 与证据保留。
6. 取得运行时证据后，再决定 I3 setup 生成是否值得实施。
7. XLua、运行时日志、CDL、渲染诊断等专用能力继续留在提供方；后续映射可以暴露能力，但不合并规则。

## 9. Non-goals

- 把 CGame 领域规则合入 Sacha Core；
- 让任一提供方成为 Sacha 必选依赖；
- 自动安装、refresh 或发布插件；
- 重建旧 CGame 工作流阶段、hook 或面包屑；
- 把产品路径、宏、构建命令或机器配置加入 Sacha；
- 把 Manager 变成领域调查的必经入口；
- 替代 Project `AGENTS.md` 或 Project Integration 权威。

## 10. 后续迭代检查清单

每轮合入前：

- 核对当前 Workflow Contract 与 Project Integration 边界；
- 核对实时 provider manifest、Skill 名称与输出契约；
- 判断改动属于 Core-neutral、Adapter-specific 还是 Project Integration-owned；
- 定义 provider 缺失时的 fallback 与恢复入口；
- 为每条新路由绑定可观测验证；
- 将安装/发布授权保持为独立边界；
- 保护 Sacha 当前进行中的源码候选改动。

当前源码证据入口：

- `<capability-marketplace-root>\DOMAIN-PLUGINS-ARCHITECTURE.md`
- `<capability-marketplace-root>\cgame-unity\DESIGN.md`
- `<capability-marketplace-root>\cgame-engine\DESIGN.md`

这些路径只是当前本机 workspace 的证据 locator，不是可移植 Core 常量。
