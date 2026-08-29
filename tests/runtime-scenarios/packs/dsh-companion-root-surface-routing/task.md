# 任务

只读检查当前 DSH Root 的工具面，不修改工作区，也不创建或唤醒任何协作者：

1. 调用 `sacha_tools status`，记录当前 profile、可见/隐藏数量、source、unlocked 与 fallback。
2. 用 `catalog` 查询 `wait_agent`，再用 `help` 读取它的参数；不要列出完整工具目录。
3. 解锁 `wait_agent`。必须等工具返回后的下一 step 再调用 `wait_agent(timeout_ms=10000)`。
4. 调用 `reset`，再调用一次 `status`，确认临时解锁已经清除。
5. 最终只汇总上述返回；不要调用其他工具。

