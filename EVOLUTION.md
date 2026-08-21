# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.4`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：新增四个仅供插件开发的仓库 Skill，分别负责文档治理、插件评审、Runtime 场景与简化审计；Runtime Reviewer 补强接口、消费者、真实入口和负例审查，Executor 补强按交付层选择证据，document-project 补强项目文档语义复核；新增 `reviewer-semantic-chain` 场景及 release 对开发 Skill 和场景脚本的最窄验证映射。
- 当前 breaking boundary：不新增或删除发布插件入口、Role、Gate、Artifact、Registry、Hook、MCP、配置 schema、部署接口或外部授权；`.agents/skills/**` 只服务插件开发，Runtime Skill 只补强现有职责内流程，不改变既有 Human 触发词、Outcome、路由或发布 root。
- 当前成熟度：`0.12.4` 采用普通发版证据边界；candidate coherence、25 个 release 测试、3 个场景校验测试、完整 Plugin validator 和四个开发 Skill validator 均通过，独立 Review 为 `Accepted`，`reviewer-semantic-chain` source-scenario 通过独立评估；安装/cache parity 与 fresh discovery 未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
