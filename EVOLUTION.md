# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；成熟度只记录已经完成的关键证据和具体已知问题，不枚举未触发的验证项。现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`1.0.0`；发布身份以同名 annotated tag `v1.0.0` 为准。
- 当前源码版本：`1.0.0`，本次确定范围无剩余待发布改动。
- 当前 release Scope：纳入 Astra 基线、Codex v2 能力与模型路由、Pi 完整退役、生成器正确性、术语单源和测试/场景精简；开发与发版复用有效证据；运行流程按当前决定与实际收益研究、协调和增量评审，实施批准覆盖满足全部阻塞验收后的唯一 Spec 状态收口。仓库同时包含 DSH 明确指令切换和状态展示修复；独立 DSH 配套包不随主插件发布或安装。
- 当前 breaking boundary：Codex 不再提供 v1 或接口/模型自动回退，使用方须满足现行 v2 能力组合；Pi 入口、CLI 参数与配置兼容已移除，原 Pi 使用方须改用当前支持的运行环境。旧项目文件只在后续正常获授权的 setup 事务中更新，本次发布不自动迁移项目或部署 Profile。DSH 后续明确任务指令会更新基础工具集并清空临时解锁。
- 状态与文档兼容：实施批准只覆盖本次唯一 Spec 在全部阻塞验收满足后的状态行更新，正文保持原样；项目文档仍须已有具体授权，阻塞文档未完成时不得收口。生成器保留显式过期原像拒绝、临近写入复查、失败补偿及旧 SOURCE SHA-256 解析；未新增数据格式迁移要求。
- 当前成熟度：Astra 基线的源码、定向测试、结构及隔离包证据见[实施记录](docs/plan/2026-09-05-astra-full-audit/execution-report.md)，独立复核 Accepted with follow-up。阶段二的 32 项发布测试及独立复核 Accepted 见[开发与发版整理](docs/plan/2026-09-05-rule-simplification-stages/stage-2/execution-report.md)；阶段三的 44 项生成器测试、独立源码复核 Accepted，以及同一 Astra/medium 上下文五条输入的隔离 source-scenario 独立评估 pass 见[运行流程整理](docs/plan/2026-09-05-rule-simplification-stages/stage-3/execution-report.md)。这些证据分别证明其范围，不证明安装后全新发现或其他宿主行为；Astra 旧规格案例初稿 drift、修订内容 pass，但因缺工具轨迹，完整原生流程仍未证实。DSH 构建保留一条 CommonJS/ESM 建议警告，部署应采用已验证的干净隔离产物。

## `1.0.0` 后续方向

用户已决定从 `0.x` 预发布版本线进入 `1.0.0` 主版本。真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不作为人为举证门槛；已知问题与证据边界按实际影响处理。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
