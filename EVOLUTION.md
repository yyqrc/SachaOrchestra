# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.11.10`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Codex Code Mode 收敛为非 Agent 只读批量传输，canonical JavaScript 归发布插件内 Runtime asset；原生 v1/v2 Agent 生命周期保持不变，既有 v1 Agent Code Mode 场景原样保留为已取代证据；发布脚本为两套场景 verifier 选择真实正反例测试。
- 当前 breaking boundary：不新增 Role、Gate、Artifact、Registry、Hook、MCP 或外部授权；保留正常收尾候选、生成器 `human-request | goal-closeout` schema、Project Integration 策略和写入授权。
- 当前成熟度：待发布阶段一致性、asset 9 项测试、release 22 项测试、场景 verifier 2 项测试、Plugin 结构验证和 source/current Runtime 场景已通过；安装后 fresh Runtime 未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
