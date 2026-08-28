# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.11`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Codex 将只读调查、实施和独立复核能力与模型路线解耦；`using-sacha` 保持自动入口，其他 Sacha Skill 改为显式或按 Workflow 稳定 path 加载；Coordination 将上下文负担纳入拆分与派发，多个独立单元由 Manager 统一管理，单个合适单元直接派发；入口接受与 Human 输出不再从任务对象或源码内部结构推断。setup-agents 新增三个能力 Agent，Luna 改为逐次模型派发并移除 Luna/K3 固定模型定义。
- 当前 breaking boundary：Human 只有明确要求编排、选择接受或直接调用规范 Role 时才接受 Sacha；除 `using-sacha` 外的 Sacha Skill 不再参与隐式目录；Manager Gate 会在至少两个输入自足、输出隔离且可独立检查的单元成立时打开；Codex 不再提供 `sacha_luna_worker`、`sacha_luna_worker_xhigh` 与 `sacha_k3_worker` 源码定义。
- 当前成熟度：`0.12.11` 采用快速发版证据边界；44 项相关 Python 测试、受影响 Skill 校验、插件结构校验和当前 v2 原生 worker 的 Luna 创建参数通过。安装后 Skill 入口行为、三个新 Agent 的 fresh discovery、模型三级优先级、`sandbox_mode` 继承、Manager 实施隔离场景及 v1 分支未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
