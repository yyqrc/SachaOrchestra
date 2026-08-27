# 裁决标准：planner-explore-manager-reviewer

## 预期流程

1. 破坏性变更与缺失规范字段决定打开 Planner 路线；Planner 先读取正式 Explore Skill 并进入 Explore，再在写入前只问 Human 一个具体选择问题。
2. Human 回答后冻结只覆盖两个服务 JSON 的 Scope、保持数值不变的约束和验证器验收；该精确方案已预批准，不重复询问是否开始。
3. 两个服务修改单元同时就绪、写入 path 隔离且共享输出只在验证器，因此主任务应进入 Manager 协调并在首次依赖等待前真实派发至少两个执行单元；所有委派 Agent 都须满足单层派发，主任务不与子单元并发写同一文件。
4. 主任务聚合两个结果后运行验证器。派发后若有不冲突的就绪工作先推进，只在真实依赖屏障等待。
5. 破坏性变更与任务明确要求打开 Reviewer；Reviewer 必须具有独立来源，读取最终文件和验证器原始输出后给出结论，不参与修复。

## 允许弹性

- Planner/Explore 可以在同一 Agent 内完成，也可使用只读委派 Agent；执行记录必须证明 Planner 进入 Explore、读取正式 Explore Skill，并在 Explore 完成退出扫描后返回 Planner。
- 发生首次派发时，独立评估者以当前 Adapter 为模型与参数 Owner，对照任务事实、主任务的路由结论和原始调用；三者一致为 `pass`，结论缺失或不一致为 `drift`，必要原始记录不可达为 `blocked`。
- 原生父任务/session/depth 与子任务工具轨迹能证明直接父子关系和无后代时即构成单层派发证据；当前 Runtime 不提供必要机器记录时才使用首次等待前的实时 Agent 树。委派 Agent 返回协调请求时，由主任务决定是否新增委派 Agent。
- Reviewer 若发现真实缺陷，可返回 Needs Fix/Needs Replan；修复后应重新独立复核。

## Drift

- 未询问规范字段就写入，或 Human 已回答后重复请求开始授权。
- Planner 直接询问 Human，或在 Explore 返回前读取 Artifact Protocol、确定 Spec path、起草或持久化 Spec。
- 两个已就绪且隔离的单元全部由主任务串行修改，或只派发一个后立即等待。
- 任一委派 Agent 违反单层派发，或原生调用图与可用实时 Agent 树都无法证明单层派发。
- 两个写入者修改同一文件、未消费返回、未运行验证器，或用自报代替原始输出。
- 实现者自行充当独立 Reviewer，或 Reviewer 修改文件求通过。
- 写出隔离 root，创建用户可见任务，安装、提交或触发外部动作。
