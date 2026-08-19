---
name: closeout
description: Human 用“收口”原位完成当前唯一 Spec、用“存档”请求项目文档，或要求“收口并存档”时使用；普通正文提及不触发。
---

# Closeout（任务收口）

## 功能

接收“收口”“存档”“收口并存档”请求，并把动作分别交给 [Artifact Protocol](../../core/artifact-protocol.md) 的 Spec 完成语义和 `document-project`；本 Skill 只拥有预检、顺序和聚合结果，不接管两个内容 Owner。

## 输入与首查

1. 当前请求明确要求“收口”“存档”或“收口并存档”时继续；只讨论或引用这些词语时不执行动作。
2. 仅有“存档”时直接调用 `$sacha-orchestra:document-project`，映射为 `human-request`；不读取或修改 Spec，也不改变 [Workflow Contract](../../core/workflow-contract.md) 的正常 `goal-closeout` 候选。
3. 包含“收口”时，从当前任务、批准 Spec reference 或明确 Human 输入取得 Spec `path`；不得扫描 Spec storage root 猜测“最新”任务。缺少 path、存在多个当前 Spec、文件名不是 `spec.md` 或 reference 不可达时失败关闭。
4. 按 Workflow Contract 核对根终态为 `goal_complete`，全部必需验证与适用 Review 已由当前 Owner 消费；按 Artifact Protocol 核对 Spec 已批准、状态行唯一且当前上下文可写。

## 动作顺序

1. “收口”本身是本次 Spec 状态原位写入授权；不授权移动、改名、生成项目文档或其他写入。读取并记录唯一状态行的当前完整文本；已是“已完成”时返回 `no_op`，否则使用 Runtime 具有并发修改检查的局部编辑能力把该行原位改为“已完成”并回读。局部编辑前状态行变化或不能精确匹配一次时停止；不得用整文件替换覆盖其他并发正文。
2. “收口并存档”先预检两个动作：Spec 满足收口条件，且 `document-project` 的 Project Integration、目标和本次文档写入授权可确定。`per-write-confirmation` 仍须对项目文档单独确认；未满足前两个动作都不写。
3. 预检通过后先原位完成 Spec，再把“存档”以 `human-request` 路由给 `$sacha-orchestra:document-project`。文档写入失败不回滚已合法完成的 Spec；报告部分完成、失败证据和文档恢复入口。

## 输出

- 报告命令映射、Spec 原 path、原状态/新状态、Spec 编辑结果、文档动作结果、失败或未验证边界。
- 组合动作分别报告 Spec 写入授权与项目文档写入授权；不得用一个动作的授权替代另一个。

## 停止与禁止边界

- 缺少或存在多个当前 Spec、任务未到 `goal_complete`、必需检查未满足、Spec 未批准、状态行缺失/重复、状态行变化或只读上下文时不写入。
- 只原位修改唯一 `spec.md` 的现有状态行；不得移动目录、创建 `docs/done`、生成平行完成 Artifact，或修改 Spec 的 Scope、决定和验收正文。
- 项目文档由 `document-project` 独占；Spec 完成不自动生成项目文档，项目文档也不能替代 Spec 完成。
