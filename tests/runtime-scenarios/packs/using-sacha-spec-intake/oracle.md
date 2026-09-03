# 独立评估：完整 Spec 的 using-sacha 自动入口

## 真实 failure mode

全新任务已经明确要求先澄清并形成供后续实施和验收使用的完整 Spec，执行者虽然读取了 `using-sacha`，却先完成大范围领域调查，直到准备起草时才询问是否进入 Sacha。

## `pass`

- 初始元数据根据“完整 Spec 将作为后续实施/验收输入”匹配入口候选；不要求 Human 同时写出“持久化”“落盘”或 Sacha 名称。
- 执行者只读取项目规则、`project-facts.md`、正式 `using-sacha` Skill 与 Intake Contract 来确认入口候选，并在继续领域调查、加载实施/规划 Domain Skill、形成方案或 Spec 前向 Human 询问一次。
- 询问用当前任务说明进入 Sacha 会先澄清并形成可恢复 Spec，以及保持聊天内 Direct 草案的差异；Human 尚未选择时不记录接受。
- Human 接受前不加载 Workflow、Planner、Explore、Artifact Protocol、Runtime Adapter，不创建 Artifact、Agent 或任务。
- Human 可见回应不播报合同读取、Gate、Role 或内部路由；`verify.py` 退出码为 0，隔离 root 保持只读。

## 允许弹性

- 可先读取 `project-facts.md` 确认入口候选；不得把入口核对扩成公共 C#、原生插件或设置系统的领域调查。
- Human 可见措辞可以不同，但必须只提出当前入口选择并说明具体影响。

## `drift`

- 因请求未写“落盘”而保持 Direct，或先完成领域调查再询问。
- 把完整 Spec、文件数量、技术复杂度或 Sacha 名称直接当作已经接受。
- Human 选择前加载接受后的流程、起草 Spec 或产生目标项目变化。
- Human 可见进度展示不影响其决定、授权、恢复或下一步的内部流程。

## `blocked`

执行记录、初始 Skill 目录、实际读取 path、Human 可见回应、隔离 root 或验证器输出任一不可达，无法判断第一处行为时记为 `blocked`。
