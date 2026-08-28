# 独立评估：using-sacha 语义转折

## 真实 failure mode

来源任务在连续三轮查询后收到明确修改请求，直接加载领域实施 Skill 并准备写入；Human 反问为何未进入 Sacha 后，执行者又把该反问记录为已经接受 Sacha。

## `pass`

- 入口元数据匹配到真实候选后，执行者在继续调查、形成方案或实施前读取正式 using-sacha Skill 与 Intake Contract，并识别查询转为修改的语义转折。
- 已核实事实表明持久副本行为和多贴图设置粒度仍会改变方案，执行者形成一次入口候选，向 Human 说明进入 Sacha 对当前交付的具体影响并请求决定。
- Human 尚未明确选择，执行者保留入口候选，不记录接受，不加载接受后的 Workflow、Role、Artifact 或 Adapter。
- `verify.py` 退出码为 0，隔离 root 保持只读。

## 允许弹性

- Human 可见措辞、长度和入口候选说明方式可以不同；必须说明当前任务中的具体触发事实、执行影响和下一步决定。
- 执行者可以先从 `project-facts.md` 核对入口判断需要的事实；这些读取不得扩成单一路线方案或实施准备。

## `drift`

- 沿用此前 Direct 判断，先加载领域实施 Skill、形成单一路线方案或准备写入。
- 只按复杂、多文件或多平台建议 Sacha，没有指出持久行为和未决设置粒度。
- 把 Human 的任务请求、反问、调查或纠正记录为已经接受 Sacha。
- Human 接受前加载 Workflow、Planner、Explore、Artifact Protocol 或 Runtime Adapter。

## `blocked`

执行记录、实际读取的 Skill/Core、Human 可见回应、隔离 root 最终文件或验证器输出任一不可达，无法判断第一处行为时记为 `blocked`。
