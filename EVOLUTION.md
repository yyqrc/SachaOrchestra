# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.13.0`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：首发独立 `@sacha-orchestra/dsh-companion@0.1.0`，合并 DSH continuable child surface 与 Visualizer，并在目标 Profile 为 Root 提供 `inspect | execute | review` 最小工具面、`sacha_tools` 有界查询/按需解锁、原生 Session 恢复和 Human 状态投影；同时自然化开发与安装后文本，不改变 Sacha Core、Role、Gate、授权或 Outcome。
- 当前 breaking boundary：旧 `integrations/dsh/sacha-visualizer` 与 `sacha-subagents` 被单一 `sacha-companion` 取代；DSH Root 不再默认暴露完整工具目录，隐藏能力必须经下一 `request/header` 生效的精确解锁。continuable child 不继承 Root `sacha_tools`。未迁移的 Desktop Profile 旧本地链接会失效，迁移需要单独授权。
- 当前成熟度：`0.13.0` 普通发版候选 tree `eccead82e606601147bdec9e02ad317fcbeeac17` 的 metadata coherence、release/companion 测试、clean 35-file companion package 和插件结构校验通过；Windows DSH Web Profile 的真实 inspect/execute/review header、同 response guard、cold resume、Client capability binding、按需 `write` 展开与 continuable child 隔离均有直接证据，独立 Review 为 `Accepted with follow-up`。Agent Plugin 安装/cache parity、Desktop 迁移、Linux、Code Mode、family late-registration 完整 DSH 场景与非 reduced-motion 最终动画未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
