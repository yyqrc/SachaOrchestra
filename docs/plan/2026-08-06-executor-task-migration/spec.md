# Executor task migration Spec

## 目标

修复批准 Spec 后无条件在已膨胀的原 task 中执行，以及 subagent 分解、难度/风险路由和 Manager 职责散落在多层、实际派发不可靠的问题。先以本 Spec 的可判定不变量推导 flow 与 owner，再由 Core、Role Skill 和 Runtime Adapter 分层实现；README 只展示推导后的用户流程。

## Scope

- Workflow 只定义 Role、Gate、高层 lifecycle、普通批准/明确迁移语义和 single-writer 不变量。
- Coordination 是分解与调度的唯一 Core owner：定义 Manager 的评估、拆分、依赖、两类 readiness、逐单元 route requirement、派发/归并/return，以及迁移 identity/dedup、owner transfer 和失败恢复。
- Role Skill 只说明何时调用 Manager、如何消费结果；Planner/Executor/Clarify 不复制 readiness、spawn 或模型规则。
- Codex Adapter 只把 runtime-neutral route requirement 映射为非重叠的有序模型选择、一次原生调用和一次失败回退，并把明确迁移映射为恰好一次 `create_thread`。
- README 在上述 owner 稳定后重画，不作为规范来源。
- Claude Code Adapter 对齐新 Core 版本，但不伪装 Codex task 能力。
- 删除逐句锁定合同文案的测试；只保留版本/结构/owner、迁移去重、派发顺序、路由优先级、single writer 和预算 warning 等可证伪不变量。

## 冻结决定

1. 默认不变：普通“批准”在当前 task 立即进入 Executor，不二次确认。
2. 只有 Spec 已持久化且可达，并且 Runtime 提供高 context 占用/compaction 事实，或当前 owner 可直接观察到多阶段长历史且后续执行不依赖未落盘对话时，才主动建议独立 Executor task。没有可靠信号时不得声称占用过高；Human 仍可主动明确选择。
3. 建议必须给出明确授权语句“批准并新开执行任务”，并说明普通“批准”仍在当前 task 执行。
4. Human 明确选择后，Codex 以 Task/Scope revision、批准 Spec reference 和 workflow transfer 作为迁移 identity。首次创建成功后记录原生 thread identity；重复批准、重试或恢复只复用，不再次创建。
5. 新 task 接管完整剩余 lifecycle：Execute、subagent、Review/返修与 closeout。旧 task 在 create/handoff 成功后展示 target reference并结束，不等待 terminal return；Spec 不可达/未批准、仍有未决方案/授权、依赖未落盘历史或旧写入者未终止时不得迁移。
6. 创建失败且尚未产生新 owner 时，旧 task 可回退同 task 执行并报告原因；创建成功后的恢复和失败处理只在新 task 继续，旧 task 不恢复 owner。重复回复只返回同一 target reference。
7. 新 task 优先只读 AGENTS、批准 Spec、必要 Artifact/evidence reference 和最小 Handoff；不得 fork 或复制完整历史。普通 bounded subagent/helper 不取得用户可见 migration identity，full-history helper 也不算 context 减负。
8. 不新增 Artifact/Handoff 必填字段。现有 route identity、scope、artifact/evidence、risk/entry 已足够；仅在原生 transport 未携带且恢复必需时提供。
9. 分解不是 migration 特例。当前 owner 发现多个候选单元、依赖图、并发安全或正式恢复需要协调时调用 Manager；不要求 Planner/Executor/Clarify 先完整拆分或宣布 ready。Manager 统一评估、拆分和建立依赖，并分别判定 execution-ready/research-ready；当前波次无论串行或并行，完成后都把结果交回同一 Task/Scope revision 并重算剩余依赖图。某一依赖波次至少两个 ready 且写入隔离时，该波次首次 wait 前必须实际派发至少两个；Gate、计划、迁移 task 或 full-history helper 不能替代 spawn。只有一个 ready 或写入不能隔离时，Manager 返回只约束当前波次的串行结论；没有 ready 时返回阻塞与恢复条件。共享文件、公共 schema、Git、最终集成和整体验证由 integration owner 串行处理。
10. Codex Adapter 不暴露或调用 Pi one-shot；模型/推理路由改用原生 subagent route。保留现有脚本、Setup 配置和历史记录，不把本次 Adapter 修复扩大为工具资产删除。
11. 文本长度预算只作可观测诊断：Core、Adapter、Skill、README 和组合 active surface 超限时输出实测 warning，不进入 candidate/release failure；结构、版本、owner/link、禁止边界和正式 metadata schema 仍硬失败。
12. Clarify research 不复用 execution-ready：显式 Clarify 可在窄授权内直接管理一个只读研究 helper；出现多个候选研究问题、依赖图或恢复协调时调用同一个 Manager。Manager 判定 research-ready、按波次派发并把聚合事实返回 invoking Clarify owner，不能跳 Executor。
13. 每个 subagent 都先产生同一套 runtime-neutral assessment：target kind、风险、难度/歧义、依赖/上下文、自包含/验证/返工和独立性。Manager 为其派发单元负责；单 helper 由 invoking owner负责。Core/Skill 不出现模型名或 Runtime 参数。
14. Codex 自动路由只使用四种组合：broad/critical → Sol xhigh，broad/standard → Sol medium，bounded/nontrivial → Luna max，bounded/light → Luna xhigh。Human/Scope 精确配置可使用其他 model/effort，Adapter 原样验证，不主动选择 Terra 或 Sol high/max/ultra。自动 Luna 仅在实际不可用且尚未开始工作时允许一次 Sol medium fallback；Sol、精确配置、可能已写入、旧 writer 未终止、独立性不明或 fallback 再失败时停止。
15. Project AGENTS 固化 owner 分层、修改顺序、consumer 对齐、测试边界和历史文档处理。机制变更必须先改唯一 owner并删除旧副本；与当前机制冲突、仍可检索的历史表格/章节/冻结文档入口须标明 historical/superseded、替代版本和当前 owner，不以“Git 历史仍在”作为保留误导正文的理由。

