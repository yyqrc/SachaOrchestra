# 当前 Runtime 事实

- `v1` 与 `v2` 是两套子 Agent 协作工具接口，不是两代 `Code Mode`。
- 一次旧 `v1` Runtime 记录中，主模型可直接调用 `multi_agent_v1.spawn_agent`，`functions.exec` 内部的 `ALL_TOOLS` 也包含对应规范化工具名；JavaScript 批量调用已实际跑通。
- 当前 fresh `v2` Runtime 中，主模型可直接调用 `collaboration.spawn_agent`，普通 `v2` 派发可用。
- 同一个 fresh `v2` Runtime 的 `functions.exec.ALL_TOOLS` 共包含 228 个工具，但不包含任何 `collaboration.*` 子 Agent 工具，因此 JavaScript 当前不能嵌套调用 `collaboration.spawn_agent`。
- 现有证据只能证明当前 Runtime 的嵌套工具可达边界；不能证明 `v2` 协议本身不能并发或未来 Runtime 永远不会开放该工具。
- 为什么宿主没有把 `collaboration.*` 放入 `ALL_TOOLS`，当前没有一手证据。
- 当前讨论 Scope 只覆盖编排插件自身，不授权修改宿主、配置、源码或外部状态。
