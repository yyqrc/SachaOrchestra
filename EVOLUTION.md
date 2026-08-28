# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.10`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：DSH Adapter 删除 experimental Agent Teams task/roster 传输，改用 Root-owned continuable subagent；新增 `sacha-subagents` bundle 组合 `sacha_research` / `sacha_worker` / `sacha_review`；Visualizer 0.2 回放 Sacha Manager DAG、work-unit↔durable-child delegation 与 Root direct-child 状态，并新增 DSH barrier/Reviewer Runtime 场景和 companion release gate。入口元数据只在真实候选或 Human 显式使用时加载 `using-sacha`，`Direct` 与 `Direct Scope` 由术语合同统一拥有。
- 当前 breaking boundary：DSH 不再保留 Agent Teams fallback、Team task DAG、`spawn_teammate`/`team_task_*`/`wait_agent` 映射；Visualizer 删除旧 Team snapshot/model，并以 continuable child、settlement-driven barrier、Sacha `manager_wave`/`delegation` 与 DSH direct-child observation 为唯一主模型。入口与术语修复不改变既有 Human 接受、Gate、Role、授权或验收。
- 当前成熟度：`0.12.10` 采用快速发版证据边界；DSH bundle validator、32 项相关 Python 测试、Visualizer validator、7 个测试文件/16 项测试、Host/Client/preview 构建和 using-sacha Skill validator 通过。真实 DSH fresh discovery、三个 surface 的 toolFilter/maxDepth、并发 settlement barrier、Reviewer isolation、浏览器投影，以及安装后清晰任务/入口候选的隐式匹配未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
