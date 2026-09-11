# Sacha Orchestra 演进路线图

> 本文只保存当前版本身份、待发布 Scope、breaking boundary、成熟度和尚未实施的长期方向；成熟度只记录已经完成的关键证据和具体已知问题，不枚举未触发的验证项。现行产品入口、流程、Owner、验证与发布规则由 `PLUGIN_DESIGN.md`、`AGENTS.md` 和对应 Runtime Owner 定义。

## 当前版本线

- 当前 release：`1.0.6`；发布身份以同名 annotated tag `v1.0.6` 为准。
- 当前源码版本：`1.0.6`，本次确定范围无剩余待发布改动。
- 当前 release Scope：Planner 在设计时消费需求边界；Spec 保存预期改变、保留行为、排除做法、必要理由与验收；实施、复核和跨上下文恢复按同一规格检查。沿用既有角色与 Spec 栏目，不强制简单任务生成 Spec 或重复确认，不新增 Gate 或状态格式；独立 DSH 配套包不随主插件发布或安装。
- 当前 breaking boundary：Codex 不再提供 v1 或接口/模型自动回退，使用方须满足现行 v2 能力组合；Pi 入口、CLI 参数与配置兼容已移除，原 Pi 使用方须改用当前支持的运行环境。旧项目文件只在后续正常获授权的 setup 事务中更新，本次发布不自动迁移项目或部署 Profile。DSH 后续明确任务指令会更新基础工具集并清空临时解锁。
- 状态与文档兼容：实施批准只覆盖本次唯一 Spec 在全部阻塞验收满足后的状态行更新，正文保持原样；项目文档仍须已有具体授权，阻塞文档未完成时不得收口。生成器保留显式过期原像拒绝、临近写入复查、失败补偿及旧 SOURCE SHA-256 解析；未新增数据格式迁移要求。
- 当前成熟度：Astra 基线的源码、定向测试、结构及隔离包证据见[实施记录](docs/plan/2026-09-05-astra-full-audit/execution-report.md)，独立复核 Accepted with follow-up。阶段二的 32 项发布测试及独立复核 Accepted 见[开发与发版整理](docs/plan/2026-09-05-rule-simplification-stages/stage-2/execution-report.md)；阶段三的 44 项生成器测试、独立源码复核 Accepted，以及同一 Astra/medium 上下文五条输入的隔离 source-scenario 独立评估 pass 见[运行流程整理](docs/plan/2026-09-05-rule-simplification-stages/stage-3/execution-report.md)。这些证据分别证明其范围，不证明安装后全新发现或其他宿主行为；Astra 旧规格案例初稿 drift、修订内容 pass，但因缺工具轨迹，完整原生流程仍未证实。DSH 构建保留一条 CommonJS/ESM 建议警告，部署应采用已验证的干净隔离产物。

- 此前规则独立语义复核 Accepted；隔离入口场景按明确要求直接修改，未多余询问或创建 Spec，但可见回复暴露内部流程词，完整场景为 drift。已知表达偏差保留，不声明安装后行为、Editor 合并测试或新模型路线的实际节省比例已验证。此前入口场景的派发控制消息不可读及代理数量限制仍只按其原始证据范围说明。

- 共享编译规则独立增量复核 Accepted；`shared-compilation-input` 三阶段 source-scenario 独立评估 pass：写入未完成时不启动共享验证，稳定批次失败后保留责任，修正后一次补验通过。该 Python 场景不证明 Unity/Refresh、实际程序集依赖发现或工具层互斥。

- 委派与上下文成本场景 `delegation-context-cost` 的修补后 source-scenario 独立评估 pass（运行 `20260909-122226`，主任务 `01a08467-471a-74a0-95b8-2a55fb8a0f8c`）：隔离读取、单层派发、稳定输入验证、连续目标复用及恢复内容通过；先前运行的越界读取保留为 drift。未证明缓存收益、实际跨窗口恢复、未触发的同级事实通信或安装后发现。

- `1.0.5` 已完成源码差异、插件结构及新增场景验证器的正反例自测；Human 明确要求先发布，`delegation-serial-evidence` 真实派发场景未运行，未取得本轮独立运行裁决或可比成本数据，不声明实际 token 节省比例。

- `1.0.6` 的 `project-facing-spec` 两阶段 source-scenario 独立评估 pass（运行 `20260911-181100`；规划 `01a08ff3-2dc1-7722-b0dd-00ba8978ef08`，恢复 `01a08ff6-04b9-7e60-b97c-e15fc637fc3a`，评估 `01a08ff2-8ccb-7e42-aafd-468de027cbfe`）。新上下文只读取项目定义与实际 Spec，保留需求边界及关键排除理由；原始工具轨迹与产物复制哈希已核对。首轮 `20260911-180513` 的未定义简称及排除理由遗漏保留为 drift，补强 Planner 定稿检查后新轮通过。插件结构检查通过；这些证据不证明安装后发现、真实宿主自动压缩或领域代码执行。

## `1.0.6` 后续方向

用户已决定从 `0.x` 预发布版本线进入 `1.0.0` 主版本。真实并行、自举升级、第二 Runtime、安装后案例或额外历史 Review 不作为人为举证门槛；已知问题与证据边界按实际影响处理。

Self-hosting 是可选使用方式，不是成熟度等级。`1.0.0` 后只有真实需求出现才评估跨仓库协调、更复杂取消/恢复、动态并行度或额外 Runtime；不得为证明通用性预建产品面。
