# Sacha Orchestra 0.1.0 development log

> 时间：2026-07-12  
> 版本：`0.1.0` Foundation  
> 主任务：`SO-0.1.0-BOOTSTRAP-2026-07-12`  
> 结论：Stage 0 经独立 Reviewer 最终 `Accept`

## 起因

最初的 Author / Executor / Reviewer workflow 通过多个 Codex 窗口隔离上下文，以支持模型切换、降低 Token 成本、减少上下文污染，并让方案、执行和 Review 分开。复盘后确认：这套实现是有效的多角色工作流，但角色语义、Goal、task/thread、模型和项目规则耦合过深，难以跨项目复用，也不利于未来切换到 subagent 或自动编排。

0.1.0 的目标不是立即实现完整 Multi-Agent Orchestration，而是冻结一个可演进、可安装、可验证的 Foundation。

## 已冻结的核心决策

- 产品名为 **Sacha Orchestra**，定位是 Multi-Agent Workflow Orchestration Framework，不是 Agent OS。
- `Author` 正式迁移为 `Planner`。Planner 负责把已验证事实和用户目标转化为可执行契约，而不是单纯写文档。
- 最小生产角色集为 Planner、Executor、Reviewer，不按传统公司岗位拆出常驻 QA、Tester、Architect、Security 或 Performance Role。
- Manager / Conductor 是按需启用的编排控制面，不是固定流水线中的第四个生产角色。
- 不使用单一“简单/复杂”总分；采用三个独立门控：
  - 方案不确定性触发 Planner；
  - 后果与验证风险触发 Reviewer；
  - 协调复杂度触发 Manager。
- 默认路线是 Executor-only。Planner、Reviewer 和未来 Manager 只在各自门控成立时加入。
- Role、Gate、生命周期、Artifact 和 Handoff 属于 Core；task/thread、模型、Skill 发现、安装和恢复属于 Runtime Adapter；项目命令与证据规则属于 Project Integration。
- Artifact 渐进生成：小任务可不落盘；跨上下文、恢复或正式 Review 时使用 `spec.md`、`execution-report.md`、`review.md`。
- Handoff Envelope 保留为九字段协议，不新增复杂状态机或大量状态文件。
- `0.1.0` 表示 Foundation；`Contract Version: 1` 只表示首版合同 schema。产品 `1.0.0` 必须是可用版本。
- 先在 RenderDocAnalysis 中把 Hybrid 路线验证完整；第二项目验证暂不作为 1.0.0 前置条件。
- 框架在能力达到对应 self-hosting 门槛后，原则上使用自身 Planner / Executor / Reviewer，以及成熟后的 Manager，继续开发和升级自身。

完整架构与版本门槛见 [Evolution](../../architecture/evolution.md)。

## Stage 0 实施

Ultra Executor 按冻结的 [`spec.md`](spec.md) 顺序完成 Foundation：

- 创建 repo-local marketplace 元数据和单一插件源 `plugins/sacha-orchestra`；
- 建立平台中立的 [`workflow-contract.md`](../../../plugins/sacha-orchestra/core/workflow-contract.md)；
- 建立 [`artifact-protocol.md`](../../../plugins/sacha-orchestra/core/artifact-protocol.md)，定义 Artifact 权威边界与九字段 Handoff Envelope；
- 建立 [`runtime-adapter.md`](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md)，把 Core 映射到 Codex context、Skill、安装、恢复和 fresh-context 验证；
- 创建 `planner`、`executor`、`reviewer` 三项正式 Skill；
- 保留 `spec-author` 为 deprecated、explicit-only 兼容 alias，并禁止隐式命中；
- 未创建 Manager、Runtime Registry、Work Packet、并行写入者、hooks、MCP server、app 或 Stage 1 Project Integration；
- 使用官方 Skill/plugin validator、结构检查、安装/发现检查和 fresh-context runtime smoke 分别验证，避免把一种证据升级为另一种 claim。

详细命令、退出码、失败计数和实际路径记录在 [`execution-report.md`](execution-report.md)。

## Runtime smoke 与合同返修

中立烟测 `SO-0.1.0-SMOKE-001` 覆盖了 Planner → Executor → Reviewer 的前向路径和返修路由：

