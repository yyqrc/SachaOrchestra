# Executor task migration Review

## R1 Verdict（已失效）

Accepted；后续 owner-transfer 语义改变使该 Baseline 失效，等待 R2。

## Findings

无。

首轮 Review 曾发现两个阻塞项：README/Adapter 仍暴露已移除的 Pi 执行路线；Execution Report targeted 计数失效。Executor 修复 consumer、增加 coherence 反向断言并更正证据索引后，同一独立 Reviewer scoped re-review 通过。

## 验证

- migration targeted：7/7 passed。
- candidate coherence：pass，0 failures。
- scoped `cprobe`：0 staged、0 conflict、0 whitespace error。
- 实现 Baseline：全量 unit 24/24、Project Setup 45/45。

## 剩余边界

R1 只接受当时的 source/static 层；不覆盖后续“旧 task 不等待、完整 owner transfer”修订。

## R2 Verdict

Needs Fix。

## R2 Findings

- Coordination 的通用 transition 不变量仍强制 terminal return，与单向 owner transfer 冲突。
- Codex/Claude Adapter 的 Workflow owner 表仍把旧 root/主对话描述为一直推进到根终态。
- Execution Report 仍要求 Claude terminal return；回归也未反向锁定这些旧语义已消除。

上述项已由 Executor 修复，等待 R3 scoped re-review。

## R3 Verdict

Accepted（source/static Scope）。

## R3 Findings

无。R2 的 return 不变量、Runtime owner 表、Execution Report 与反向回归缺口均已关闭。

独立 Reviewer 复核了显式授权、identity/dedup、single writer、create 前失败回退、成功后旧 task 不恢复 owner、最小 Handoff、ready 单元 subagent 派发、独立 Reviewer 和 Codex Adapter Pi 路线移除；targeted 7/7、candidate coherence 与 scoped `cprobe` 均通过。

## R3 剩余边界

未覆盖安装后 fresh discovery、真实 context/compaction signal、`create_thread` owner transfer、重复输入 dedup，以及 target 端完整 Execute→Review/返修→closeout 的 Runtime 行为。

## R4 Verdict

Needs Fix。

## R4 Finding

- 通用派发重评估在 Coordination、Codex Adapter 和测试中被收窄成“首次出现可委派工作”，会漏掉执行中后续新形成的一批 ready 单元；Adapter 还漏列“依赖满足”。

Executor 已统一为实施前及每次出现新可委派工作时重新识别，并补齐依赖条件；等待 R5 re-review。

## R5 Verdict

Accepted（source/static Scope）。

R4 finding 已关闭：Coordination、Codex Adapter、普通同-task 回归和 Spec 均锁定“实施前及每次出现新可委派工作时”重新识别，并保留“依赖满足”。阻塞 findings 为 0。

剩余 Runtime 边界：未实测执行过程中后续新增 ready 单元触发再次分解、实际 `spawn_agent` 数量/时序，以及普通同-task和 migration target 的真实派发行为。

## R6 Verdict

Needs Fix。

R6 发现 `test_prompt_surfaces.py` 仍以 `description <= 100`、`default_prompt <= 90` 阻塞 unit，绕过 coherence advisory。Executor 已删除该重复长度测试，并让 validator-design 覆盖这个 release-blocking test surface；等待 R7。

## R7 Verdict

Accepted（source/static Scope）。

纯文本字符/行数 hard fail 已清除；统一 advisory warning 不影响 status/exit。正式 metadata schema、结构、版本、owner/link、禁止边界以及生产输出安全上限仍保持 hard fail。阻塞 findings 为 0。

## R8 Verdict

Needs Fix。

- Evolution 的旧 Managed Parallel 章节仍要求调用方先准备 ready Work Packet，并把 Manager 收窄为核对既有 packet，与 Coordination 7 的唯一 owner 冲突。
- Spec/Artifact validator 仍有一组 Documentation 中文整句 `assertIn`，不能证明行为，且与测试精简声明冲突。

## R9 Verdict

Accepted（source/static Scope）。

R8 两项已关闭：Evolution 允许多个候选单元直接进入 Manager，并只引用 Coordination 的评估、拆分、依赖、readiness、派发与归并 owner；Documentation 逐句文案测试已删除，保留的 3 项只覆盖公共 API、真实生成输出和旧标识禁入。

独立重跑：Spec/Artifact 3/3、完整 `test_*.py` 22/22、candidate coherence 0 failure/4 advisory；有界 cprobe 完整、0 conflict、0 whitespace error。未发现新 blocking finding。

