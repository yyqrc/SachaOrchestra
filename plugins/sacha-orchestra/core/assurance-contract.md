# Assurance Contract（验收合同）

> 状态：规范性 Core 验收合同

## 1. 范围

本文是 Reviewer Gate 打开后的 Baseline、验收矩阵、Outcome 与重新 Review 权威。Role/Gate 与 Runtime 路由由 [Workflow Contract](workflow-contract.md) 定义；Outcome 只能返回 Executor、Planner、证据/恢复 Owner 或收尾，不另建流程旁路。
Review Artifact 与 Handoff 的定义见[术语合同](terminology-contract.md)，生成与恢复规则见 [Artifact Protocol](artifact-protocol.md)。Reviewer Gate 关闭时不加载本文。

## 2. Baseline 与证据

正式 Review 维护一个实现 Baseline。Git 使用可解析的 commit/range/diff/文件集；其他状态才补 manifest/hash。
Baseline/`acceptance_revision` 变化使旧裁决失效；仅证据变更只复核 `changed_check_ids`，Review 记录只追加。

验收矩阵使用稳定的 `check_id`。摘要保留 Scope/修订号、必需/已尝试状态、结果、reference、风险、恢复入口、人工状态与计数。
人工状态为 `pending | completed_passed | completed_failed | completed_inconclusive`。未知、冲突、过期、不可达或计数不一致时保持未验证；Provider、报告和自报不拥有裁决权。

Reviewer 检查真实状态并只重跑能改变裁决的高风险验证。自动化无法证明的检查给出具体 Human/外部路线，并按证据状态选择 Outcome。

验收按实际执行者路由：A 类由 Agent 准备、执行并判断；B 类由 Human 提供设备、场景、账号或其他前置，Agent 在恢复后执行并判断；C 类由 Human 观察或判断，必须给出准备条件、操作、预期结果和回传证据。B 类等待期间保持同一工作流的恢复入口，条件满足后自动续跑；C 类结果写入现有人工状态。发布阻塞的 B/C 类检查未完成时使用 `Needs Evidence` 或 `Blocked`，非阻塞项使用 `Accepted with follow-up`。

## 3. Outcome 与路由

| Outcome | 使用边界 |
| --- | --- |
| `Accepted` | Scope 与全部发布阻塞检查满足 |
| `Accepted with follow-up` | 仅剩非阻塞人工、环境或证据后续 |
| `Needs Evidence` | 必需证据不足 |
| `Needs Fix` | 已知缺陷、真实失败或不可接受风险 |
| `Needs Replan` | 批准合同缺失、错误或失效 |
| `Blocked` | 安全替代耗尽，依赖 Human/外部状态 |

`Needs Fix` 返回原 Executor；`Needs Replan` 返回 Planner；`Needs Evidence` 返回唯一证据 Owner。局部阻塞项只暂停冲突范围；其他安全且已授权分支继续。Reviewer 保持独立，只依据真实状态和原始证据裁决；合同修订与实现修复分别由 Planner 和 Executor 完成。
