# DSH Single Companion 与 Root Tool Surface 迭代

> 状态：Human 已批准实施（Scope revision 2）

## 目标

把现有 DSH child surface 与 Visualizer 合并为一个 `@sacha-orchestra/dsh-companion`，并在安装该 companion 的整个 DSH Profile 中实现任务感知、可恢复的 Root 最小充分工具面。Root 首轮不再暴露完整长尾目录；隐藏能力通过一个 companion-owned control tool 查询和解锁。Sacha Core、Role、Gate、授权、Outcome 与完成判断保持不变。

Revision 1 已完成 continuable child、research/review allow-list、Reviewer/barrier Runtime 和 Visualizer reduced-motion 修复；其原始结果保留在本任务的 Execution Report、Review 和 `.temp/runtime-scenarios/2026-08-29-dsh-adapter-full-chain-01/`，Revision 2 在此基础上继续。

## 范围

本次包含：

- 把 `integrations/dsh/sacha-visualizer` 与 `integrations/dsh/sacha-subagents` 合并为唯一 `integrations/dsh/sacha-companion` / `@sacha-orchestra/dsh-companion`；
- 单包同时提供 DSH Profile bundle、Root tool-surface policy、`sacha_research` / `sacha_worker` / `sacha_review`、Host 状态路由、`sacha_visual_event` 与 Web Client Visualizer；
- 对安装该 companion 的整个 Profile 中所有 live Root Agent 生效；Root 必须同时满足 AgentRegistry root 且没有原生 `subagent/descriptor`。continuable activation 虽会出现在 `roots()`，仍按 descriptor 判为 child；subagent、teammate 与其他非 Root Agent 不安装 Root policy，并在自身 scope 移除从 Root 继承的 `sacha_tools`；
- 在 `agent/session-start` 先安装 fail-closed Root policy；首条 human inbox message 进入但 driver 尚未 assembly 时，确定 `inspect | execute | review` 基础 profile，歧义默认 `inspect`；后到达的 global tools 通过 `tools/change` 纳入同一个有界 snapshot 并原子替换 policy；
- 使用 DSH scoped restriction、assembly filter 与 execution guard 保持 schema、prompt guidance、lookup 和执行一致；
- 注册一个 exact-scope `sacha_tools`，用 `status | catalog | help | unlock | reset` 处理可见状态、隐藏工具查询与下一 step 解锁；
- 从既有 durable `agent/inbox/spliced` / 首条 human `user/message`、成功配对的 `sacha_tools` call/result 和 `request/header` 重建 surface，不新增自定义 Session event；
- Visualizer 在现有“任务进展”层级中显示当前工具面模式、可见/隐藏数量、临时解锁与 fallback 警告；精确工具列表留在状态 route/详情，不占默认面板主要空间；
- 更新单包 validator、release path、安装迁移、Runtime task pack 与真实 DSH Web 验收。

本次不包含：

- 改变 Intake、Workflow、Coordination、Assurance、Artifact、Role/Skill 职责或 `using-sacha` 入口；
- 吸收 Routing Suite 的 spec/react/weak persona band、模型特定 trajectory 结论、近距离引导、严格阶段 Workflow、mode subagent、injector/hot-reload 或第二套 Tool Registry；
- 首个 durable tool call 后自动恢复完整 Standard catalog；长尾能力只通过明确解锁或安全 fallback 进入下一次请求；
- 新增 Sacha 专属流程节点、Gate、Artifact、授权、完成判断或远程服务；
- 修改 DSH 源码 checkout、Codex Adapter、Project Capability Binding、其他 Runtime、commit、tag、push 或 release。

## 项目事实与技术决定

