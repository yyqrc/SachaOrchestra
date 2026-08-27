# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.8`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：`using-sacha` 在收到当前可执行目标以及查询或诊断转为方案、修改或持久化时必须先完成入口判断；Planner 发现未收口决定时必须先进入 Explore，再继续 Spec。新增对应语义转折 Runtime 场景，并纳入 `@sacha-orchestra/dsh-visualizer` 的 Sacha/Jojo 猫咪素材、Role/状态叠加、会话展开持久化和开发预览站。
- 当前 breaking boundary：`0.12.8` 修正既有默认入口与 Planner→Explore 路由，不增加入口、Role、Gate、Artifact 或 Owner。DSH companion 仍独立于 Agent Plugin 发布 `root` 和三个 marketplace，其素材与界面变化不改变 Sacha Runtime 流程。
- 当前成熟度：`0.12.8` 采用快速发版证据边界；using-sacha Skill validator、Runtime 场景 verifier 3 项测试，以及 companion Host/Client/预览站 typecheck、16 项测试、Host/Client bundle 和预览生产构建通过。新入口场景尚未在安装后的全新 Runtime 执行；Agent Plugin 安装/cache parity、fresh discovery、真实 DSH Session、官方 Agent Teams 和面板 Human 验收未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
