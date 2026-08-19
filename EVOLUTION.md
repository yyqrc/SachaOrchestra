# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.11.11`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Clarify 在 Human 背景不足时先调查解释并允许反问/纠正，只有共享事实与影响后才请求真实取舍；setup-agents 在同一事务中管理 Luna、DeepSeek Flash/Pro 与 K3 五个官方 Agent 定义，并补齐场景 verifier 和发布验证路由。
- 当前 breaking boundary：不新增 Role、Gate、Artifact、Registry、Hook、MCP 或外部授权；保留正常收尾候选、生成器 `human-request | goal-closeout` schema、Project Integration 策略和写入授权。
- 当前成熟度：Clarify source-scenario 与独立评估已通过；setup-agents 13 项、场景 verifier 2 项、发布脚本 22 项、Skill/Plugin 结构和待发布阶段一致性已通过，独立 Review 为 `Accepted with follow-up`；安装后 fresh Runtime 未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
