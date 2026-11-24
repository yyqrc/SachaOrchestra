# Sacha Companion for DeepSeek Harness

> 文档身份：独立 DSH companion package；不进入 `plugins/sacha-orchestra` 的 Agent Plugin 发布 `root`。

`@sacha-orchestra/dsh-companion` 是 Sacha 在 DeepSeek Harness（DSH）中的唯一配套包，负责以下工作。

1. 管理主会话可用的工具，支持查询、解锁和恢复。
2. 提供可接收后续指令的子代理工具 `sacha_research`、`sacha_worker` 和 `sacha_review`。
3. 在面板上显示已记录的工作依赖、派发、评审和证据，以及直属子代理与主会话工具的状态。

它提供已有工具和状态的记录与显示。工作方式、角色、启动条件、范围、授权、调度、评审和完成仍按主插件规则决定。安装配套包只改变目标 DSH 配置的工具组合和显示能力。

## Root 最小充分工具面

Companion 只安装在 live Root Agent。当前 DSH 的 continuable activation 也会进入 `AgentRegistry.roots()`，因此 Root 还必须没有原生 `subagent/descriptor`；subagent、teammate 与其他非 Root Agent 不安装 Root policy，并在自己的 scope 移除从 Root 继承的 `sacha_tools`，其他 child toolFilter 不变。Root 在 `agent/session-start` 先安装失败关闭保护，保证冷恢复时也不会先以完整工具集运行。启动期晚注册的 global tools 由 `tools/change` 加入同一个目录快照；替换时先成功安装新策略，再移除旧策略：

| 阶段 | 进入条件 | 可用工具 |
| --- | --- | --- |
| `bootstrap` | 会话首个请求 | read/read_image/glob/grep 和记录面板事件的 `sacha_visual_event` |
| `resident` | 首条已记录的非 `sacha_tools` 工具调用或助手消息，或模型显式切换 | 增加 write/edit、当前平台 shell、todo、web、skill、ask_user_question 与 `sacha_research`/`sacha_worker`/`sacha_review` |

阶段由会话中已保存的事件决定。自动切换取首个符合上表条件的 `tool/call` 或 `assistant/message`。

- `sacha_tools` 始终可见。查询、解锁或显式切换等控制调用不触发自动切换。
- 上下文压缩会追加一条遮蔽消息用的 `user/message`。原始事件仍在，压缩前后的阶段和工具集相同。运行和恢复都按同一份事件记录判断。
- 模型可用 `sacha_tools` 的 `phase` 动作显式选择阶段，以恢复或调整可用工具集。之后由显式选择决定阶段。

MCP/App、Agent Teams、普通 subagent/workflow、调试器、部署和其他长尾工具在两个阶段都默认隐藏，需要时通过 `catalog` 查询与 `unlock` 取得。工具收窄不改变底层 sandbox/权限，也不能给已隐藏工具之外的操作授权。切换只提交已成功应用的状态，不宣称已停止此前运行的工具或进程。

正确性由三层共同保证：

- `agent.ctx.tools.restrict()` 过滤 global 与 standing-preset 继承工具；
- `system-prompt/assemble` 过滤 same-scope schema 与配置明确的隐藏工具 guidance；
- `agent.ctx.tools.guard()` 在执行前拒绝不属于 effective surface 的调用。

只存在其中一层不算成功：same-scope Agent Teams 等工具不受自身 restriction 过滤，独立 guidance 也不会随 schema 自动消失。

### PTC（`mode: 'ptc'`）下的阶段收窄

PTC 下 wire schema 只有保留的 `run_code`，其余工具经**生成的 SDK 段**到达模型；SDK 与程序内绑定都从同一个 `view(scope).visible` 生成。因此阶段收窄依然成立，但 `run_code` 必须当作**传输层**而非能力处理：

