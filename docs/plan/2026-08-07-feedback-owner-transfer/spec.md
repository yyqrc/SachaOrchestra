# Feedback 单向 owner transfer 与 productive wait Spec

- 状态：Approved，Human 于 2026-08-07 批准实施
- 目标版本：`0.8.1` source candidate

## 问题

`0.8.0` 把显式 Feedback 建模为 Source 创建或复用 repair target 后继续等待根终态。真实任务 `019fd655-16e5-7a43-8555-dee216b4c3b6` 中，Source 虽尝试跟踪 target，却在消费终态前中断；repair target `019fd75d-09f0-76d1-b9e2-b3e912fbc32a` 独立完成修复、验证、发布与安装。插件重装也不会让旧 Source 成为新版本的 fresh Runtime 证据，因此该等待没有直接消费者价值。

现有调度还只规定首次 wait 前的派发数量，没有明确“派发后先推进其他不冲突 ready 工作，只有到依赖屏障才等待”，容易产生立即 wait、重复 timeout 或无意义进度读取。

## 决定

1. 显式 Feedback 是单向 repair owner transfer。Source 只读调查，以 repair workspace、当前 Task/Scope revision、objective、owner 和 deviation provenance 组成完整 identity，复用或创建唯一 repair target，交付原生 task reference 后结束，不 join、不等待、不转述 target 最终结果。
2. 只有完整 identity 精确匹配且仍 active/resumable 的 target 可作为 repair owner 复用。已 terminal 的同 revision/provenance 精确重复只按 `no_op` 返回既有 reference，不产生新 transfer；其他 terminal/stale 候选不算匹配，必须使用当前 revision/provenance 选择或创建 owner。
3. repair target 是最终用户可见 repair workflow owner，不得再次做用户可见 task migration；它仍可按 Coordination 使用 Manager、subagent、独立 Reviewer 和有界验证任务。
4. 派发不自动触发 wait。当前 owner 先重算并推进所有不依赖未完成结果、且不与活跃工作冲突的 ready 单元；只有存在真实活跃目标、当前 owner 是其结果 consumer、下一 transition 依赖该结果，且没有其他 ready 工作时才进入等待。
5. timeout 只提供新 liveness 证据；不得 busy polling、重复读取相同进度或因 timeout 重复创建 target。
6. 修复改变安装后 Skill/Adapter/Runtime 行为时，只有 Human 已授权安装与 fresh Runtime 验证，repair target 才派发使用原 Feedback 最小事实的只读验证单元。target 先完成其他 ready 工作，在验收依赖屏障消费验证结果；未授权或未运行时明确标记 Runtime 未验证。

## Owner 与消费者

- Workflow 只表达 Feedback 单向交接和普通 migration 的高层差异。
- Coordination 唯一拥有 repair owner transfer、禁止嵌套 migration、dependency frontier 和 productive wait。
- Runtime Adapter 只映射查询、创建、交接与必要等待工具；不自行判定 ready 或 consumer。
- Feedback Skill 只执行 Source/Target procedure，不复制 Runtime API。
- README/Evolution 从现行 owner 派生；测试保护结构、顺序和禁止组合。

## 验收

- Feedback Source 查询/复用/创建唯一 target并交付 reference 后结束；Feedback transport 不调用 terminal wait。
- 可复用 target 必须匹配当前 revision/provenance 且仍 active/resumable；terminal/stale 候选不会被误当成新的 repair owner。
- repair target 不再进行用户可见 migration，但内部 delegation/Review/验证仍可用。
- 调度顺序明确为“派发 → 重算 ready → 推进不冲突工作 → 依赖屏障 wait → 消费结果 → 重算”。
- 无 result consumer 的 owner transfer 不等待；有 consumer 但仍有其他 ready 工作时也不等待。
- 两个 deployment manifest 为 `0.8.1`，Evolution 保留 `0.8.0` 发布事实并标记被当前 candidate 替代的 Feedback join 说明。
- 相关单测、Project Setup、Skill/Plugin validator 与 candidate release coherence 通过；未安装、未运行 fresh task 时如实标记未验证。

## 授权边界

本批准授权 SachaOrchestra workspace 内完成上述源码、文档、断言、版本 manifest 与静态验证。没有授权安装、创建 fresh 验证 task、提交、push、tag 或发布。
