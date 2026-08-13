# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.11.8`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：`document-project` 接受 Human 显式文档请求或 Workflow 收尾候选路由；显式调用直接处理当前文档目标，不接受 Sacha、不补走 Planner、Executor 或 Reviewer。
- 当前 breaking boundary：不新增 Role、Gate、Artifact、Registry、Hook、MCP 或外部授权；保留正常收尾候选、生成器 `human-request | goal-closeout` schema、Project Integration 策略和写入授权。
- 当前成熟度：生产入口测试、Skill/Plugin validator 与源码/静态一致性验证已通过；显式触发、正常收尾触发及不补走生产 Role 的真实 Runtime 行为未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
