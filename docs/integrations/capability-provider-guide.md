# Capability Provider 接入指南

> Audience: capability provider 维护者
> Status: 开发期指南；非 Runtime 加载依赖

## 责任边界

- Provider catalog：稳定 capability id、canonical Skill、副作用上界。
- Canonical `SKILL.md`：触发、前置、具体副作用、步骤、输出与领域证据。
- Project-local `SKILL.md`：无 provider catalog 时，正文拥有可拆分 goal 与是否可独立调用的证据。
- Setup/Binding：候选解析、项目 Skill 正文评估、Human 确认的 load policy、对账与写入。
- Sacha：Intake、Gate、Scope、授权、Role 路由与 verdict。

Catalog、Binding 或 Skill 可见性均不证明安装或运行正确，也不授予写入、运行时操作或外部动作。

## Schema v2

Provider 可在 plugin 根提供 `capabilities.json`：

```json
{
  "schema_version": "2",
  "provider": "cgame-unity",
  "capabilities": [
    {
      "id": "project.inspect",
      "skill": "cgame-unity:project-inspect",
      "side_effect": "read_only"
    }
  ]
}
```

机器约束：

- 根字段必须且只能是 `schema_version`、`provider`、`capabilities`。
- `schema_version` 必须为字符串 `"2"`；`provider` 必须等于 Runtime 暴露的 canonical plugin name。
- 每项字段必须且只能是 `id`、`skill`、`side_effect`。
- `id` 使用小写字母、数字、`.`、`-`，且在 provider 内唯一。
- `skill` 必须属于该 provider，并在当前 Runtime context 可见。
- `side_effect` 只能是 `read_only` 或 `project_generated_state`，表示副作用上界，不是授权或 load policy。

Catalog 不保存 summary、触发、前置、具体影响或输出；这些事实只有 canonical `SKILL.md` 拥有。Catalog 也不保存 load policy：Setup 必须展示候选，Human 选择 `on-demand`、`after-write-authorization`、`review-only` 或 `risk-matched` 后，才能形成可写入 Binding 的 mapping。

## Setup 消费

1. Plugin provider：Setup 只从当前 Runtime 已暴露的 plugin/Skill metadata 建立候选；仅在已有稳定 locator 时定点读取同 plugin 的 catalog。Resolver 校验 schema、provider identity、ID、canonical/当前可见 Skill 与 side-effect 上界；无效 catalog 回退 metadata 并 warning。
2. Project-local Skill：Setup 只扫描目标项目内已确认的 authority/independent root，完整读取每个 `SKILL.md` 正文；mirror 复用 authority，ignore 不消费。仅在正文声明为调用必需时读取项目内直接 locator。
3. 项目 Skill 的 id、目录名、frontmatter name/description 和关键词只用于定位，不得推导 capability。Setup 从正文拆分零到多个 goal unit，记录 goal、类型、副作用、静态入口、运行时前置、reason、覆盖步骤/输出的正文行与 Skill SHA-256，并判定 `schedulable`、`support_only` 或 `unavailable`。
4. 只有正文定义可独立交付的有界目标、Skill 在当前 Runtime 可见且必需静态入口存在的 unit 才可进入候选；capability id 在该判定后分配。support/helper/reference/maintenance-only 或不可用 unit 不生成 mapping。
5. Generator 核对项目 Skill 评估的 root 身份、完整覆盖、正文行、SHA-256、必需路径和 Runtime 可见性；它不从 prose、name 或 id 自行推断语义。缺评估、证据过期、歧义、冲突或未确认 policy 均不得写入。
6. Human 集中确认 project root、reconciliation、每项 load policy、planned diff 与 hash 后，生成器才可写入。
7. Binding 只保存 `capability id → canonical Skill + load policy`；项目 Skill assessment 是本轮证据，不保存 catalog/Skill 正文、路径、query、前置或输出，rerun 重新读取。

Provider 不可见时保留既有 mapping 并使用 fallback；只有 Human 确认的 reconcile 集合可移除或替换 mapping。

## Project Integration 同层配置

Setup 分别确认四类项目值，不得互相推导：