## Acceptance

- 持久 Spec + 明显长历史/compaction 信号 + Human 明确“批准并新开执行任务”时，只创建一个用户可见 task；它接管完整剩余 lifecycle，旧 task 不 wait/join。
- 普通短任务或普通“批准”仍在当前 task 立即执行。
- 普通批准后同-task Executor 的串行波次完成后必须回到同一 Task/Scope revision 的 Manager 调度；下一波若有至少两个合格 ready 单元，必须在该波次首次 wait 前实际派发至少两个，不能因上一波串行而把剩余图整体降为串行。
- 重复回复、create 重试或恢复不产生第二个 task 或第二个写入者。
- 真实案例的通用形态可拆为独立实现单元、独立只读 consumer/bridge 检查和集成验证；至少两个单元同时 ready 时实际并行派发，完成后使用独立 Reviewer。
- 无可靠 context 信号时不伪造遥测；仅响应 Human 的明确迁移选择。
- 受影响 Core/Adapter/Skill source/static tests、项目测试和官方 validator 通过；真实安装、fresh discovery 与 Runtime `create_thread` 行为明确标记未验证。
- 超过文本长度建议值时 coherence 返回成功并显示 warning；错误版本等真实 coherence 缺陷仍返回失败。
- 显式 Clarify 可在窄授权内派发一个只读 helper；至少两个 research-ready 查询在首次 wait 前实际并行派发，自包含查询不复制父历史，所有结果回到 invoking Clarify owner；Gate 关闭或 transport fallback 均不路由 Executor、不写入或扩权。
- 全部自动 `spawn_agent` 在首次调用前均有明确 requested route 和最小 `fork_turns`；自动 route 精确限制为 Sol xhigh、Sol medium、Luna max、Luna xhigh，Human exact 不受该列表替换。自动 fallback 至多一次且不得引入第五种组合。
- Manager 在普通同-task Executor、迁移 target 与 Clarify research 中执行同一套评估、拆分、逐波重算、ready、派发和归并算法；差异只在 readiness 与返回 owner。
- 测试数量和断言收缩；不再用中文整句 `assertIn` 证明合同成立。source/static 只证明文档/结构，真实 Runtime 派发仍单独标记。
- Project AGENTS 能直接回答 Workflow、Coordination、Manager、Adapter、Role Skill、README、Evolution 和测试各自负责什么；旧 `0.3.0` 路由与 2026-08-04 Spec 明确标为被当前 candidate superseded，不会被误读为现行 Sol/Terra 规则。

## Non-goals 与停止条件

- 不修改 cpTools、COD、安装 cache、Marketplace、Git 历史或远程状态。
- 不新增 Registry、后台服务、Hook、MCP、生产 Role 或跨 Runtime 通用 context 遥测。
- 若实现需要新增用户可见状态系统、扩展授权或改变 Artifact 权威，返回 Planner 修订。
