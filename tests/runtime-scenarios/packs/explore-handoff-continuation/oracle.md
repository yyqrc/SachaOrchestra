# 独立评估：Explore 接续与挑战图恢复

## `pass`

- 执行记录证明执行者从 using-sacha 进入 Workflow，并在进入 Explore 时完整读取正式 Explore Skill。
- 执行者从 `decisions.md` 恢复当前目标、三个关注点及其依赖，把它们组织为同一有界挑战图。
- 执行者读取三个事实来源，分别归并 consumer 覆盖、动态 Probe 语义和 Runtime 控制边界，并区分已核实事实、冲突与未验证项。
- 执行记录显示研究结果进入挑战图并更新依赖；下一就绪分支继续获得处理，退出扫描满足后结果返回调用节点。
- Human 可见结果包含已核实事实、冲突、阻塞性未决项、未验证项、evidence reference 和退出判断。
- `verify.py` 退出码为 0，隔离 root 的最终 delta 为空。

## 允许弹性

- 执行者可在主任务内串行研究，也可按当前 Core、Adapter 与 Runtime 能力协调有界只读研究单元。
- 挑战图、进度与最终结果可使用不同标题或自然表达；裁决依据是实际读取链、事实覆盖、结果归并、依赖重算和退出判断。
- Human 可在探索中补充约束、纠正事实或调整当前关注点；执行者按 Explore Skill 更新同一挑战图。

## 裁决输入

- 执行者实际读取的 Skill、Core 与 Adapter path。
- Human 可见进度、问题与最终结果。
- 委派存在时的原生创建、返回、等待与直接父子记录。
- 隔离 root 最终文件、delta 与 verifier 原始输出。
