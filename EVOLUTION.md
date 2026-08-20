# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.3`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Spec 与探索决定记录中的新增实现标识和项目概念按目标项目来源、目标位置、相邻 Owner、直接消费者与命名习惯核对；Planner/Explore 消费 Artifact Protocol，`project-facing-spec` 场景区分项目正式同名标识与 Handoff 临时命名；插件开发新增或扩展规则在交付前执行固定合规复核。
- 当前 breaking boundary：不新增或删除入口、Role、Gate、Artifact、Registry、Hook、MCP、配置 schema、部署接口或外部授权；Runtime Core/Skill 只补强项目命名来源、决定记录写入和批准前回读，不改变既有 Human 触发词和结果语义。
- 当前成熟度：`0.12.3` 采用快速发版证据边界；本次 Core、Skill、开发规则与 Runtime 场景包已完成有界 diff、Owner/直接消费者合规复核、版本身份和 whitespace 复核，跳过普通回归、Skill/Plugin validator、安装/cache parity、fresh discovery 和 Runtime 场景验收。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
