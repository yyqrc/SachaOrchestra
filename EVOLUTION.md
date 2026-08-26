# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`0.12.7`。
- 当前待发布源码版本：未开始。
- 当前 release Scope：新增 DeepSeek Harness Runtime Adapter，映射官方 experimental Agent Teams 的单层派发、共享 task DAG、mailbox、等待/取消、能力降级与证据边界；新增独立 `@sacha-orchestra/dsh-visualizer` companion package，以标准 `tool/call` / `tool/result` 回放 Sacha 已提交转换，并只读投影可选的官方 Team roster/task 状态。
- 当前 breaking boundary：`0.12.7` 是加法变化；不删除或改写既有入口、Role、Gate、Artifact 与 Codex/Claude Code/Cursor Adapter。DSH companion 不进入 Agent Plugin 发布 `root` 或三个 marketplace，官方 Agent Teams 缺失时只降级 Team 面，不改变 Sacha 流程。
- 当前成熟度：`0.12.7` 采用普通发版证据边界；candidate coherence 0 failures、release script 28 项测试、Sacha Plugin validator，以及 companion staged snapshot 的离线安装、Host/Client typecheck、11 项回放/校验/DAG/面板几何/素材映射测试、bundle 构建与 pack dry-run 通过，独立 Review 为 `Accepted with follow-up`。隔离 DSH Web Profile 已完成 Host、client manifest、布局持久化、固定 DAG、分段进度、鲸鱼素材、state route 与静态素材白名单冒烟；隔离 keyless Agent loop 已持久记录 3 次 `sacha_visual_event` 且 zstd 日志无 torn frame。Sacha Agent Plugin 的 DSH fresh discovery、官方 Agent Teams 派发/恢复、用户 Profile 安装/重启以及真实面板 Human 验收未验证。

## `1.0.0` 与后续方向

`0.x` 保持为 `1.0.0` 前的预发布版本线。Core、Adapter、Skill 职责和 breaking boundary 稳定且没有已知 release-blocking 缺陷时，Human 可决定进入 `1.0.0` 发布收尾；真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不是人为举证门槛。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
