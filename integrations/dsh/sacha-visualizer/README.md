# Sacha Visualizer for DeepSeek Harness

> 文档身份：独立 DSH companion plugin 使用；不进入 `plugins/sacha-orchestra` 的 Agent Plugin 发布 `root`。

本插件让 DSH Web UI 显示当前 Root Session 中已经提交的 Sacha 流程转换，并同时观察该 Root 的 **continuable direct subagents**。它不接受 Sacha、不判断流程、不改变授权、不调度 child，也不把界面状态提升为完成或验收证据。

## 数据来源

```text
Sacha DSH Adapter
  └─ sacha_visual_event 工具调用/成功结果
       └─ Root Session 标准 tool/call + tool/result 日志

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

- Sacha 面：显示当前 phase、Planner/Manager/Reviewer Gate、Manager wave、Reviewer Outcome 与 Evidence 状态。
- Subagent 面：只显示 Root Session 的 continuable **direct child**；包括 durable id、label、`running | idle | ready` 和是否观察到下级 child。
- 若 child `hasChildren=true`，面板只显示“需要复核 Sacha 单层派发”的 Runtime warning；它不自行判定任务失败。
- Manager dependency/wave 由 Sacha 已提交的 `manager_wave` 事件投影；Visualizer 不维护第二份 Runtime task DAG。
- 不读取或显示 Agent Teams roster、task revision、`blockedBy`、task owner、`writeScopes`、peer mailbox 或 Team readiness。
- 不注册自动调度器，不创建 subagent，不发送 `send_message`，不 interrupt child，不修改 Sacha Artifact。
- 当前 Session 没有活动时低频探测；发现 Sacha/subagent 状态后提高刷新频率。切换 Session 后停止旧 Session 的轮询。
- 每个会话默认收起；首个已提交事件或 direct child 到达时自动展开一次，Human 手动收起后该会话不再自动弹出。

## 构建与验证

```powershell
pnpm install
pnpm verify
```

`pnpm verify` 执行 Host/Client/预览 typecheck、Vitest、Host/Client bundle 和预览构建。静态通过只证明源码与 bundle；真实 DSH 仍需验证 subagent service、Session 回放、Web client bundle 和浏览器交互。

## DSH 本地安装

完整使用分为三层：

1. Sacha Agent Plugin：让 DSH 发现 `using-sacha` 与下游 Skill；
2. DSH continuable subagent composition：供 Sacha Adapter 派发 child；
3. 本 visualizer companion：提供 `sacha_visual_event` 与 Web 面板。

### 1. 安装 Sacha Agent Plugin

Sacha 是目录形式 Agent Plugin。使用当前 DSH 对 Agent Plugins 的正式兼容 loader，让 `$DSH_HOME/agent-plugins/sacha-orchestra` 指向仓库的 `plugins/sacha-orchestra`，并在 fresh Session 中确认 Skill catalog 实际发现 `sacha-orchestra-using-sacha`。磁盘目录本身不构成 discovery 证据。

### 2. 配置 continuable subagent

Sacha DSH Adapter 不再依赖 experimental Agent Teams。目标 DSH Profile 应提供正式 continuable subagent 能力：

```yaml
- name: '@deepseek-ai/dsh-subagent'
- name: '@deepseek-ai/dsh-subagent-spawn-in-process'
- name: '@deepseek-ai/dsh-tool-subagent'
  config:
    provider: spawn
    toolName: sacha_worker
    backgroundMode: continuable
    maxDepth: 1
- name: '@deepseek-ai/dsh-tool-subagent-control'
- name: '@deepseek-ai/dsh-tool-subagent-control/list-agents'
- name: '@deepseek-ai/dsh-tool-subagent-report'
```

生产组合推荐进一步用多个 `dsh-tool-subagent` 实例暴露：

- `sacha_research`：调查/研究 child；
- `sacha_worker`：implementation child；
- `sacha_review`：独立 Reviewer child。

具体 `toolFilter`、persona、child provider/model/reasoning 必须按目标 DSH 版本真实工具名和 provider capability 配置；未知工具名或未支持 capability 应在装配时失败，而不是由 Sacha 静默忽略。Sacha Core 不依赖这些具体名称；Adapter 只有在当前 Runtime 发现并核对后使用。

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
- child view：该 Root 的 continuable direct child 出现在面板，状态与 live Agent registry 一致；
- Client：浏览器实际加载 `/plugins/@sacha-orchestra/dsh-visualizer/client.js`。

安装、Profile 修改、junction、重启与依赖装配属于外部状态动作，不由普通 Sacha 实施或本仓静态验证自动授权。

## Sacha Adapter 配合

`plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md` 是 DSH transport 的唯一规范 Owner。主任务只能在真实转换提交后调用 `sacha_visual_event`；记录失败不回滚 Sacha 流程。

Visualizer 不从 child label 推导 Role 或权限。猫咪道具可以按 label 做纯展示推断，但 Runtime truth 只有 child id、label、activity、direct-parent 关系和 `hasChildren`。面板颜色、child 状态和 `sacha_visual_event` 成功都不能替代源码、包、Runtime 或 Human 验收证据。
