# Spec Artifact 与 Spec storage 统一修复

> 状态：Human 已批准实施
> 触发：`G:\COD\Client` 的真实 Planner 持久化产物出现 `plan.md` / `spec.md` 分叉
> 权威：本文件冻结本 repair objective 的 Scope、决定与验收；实施事实仍以源码、diff 和命令输出为准

## 目标

把持久任务权威统一为 `Spec Artifact`。Planner 只有在批准、breaking 或跨 context 恢复需要时才持久化，并在任务目录默认写入 `spec.md`。Project Integration 对外只暴露 `Spec storage`；`Plan` 仅表示 lifecycle 中按需发生的规划活动或 `inline plan`。

## Scope

本次只修改以下直接消费者：

- `plugins/sacha-orchestra/core/artifact-protocol.md`
- `plugins/sacha-orchestra/core/workflow-contract.md`
- `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md`
- `plugins/sacha-orchestra/adapters/claudecode/runtime-adapter.md`
- `plugins/sacha-orchestra/skills/planner/SKILL.md`
- `plugins/sacha-orchestra/skills/executor/SKILL.md`
- `plugins/sacha-orchestra/skills/setup-project/SKILL.md`
- `plugins/sacha-orchestra/skills/project-documentation/SKILL.md`
- `plugins/sacha-orchestra/skills/setup-project/scripts/generate_project_integration.py`
- `docs/integrations/capability-provider-guide.md`
- `docs/architecture/evolution.md`
- `tests/validate_project_setup.py`
- `tests/validate_spec_artifact_contract.py`
- 本 Spec

Core 合同版本随规范性语义变更递增。产品版本、deployment manifest、README 不在本次 Scope；只有实施发现它们存在当前语义的直接错误或 Human 另行冻结版本时才返回 Planner 修订本 Spec。

## Non-goals

- 不读取、迁移或兼容旧 `Plan storage`、`- Plan：...`、`plan_storage`、`plan_root`、`--plan-root*`。
- 不移动或改写 `G:\COD\iwiki` 中已生成的消费项目文件。
- 不规定固定的 Plan Artifact、Plan 章节或 Spec 内部章节；Spec 可按任务需要记录阶段与执行顺序。
- 不改变三个生产 Role、Gate、Handoff 核心语义、Project Documentation 权威边界或 capability/provider 责任。
- 不安装、refresh、修改 cache、commit、push、tag 或发布。

## 冻结决定与重命名矩阵

| 旧语义/接口 | 当前唯一语义/接口 |
| --- | --- |
| `Plan Artifact` | `Spec Artifact` |
| 持久的 `Plan` / 批准 Plan locator | 持久的 `Spec` / 批准 Spec locator |
| Planner 持久化文件名未规定或生成 `plan.md` | 任务目录默认 `spec.md` |
| `Plan storage` / `- Plan：...` | `Spec storage` / `- Spec：...` |
| `plan_storage` | `spec_storage` |
| `plan_root_kind` / `plan_root` | `spec_root_kind` / `spec_root` |
| `--plan-root-kind` / `--plan-root` | `--spec-root-kind` / `--spec-root` |
| `plan_root_unreachable` | `spec_root_unreachable` |

旧名必须从当前 Core、Skill、生成器和验证代码中删除。生成器只解析新 `Spec` 输出；旧输入不形成隐式配置，也没有 alias、fallback 或迁移提示。

## 实施约束

- `Spec storage` 与 Project Documentation 的 policy/root/write authorization 保持独立。
- Setup dry-run 不创建 Spec 根；外部根继续拒绝项目内路径与文件系统/盘符根，不可达时只给 `spec_root_unreachable` warning。
- 写入继续要求完整 planned delta、匹配的 SHA-256、managed marker 与旧文件 hash；并发变化拒绝，失败保持原子写/补偿恢复语义。
- Planner 的生产入口必须明确：需要持久化时，在 confirmed `Spec storage` 下创建任务目录，并默认写入 `spec.md`；没有 confirmed storage 时使用项目现有约定，不调用 Setup。
- lifecycle 的 `Plan（按需）` 和 `inline plan` 可以保留，但不得成为持久 Artifact 名称。

## 验收

1. Artifact Protocol、Workflow Contract 与 Planner Skill 对 `Spec Artifact`、按需 Plan 活动、默认 `spec.md` 的描述一致，且合同回归能定位这些生产入口。
2. Setup Python API、CLI、JSON 结果与生成的 Project Integration 只使用 `spec_*`、`--spec-root*`、`Spec storage` / `- Spec：...`；旧 CLI 参数被 argparse 拒绝，旧输出不被解析为 storage。
3. 行为测试证明 Spec storage 与项目文档根独立，project-relative 与 external-absolute 均保留 portability；dry-run 不建根，不可达根产生 `spec_root_unreachable`，盘符根被拒绝。
4. 行为测试继续证明 planned delta confirmation、旧 SHA、并发变化、原子写与回滚保护没有退化。
5. Planner 产物默认文件名 `spec.md` 有可执行/可解析的生产入口断言；生成器结果明确暴露 `file_name = spec.md`。
6. 当前 Core、Skill、生成器和验证代码不再包含旧持久化标识；Evolution 只记录当前 repair 与无兼容边界，不改写历史 Artifact。
7. `python -B tests/validate_project_setup.py`、受影响 Skill 官方 quick validator、plugin validator 与 `git diff --check` 均读取退出状态；失败、warning 与未验证层分别报告。

## 停止条件

- 需要保留任何旧读取兼容、迁移消费项目数据或改变 Project Integration schema marker/version。
- 需要决定新的产品版本、修改 deployment manifest 或进入发布/安装。
- 发现本 Scope 外的当前直接消费者会导致新旧语义并存。
- 目标文件出现无法语义合并的用户改动，或验证暴露需改变冻结语义的缺陷。

上述情况返回 Planner/Human；同 Scope 的实现缺陷、测试失败和 locator 漏改由 Executor 直接修复并重验。
