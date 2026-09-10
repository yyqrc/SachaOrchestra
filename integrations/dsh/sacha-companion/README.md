# Sacha Companion for DeepSeek Harness

> 文档身份：独立 DSH companion package；不进入 `plugins/sacha-orchestra` 的 Agent Plugin 发布 `root`。

`@sacha-orchestra/dsh-companion` 是 Sacha 在 DeepSeek Harness（DSH）中的唯一配套包。它合并三个以前分开的责任面：

1. Root Session 的任务感知工具暴露、查询、解锁与恢复；
2. `sacha_research` / `sacha_worker` / `sacha_review` continuable child surfaces；
3. Sacha Manager、delegation、Review、Evidence、Root direct child 与工具面状态的 Host/Client 可视化。

它不接受 Sacha、不决定 Role/Gate/readiness/Scope/授权/调度/Outcome/完成，也不维护第二份 Workflow 或 DAG。安装 package 只改变目标 DSH Profile 的 Runtime 工具组合与观察面。

## Root 最小充分工具面

Companion 只安装在 live Root Agent。当前 DSH 的 continuable activation 也会进入 `AgentRegistry.roots()`，因此 Root 还必须没有原生 `subagent/descriptor`；subagent、teammate 与其他非 Root Agent 不安装 Root policy，并在自己的 scope 移除从 Root 继承的 `sacha_tools`，其他 child toolFilter 不变。Root 在 `agent/session-start` 先安装失败关闭保护，保证冷恢复时也不会先以完整工具集运行。启动期晚注册的 global tools 由 `tools/change` 加入同一个目录快照；替换时先成功安装新策略，再移除旧策略：

| Phase | 进入条件 | 工具面 |
| --- | --- | --- |
| `bootstrap` | 会话首个请求 | read/read_image/glob/grep、`sacha_visual_event`（只读，最小起步面） |
| `resident` | 首个耐久晋升信号，或模型显式切换 | 增加 write/edit、当前平台 shell、todo、web、skill、ask_user_question 与 `sacha_research`/`sacha_worker`/`sacha_review` |

阶段由**耐久会话事件**推导，不解析人类消息措辞：

- 晋升信号是 Runtime 自己写入的首个 `tool/call` **或** `assistant/message`，两者先到者生效。模型发出第一个工具调用或第一条回复，就证明它已经理解任务，工具面随即打开，不需要任何人去读用户那句话想表达什么。
- 本包自身的控制调用不参与晋升。`sacha_tools` 始终可见，若把它计入，一次 `status` 查询、一次单工具 `unlock`，甚至模型主动收窄到 `bootstrap` 本身，都会被误判为"开始干活"。
- 上下文压缩只追加一条遮蔽用的 `user/message`，原始事件仍留在耐久日志中，因此**压缩后阶段与工具面保持不变**，模型不会在任务中途突然失去 write/shell/委派能力。恢复路径与运行路径都从同一份事件推导，两者不会分歧。
- 模型可随时用 `sacha_tools` 的 `phase` 动作显式切换阶段（见下），这是分类之外的**自救路径**；一旦显式切换，自动晋升不再覆盖该选择。

MCP/App、Agent Teams、普通 subagent/workflow、调试器、部署和其他长尾工具在两个阶段都默认隐藏，需要时通过 `catalog` 查询与 `unlock` 取得。工具收窄不改变底层 sandbox/权限，也不能给已隐藏工具之外的操作授权。切换只提交已成功应用的状态，不宣称已停止此前运行的工具或进程。

正确性由三层共同保证：

- `agent.ctx.tools.restrict()` 过滤 global 与 standing-preset 继承工具；
- `system-prompt/assemble` 过滤 same-scope schema 与配置明确的隐藏工具 guidance；
- `agent.ctx.tools.guard()` 在执行前拒绝不属于 effective surface 的调用。

只存在其中一层不算成功：same-scope Agent Teams 等工具不受自身 restriction 过滤，独立 guidance 也不会随 schema 自动消失。

## `sacha_tools`

`sacha_tools` 是每个 Root exact scope 中唯一的工具面控制入口，始终可见；它不执行被管理工具，也不授予权限。

| action | 结果 |
| --- | --- |
| `status` | 当前 phase、可见/隐藏数量、临时解锁和 recovery 来源 |
| `catalog` | 按 query 有界列出已采样目录中的隐藏工具信息；多个词按任意词匹配名称、描述与 family |
| `help` | 返回一个具名工具的描述与参数 schema |
| `phase` | 显式切换 `bootstrap`/`resident`；切换后自动晋升不再覆盖该选择 |
| `unlock` | 把具名工具或已定义 family 加入下一 step 的可见/可执行 surface |
| `reset` | 清除临时解锁并恢复当前 phase |

`unlock` 与 `phase` 成功后，同一 assistant response 中紧随的未广告工具仍被拒绝；只有下一 step 的 `request/header.tools` 已出现该工具后才能执行。这样模型不能在没有见过 schema 的同一批调用里获得新能力。

`catalog` 的检索按词切分并做任意词匹配，因此 `unity editor bridge` 这类自然多词查询能返回它所指的工具；整串匹配会让这类查询恒返回空，使被隐藏的 `sacha_worker`/`sacha_review` 无法被发现。

工具目录保存当前 Root 初始采样和启动期追加的信息，不再按 256 项截断名称；查询返回数量及每项描述、参数大小仍有界限。同名工具更新、删除和上级作用域的动态变化未实现完整同步，执行仍以当前原生工具和 guard 结果为准。

Root policy 不新增自定义 Session event。冷恢复按原生事件顺序重放阶段与成功配对的 `sacha_tools` tool/call+tool/result；显式 `phase` 控制之前的旧控制调用，即使结果晚到也不能重新解锁。失败或未配对的结果不改变恢复状态。每个 `request/header` 是实际工具暴露的审计证据。

