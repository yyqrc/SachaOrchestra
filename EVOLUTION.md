# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.9`。
- 当前待发布源码版本：未定版；Draft Scope 为 DSH continuable-subagent transport 与 Runtime surface/observability 迭代。
- 当前待发布 Scope：DSH Adapter 删除 experimental Agent Teams task/roster 传输，直接使用 Root-owned continuable subagent；新增 `sacha-subagents` bundle 组合 `sacha_research` / `sacha_worker` / `sacha_review`；Visualizer 0.2 改为回放 Sacha Manager DAG、work-unit↔durable-child delegation 与 Root direct-child 状态；新增 DSH barrier/Reviewer Runtime task pack、Manager DAG/event replay 测试和 companion release gate。Codex/Claude 的进一步 progressive disclosure 仍只保留设计，不在本次已实施 Scope 内。
- 当前 breaking boundary：DSH 不再支持或保留 Agent Teams fallback、Team task DAG、`spawn_teammate`/`team_task_*`/`wait_agent` 映射；Visualizer 的旧 Team snapshot/model 也被删除。现行 DSH transport 以 continuable child + settlement-driven barrier 为唯一主路径，Visualizer 以 Sacha `manager_wave`/`delegation` 和 DSH direct-child observation 为唯一主模型。
- 当前成熟度：源码、Adapter、bundle、Visualizer 数据模型、静态 validator、release mapping 与 Runtime scenario oracle 已落库；真实 DSH fresh discovery、三个 surface 的 toolFilter/maxDepth 行为、并发 settlement barrier、Reviewer isolation、Visualizer Host/Client `pnpm verify` 和浏览器投影仍需目标 Runtime 直接证据。Draft PR 在这些证据完成前不应视为 release-ready。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
