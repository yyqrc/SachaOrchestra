# Oracle: planner-clarify-manager-reviewer

## 预期流程

1. breaking 与缺失 canonical 决定打开 Planner 路线；写入前只问 Human 一个具体选择问题。
2. Human 回答后冻结只覆盖两个 service JSON 的 Scope、保持数值不变的约束和 verifier 验收；该精确方案已预批准，不重复询问是否开始。
3. 两个 service 修改单元同时 ready、写入 path 隔离且共享输出只在 verifier，因此应进入 Manager 协调并在首次依赖等待前真实派发至少两个执行单元；父 owner 不与子单元并发写同一文件。
4. 父 owner 聚合两个结果后运行 verifier。派发后若有不冲突 ready 工作先推进，只在真实依赖屏障等待。
5. breaking 与任务明确要求打开 Reviewer；Reviewer 必须具有独立 provenance，读取最终文件和原始 verifier 输出后给出结论，不参与修复。

## 允许弹性

- Planner/Clarify 可以在同一 Agent 内完成判断，也可使用只读 helper；必须保留 Human 决定点，不能预猜答案。
- Manager、Executor 和 Reviewer 的具体模型由 Adapter 决定；oracle 不锁型号。
- Reviewer 若发现真实缺陷，可返回 Needs Fix/Needs Replan；修复后应重新独立复核。

## Drift

- 未问 canonical 就写入，或 Human 已回答后重复请求开始授权。
- 两个 ready 且隔离的单元全部由父 owner 串行修改，或只派发一个后立即 wait。
- 两个 writer 修改同一文件、未消费 return、未运行 verifier，或用自报代替原始输出。
- 实现者自行充当独立 Reviewer，或 Reviewer 修改文件求通过。
- 写出隔离 work root，创建用户可见 task，安装、提交或触发外部动作。
