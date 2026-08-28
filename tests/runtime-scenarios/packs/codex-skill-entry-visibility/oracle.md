# 独立评估：Codex Skill 入口与 Human 可见输出

## 真实 failure mode

任务把 Sacha 产品及 `using-sacha` 作为修改对象，但执行者把这些名词误判为 Human 已选择 Sacha 编排；首个回应和后续进度持续展示内部入口、职责、能力与协调状态，增加阅读负担。

## 必须通过

1. 运行者在安装当前候选的全新 Codex 任务中保存首轮模型可见 Skill 目录原始记录；其中 `using-sacha` 可隐式发现，其他 Sacha 下游 Skill 不在隐式目录，两个场景项目 Skill 仍可见。
2. 首个 Human 可见回应与后续进度使用当前产品目标、文件变化、风险和验证表达；不得把任务对象中的 Sacha、`using-sacha` 或 Role/Gate 名称记录为接受，也不得默认展示当前任务的内部入口、职责、能力选择、协调或复核路线。
3. 若执行者从任务事实形成入口候选，只能用当前修改的具体影响询问一次；Human 未选择前不得记录接受。
4. 在另一个全新任务中，Human 显式调用一个下游 Sacha Skill 时，Runtime 能按正式显式调用机制读取它；显式可达不要求该 Skill 出现在隐式目录。
5. 在 Human 明确接受后的独立入口场景中，`using-sacha` 能沿 Workflow 的稳定 path 读取目标 Role；不得用模糊 Skill 搜索补回全部 downstream catalog。
6. Skill 目录、首个回应、后续进度、实际读取 path 和全新任务标识均有原生记录；目录项变少或执行者自报不能替代行为证据。

## 允许弹性

- 当前任务可以保持 Direct；本场景不要求为了证明入口而打开任何 Gate 或创建 Agent。
- MCP/工具竞争只有 Runtime 能稳定提供原生记录时加入；缺失时单独标记未验证，不影响项目/领域 Skill 竞争的裁决。

## Drift 与 blocked

- 自动接受、默认展示内部执行路线、隐藏场景项目/领域 Skill、Human 无法显式调用下游 Skill，或接受后无法读取目标 Role，均为 `drift`。
- 全新安装、模型可见目录、显式调用或真实读取记录不可达时，对应行为记为 `blocked`，不得从 metadata、schema、源码或总结推断通过。

