# Sacha Visualizer for DeepSeek Harness

> 文档身份：独立 DSH companion plugin 使用；不进入 `plugins/sacha-orchestra` 的 Agent Plugin 发布 `root`。
> 当前包版本：`0.2.0`。本版删除旧 Agent Teams snapshot/task 模型；旧 Session 中不符合新 `manager_wave.manager_units` 结构的历史可视化调用会被忽略并报告观测 warning，不保留兼容状态机。

本插件让 DSH Web UI 显示当前 Root Session 中已经提交的 Sacha 流程、Manager 波次/依赖、work unit 到 durable child 的映射，并同时观察该 Root 的 **continuable direct subagents**。它不接受 Sacha、不判断流程、不改变授权、不调度 child，也不把界面状态提升为完成或验收证据。

## 数据来源

```text
Sacha DSH Adapter
  └─ sacha_visual_event 工具调用/成功结果
       ├─ phase / gate / review / evidence
       ├─ manager_wave：Sacha Manager DAG 快照
       └─ delegation：work unit ↔ durable child id

DSH continuable subagent service
  └─ ctx.subagents.listChildren(rootSessionId)
       └─ durable child id / label / hasChildren
  └─ ctx.agents
       └─ running / idle / ready

Host snapshot route
  └─ /plugins/sacha-visualizer/state?sessionId=<root-session>
       └─ Web Client shell.overlay 面板
```

`sacha_visual_event` 只校验并返回记录结果；可回放事实来自 DSH 已有的 `tool/call` / `tool/result`。只有成功工具结果对应的调用进入 Sacha 面板状态。

## 能力边界

- Sacha 面：显示当前 phase、Planner/Manager/Reviewer Gate、Reviewer Outcome 与 Evidence 状态。
- Manager 面：`manager_wave` 保存当时已经由 Sacha Manager 决定的 work-unit 快照，每个 unit 有 `id`、Human 可读 label、Sacha state 与 `blocked_by`；面板据此画依赖 DAG。
- Delegation 面：只有 continuable child 真正发布并返回 durable id 后，Adapter 才记录 `delegation`；面板用它把 Manager work unit 与真实 child 对上，并可显示 Role/surface 与已验证 route。
- Subagent 面：只显示 Root Session 的 continuable **direct child**；包括 durable id、label、`running | idle | ready` 和是否观察到下级 child。
- 若 child `hasChildren=true`，面板只显示“需要复核 Sacha 单层派发”的 Runtime warning；它不自行判定任务失败。
- Manager DAG 的权威来源是 Sacha 已提交事件，不是 Runtime task board；Visualizer 不维护第二份调度状态。
- 不读取或显示 Agent Teams roster、task revision、task owner、`writeScopes`、peer mailbox 或 Team readiness。
- 不从 child label 推导 Sacha Role、Scope、授权或完成；label 只允许做猫咪道具等纯展示选择。
- 不注册自动调度器，不创建 subagent，不发送 `send_message`，不 interrupt child，不修改 Sacha Artifact。
- 当前 Session 没有活动时低频探测；发现 Sacha/subagent 状态后提高刷新频率。切换 Session 后停止旧 Session 的轮询。
- 每个会话默认收起；首个已提交事件或 direct child 到达时自动展开一次，Human 手动收起后该会话不再自动弹出。

## 构建与验证

```powershell
pnpm install
pnpm verify
```

`pnpm verify` 执行 Host/Client/预览 typecheck、Vitest、Host/Client bundle 和预览构建。静态通过只证明源码与 bundle；真实 DSH 仍需验证 Session 回放、Manager DAG 事件、delegation 绑定、subagent service、Web client bundle 和浏览器交互。

## DSH 本地安装

完整使用分为四层：

