# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.5`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Explore 补齐 Human 不理解或请求辅助理解时的解释流程，修正触发、调用身份、挑战图更新和 Human 决定记录的重复或冲突；顶层设计、Intake、Roadmap 与发布 README 明确 Explore 可按 Artifact Protocol 写探索决定记录，同时保持目标项目源码、配置、资源和外部状态只读；Codex 显式调用策略保持不变。
- 当前 breaking boundary：`0.12.5` 不新增或删除发布插件入口、Role、Gate、Artifact、Registry、Hook、MCP、配置 schema、部署接口或外部授权；只澄清 Explore 既有职责、Human 交互映射与探索决定记录授权，不授予目标项目实施或外部状态写入。
- 当前成熟度：`0.12.5` 采用普通发版证据边界；candidate coherence 0 failures、完整 Plugin validator、Explore Skill validator 与精确 staged tree whitespace 复核通过，独立 Review 为 `Accepted with follow-up`；真实 task-package Runtime 场景、安装/cache parity 与 fresh discovery 未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
