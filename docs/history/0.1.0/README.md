# Sacha Orchestra 0.1.0 history

本目录保存 0.1.0 Foundation 的可移植开发历史。它用于在新机器或新上下文中恢复“为什么这样设计、实际做过什么、哪些证据通过、哪些能力尚未实现”，不替代规范性 Core 合同。

## 权威资料

| 资料 | 作用 | 状态 |
| --- | --- | --- |
| [`spec.md`](spec.md) | Stage 0 范围、切片、门控和验收合同 | 冻结历史 Artifact |
| [`evolution.md`](../../architecture/evolution.md) | 长期方向、成熟度、self-hosting 和 `1.0.0` 门槛 | 只读架构护栏 |
| [`execution-report.md`](execution-report.md) | Executor 的实施与验证证据索引 | 已完成历史 Artifact |
| [`review.md`](review.md) | 独立 Review、首次 Reject、证据返修和最终 Accept | 已完成历史 Artifact |
| [`development-log.md`](development-log.md) | 0.1.0 的可移植决策与实施时间线 | 维护记录 |
| [`session-index.md`](session-index.md) | 原 Codex/ChatGPT 任务身份与结果索引 | 维护记录 |
| [路径迁移记录](../../migrations/2026-07-12-workspace-relocation.md) | 旧根到新根的字节级迁移和安装源复核 | 迁移证据 |

## 接续边界

- 0.1.0 是已经验收的 Foundation，不是当前待执行 Spec。
- 不修改冻结 Artifact 来“更新现状”；新工作创建新的 Planner Spec 和独立证据链。
- `1.0.0` 仍要求 RenderDocAnalysis 中完整 Hybrid 可用，以及 Sacha Orchestra 自身升级能力达到演进文档规定的门槛。
- 当前仓库未保存原始 Codex 数据库或完整私有会话。任务 ID 和结论被保留用于追溯；其他机器应以仓库 Artifact 为恢复依据。

