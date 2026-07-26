# Sacha Orchestra 0.1.0 task index

本索引保留 0.1.0 设计、实施、烟测、Review 和迁移的任务身份与可移植结论。Codex task ID 是来源定位信息，不是跨机器运行时依赖；新机器应以仓库中的冻结 Artifact 为权威输入。

## 背景讨论

| 来源 | 标识 | 可移植结论 |
| --- | --- | --- |
| ChatGPT conversation | `6a528479-b178-83e8-8df1-b39ffb5f5777` | Global / Project AGENTS 分层；从多窗口角色流转演进为跨项目编排；Author → Planner；角色精简；Sacha Orchestra 命名与定位 |

原始长对话未复制进仓库。关键架构决定已固化到 `spec.md`、`evolution.md` 和本目录的开发日志。

## 设计与规格

| Codex task | 标题 | 结果 |
| --- | --- | --- |
| `019f52a3-86c4-7481-ab2e-fe22360efaed` | Sacha Orchestra 迁移-方案设计 | 只读评审现有 Author / Executor / Reviewer 与窗口耦合，提出 Planner、三门控、Core / Adapter / Project 分层和渐进 Artifact |
| `019f52ce-bfa3-7fb0-b16d-84477eee9977` | 设计 Sacha Orchestra 架构 | 接收压缩版架构提示；其输出被后续完整规格纠偏与吸收 |
| `019f52d3-a214-7721-8a2c-6551c5e60c5f` | 修复 spec.md 生成 | 早期接续任务；识别 workspace 尚不存在、提示词中断和阶段命名问题 |
| `019f52d4-f997-7eb0-93b7-dd28dde8c7dc` | 修正 spec.md 生成 | 主 Planner / Human Conductor 接续任务；补齐 0.1.0 Foundation、1.0.0 可用门槛、RenderDoc 验证策略、self-hosting 原则并冻结 `spec.md` 与 `evolution.md` |

## Stage 0 实施与 smoke

| Codex task | 标题 | Task ID / 结果 |
| --- | --- | --- |
| `019f5492-f179-7c93-ba3b-7bc9a1e45b33` | Sacha Orchestra 0.1.0 Bootstrap | `SO-0.1.0-BOOTSTRAP-2026-07-12`；Ultra Executor 完成 Stage 0 Foundation、安装、验证和 evidence repair 接续 |
| `019f54de-a41c-7340-98a4-235675539e3a` | Plan planner smoke | `SO-0.1.0-SMOKE-001`；Planner 产出中立单文件 Spec，后续接收 Reviewer 返修并纠正 41/39 字节合同缺陷 |
| `019f54e0-00e7-7062-90d0-daae06556c17` | Create smoke artifact | `SO-0.1.0-SMOKE-001`；Executor 只写授权文件，如实报告验收矛盾，并在修正规格后只做验证续跑 |
| `019f54e2-067f-71a3-96f0-63cc752d0826` | Review smoke fixture | `SO-0.1.0-SMOKE-001`；Reviewer 独立区分 Spec defect 与实现 defect，路由返修后最终接受 |
| `019f54e8-42d9-7551-bc65-ffa3ed208722` | 制定隐式路由烟测方案 | 普通规划请求隐式选择正式 Planner，未调用兼容 alias |
| `019f54e8-5c1f-7692-8129-fdba81e83256` | 验证 spec-author alias | `SO-0.1.0-ALIAS-001`；显式 alias 报告 deprecated 并转发 Planner，未形成第四 Role |
| `019f54e8-6611-7b00-bcbb-696c95f42f20` | Review SH1 readiness | `SO-0.1.0-SELFHOST-READ-001`；只读 self-inspection 入口可达，明确排除 SH2/SH3/1.0.0 claim |

## 正式 Review 与迁移

| Codex task | 标题 | 结果 |
| --- | --- | --- |
| `019f54f7-5de6-7fa2-84cc-54ec60dddf12` | Review Stage 0 bootstrap | 首轮因原始 runtime evidence 不可达而 Reject；证据重建后独立复审最终 Accept，完整审计轨迹保留在 `review.md` |
| `019f550b-ddef-70d3-bd13-35c40a8f517d` | Sacha Orchestra 路径迁移收尾 | 验证新根、重新注册/安装、检查 source 和冻结哈希；旧空目录在原任务释放句柄后清理 |

## 恢复顺序

另一台电脑或新上下文不需要重放上述会话。按以下顺序恢复：

1. 根 `AGENTS.md`；
2. [`README.md`](README.md) 与 [`development-log.md`](development-log.md)；
3. 当前任务涉及的 Core / Adapter / Skill 权威文件；
4. 需要核查 Stage 0 时，再读取本目录 `spec.md`、`execution-report.md` 和 `review.md`；
5. 任何新实现都建立新的 Planner Spec，不把 task ID 当作授权或状态数据库。

未纳入仓库：Codex 本地数据库、缓存、隐藏推理、原始私有会话全文、凭据、机器级配置和已清理 smoke fixture。
