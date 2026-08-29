# DSH Single Companion 与 Root Tool Surface 实施报告

> 身份：Scope revision 2 的当前实施记录；取代同路径旧 Revision 1 报告。
>
> Outcome：`Accepted with follow-up`

## Human 确认目标

- 把 `sacha-subagents` 与 `sacha-visualizer` 合并为单一 `@sacha-orchestra/dsh-companion`；不再新增 companion plugin。
- 在获授权的整个 DSH `web` Profile 对 Root 实施 Routing Suite 的标准吸收：按任务选择 `inspect | execute | review` 小工具面、用 `sacha_tools` 有界查询和按需解锁、从既有 Session 记录恢复，并把状态投影到现有 Visualizer。
- 不吸收 persona bands、严格 phase、injector、mode subagent 或首次 durable call 后自动恢复完整目录。
- 不改变 Sacha Core、Workflow、Role、Gate、授权、Artifact、Outcome 或完成判断。

## 实际 Owner 与文件变化

- `PLUGIN_DESIGN.md`、根 `AGENTS.md`、根 `README.md`：开发控制面改为单一 DSH companion Owner 与导航。
- `plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md`：保存 DSH Root surface、continuable child、回退、恢复和直接证据映射；没有反向定义 Core 判断。
- `integrations/dsh/sacha-companion/**`：由原 Visualizer 目录迁移并吸收原 subagent bundle；保留 Visualizer 内部 endpoint/storage identity，新增 Root policy、五个平台条件 child rows、Host state 与 Human 面板投影。
- 删除旧 `integrations/dsh/sacha-visualizer/**` 与 `integrations/dsh/sacha-subagents/**` tracked 路径；release 映射把这些退休路径仍路由到新 companion 测试与 validator。
- `tests/validate_dsh_companion.py`、`tests/test_dsh_companion.py`：合并 package/bundle/child surface 结构与负例。
- `tests/runtime-scenarios/packs/dsh-companion-root-surface-routing/**`：新增真实 Root surface 场景包、Oracle 与空白 fixture。
- `scripts/release.py`、`tests/test_release.py`：单包候选验证与旧双包删除迁移覆盖。
- `docs/plan/2026-08-29-dsh-adapter-full-chain/spec.md`：保存 Human 批准的 Revision 2 不变量、实现边界与验收。

没有修改 `plugins/sacha-orchestra/core/**`、Workflow、Role Skill、Codex Adapter 或 Capability Binding。

## Root policy 实现

- `agent/session-start` 先安装 fail-closed policy，保证 cold resume 的 settlement/relay 不会先以完整工具面运行；首条 Human inbox 在 driver wake 前完成分类。
- 明确只读阶段与问题默认 `inspect`；明确实施为 `execute`；明确只读复核为 `review`。附带“不要修改 Core”“交付前独立复核”不会覆盖主实施动作。
- `restrict()` 只处理 inherited tools；`system-prompt/assemble` 过滤 same-scope schema 与具名 guidance；`guard()` 拒绝未允许或尚未由最后 request header 广告的调用。
- 用 rc.2 公共 `restrict({allow: []})` 同步探针区分 inherited 与 exact-scope 工具；Agent Teams 与第三方 same-scope 工具可以查询并在下一 step 解锁。
- `tools/change` 有界合并启动期 late global registrations，并用 new-first 顺序替换 policy；失败保留旧限制。
- `sacha_tools status` 只返回 profile、数量、source、unlocked、fallback 与 warnings；`catalog/help` 才按 query 有界返回 metadata。
- durable fold 优先消费成功 control result 中已提交的 exact `unlocked`，不会把历史 family selector 扩展到未来同 family 工具。
- continuable activation 虽进入 `AgentRegistry.roots()`，仍以原生 `subagent/descriptor` 判为 child；child 不安装 Root policy，并在自身 scope 移除继承的 `sacha_tools`，其他 toolFilter 不变。

## 静态、构建与 package 证据

- Host、Client、Preview TypeScript：3/3 通过。
- Vitest：8 files、32 tests 全部通过；含真实 Cordis/SystemPrompt/ToolRuntime/Scope 分层、late global merge、classification、durable exact recovery、child control suppression。
- Python：`tests.test_release` 与 `tests.test_dsh_companion` 共 35/35 通过。
- `tests/validate_dsh_companion.py`：通过；5 个平台配置 row、3 个 surface、research/review allow-list、worker deny、`maxDepth: 1` 与 peer range 符合预期。
- 从无 `lib` 的隔离 `clean-package-candidate` 执行 offline frozen install、`pnpm verify` 与 `pnpm pack --dry-run --json`：35 files；Host、Client、policy、patch 与 artwork 齐全，无 dirty checkout 的旧 `activity-model` 残留。
- 受影响 Scope 的 `cprobe` 均 `budget.complete=true`、`whitespace.errors=0`、无 staged/conflicted 内容。