1. Sacha Agent Plugin：让 DSH 发现 `using-sacha` 与下游 Skill；
2. `integrations/dsh/sacha-subagents`：可选 Sacha continuable-subagent bundle；
3. DSH continuable subagent service/control：实际 child 生命周期、settlement、message 与列表；
4. 本 visualizer companion：提供 `sacha_visual_event` 与 Web 面板。

### 1. 安装 Sacha Agent Plugin

Sacha 是目录形式 Agent Plugin。使用当前 DSH 对 Agent Plugins 的正式兼容 loader，让 `$DSH_HOME/agent-plugins/sacha-orchestra` 指向仓库的 `plugins/sacha-orchestra`，并在 fresh Session 中确认 Skill catalog 实际发现 `sacha-orchestra-using-sacha`。磁盘目录本身不构成 discovery 证据。

### 2. 安装 Sacha subagent bundle

当前 standard coding preset 可以安装仓库内 companion bundle：

```powershell
$subagents = Join-Path $sachaRoot 'integrations/dsh/sacha-subagents'
Push-Location $dshRepo
pnpm dsh plugin --profile web add $subagents
pnpm dsh --profile web --dump-config
Pop-Location
```

它组合官方 `@deepseek-ai/dsh-tool-subagent`，暴露：

- `sacha_research`
- `sacha_worker`
- `sacha_review`

具体能力与限制见 [`../sacha-subagents/README.md`](../sacha-subagents/README.md)。该 bundle 当前面向 standard coding preset；目标 Profile 不满足其显式 toolFilter 前提时应响亮失败，而不是静默削弱约束。

如果不安装该 bundle，Sacha Adapter 仍可使用当前 Runtime 已核对的等价 continuable surface；Visualizer 不依赖 bundle 本身，只依赖真实 child 和 Adapter 记录。

fresh Session 中至少核对：

- 对应 continuable delegation tool；
- `send_message`、`interrupt_agent`、`list_agents`；
- child 创建返回 durable id；
- child settlement 能回到 parent；
- `list_agents` 能看到 direct continuable child。

### 3. 构建并安装 visualizer

```powershell
$visualizer = Join-Path $sachaRoot 'integrations/dsh/sacha-visualizer'
Push-Location $visualizer
pnpm install
pnpm verify
Pop-Location

Push-Location $dshRepo
pnpm dsh plugin --profile web add $visualizer
pnpm dsh --profile web --dump-config
Pop-Location
```

组合结果必须包含：

```yaml
- id: sacha-visualizer
  name: '@sacha-orchestra/dsh-visualizer'
```

新建 fresh Root Session 后分层确认：

- Agent Plugin：`using-sacha` 可被正式发现；
- subagent：启动一个 continuable child 后，`list_agents` 返回同一 durable child id；
- visualizer：工具面出现 `sacha_visual_event`，产生 Sacha 活动后右侧面板出现；
- Manager graph：一次 `manager_wave` 成功记录后，面板显示对应 unit 与 dependency edges；
- delegation：child id 返回后记录 `delegation`，同一 unit 节点和 child 卡显示一致绑定；
- child view：该 Root 的 continuable direct child 出现在面板，状态与 live Agent registry 一致；
- Client：浏览器实际加载 `/plugins/@sacha-orchestra/dsh-visualizer/client.js`。

安装、Profile 修改、junction、重启与依赖装配属于外部状态动作，不由普通 Sacha 实施或本仓静态验证自动授权。

## Sacha Adapter 配合

`plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md` 是 DSH transport 的唯一规范 Owner。主任务只能在真实转换、Manager DAG 或 child binding 已提交后调用 `sacha_visual_event`；记录失败不回滚 Sacha 流程或 child 生命周期。

Runtime truth 只来自 Manager 已提交事件和 DSH 原生 child/session 事实。面板颜色、DAG 节点、child 状态、请求 route 和 `sacha_visual_event` 成功都不能替代源码、包、Runtime 或 Human 验收证据；只有 Runtime 直接证明的 route 才显示为 effective route。
