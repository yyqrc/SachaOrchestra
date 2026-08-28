# Oracle：Codex 能力 Agent 与模型优先级

## 目标

分别验证当前 Codex v1 与 v2 能否组合能力 Agent 与逐次模型路线，并实测“显式派发字段 → Agent 默认值 → 父任务路线”的优先级；两套协作界面独立裁决。

## 必须通过

1. 候选安装包含没有 `model`/`model_reasoning_effort` 的 `sacha_readonly_worker`、`sacha_executer` 与 `sacha_reviewer`；全新 Runtime 能发现三个类型。`sacha_executer` 不设置 `sandbox_mode`，另外两个类型实际为 `read-only`。
2. v2 schema 暴露 `agent_type + model + reasoning_effort + fork_turns` 时，首次创建能同时提交能力 Agent、本次模型/强度和 `fork_turns="none"`；v1 只有当前 schema 暴露等价组合时才提交 `agent_type + model + reasoning_effort + fork_context=false`。
3. 优先级矩阵分别保留请求值、Agent TOML 默认值、父任务模型路线和实际遥测：
   - `sacha_deepseek_worker` 同时传显式 Luna 路线时，实际值采用显式派发字段；
   - `sacha_deepseek_worker` 省略显式模型字段、父任务使用其他路线时，实际值采用 Agent 默认值；
   - `sacha_executer` 省略显式模型字段时，实际值采用父任务路线，并继承父任务实际 `sandbox_mode`；
   - `sacha_reviewer` 传显式 Sol 路线时，实际值采用显式字段且实际 `sandbox_mode="read-only"`。
4. 每个探针都是主任务直接创建的子任务，不读取或修改项目文件、不创建下级 Agent；只读探针的写入尝试必须被 Runtime 拒绝，实施 Agent 的可写范围不得超过父任务实际 `sandbox_mode` 与授权。
5. 正式 Reviewer 未参与候选实现，自己读取最终文件、验收基线与原始证据，不默认修复，并返回 Assurance Contract 定义的 Outcome。
6. Luna 通过逐次模型字段直接派发；候选安装不再包含 Luna/K3 固定模型 Agent。DeepSeek 固定模型 Agent 只用于精确路线、兼容分支和本优先级探针，不承载只读、实施或复核边界。

## v1/v2 分支

- 某一协作界面不支持能力 Agent 与逐次模型组合时，该分支为 `blocked`，或只对写入单元使用 Adapter 明示的兼容路线；不得声称两套统一支持。
- 只读研究与正式独立 Reviewer 缺少真实只读能力 Agent 时必须停止，不能用提示词或普通 worker 冒充。

必要 schema、全新发现、创建参数、`parent/depth`、只读探针或任一优先级的实际模型遥测不可达时，对应项记为 `blocked`；不得用参数接受或 Agent 自报补齐。

