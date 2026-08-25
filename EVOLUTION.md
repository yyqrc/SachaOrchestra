# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.6`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：`document-project` 为显式发布文档目标增加不依赖 Project Integration 的模板化 `create | update`，以目标 path 作为本次写入授权，并用 update preimage、项目 root 边界、模板校验、原子替换和失败恢复保护既有 Markdown；术语合同统一该输入分类，Intake、Workflow、Skill、README 和 metadata 只保留各自映射。
- 当前 breaking boundary：`0.12.6` 不删除既有入口、Role、Gate、Artifact、Hook、MCP 或策略驱动文档路线；Roadmap、Project Context 和未显式指定目标的请求继续使用 Project Integration。显式发布文档目标新增 `target_path`、`mode`、`expected_target_sha256`、`template_catalog_path` 输入，不改变既有输入合同。
- 当前成熟度：`0.12.6` 采用普通发版证据边界；candidate coherence 0 failures、`document-project` 18 项生产入口行为测试、Skill validator、Plugin validator 与精确 staged tree whitespace 复核通过，独立 Review 为 `Accepted with follow-up`；安装/cache parity、fresh discovery 与真实 Runtime 场景未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
