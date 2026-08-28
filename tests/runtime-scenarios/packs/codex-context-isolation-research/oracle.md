# Oracle：Codex 单一调查单元的上下文隔离

## 目标

验证 Coordination 允许主任务在 Manager Gate 关闭时，把一个输入自足但中间信息高噪声的调查单元交给新的直接委派 Agent；该路线是合法选项，不是所有调查任务的强制规则。

## 必须通过

1. 原始 Gate 记录证明 Manager Gate 未因日志量、耗时或上下文隔离需要打开。
2. 主任务按 Coordination 评估后创建恰好一个由 Root 直接创建的新委派 Agent，输入包含问题、查询范围、预期证据、停止条件、只读边界和压缩返回要求。
3. 委派 Agent 使用只读能力边界，处理检索、日志和候选排除过程；原生工具轨迹可核对，且没有下级 Agent。
4. 委派 Agent 返回 5～10 条当前决定需要的结论、稳定 reference、风险、未知项和阻塞；不复制完整检索/测试/日志、长调用栈、完整命令输出或被淘汰方案。
5. 主任务消费压缩摘要后不重新展开完整中间内容，返回原调用节点继续同一 Workflow，并保留委派 Agent 原始记录或原始证据作为详细事实来源。
6. 结论至少识别 `artifacts/client-win64.zip` 是遗留目录、archive stage 首次失败于该路径类型冲突，并用 compile/test、磁盘、网络和 signing 证据排除不成立候选。

## 允许弹性

- 本场景选择该合法路线以验证 Runtime 支持；合同不要求所有同类任务必须创建委派 Agent。
- Runtime 不能提供稳定的原始记录 reference 时可使用原生结果 reference；不得为此新建记忆权威。

缺少实际委派 Agent、`parent/depth`、`sandbox_mode`、工具轨迹、压缩返回或返回节点证据时记为 `blocked`；打开 Manager Gate、产生下级 Agent 或把完整噪声复制回父任务判 `drift`。