- `phaseAllowsTool('run_code')` 在两个阶段恒为 true —— 它是 PTC 下抵达任何其他工具的唯一通道，按阶段关闭等于关闭整个工具面；
- `createToolCatalog` 排除 `run_code` —— 它不应作为"可解锁的隐藏能力"出现在 `catalog`/`unlock` 或能力面板里；
- `filterPromptAssembly` 无条件保留 `run_code` 与 `tools:sdk` / `tools:ptc-only` 段 —— 否则 assembly 的工具表为空，或模型读到 `run_code` 却没有可调用的 SDK 声明；
- `guardReason` 放行 `run_code`，并对**传输子派发**（`exec.parent !== undefined`，即程序内的 `tools.x(...)`）跳过 `advertised` 检查。`advertised` 记录的是最新 `request/header.tools`，PTC 下它只含 `run_code`；用它校验子派发会拒绝程序能合法绑定的每一个工具。子派发只受 `allowed` 约束，而 `allowed` 正是 SDK 段的渲染来源，因此与模型被承诺的面完全一致。

`nested` 只放宽广告检查，**不放宽能力闸门**：阶段不允许的 write/shell/委派在程序内同样被拒。

## `sacha_tools`

`sacha_tools` 是每个 Root exact scope 中唯一的工具面控制入口，始终可见；它不执行被管理工具，也不授予权限。

| action | 结果 |
| --- | --- |
| `status` | 当前 phase、可见/隐藏数量、临时解锁和 recovery 来源 |
| `catalog` | 按 query 有界列出已采样目录中的隐藏工具信息；多个词按任意词匹配名称、描述与 family |
| `help` | 返回一个具名工具的描述与参数 schema |
| `phase` | 显式切换 `bootstrap` 或 `resident`。之后以这次选择为准 |
| `unlock` | 让指定工具或工具组在下一次模型请求中可见、可用 |
| `reset` | 清除临时解锁并恢复当前 phase |

`unlock` 与 `phase` 成功后，等下一次模型请求实际提供目标工具再调用。直接模式用 `request/header.tools` 核对已声明的工具。同一回复中尚未声明的工具会被拒绝。PTC 的请求头只有 `run_code`，用模型本轮收到的工具 SDK 核对工具列表。程序内调用按当前允许的工具集检查。两种模式都用实际调用结果核对工具是否放行。

`catalog` 的检索按词切分并做任意词匹配，因此 `unity editor bridge` 这类自然多词查询能返回它所指的工具；整串匹配会让这类查询恒返回空，使被隐藏的 `sacha_worker`/`sacha_review` 无法被发现。

工具目录保存当前 Root 初始采样和启动期追加的信息，不再按 256 项截断名称；查询返回数量及每项描述、参数大小仍有界限。同名工具更新、删除和上级作用域的动态变化未实现完整同步，执行仍以当前原生工具和 guard 结果为准。

Root policy 沿用原生 Session 事件。冷恢复按事件顺序重放阶段与成功配对的 `sacha_tools` `tool/call` 和 `tool/result`。显式 `phase` 之前的旧调用即使结果晚到，也不能重新解锁。失败或未配对的结果不改变恢复状态。恢复后的工具暴露和执行限制按本节对应模式的证据核对。

## Continuable child surfaces

三个 surface 均使用官方 `@deepseek-ai/dsh-tool-subagent`、`provider: spawn`、`backgroundMode: continuable` 与 `maxDepth: 1`。Sacha 主路径调用必须省略 `run_in_background` 或显式传 `true`；foreground one-shot 不满足 durable child/settlement/recovery 合同。

### `sacha_research`

- allow-list：`read/read_image/glob/grep/web_search/skill`；
- scope-local `report` 由 DSH continuable child setup 保留；
- 无项目写入、shell、MCP/App、Agent Teams、Sacha sibling 或下级派发工具。

### `sacha_worker`

- 保留实施与验证工具；
- deny 只写 `subagent_fork`：`tools.restrict()` 按 `restrictableNames` 校验，该集合只含 scope **继承**的名字，因此 scope 自身注册的工具虽可见、也计入 known，却不可 restrict；`subagent` 即属此类（实测 child scope 可见它，但 `restrict({ deny: ['subagent'] })` 在该 scope 抛错）；
- `workflow` 在 PTC preset 下 disabled，同样不可移植；
- `restrict()` 对第一个不可限制的名字就**整体抛错**，所以多写一个这样的名字不是收窄能力，而是让整个 surface 无法创建；
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

