# Feedback 独立入口、owner transfer 与 productive wait Spec

- 状态：Approved，Human 于 2026-08-07 批准实施
- 目标版本：`0.8.1` source candidate
- 补充决定：Human 于 2026-08-07 确认 Feedback 必须在另一个真实任务手动调用；本次调用本身就是来源任务调查与 owner transfer 授权。Feedback 可承接流程问题、使用反馈或插件开发想法

## 问题

`0.8.0` 把显式 Feedback 建模为 Source 创建或复用 repair target 后继续等待根终态。真实任务 `019fd655-16e5-7a43-8555-dee216b4c3b6` 中，Source 虽尝试跟踪 target，却在消费终态前中断；repair target `019fd75d-09f0-76d1-b9e2-b3e912fbc32a` 独立完成修复、验证、发布与安装。插件重装也不会让旧 Source 成为新版本的 fresh Runtime 证据，因此该等待没有直接消费者价值。

现有调度还只规定首次 wait 前的派发数量，没有明确“派发后先推进其他不冲突 ready 工作，只有到依赖屏障才等待”，容易产生立即 wait、重复 timeout 或无意义进度读取。

## 决定

1. Human 在另一个真实任务手动调用 Feedback，输入为具体的流程问题、使用反馈、插件开发建议或能力想法。
2. 本次调用本身授权来源任务有界只读调查与单向 owner transfer。完整反馈身份由反馈 workspace、具体 objective、owner，以及 Human 已提供时的来源 reference 组成；只有身份精确匹配且仍 active/resumable 的唯一目标任务可以复用。无可复用目标时在本次调用授权内创建唯一目标任务，不追加创建确认。
3. 已 terminal 的同一反馈身份精确重复只按 `no_op` 返回既有 reference，不产生新 transfer；其他 terminal/stale 候选不算匹配，无法消歧时停止。来源任务交付原生任务 reference 后结束，不 join、不等待、不转述目标任务最终结果。
4. 目标任务从 README 普通入口重新判断，并使用通用的 Planner、Executor、Reviewer、Manager、验证、迁移与收尾规则。
5. 派发不自动触发 wait。当前 owner 先重算并推进所有不依赖未完成结果、且不与活跃工作冲突的已就绪单元；只有存在真实活跃目标、当前 owner 是其结果 consumer、下一 transition 依赖该结果，且没有其他已就绪工作时才进入等待。
6. timeout 只提供新 liveness 证据；不得 busy polling、重复读取相同进度或因 timeout 重复创建目标任务。
7. 目标任务若改变安装后 Skill/Adapter/Runtime 行为，仍按普通任务的授权和验收决定是否执行安装与 fresh Runtime 验证；未授权或未运行时明确标记 Runtime 未验证。

## Owner 与消费者

- Workflow 只表达 Feedback 单向交接和普通 migration 的高层差异。
- Coordination 唯一拥有 Feedback owner transfer、禁止嵌套 migration、dependency frontier 和 productive wait。
- Runtime Adapter 只映射查询、创建、交接与必要等待工具；不自行判定 ready 或 consumer。
- Feedback Skill 只执行来源任务/目标任务 procedure，不复制 Runtime API。
- README/Evolution 从现行 owner 派生；流程语义由 owner review 与真实 scenario/runtime 证据核对，测试只保护生产行为和机器状态。

## 验收

- Human 在另一真实任务显式调用 Feedback，可提交流程问题、使用反馈或插件开发想法。
- 调用本身授权来源任务查询、复用或创建唯一反馈目标任务；不追加创建确认。交付 reference 后来源任务结束，Feedback transport 不调用 terminal wait。
- 可复用目标任务必须匹配完整反馈身份且仍 active/resumable；terminal/stale 候选不会被误当成新的活跃 owner。
- 目标任务从普通入口重新判断，并使用通用的 Planner、Review、migration、delegation 和验证路线。
- 调度顺序明确为“派发 → 重算 ready → 推进不冲突工作 → 依赖屏障 wait → 消费结果 → 重算”。
- 无 result consumer 的 owner transfer 不等待；有 consumer 但仍有其他 ready 工作时也不等待。
- 两个 deployment manifest 为 `0.8.1`，Evolution 保留 `0.8.0` 发布事实并标记被当前 candidate 替代的 Feedback join 说明。
- 相关单测、Project Setup、Skill/Plugin validator 与 candidate release coherence 通过；未安装、未运行 fresh task 时如实标记未验证。

## 授权边界

本批准授权 SachaOrchestra workspace 内完成上述源码、文档、断言、版本 manifest 与静态验证。没有授权安装、创建 fresh 验证 task、提交、push、tag 或发布。
