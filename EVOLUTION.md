# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.14.0`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Project Integration 从 capability id mapping 收敛为 canonical Skill identity + load policy；Schema 4 只持久化 Skill 与策略，Setup 决策使用 canonical `description` 但不复制摘要；只读 `change-guard` 可在设计与规划阶段按需加载，实际修改 Skill 使用 `change-authorized`。
- 当前 breaking boundary：Project Integration 升为 Schema 4，移除持久化 capability id，并把 `after-write-authorization` 替换为 `change-authorized`；现有 Schema 3 可由新版 Setup 读取，但必须显式刷新后才成为现行 Skill loading。Setup CLI 使用 `--skill-loading`、`--reconcile-skill-loading` 和 `--unavailable-skill`。
- 当前成熟度：`0.14.0` 普通发版候选 tree `d1fcb6a6b54b199f60845ff1be26302514f8e890` 的 candidate coherence、并行 `release.py prepare`、全量单元测试 `117/0`、Setup Skill 与插件结构校验通过，独立插件 Review 为 `Accepted with follow-up`。Client、LookDevProject、UnitySource、cpTools 的生产 Setup dry-run 均为 `ready` 且只计划更新 `workflow-rule.md`；Codex v2 source-scenario 已直接证明 description/path 选择、`on-demand`、只读 Skill child 和 Unity/C# 约束结果，完整场景因 v1 缺失、DeepSeek encrypted v2 投递、首次 message rollout 加密、安装后 fresh discovery 与部分工具面不可达而保持 `blocked`，未发现语义 drift。Agent Plugin 安装/cache parity、发布后 fresh discovery、其他 Runtime 与 Human 验收未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