| 配置 | Owner | 保存内容 | 不承担 |
| --- | --- | --- | --- |
| Capability bindings | Provider catalog 或项目 Skill 正文评估、Setup/Human | capability id、canonical Skill、load policy | Spec/文档路径、写入授权 |
| Spec storage | Setup/Human、Planner 消费 | 独立 root、portability、任务目录模式、默认 `spec.md` | 是否需要持久 Spec、发布文档 |
| Project documentation | Setup/Human、Documentation writer 消费 | policy、独立 root、portability、write authorization | Spec/Review/Handoff 权威、provider mapping |
| Pi one-shot model routing | 本机 Pi 只读巡检、Setup/Human | 通用 route 到精确 `provider/model` 的项目内映射 | plugin 默认型号、完整模型清单、运行授权 |

Provider query 只展开 capability 候选；不得选择 Spec root、文档策略、文档 root、写入授权或 Pi 型号。需要 Pi one-shot 时，Setup 定点核对可信 `pi --list-models`；已有项目 route 优先，其余按 `glm-5.2`、`kimi k3`、`deepseek`、`gpt-5.6 luna` 家族名模糊筛选。只在当次交互展示候选，Human 确认后才保存项目内路由；不持久化完整清单，也不向 plugin 源码复制完整 provider/model。配置项当前不可见时保留并 warning，不自动替换；无匹配时 helper 使用 Pi Runtime default。四类值可在同一次 Setup 集中确认，但各自独立保存、rerun 分别保留。

## Role 消费

Human 接受 Sacha 且任务需要项目能力时，Role：

1. 从 confirmed Binding 读取 capability、Skill 与 load policy。
2. 按 policy 判断是否加载；mapping 本身不授权。
3. 确认 Skill 当前可见并完整读取 canonical `SKILL.md`，据此核对前置、具体副作用、输出和领域证据。
4. Provider 返回领域结果与 evidence locator；最终路由和 verdict 仍由 Sacha 合同决定。

无 Binding、无 mapping、Skill 不可见或前置不足时，回退 Project AGENTS、可发现 Domain Skill 或 Role 原生路线，并保留未验证项。

## 经验候选与项目存档

Provider 可声明 `experience.extract` 一类 `read_only` capability，把真实任务证据分类为项目事实和高价值 domain/reference candidate。候选应来自现有按需 Reference 未覆盖、需要额外多文件、源码、产物或 Runtime 调查才能复核的具体机制；一次窄搜索即可取得的路径、owner、API 声明、通用规则、未实施方案或未复核文档不进入候选。该能力：

- 不直接修改项目文档、provider 源码或 catalog；
- 不决定文档 policy、root、授权、类型或最终正文；
- 不依赖 Sacha、Role、Documentation writer 或预先配置的项目存档；
- 只以当前源码、配置、产物、日志或 Runtime 观察为证据，会话总结和 Agent 自报只作 locator；
- 返回项目事实，以及候选短句、适用边界、现有 Reference 缺口、最短 evidence locator 和静态/编译/Runtime 验证边界；无合格候选时明确返回“无”。

调用方配置了 Project Documentation 时，可把上述基础结果适配成 Documentation writer 的有界交接，但不得把 Spec/Execution Report/Review locator 变成发布文档依赖。Documentation writer 仅在 confirmed policy 与写入授权允许时生成自包含 `change-archive` 或 `system-guide`；未配置时只返回当前任务结果。

项目事实归项目文档。跨项目候选要进入 provider 时，须在正常任务交付后取得 Human 同意，再路由到 provider 维护流程，以当前证据独立复核后迭代 canonical Skill/reference；不得让只读 `experience.extract` 自动 self-modify、创建任务、写文件或发 PR。维护流程不是公开消费能力时，不因存在于 `skills/` 就加入 capability catalog。

## Provider 迭代

Provider 修改能力时，更新 canonical Skill；仅在 capability id、Skill mapping 或副作用上界变化时同步 catalog。运行 provider 自身 schema/Skill/plugin 验证后，在消费项目执行 Setup dry-run；Human 确认 policy 与 reconciliation 后再刷新 Binding。新增经验提取能力时还要用真实任务验证只读边界、候选准入、证据分类、基础输出，以及调用方需要时的 Documentation 适配；不以模板或字符串存在代替真实 Skill 输出。Provider source、Runtime discovery、Binding refresh、Documentation write 和真实任务行为分别报告，不得互相替代。