- 两个现有目录共 53 个 tracked 文件；合并以 Visualizer 的 Host/Client/build package 为基底，47 个文件可原样移动，`README.md`、`package.json`、`cordis.patch.yml` 合并，subagents 的 3 文件内容被吸收后删除。
- Package path/name 改为 `sacha-companion`；为避免无消费者的 UI/storage 迁移，内部 `sacha-visualizer` plugin id、`/plugins/sacha-visualizer/*` endpoint、`sacha_visual_event` 与 localStorage key 保持不变。
- 当前 DSH 为 `0.1.1-rc.2`。`agent.ctx.tools.restrict()` 可过滤 global 与 standing-preset 祖先工具、返回可解除 disposer，并让 schema/lookup/执行一致；当前 Agent exact-scope 注册的工具不受自身 restriction 影响。
- Agent Teams 把 policy/tool 直接注册在 Root exact scope；因此 companion 必须额外在 `system-prompt/assemble` 过滤 same-scope schema 与已配置 guidance section，并用 `agent.ctx.tools.guard()` 拒绝未允许执行。仅改 schema 或仅用 restriction 都不构成正确实现。
- 新限制采用 new-first replacement：先注册候选 restriction/guard/assembly policy，成功后交换并解除旧限制；失败时保留旧 surface，不出现瞬时全量窗口。
- Root 首轮分类使用 `agent/inbox/inserted` 且只接受 `message.source.kind="user"`；该事件发生在 wake/assembly 前。`agent/pre-step` 晚于 `systemPrompt.assemble()`，不得用作首轮 surface 决定。
- `sacha_tools` 是 Root exact-scope registration，天然不受 inherited restriction 移除；其 `catalog/help` 只返回当前 Agent 未受限初始 view 与启动期 late global registration 合并后的有界 metadata，`unlock` 只接受该 snapshot 中的名字或已定义 family。
- 同一 assistant response 中，`sacha_tools.unlock` 后紧随的未广告工具必须由 request-header guard 拒绝；只有下一 step 的 `request/header.tools` 已包含该工具后才能执行。
- Root 基础 profiles：
  - `inspect`：读取、搜索、`skill`、必要 Web、Human 交互、`sacha_research` 与 companion 观测；
  - `execute`：在 inspect 基础上增加文件写入、平台 shell、任务清单、必要 job 与 `sacha_worker`；
  - `review`：读取/搜索、平台 shell、`skill` 与 `sacha_review`，不直接暴露项目写工具；
  - MCP/App、Agent Teams、普通 subagent/workflow、调试器、部署和其他长尾工具默认隐藏，通过 `sacha_tools` 查询/解锁。
- 首条 human message 使用确定性保守分类：明确实施/修改/构建为 `execute`，明确复核为 `review`，其他为 `inspect`。Role Skill 的成功加载可作为后续 profile hint，但不改变 Role/Gate/授权事实。
- 不新增自定义 Session event：当前 DSH persistence 对外部 unknown event 会失败。Cold resume 按“最后一次成功 `sacha_tools` control → 首条 human message 分类 → pending human inbox → bootstrap”重建；`request/header` 只记录实际 exposure 审计。
- Visualizer 目标读者只需要知道当前是“查看/处理/确认结果”、工具已收窄或临时开放、是否需要处理 fallback；完整 tool name、schema、Session id 与内部 mode 只留在状态数据或诊断详情。

## 实施前提与依赖

- 迁移前重新核对 Visualizer 4 个 pre-existing dirty 文件仍为同一内容；目录移动必须保留字节内容与修改，不格式化或回退。
- 当前只迁移获授权的 `web` Profile；`desktop` Profile 仍只装旧 Visualizer，除非 Human 另行授权。最终结果必须披露该安装差异。
- Root policy 只使用当前 DSH 已确认的 `Agent.ctx`、ToolRuntime、SystemPrompt 和 Session 现有事件；任一 seam 在真实 loader composition 中不可达时停止相关写入，不改 DSH 源码绕过。
- Agent Teams same-scope schema/section/execute 三层必须使用同一 effective allow 集；不一致时 companion 启动或请求失败关闭，不静默放宽。

## 实施方案

