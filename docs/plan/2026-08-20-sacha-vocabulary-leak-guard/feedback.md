# Feedback：Sacha 工作流词汇不得进入目标项目实现命名

> 文档身份：插件开发使用；不进入发布插件。
> 文档性质：来源任务 Feedback payload（有界只读调查 + 建议）。不是已批准 Spec、不是执行授权；实际修改由插件维护者按根 `AGENTS.md` 的术语提炼与内容归属规则路由，并遵循 `需求不变量 → PLUGIN_DESIGN.md → Workflow/对应 Core → 节点 Skill/Adapter 消费者` 的变更顺序。

## 1. 反馈标识与转移状态

- 反馈标识：Sacha 工作流词汇泄漏到目标项目实现命名（`sacha-vocabulary-leak-guard`）。
- 来源任务：CODM `Runtime DirectAndSkyOnly` 计划澄清（`G:\COD\iwiki\docs\plan\2026-08-12-direct-and-sky-only-runtime\`）。
- Owner 转移状态：来源 Runtime 未暴露线程查询/创建工具，Feedback 技能要求的 `list_threads`/`create_thread` 不可用，未能完成唯一目标任务 Owner 转移；本文档作为持久 payload 交付，维护者消费后自行路由，来源任务不等待终态。
- 未经证实的范围：本反馈只防后续再犯；是否回改 CODM 任务的 `spec.md`/`decisions.md` 由 Human 另行决定，本反馈不要求。

## 2. 问题

Planner 产出 Spec/探索决定记录时，Sacha 或 Agent 工作流词汇可能直接成为目标项目的实现标识或概念命名。Executor 照抄后会向目标项目引入不符合该项目命名习惯的代码标识，或与 Sacha 自身的 Gate 等概念同名混淆读者。本次 CODM 任务的 Artifact Protocol 隔离机制挡住了大部分流程词（Owner、Handoff、Artifact 等），但仍有词汇漏入。

## 3. 证据（来自 CODM 任务实况）

| 词汇 | 出现位置 | 目标项目现状 | 风险 |
| --- | --- | --- | --- |
| “Scope 守卫” | `spec.md` §3.5/§5.5/§6.1/§6.2；`decisions.md` §Probe 退化状态传播与 stripping 段 | `ShaderStripping.cs` 无 Scope 概念，只有 `ShouldBeStripped`/`NotHandled` 判定与 `s_BypassMarkedShortcut` | 高：Executor 可能建立名为 ScopeGuard 的函数或注释 |
| “GM allow gate” | `spec.md` §2.1/§3.2/§5.2；`decisions.md` §Runtime 状态段 | 项目 GM 无 gate 词，先例是 `Toggle` 命令与 `SetCurrentModeRealtimeShadowEnabledRuntime` 等开关命名 | 高：与 Sacha 的 Gate 概念同名，读者混淆 |
| `nativeQualityEligible` / `nativeGMAllow` | `decisions.md` 指代名（`spec.md` 未直接写死） | `Graphics.bindings` 既有属性无 `native` 前缀：`enableLowQualitySettings`、`enableUnityInfo_LightProbe`、`isOptLightProbeFind`、`enableStreamingLightProbeCache` | 高：Executor 照抄会成为项目里不存在的命名风格 |
| “effective bool” | `decisions.md`；`spec.md` §5.1 | 项目无此词 | 中：建议“最终开关快照” |
| “职责函数” | `spec.md` §5.3 | 项目无此组合词；`spec.md` 其他位置已用更贴切的“节点函数” | 低：建议统一为“节点函数/处理函数” |
| “consumer / 消费者” | `spec.md` §2.1/§5.1；`decisions.md` 多处 | 项目 C++ 注释不用此词 | 低：建议“调用点” |
| “Grill” | `decisions.md` §旧项更新 | 纯 Sacha 黑话 | 低：探索记录可留，但建议删 |

## 4. 根因：现有契约缺三条守卫

1. Artifact Protocol §2.1 有“移除 Sacha 上下文后仍须可读、可执行”和“不得把临时规划抽象升级为项目术语”，但没有明确禁止把 Sacha/Agent 工作流词汇本身用作实现标识或项目概念命名。
2. 没有要求新增实现标识必须核验目标项目命名习惯；`nativeQualityEligible`/`nativeGMAllow` 正是未核验 `Graphics.bindings` 既有习惯的结果。
3. Planner 第二遍回读只检查“保留英文标识是否回指项目来源”与“Executor/Reviewer 能否读懂”，没有“新增命名是否符合目标项目命名习惯”这一项，因此“Scope 守卫”“职责函数”漏过三遍回读。

## 5. 建议修改（三处小改，不动流程/Owner/Gate）

### 5.1 Artifact Protocol §2.1（内容边界）

在 L44-46 “Planner → 写入新增项目概念”之后增加一条：

```text
Planner → 新增实现标识（属性、函数、keyword、字段、类名）或项目新概念 → 必须遵循目标项目现有命名习惯；Sacha/Agent 工作流词汇（如 Gate、Scope、consumer、effective、职责函数）不得作为实现标识或项目概念进入 Spec 或探索决定记录。
```

### 5.2 术语合同（Runtime 侧术语表加边界声明）

在术语表前后加一条边界：

```text
插件术语只服务插件流程；不得作为目标项目命名候选，也不得原样或改写后进入 Spec/探索决定记录。
```

（同步规则：本文是插件内共享术语的唯一 Runtime Owner 修改，须按根 `AGENTS.md` 术语提炼与同步规则，同次更新 `docs/CONTEXT.md` 对应条目并核查直接消费者。）

### 5.3 Planner Skill 第二遍回读

在“逐项核对英文标识与已确认项目来源精确匹配”之后增加检查项：

```text
枚举 Spec 中所有新增实现标识，逐个对照目标项目既有命名习惯（属性/函数/keyword/字段的命名前缀与风格）；Sacha/Agent 工作流词汇必须改写为项目习惯命名或删除。
```

## 6. 影响与可证伪

- 影响面：只约束 Planner 产出词汇，不改变入口、Role、Gate、Artifact 结构、授权或外部动作；三处均为现有 Owner 的补强，不新增 Owner 或机制。
- 可证伪方式：构造一份含“Scope 守卫”“GM allow gate”等词汇的 Spec 草案，按修订后的 Planner 回读执行，应被第二遍检查拦截；未拦截即修订失效。
- 实施前提：维护者确认根 `AGENTS.md` 第 90 条“新增规则必须对应真实失败”成立——本反馈已提供真实失败证据（第 3 节），并明确指出直接消费者（Planner 回读、Spec/decisions 产出）与改变的判断（新增命名必须核验项目习惯）。

## 7. 未验证边界

- 未验证 Owner 转移：本 Runtime 未完成 Feedback 目标任务创建/复用，本文档只是 payload。
- 未验证其他项目：证据只来自 CODM 一个项目；护栏是通用规则，但“哪些词属于项目习惯”仍需逐项目核验，不能由本反馈列举。
