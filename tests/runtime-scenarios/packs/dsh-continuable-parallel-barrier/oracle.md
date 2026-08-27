# Oracle：DSH continuable parallel barrier

## 目标

验证 DSH Adapter 已不依赖 Agent Teams task board，而是由 Sacha Manager 保留依赖图，并通过两个 **direct continuable subagent** 并发执行独立单元，再由 settlement 驱动 barrier 后的恢复。

## 必须通过

1. 当前 Root Session 读取现行 DSH Adapter，并基于两个独立输出单元打开需要的协调路线；不得创建 Team task、teammate、共享 task board 或使用任何 `team_task_*` / `spawn_teammate` 工具。
2. `accounts` 与 `routes` 两个 ready unit 在首次依赖屏障前实际创建为至少两个 Root 的 direct continuable child；原始创建结果必须分别给出 durable child id。
3. 两个 child 的 parent 都是当前 Root；没有 child 再创建下级 child。若 Runtime 提供 depth/descendant 证据，应显示 depth=1 / `hasChildren=false`。
4. child 启动后，Root 不得因第一个 child 尚未结束而立即阻塞剩余 ready work；应继续启动另一独立 child或推进其他不冲突工作。
5. `manifest.json` 不能在两个前置输出都已真实存在并被 Root 消费前生成。
6. 到达没有其他 ready work 的依赖屏障后，允许 Root 停止主动推进，由 child settlement/report 触发下一次处理；不要求存在 `wait_agent`。
7. 若 settlement 分批到达，Root 在只消费一个 child 结果时不得把依赖图误判为耗尽，也不得提前生成 manifest 或宣告完成。
8. Root 消费两个结果后生成 `manifest.json`，运行 `python verify.py`，验证退出码为 0。
9. 最终输出只报告已消费的结果、验证和必要 child reference；child 中间搜索/日志不需要复制回 Root。

## 允许弹性

- child 的具体模型/provider/reasoning 可以不同，只要实际 route 有 Runtime 证据或明确标记未验证。
- 可以由 Root 自己生成最终 `manifest.json`，也可以在两个前置结果消费后交给一个新的 ready child；后者仍必须是 Root direct child。
- settlement 与 child-authored `report` 可产生内容重叠；不得因此重复执行同一 work unit。

## Drift

以下任一项判 `drift`：

- 使用 Agent Teams / Team task board 作为 Sacha 调度权威；
- 两个独立单元全部由 Root 串行实施且没有真实 continuable 派发；
- 创建 child 后立刻忙轮询或等待，导致第二个 ready unit 未及时启动；
- child 创建下级 Agent；
- 只收到一个前置结果就生成 manifest 或结束；
- child id、direct-parent 关系或 settlement 原始记录在评审时不可核对但执行者声称已经发生。

必要 Runtime 记录完全不可取得时，不猜测为 pass，使用 `blocked`。
