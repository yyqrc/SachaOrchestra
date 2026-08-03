# Assurance Contract

> Contract Version: 1
> Status: Normative Core assurance contract

## 1. 范围

本文是 Reviewer Gate 打开后的 Baseline、验收矩阵、Outcome 与 re-review 权威。Role/Gate 由 [Workflow Contract](workflow-contract.md) 定义。
持久 Review/Handoff 由 [Artifact Protocol](artifact-protocol.md) 定义。Reviewer Gate 关闭时不加载本文。

## 2. Baseline 与证据

正式 Review 维护一个实现 Baseline。Git 使用可解析 commit/range/diff/file set；其他状态才补 manifest/hash。
Baseline/`acceptance_revision` 变化使旧 verdict 失效；evidence-only delta 只复核 `changed_check_ids`，Review Entry append-only。

验收矩阵使用稳定 `check_id`。摘要保留 Scope/revision、required/attempted、result、locator、risk、resume entry、人工状态与计数。
人工状态为 `pending | completed_passed | completed_failed | completed_inconclusive`。未知、冲突、stale、不可达或计数不一致保持未验证；Provider、报告和自报不拥有 verdict。

Reviewer 检查真实状态并只重跑能改变 verdict 的高风险验证。缺证据不等于实现缺陷；自动化不能证明的检查给出具体 Human/external 路线。

## 3. Outcome 与路由

| Outcome | 使用边界 |
| --- | --- |
| `Accepted` | Scope 与全部 release-blocking 检查满足 |
| `Accepted with follow-up` | 仅剩非阻塞人工、环境或证据后续 |
| `Needs Evidence` | 必需证据不足 |
| `Needs Fix` | 已知缺陷、真实失败或不可接受风险 |
| `Needs Replan` | 批准合同缺失、错误或失效 |
| `Blocked` | 安全替代耗尽，依赖 Human/外部状态 |

实现缺陷 → 原 Executor；合同问题 → Planner；缺证据 → 唯一 evidence owner。局部 blocker 只暂停冲突范围；其他安全且已授权分支继续。Reviewer 不为通过改合同、不默认修复、不用 Executor 自报替代独立判断。