1. 修改 `PLUGIN_DESIGN.md`、根 `AGENTS.md` 与 DSH Adapter，建立单一 companion 的 Owner、产品边界和读取入口；Core/Workflow/Role Skill 不变。
2. 冻结两个旧目录、当前 Profile 和 Visualizer dirty preimage；把 Visualizer package 移到 `sacha-companion`，合并 child patch、peer dependencies、README 与 package identity，删除旧 subagents package。
3. 在 companion Host 增加 Root policy：root attach/HMR、tool snapshot、inbox classifier、profile state、restriction replacement、assembly filter、execution guard 和 `sacha_tools`。
4. 复用现有 Session records 实现 recovery fold；Host state route 增加 tool-surface snapshot，Normalizer/Client 只增加读者需要的简短状态。
5. 合并 validators 和 release mapping，更新根导航、Adapter path、CAT_ART_PROMPT 等当前消费者；历史 `docs/plan/**` 保留旧路径作为当时事实，不批量现代化。
6. 新增 `dsh-companion-root-surface-routing` task pack，验证 inspect/execute/review 首个 `request/header.tools`、隐藏长尾、catalog/help、same-response unlock 拒绝、next-step unlock、reset、cold resume、subagent 不继承 Root policy、Agent Teams same-scope 隐藏与 fallback。
7. 运行单包 offline install/verify/pack、相关 Python tests、`cprobe`；迁移 `web` Profile：remove 两个旧包、add 一个 companion，核对 package/lock/bundle/junction/dump-config 后重启唯一 DSH Web。
8. 用 fresh Root A/B 对比 Standard baseline 与 companion：工具数/schema tokens、错误工具选择、合法任务完成、unlock 额外轮次、resume exposure；复跑 continuable barrier/Reviewer 受影响路径和真实 Visualizer Human 验收。

## 验收标准

- `web` Profile 只安装一个 `@sacha-orchestra/dsh-companion`；旧 visualizer/subagents dependency、bundle row 与 junction 消失，无无关依赖升级。
- fresh inspect/execute/review Root 的首个 `request/header.tools` 与分类 profile 一致；MCP/App/Agent Teams/普通 subagent/workflow 默认不在 schema，隐藏调用被 guard 拒绝。
- `sacha_tools` 始终可见；catalog/help 有界返回真实 snapshot；unlock 同 response 不允许隐藏工具，下一 step header 出现后才允许；reset 恢复基础 profile。
- DSH 重启或 cold resume 后，surface 与成功 control 历史一致；不依赖未落盘内存、自定义未知 event 或 Agent 自报。
- child `sacha_research/worker/review` 保持 Revision 1 的 toolFilter、continuable、depth、settlement 和独立 Reviewer 行为，且不安装 Root `sacha_tools` policy。
- Visualizer 状态 route 与真实 `request/header.tools` 一致；默认面板用自然中文显示当前工具面状态，不暴露无行动价值的完整内部目录。
- Root 125-tool 误调复现消失；合法 inspect/execute/review 任务与原验证器通过，fallback/discovery 失败明确且可恢复。
- Core、Workflow、Role Skill、Codex Binding 与其他 Runtime 0 修改；Linux、desktop 或其他未执行环境明确标未验证。

## 失败保护与回退

- Visualizer dirty hash/计数变化、迁移目标已存在、目录移动不能保持内容、Profile 安装拟更新无关依赖或单包 pack 缺文件时停止。
- 分类、restriction、assembly filter、guard 或 recovery 任一层不一致时保留旧安装/当前运行进程和 evidence，不用提示词代替 enforcement。
- Profile 迁移先保存 package/lock/patch/process preimage；旧包 remove 与新包 add 任一步失败时，不继续重启，报告部分完成与恢复命令。
- `sacha_tools` 不提供删除、安装、权限、网络或任意命令能力；unlock 只改变当前 Root 的 model-visible/executable tool surface，不授予工具本身没有的权限。
- 不删除 Runtime Sessions、`.temp` evidence 或旧包源码历史；不执行 Git/release 动作。

## 风险与未验证项

- DSH `tools.restrict` 不删除独立 guidance，需真实验证 assembly filter 的 section allow/deny 映射；不存在 tool→section 自动 Owner metadata。
- Profile 含第三方 exact-scope tools 时，snapshot/assembly/guard 必须能一致处理；未知 local tool 默认隐藏并进入 catalog diagnostics。
- 当前 Routing Suite 的 persona/trajectory 证据与其 v34 研发线不作为本项目验收；本项目只吸收 task-aware surface、查询/解锁和恢复机制。
- `desktop`、Linux、Code Mode、长期 compaction 后 surface 与非 reduced-motion UI 另行验证，不阻塞当前 Windows Web Profile。

## 主要代码与资源位置

- `integrations/dsh/sacha-companion/**`
- `plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md`
- `PLUGIN_DESIGN.md`
- `AGENTS.md`
- `README.md`
- `scripts/release.py`
- `tests/validate_dsh_companion.py`
- `tests/test_dsh_companion.py`
- `tests/runtime-scenarios/packs/dsh-companion-root-surface-routing/**`