剩余 Runtime 边界：未验证安装后 fresh discovery、真实 context/compaction signal、`create_thread` 去重/owner transfer、自动模型 route/fallback、wait/cancel，以及迁移 target 的完整 Execute→Review→closeout。

## R9 后续 Baseline

Human 后续把 Codex 自动模型收敛为 Sol xhigh、Sol medium、Luna max、Luna xhigh，并要求简化难度分类；因此 R9 不覆盖这一后续 delta。当前 source/static 自检为 route 4/4、完整 unit 22/22、candidate coherence 0 failure；未将其记作独立 Reviewer verdict。

同一后续 Baseline 又把 owner/consumer/历史 superseded 纪律写入 Project AGENTS，并标记 Evolution `0.3.0` 与 2026-08-04 旧 Spec 的冲突操作说明；仍属于 R9 后自检，不改写 R9 provenance。

## R10 Verdict

Needs Fix。

最终 release Review 发现合法 Clarify `research-ready` 会按 Codex Adapter 四档路由进入 Luna named agent，但两个 Agent definition 只接受 Scope/验收已冻结的 Executor 子任务；实例 started 后拒绝时也不能安全 fallback。现有绿色测试没有交叉核对 route 与 named definition 的接受边界。

## R11 Verdict

Accepted（source/static Scope）。

R10 finding 已关闭：两个 Luna definition 现在都明确接受 `execution-ready` 和只读 `research-ready`，后者不再要求实施 Scope/验收冻结；既有 Setup Agents 幂等测试对实际写入并回读的两个 TOML 核对 execution/research readiness、研究只读、旧拒绝句消失及重复执行。

独立重跑：Setup Agents 13/13、完整 unit 22/22、candidate coherence 0 failure/4 advisory、Setup Agents quick validator 与 plugin validator 全部通过；scoped `cprobe` 完整、0 conflict、0 whitespace error。最终 blocking finding 为 0。

剩余 Runtime 边界：安装/cache parity、fresh discovery、真实 Clarify research 自动路由、模型/fallback、`create_thread`、wait/cancel、依赖波次与 migrated target 完整 lifecycle 尚未由本 source/static verdict 证明。

## R12 Verdict

Needs Fix。

候选安装后的 fresh Feedback dry-run 发现两个相连缺口：Codex Adapter 在压缩时丢失了 Feedback 所需的原生 task 查询、唯一创建和 terminal join 映射；若该 repair target 再按普通批准迁移，上游 Feedback Source 仍等待旧 target，而合同没有安全重绑 return consumer 的 transport。Executor 已恢复 Feedback 的 `list_threads`/有界 `read_thread`、`create_thread`、`wait_threads` 映射，并禁止有上游 return consumer 的 task 做用户可见 migration，等待 R13 scoped re-review。

## R13 Verdict

Accepted（source/static Scope）。

R12 两项已关闭：Feedback Source 通过独立原生 transport 查询、唯一复用/创建 repair target，并以带 cursor 的有界 `wait_threads` 消费一次根终态；repair target 有上游 return consumer，保持唯一 workflow owner，不得嵌套 migration。普通批准后的用户可见 migration 仍只在无上游 consumer 时做 no-wait 单向 owner transfer，两条路径的 single writer 与 identity/dedup 无冲突。

独立重跑：targeted scenario 3/3、完整 unit 22/22、Project Setup 45/45、candidate coherence 0 failure/4 advisory、Feedback quick validator、plugin validator 与 scoped `cprobe` 全部通过。release validator 只检查 section/tool 结构，return-consumer 语义由 scenario test 覆盖，未重新引入中文整句发布阻塞。

剩余 Runtime 边界：尚未实测真实 `list_threads`/`read_thread` 唯一匹配、无匹配 `create_thread`、cursor timeout、`wait_threads` 根终态一次消费、重复输入 dedup，以及 repair target 实际拒绝嵌套 migration。

## Installed dry-run

最终 source candidate 精确重装后，fresh installed Feedback simulation 判定 `顺畅（source/static）`：安装包可以从显式 Feedback 的唯一 query/create/wait transport，连续推导到 target 内 Planner/Clarify、普通批准同 task Executor、Manager 依赖波次、四档 subagent route、独立 Reviewer、closeout 和唯一 terminal return；有上游 consumer 的 repair target 不再嵌套迁移。该结果没有实际调用 task/subagent transport，不提升 R13 的 Runtime 证据等级。
