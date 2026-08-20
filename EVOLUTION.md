# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.1`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：区分插件开发控制面与发布插件 Runtime，新增 `docs/AGENTS.md` 和按需加载的发版/安装指南，压缩根规则中的产品入口、场景与发版副本，修正仓库导航、开发术语视图和 Capability Provider 维护路线；Feedback 与 Closeout Skill 分别把入口/Owner 转移和 Spec 完成判断交还现有 Core Owner。
- 当前 breaking boundary：不新增或删除入口、Role、Gate、Artifact、Registry、Hook、MCP、配置 schema、部署接口或外部授权；Runtime Skill 只收敛读取与 Owner 消费，不改变既有 Human 触发词和结果语义。
- 当前成熟度：`0.12.1` 采用快速发版证据边界；本次开发控制面与 Skill 正文已完成有界 diff、链接和 whitespace 复核，跳过普通回归、Skill/Plugin validator、完整 release coherence、安装/cache parity、fresh discovery 和 Runtime 验收。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