1. Planner 规划一个单文件、无尾换行的 ASCII fixture，并错误地把字节长度写成 `41`。
2. Executor 严格按合同写入后发现实际内容是 `39` 字节；验证退出 `1`，如实报告 warning 和 failure，没有把“内容匹配”静默升级为完成。
3. 独立 Reviewer 复核真实字节，判断为 Spec defect，而不是实现 defect，并路由回 Planner。
4. Planner 在同一 Task ID 和不扩大 Scope 的前提下修正验收长度。
5. Executor 只做验证续跑，不进行额外写入；结果 `39/39`、字节和 SHA-256 匹配。
6. Reviewer 最终接受该烟测。

这个过程证明了门控、证据纪律、动态返修和九字段 Handoff 在 Stage 0 的最小闭环，而不是证明完整 Hybrid 或自动 Manager 已实现。

另外完成：

- 普通规划请求隐式命中正式 Planner；
- `spec-author` 不会被普通规划隐式发现；
- 显式调用 deprecated alias 会报告弃用并转发 Planner；
- fresh context 可进入 SH1 只读自检路径，但不宣称 SH2/SH3。

## 正式 Review 与证据返修

首次正式 Reviewer 没有发现插件源或合同缺陷，但由于烟测 fixture 已清理，原始运行时证据无法从当时可达资料中独立重建，因此给出 `Reject — Needs Evidence`。这次 Reject 被保留为审计记录。

Executor 随后只补齐证据可达性：不改 Core、Skill、版本、冻结 Artifact 或安装状态。独立 Reviewer 通过任务搜索和原始 turn 读取重新检查 Planner、Executor、Reviewer、隐式路由、alias 和 SH1 六类证据，关闭 evidence gap，最终对 Stage 0 给出 `Accept`。

完整初审、阻塞原因、证据修复和最终 Handoff 位于 [`review.md`](review.md)。

## 工作区迁移

初始实现位于：

```text
C:\Users\<user>\Documents\MarketPlace\SachaOrchestra
```

考虑到外层 `MarketPlace` 与仓库内部 repo-local marketplace 概念重复，工作区迁移到：

```text
C:\Users\<user>\Documents\SachaOrchestra
```

迁移采用全文件相对路径与 SHA-256 比对，20 个文件 missing `0`、extra `0`、mismatch `0`；随后重新注册新根 marketplace、安装同一 `0.1.0` plugin，并验证 source 不再指向旧根。旧绝对路径保留在历史 Artifact 中，因为它们描述真实执行地点，不做追溯改写。

详情见 [workspace relocation](../../migrations/2026-07-12-workspace-relocation.md)。

## Git 历史说明

Stage 0 实施和 Review 时工作区尚未初始化 Git。为支持其他机器接手，Git 历史在验收和路径迁移后建立，并按以下语义重建：

- 架构与执行合同基线；
- 0.1.0 Foundation 插件实现；
- Executor / Reviewer / relocation 证据与可移植历史。

这些提交是由冻结 Artifact 重建的语义里程碑，不声称是开发期间实时产生的原始提交。`.gitattributes` 对五份历史证据禁用 EOL 规范化，以保持记录的 SHA-256 可复核。

## 冻结 Artifact 哈希

| Artifact | SHA-256 |
| --- | --- |
| `spec.md` | `369038E224BBC4BA6DB43E64523417F42199E86FF596376BAFABAB91694B585F` |
| `execution-report.md` | `F02C530F416A77A6179D97DDDFE7794A342A0D5B83F9C2EACCEAE3703380C268` |
| `review.md` | `8E20E8AE9C46132627141682C8B214C5AF490F355B7D78612A715FAA0943ACA9` |
| `docs/architecture/evolution.md` | `A5996976C6C84E3A25BF699B5EA977A3317967B37B24B1CEA53D368EC2214027` |

## 0.1.0 能力边界

已验证：

- 三项正式 Role Skill 的 schema、安装、发现和最小调用；
- Core / Adapter / Project 分层；
- 渐进 Artifact 和九字段 Handoff；
- 前向执行、Spec 返修、证据返修、隐式路由和 explicit-only alias；
- SH1 只读自检入口。

未实现或未宣称：

- Manager / Router 自动编排；
- Runtime Registry、Work Packet、依赖图或并行写入管理；
- RenderDocAnalysis 完整 Hybrid 项目接入；
- SH2 bounded self-change、SH3 upgrade self-hosting；
- 完整 self-hosting、生产可用或产品 `1.0.0`。

