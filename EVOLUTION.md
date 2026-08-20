# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.2`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：using-sacha、Planner 或 Roadmap 进入 Explore 时完整加载节点 Skill；Explore 从 Handoff、探索决定记录或旧 task 恢复有界挑战图，并在研究单元返回后归并结果、重算依赖和继续就绪分支；新增接续 Explore 的 Runtime 场景包。
- 当前 breaking boundary：不新增或删除入口、Role、Gate、Artifact、Registry、Hook、MCP、配置 schema、部署接口或外部授权；Runtime Skill 只收敛读取与 Owner 消费，不改变既有 Human 触发词和结果语义。
- 当前成熟度：`0.12.2` 采用快速发版证据边界；本次 Core、Skill 与 Runtime 场景包已完成有界 diff、Python 语法和 whitespace 复核，跳过普通回归、Skill/Plugin validator、完整 release coherence、安装/cache parity、fresh discovery 和 Runtime 验收。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或第二 Runtime；不得为证明通用性预建产品面。
