# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.12`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Codex 能力 Agent 将只读研究、实施验证与独立复核分别映射为 `sacha_researcher`、`sacha_executer` 与 `sacha_reviewer`，并只在宿主支持的 feature/Skill 范围内缩减能力面；setup-agents 安全迁移旧 `sacha_readonly_worker`。Capability Binding 在派发前解析当前 Runtime 唯一可达的 canonical `SKILL.md` path，并通过 child 首次工作单元精确传入；原生工具搜索只按每个 root/child 的实际工具面条件使用。
- 当前 breaking boundary：Codex 不再提供 `sacha_readonly_worker` 源码定义；Researcher 只承担无写入授权的读取与分析，但配置降权不构成宿主硬只读证明。Reviewer 保留裁决所需的验证能力且不默认修复交付实现。Capability Binding 与 Project Integration schema 不增加绝对 path、工具字段或平行 Registry。
- 当前成熟度：`0.12.12` 普通发版候选的 metadata coherence、19 项 setup-agents 测试和插件结构校验通过，独立 Review 为 `Accepted with follow-up`。安装/cache parity、`sacha_researcher` fresh discovery、旧 Agent 消失、三类 Agent 的真实工具面/permission profile、模型优先级、child 首次读取 canonical Skill、v1 分支与 `tool_search` Runtime 行为未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
