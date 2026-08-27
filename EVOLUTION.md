# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.9`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：Human 可见进度与结果使用当前任务的对象和动作表达；入口判断、能力选择、职责路由、协作调度、记录和传输状态只在影响 Human 决定、授权、恢复或下一步时展示。`using-sacha` 直接处理时不单独报告入口结果，Direct 与完整流程场景分别核对任务表达和内部运行证据。
- 当前 breaking boundary：`0.12.9` 只修正 Human 可见输出投影，不改变入口、Role、Gate、Artifact、Owner、授权或 Runtime 传输。
- 当前成熟度：`0.12.9` 采用快速发版证据边界；4 个目标文件的有界 diff 与 whitespace 已核对，`executor-only` source-scenario 的任务结果和 verifier 通过。完整父任务 Human 投影、完整 Sacha 流程、安装/cache parity 与 fresh discovery 未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
