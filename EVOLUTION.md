# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.0`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：把显式 `clarify` 支持入口无兼容改名为 `explore` 并补强陌生领域证据链；新增主流程外显式 `roadmap`，按需复用 Explore，把自包含长期阶段、依赖和 Spec 映射交给 document-project 写入 Project Integration 明确配置的 Roadmap root；setup-project、专用 Roadmap Profile/template、文档生成器和 Runtime 场景同步文件模式、项目文风与安全写入路径。
- 当前 breaking boundary：删除 `$sacha-orchestra:clarify` 及其目录/场景身份，不提供别名或兼容包装；新增 Roadmap Skill、共享术语和独立存储配置，但不新增 Role、Gate、Artifact、Registry、Hook、MCP 或外部授权，不让 Roadmap 接受 Sacha、替代 Spec 或执行阶段。
- 当前成熟度：`0.12.0` 已通过同一 staged tree 的 candidate coherence、目标 Skill 与完整 plugin 结构校验、最窄测试，以及独立 Review `Accepted with follow-up`；Explore 与 Roadmap source-scenario 均通过独立评估，Roadmap 场景实际选择 `document_type=roadmap` 的项目 Profile，覆盖配置 root/文件模式、按需 Explore、脱离 Sacha 的自包含阶段/Spec 映射和 document-project 原子创建。安装后 fresh discovery/Runtime 未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
