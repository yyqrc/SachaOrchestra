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
3. 包含“收口”时，读取 [Artifact Protocol](../../core/artifact-protocol.md) 的 Spec 完成规则，并把当前任务、批准 Spec reference 或 Human 明确提供的 `path` 交给该 Owner；本 Skill 不扫描或自行判定替代 Spec。
4. 将当前根终态、验证与 Review 消费状态、写入授权和可写上下文交给 Artifact Protocol 预检；只消费其结果，不在本 Skill 重建 Spec 完成条件。

## 动作顺序

1. “收口”本身只构成本次 Spec 状态写入授权；按 Artifact Protocol 执行 Spec 完成，并聚合其实际编辑、`no_op` 或失败结果。本 Skill 不另行实现状态行匹配、并发编辑、回读或恢复算法。
2. “收口并存档”先预检两个动作：Spec 满足收口条件，且 `document-project` 的 Project Integration、目标和本次文档写入授权可确定。`per-write-confirmation` 仍须对项目文档单独确认；未满足前两个动作都不写。
3. 预检通过后先原位完成 Spec，再把“存档”以 `human-request` 路由给 `$sacha-orchestra:document-project`。文档写入失败不回滚已合法完成的 Spec；报告部分完成、失败证据和文档恢复入口。

## 输出

- 报告命令映射、Spec 原 path、原状态/新状态、Spec 编辑结果、文档动作结果、失败或未验证边界。
- 组合动作分别报告 Spec 写入授权与项目文档写入授权；不得用一个动作的授权替代另一个。

## 停止与禁止边界

- Artifact Protocol 拒绝 Spec 完成时失败关闭；本 Skill 不自行选择替代 Spec、绕过完成条件、直接编辑状态行或创建补偿 Artifact。
- 项目文档由 `document-project` 独占；Spec 完成不自动生成项目文档，项目文档也不能替代 Spec 完成。