配套包的开发和测试基准为 DSH `0.2.0-rc.1`，组件依赖见 [package.json](package.json)。`0.2.2-rc.1` 的 `dsh-tool-subagent` 会拒绝本包使用的 `persona` 和 `toolFilter` 配置。该版本需要先适配子代理配置，再加载本配套包。

依赖版本范围用于依赖解析，DSH `0.2.2-rc.1` 也会用它检查宿主版本。工具能否加载和使用，仍需核对实际版本和接口。

目标 Profile 使用兼容的 standard coding preset 或等价组合，须提供以下能力。

- Agent/Session/ToolRuntime/SystemPrompt 与 Web Host/Client runtime；
- `@deepseek-ai/dsh-subagent`、spawn provider、continuable settlement/report；
- standard `read/read_image/write/edit/glob/grep`、平台 shell、skill、Web 与 control tools；
- React 与 DSH Client layout/slot surface。

遇到未知允许项、缺少委派提供方、工具声明和执行限制无法同步，或构建及打包缺文件时，停止并报告具体错误。

## 构建与验证

```powershell
pnpm install --offline --frozen-lockfile
pnpm verify
pnpm pack --dry-run --json
```

`pnpm verify` 执行 Host/Client/Preview typecheck、Vitest、Host/Client bundle 与 Preview build。静态结果不证明 Profile 安装、首轮 surface、unlock、resume、continuable child 或真实页面。

## 安装与迁移

同一 Profile 使用一个配套包。安装或迁移前，对照 [Profile 前提](#profile-前提)，核对目标 Profile 实际使用的 DSH 组件版本和所需能力。有配置不兼容时先处理兼容问题。核对通过后，在仓库根目录执行以下命令。

```powershell
$companion = (Resolve-Path -LiteralPath 'integrations/dsh/sacha-companion').Path

dsh plugin --profile web add $companion
dsh --profile web --dump-config
```

执行前保存 Profile package、锁文件、patch 和进程身份。迁移旧 Profile 时，先核对是否仍安装 `@sacha-orchestra/dsh-visualizer`、`@sacha-orchestra/dsh-subagents`。只有实际存在且用户已授权迁移的旧包，才在添加配套包前用 `dsh plugin --profile <profile> remove <package>` 移除。任何一步拟升级无关依赖或发生部分失败时，保留现场并停止，不手改 Profile manifest 或锁文件绕过。安装后重启目标 DSH Profile，从全新的主会话核对以下结果。

1. 核对首次模型请求的 `bootstrap` 工具集，以及自动切换后下一次请求的 `resident` 工具集。工具列表按 [`sacha_tools` 章节](#sacha_tools)中对应模式的证据核对。
2. 核对 `sacha_tools` 的状态、查询、切换、解锁和重置。按对应模式核对工具的声明与实际执行结果。直接模式须检查同一回复中未声明的工具被拒绝，以及下一次请求中已经声明的工具可以调用。
3. DSH restart/cold resume 后 exposure 恢复，且压缩后 phase 不回退；
4. 三个 Sacha continuable surface、depth、settlement、Reviewer isolation；
5. state route 与真实 Manager/delegation/child/tool-surface 对齐；
6. Web Client 实际加载 `/plugins/@sacha-orchestra/dsh-companion/client.js`，面板几何、中文、状态与 reduced-motion 通过。

安装、迁移和重启由当次明确请求授权；示例中的 `web` 应替换为已获授权的目标 Profile。

## Adapter 配合与边界

`plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md` 是 DSH transport、surface requirement、回退、恢复与证据映射 Owner。Companion 实现 Profile 层工具暴露和观察，不把分类结果升级为 Sacha Role/Gate/授权事实。

分别核对源码、package/Profile、实际调用和用户页面。工具暴露以对应模式的请求证据为准，工具放行、会话恢复与页面显示分别以调用结果、Session export 和浏览器证据为准。执行者总结、工具颜色、配置存在、`sacha_tools` 成功或 state route 返回均不能替代这些直接证据。
