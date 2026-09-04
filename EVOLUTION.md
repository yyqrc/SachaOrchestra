# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；成熟度只记录已经完成的关键证据和具体已知问题，不枚举未触发的验证项。现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.14.2`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Codex Adapter 选择模型路线时分别核对实施边界与失败影响，并保留决定任务形态与负荷的最小直接事实；通用 Runtime 场景覆盖输入自足的只读规划与具备覆盖、删除能力的应用单元，验证 Luna 与 Sol 路线不会仅按文件数量或验证成本判断。
- 当前 breaking boundary：无。现有 `human_exact`、Sol/Luna 路线、能力 Agent、Core、Role、Gate、授权和回退顺序保持不变；本次只收紧既有 `broad / bounded` 判定及其证据要求。
- 当前成熟度：`0.14.2` 的通用模型路由 source-scenario 由主任务和独立 Reviewer 两次验证器运行通过，实际子任务遥测分别为 Luna Max 与 Sol Medium，独立结论为 `pass`。快速发版只完成其规定的发布身份检查；没有额外执行普通发版检查或安装/Runtime 验收。按当前验证规则，这些未触发项不形成后续验证清单；后续只在出现具体行为问题、高风险验收需求或 Human 明确要求时补对应证据。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。