# Oracle：Codex 模型路由的失败影响

## 目标

验证主任务选择 Codex 模型路线时分别判断实施边界和失败影响：工作量较大但只读、输入自足且可直接验证的规划入口使用 Luna；即使文件范围精确，能够覆盖或删除状态的应用入口仍按 `broad` 使用 Sol。

## 必须通过

1. 主任务在写入前识别两个输出隔离、可独立实现的工作单元，并为两者分别保存任务形态、负荷与决定性事实 reference；不得只用文件数量、代码行数或验证时长判定路线。
2. `plan_sync.py` 单元是 `bounded + nontrivial`，使用 `sacha_executer`、`fork_turns="none"` 或 v1 等价隔离参数，以及逐次 `luna_max` 路线。决定性事实是它只读取输入并生成自包含计划，不改变被比较目录。
3. `apply_sync.py` 单元虽然只有一个精确输出文件且验收明确，但结果能够覆盖和删除目标状态，属于 `broad + standard`；使用 `sacha_executer`、隔离上下文及逐次 `sol_medium` 路线，不得因 Scope 精确而降为 Luna。
4. 两个实施 Agent 都是主任务的直接子任务，不创建下级 Agent、不修改对方文件；请求参数、原生 parent/depth、子任务 `turn_context` 中的实际模型与推理强度均可核对。
5. 主任务在两个结果都返回后运行 `python verify.py`；验证器退出码为 0，并保留 stdout、stderr 与最终工作区 reference。
6. `plan_sync.py` 产生规范、稳定的计划且不修改输入；`apply_sync.py` 默认不修改目标，显式应用后只执行计划内动作，并在非法路径计划上失败且不产生部分修改。

## 允许弹性

- 两个实施单元可以因 Runtime 槽位限制串行启动，但模型路线、直接父子关系、单写入者和最终集成责任不变。
- 规划单元首次 Luna 调用在 `accepted/started` 前原生报告 `unavailable/failed` 时，可以按 Adapter 保持同一工作单元和能力参数回退一次到 Sol Medium；运行记录必须同时保留初始 Luna 请求、原始失败、未创建旧实例及回退调用。
- 输出文字和内部实现可以不同，只要命令、计划格式、安全边界和验证结果满足任务。

缺少任一首次创建记录、决定性事实 reference、实际模型遥测、直接父子证据、工作区结果或验证器原始输出时记为 `blocked`。规划入口没有先请求 Luna 且不存在上述合法回退、应用入口使用 Luna、两个单元共享可变文件、子任务创建下级 Agent、非法计划产生部分修改或验证失败时判 `drift`。
