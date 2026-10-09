# Assurance Contract（验收合同）

> 状态：规范性 Core 验收合同

## 1. 范围

本文定义验收执行分类，以及正式 Review 的 Baseline、验收矩阵、Outcome 与重新 Review。Executor 需要分配 Agent/Human 验证责任时读取第 2 节的 A/B/C 定义，不因此建立正式 Review 矩阵或作独立裁决。Reviewer 按正式路由读取本文；Role/Gate 由 [Workflow Contract](workflow-contract.md) 定义。
Review Artifact 与 Handoff 的定义见[术语合同](terminology-contract.md)，生成与恢复规则见 [Artifact Protocol](artifact-protocol.md)。

## 2. Baseline 与证据

正式 Review 维护一个实现 Baseline。Git 使用可解析的 commit/range/diff/文件集；其他状态才补 manifest/hash。
Baseline/`acceptance_revision` 变化后需对当前交付形成裁决；复核新增差异、直接影响及因此失效的证据，仍有效的检查可复用。仅证据变更只复核 `changed_check_ids`，Review 记录只追加。

验收矩阵使用稳定的 `check_id`。摘要保留 Scope/修订号、必需/已尝试状态、结果、reference、风险、恢复入口、人工状态与计数。
人工状态为 `pending | completed_passed | completed_failed | completed_inconclusive`。未知、冲突、过期、不可达或计数不一致时保持未验证；Provider、报告和自报不拥有裁决权。

Reviewer 检查真实状态并只重跑能改变裁决的高风险验证。证据按目标结果与具体风险判定；Reviewer 必须核对每块改动的必要性，无依据且扩大维护或回退成本的扩展必须返回修正，纯表达偏好不阻塞交付。自动化无法证明的检查给出具体 Human/外部路线，并按证据状态选择 Outcome。

涉及用户操作或结果呈现的交付，沿 Spec 或已确认目标中的同一主要使用过程核对生产入口、明确要求及关键联动；各模块单独通过不能替代跨区域、跨阶段的结果一致性。验收证据须能支持对应操作及可观察结果，不能只报总通过数；源码能确认的缺陷先查明，真实交互、裁剪、缩放或宿主显示行为则使用适用的生产环境证据。界面草稿只能支持设计对齐，不能替代生产算法、性能或宿主行为验证；仍有效的原始证据可复用。

实现不符合既定行为属于 Needs Fix；完成原目标所必需但 Spec 缺失、矛盾或失效的设计属于 Needs Replan；实测后提出的新用途或偏好按新的 Human 决定处理，不能倒推为旧实现违约，也不能把原先明确要求的遗漏降为后续优化。结果路由沿第 3 节，不因上述核对新增验收范围或强制 Human 试用。

存在批准 Spec 时，本文从其中的项目验收标准建立验收矩阵；没有 Spec 时，使用明确目标、Scope、Human 决定和项目验收输入。验收再按实际执行者路由：A 类由 Agent 准备、执行并判断；B 类由 Human 提供设备、场景、账号或其他前置，Agent 在恢复后执行并判断；C 类由 Human 观察或判断，必须给出准备条件、操作、预期结果和回传证据。A/B/C 是验收执行分类，不写回面向项目的 Spec。B 类等待期间保持同一工作流的恢复入口，条件满足后自动续跑；C 类结果写入现有人工状态。本次交付阻塞的 B/C 类检查未完成时使用 `Needs Evidence` 或 `Blocked`，非阻塞项使用 `Accepted with follow-up`。

## 3. Outcome 与路由

| Outcome | 使用边界 |
| --- | --- |
| `Accepted` | Scope 与全部本次交付阻塞检查满足 |
| `Accepted with follow-up` | 仅剩非阻塞人工、环境或证据后续 |
| `Needs Evidence` | 必需证据不足 |
| `Needs Fix` | 已知缺陷、真实失败或不可接受风险 |
| `Needs Replan` | 批准合同缺失、错误或失效 |
| `Blocked` | 安全替代耗尽，依赖 Human/外部状态 |

`Needs Fix` 返回原 Executor；`Needs Replan` 返回 Planner；`Needs Evidence` 返回唯一证据 Owner。局部阻塞项只暂停冲突范围；其他安全且已授权分支继续。Reviewer 保持独立，只依据真实状态和原始证据裁决；合同修订与实现修复分别由 Planner 和 Executor 完成。
