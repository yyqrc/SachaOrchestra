# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.14.1`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Roadmap 推荐独立任务形成完整 Spec 时明确保留 Sacha Planner 入口，Human 确认后由 Codex Adapter 创建并核对目标首轮；`using-sacha` 把供后续实施或验收使用的完整 Spec 识别为入口候选，并在领域调查前完成一次选择。Human 可见进度不再重复播报合同、Gate、Role 或内部路由。
- 当前 breaking boundary：无。Roadmap 仍不接受 Sacha、不创建或执行 Spec；普通任务创建不表示接受，目标项目写入、实施、安装、Git 和其他高影响授权不随新任务传递。
- 当前成熟度：`0.14.1` 的场景验证器与发版选择单测 `32/0`、`using-sacha` Skill 校验和插件结构校验通过，精确候选路径无冲突或空白错误。快速发版跳过普通回归、完整 release coherence、安装/cache parity、fresh discovery 和 Runtime；两个新增真实场景尚未在安装后的全新 Codex 任务中执行。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