## 安装与进程

- DSH：`0.1.1-rc.2`。
- 获授权的 `web` Profile 当前 dependency 与 bundle 只保留 `@sacha-orchestra/dsh-companion`；junction 指向当前 checkout 的 `integrations/dsh/sacha-companion`。
- 最终 DSH Web PID `86784`，命令为 `dsh web --no-open`，监听 `127.0.0.1:3080`。
- Profile 安装被既有 `dsh-context@0.38.1` minimum-release-age 检查拦截时，只在一次命令内临时加入该精确版本并在成功后移除；没有放宽全局配置。
- 本轮未在迁移前保存紧邻的 package/lock preimage，因此不能独立声称其他依赖版本确定未变化；只能确认当前单 companion Profile 可构建和运行。

## Runtime 直接证据

原始证据保存在 `.temp/runtime-scenarios/2026-08-29-dsh-companion-routing-01/`。

### Inspect、查询、解锁、reset 与 cold resume

- Root：`session-b7d00cb5-d288-41c1-8aa7-1555bb8d960a`。
- seq 12 首 header：10 tools；MCP/App、Agent Teams、普通 subagent/workflow 与写入长尾均隐藏。
- seq 274–277：`status` 只返回 10/116 与恢复摘要；`catalog(query=wait_agent)` 能发现 Root exact-scope `wait_agent`。
- seq 788–789：解锁 `wait_agent` 成功；seq 792 下一 header 才增加为 11 tools；seq 851–852 原生调用返回 `noProgress=no-active-peer`。
- seq 1067–1071：`reset` 后 header 恢复 10 tools。
- 重启后 status 为 `profile=inspect`、10/116、`source=control`、`unlocked=[]`、`fallback=false`；late global catalog 保持 126 个总工具视图。

### Same-response guard

- Root：`session-f642354a-d661-4914-9064-56ca5c3789e3`。
- seq 12 首 header 不含 `list_agents`。
- 同一 assistant message/step 内，seq 1031 请求 unlock，seq 1033 同时请求 `list_agents`；seq 1032 unlock 成功，但 seq 1034 的 `list_agents` 以 `isError=true` 拒绝，原因为尚未由最新 request header 广告。
- seq 1037 下一 header 才出现 `list_agents`。

### Execute 与 review 分类

- Execute Root `session-5a8cfbd5-0720-461c-a7aa-8eb6a1d5a557`：真实长句含“不要修改 Core”“交付前完成独立复核”，首 header 仍为 18-tool execute surface。
- Review Root `session-3d2c5c20-06ef-4c4e-bc22-af2e8c330452`：任务“审查这些改动，给出修改建议”，首 header 为 9-tool review surface，含 `pwsh`/`sacha_review`，不含 write。

### Continuable child 隔离

- Root `session-43b3e722-de47-4d53-bd16-c980e3a6f754` 创建 research child `e620640c-bcc0-4c8e-9478-255cb2b276cb`。
- child descriptor：`mode=continuable`、`provider=spawn`、原 research allow-list。
- child header 仅 `glob/grep/read/read_image/report/skill/web_search`，无 `sacha_tools`；实际调用 `glob/grep/read/report`，无下级创建。

### Visualizer

- live state route 返回 profile、visible/hidden/advertised 精确名单、unlocked、source 与 fallback。
- 真实浏览器面板显示“当前可用能力 / 已收窄为查看工具 / 10 个可用 / 116 个暂时收起”，不默认展开内部工具名；截图为 `tool-surface-panel.png`。
- 既有 reduced-motion selector 修复保留；最终非 reduced-motion 分时动画未重验。

## Accepted with follow-up

1. `desktop` Profile 仍链接已删除的旧 `integrations/dsh/sacha-visualizer`，是已知 stale/broken link；Desktop 不在本次获授权 Web Scope，迁移需另行授权。
2. family unlock 后 late same-family registration 不扩权由源码、真实 ToolRuntime 与 Vitest 覆盖，未另造完整 DSH Runtime 场景。
3. Linux 与最终非 reduced-motion 动画未验证。
4. 本轮缺紧邻安装前 Profile preimage，不得声称无关依赖版本确定未变化。