## Continuable child surfaces

三个 surface 均使用官方 `@deepseek-ai/dsh-tool-subagent`、`provider: spawn`、`backgroundMode: continuable` 与 `maxDepth: 1`。Sacha 主路径调用必须省略 `run_in_background` 或显式传 `true`；foreground one-shot 不满足 durable child/settlement/recovery 合同。

### `sacha_research`

- allow-list：`read/read_image/glob/grep/web_search/skill`；
- scope-local `report` 由 DSH continuable child setup 保留；
- 无项目写入、shell、MCP/App、Agent Teams、Sacha sibling 或下级派发工具。

### `sacha_worker`

- 保留实施与验证工具；
- deny standard `workflow/subagent/subagent_fork`；
- sibling Sacha tool 不写入 deny-list，避免未知名字产生装配顺序耦合；`maxDepth: 1` 负责强制单层派发。

### `sacha_review`

- allow-list：`read/read_image/glob/grep/skill` 与当前平台 shell；
- Windows/Posix 分行装配 `pwsh` / `bash`；
- shell 仍可能写文件，因此不是硬 read-only sandbox；实际 sandbox、工具目录与行为必须分别记录。

surface 创建失败时报告能力缺口，不得自动改用 standard subagent、Agent Teams teammate 或另一个 Role surface。

## Host 状态与 Visualizer

现有内部标识保持稳定：

- tool：`sacha_visual_event`；
- state route：`/plugins/sacha-visualizer/state?sessionId=<root-session>`；
- artwork route：`/plugins/sacha-visualizer/assets/*`；
- Client/localStorage 使用既有 `sacha-visualizer` namespace。

Host state 由三类事实组成：

- 成功配对的 `sacha_visual_event` tool/call+tool/result：phase、gate、manager_wave、delegation、review、evidence；
- `ctx.subagents.listChildren(rootSessionId)` 与 live Agent registry：continuable direct child 与状态；
- Companion Root policy：当前工具 phase、可见/隐藏数量、临时解锁和恢复诊断。

默认面板只显示读者会据此行动的信息：当前进展、工作依赖、协作任务、工具已收窄/临时开放与需要处理的 fallback。完整工具名、schema、Session id 与内部 route 留在 state JSON 或诊断详情。

评审和证据已知适用修订时传 `scope_revision`；只有与当前阶段修订一致的结果进入当前卡片。旧修订或未关联结果保留在历史记录。面板展开、页面可见且有工作进行时每秒查询，空闲或隐藏时改为每 5 秒查询；连接失败保留上次快照并标明历史身份，重连成功后恢复当前展示。

Visualizer 不从颜色、label 或 child 存在推导 Scope、授权、Outcome 或完成；`unit↔child` 的精确映射以 state route 和原生 Runtime 事实为准。

## Profile 前提

当前 package 面向 DSH `0.1.1-rc.2` standard coding preset 或等价组合。目标 Profile 必须提供：

- Agent/Session/ToolRuntime/SystemPrompt 与 Web Host/Client runtime；
- `@deepseek-ai/dsh-subagent`、spawn provider、continuable settlement/report；
- standard `read/read_image/write/edit/glob/grep`、平台 shell、skill、Web 与 control tools；
- React 与 DSH Client layout/slot surface。

未知 allow-list 名、缺少 provider、Root policy 不能同步 schema/section/guard 或 package build/pack 缺文件时应响亮失败，不静默放宽。

## 构建与验证

```powershell
pnpm install --offline --frozen-lockfile
pnpm verify
pnpm pack --dry-run --json
```

`pnpm verify` 执行 Host/Client/Preview typecheck、Vitest、Host/Client bundle 与 Preview build。静态结果不证明 Profile 安装、首轮 surface、unlock、resume、continuable child 或真实页面。

## 安装与迁移

同一 Profile 最终只保留一个 companion package：

```powershell
$oldVisualizer = '@sacha-orchestra/dsh-visualizer'
$oldSubagents = '@sacha-orchestra/dsh-subagents'
$companion = Join-Path $sachaRoot 'integrations/dsh/sacha-companion'

dsh plugin --profile web remove $oldVisualizer $oldSubagents
dsh plugin --profile web add $companion
dsh --profile web --dump-config
```

执行前保存 Profile package/lock/patch 与进程身份；任一 remove/add 拟升级无关依赖或产生部分失败时停止，不手改 Profile manifest/lock 绕过。安装后重启目标 DSH Profile，并从 fresh Root Session 验证：

1. 首个 `request/header.tools` 为 bootstrap 面，首个耐久信号后的 header 为 resident 面；
2. `sacha_tools` status/catalog/help/phase/unlock/reset、same-response guard 与 next-step unlock；
3. DSH restart/cold resume 后 exposure 恢复，且压缩后 phase 不回退；
4. 三个 Sacha continuable surface、depth、settlement、Reviewer isolation；
5. state route 与真实 Manager/delegation/child/tool-surface 对齐；
6. Web Client 实际加载 `/plugins/@sacha-orchestra/dsh-companion/client.js`，面板几何、中文、状态与 reduced-motion 通过。

安装、迁移和重启由当次明确请求授权；示例中的 `web` 应替换为已获授权的目标 Profile。

## Adapter 配合与边界

`plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md` 是 DSH transport、surface requirement、回退、恢复与证据映射 Owner。Companion 实现 Profile 层工具暴露和观察，不把分类结果升级为 Sacha Role/Gate/授权事实。

源码、package/Profile、Runtime、Human 页面分别只证明自身层；执行者总结、工具颜色、配置存在、`sacha_tools` 成功或 state route 返回都不能替代真实请求 header、工具执行、Session export 与浏览器证据。
