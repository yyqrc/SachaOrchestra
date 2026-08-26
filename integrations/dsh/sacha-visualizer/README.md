# Sacha Visualizer for DeepSeek Harness

> 文档身份：独立 DSH companion plugin 使用；不进入 `plugins/sacha-orchestra` 的 Agent Plugin 发布 `root`。

本插件让 DSH Web UI 显示当前 Session 中已经提交的 Sacha 流程转换、Gate、Manager 波次、Review Outcome 和证据层，并在当前 Profile 组合官方 experimental Agent Teams 时同时显示 roster、实时成员状态和共享 task DAG。它不接受 Sacha、不判断流程、不改变授权，也不把界面状态提升为完成或验收证据。

## 数据来源

```text
Sacha DSH Adapter
  └─ sacha_visual_event 工具调用/成功结果
       └─ Root Session 标准 tool/call + tool/result 日志

官方 experimental Agent Teams（可选）
  └─ ctx.agentTeams roster + task views

Host snapshot route
  └─ /plugins/sacha-visualizer/state?sessionId=<root-session>
       └─ Web Client shell.overlay 面板
```

`sacha_visual_event` 只校验并返回记录结果；可回放事实来自 DSH 已有的 `tool/call` / `tool/result`，因此本插件不增加下游 Harness 无法识别的自定义 Session event。只有成功工具结果对应的调用进入面板；未返回、失败或参数无效的调用不改变可视状态。

## 能力边界

- 完整 Sacha 面：显示 phase、Planner/Manager/Reviewer Gate、Manager 波次、Reviewer Outcome、source/package/runtime/human 四层证据和已提交时间线。
- 官方 Team 面：通过可选的 `ctx.agentTeams` 读取 Lead/teammate roster、`running/idle/inactive/provisioning/failed` 状态、task revision、owner、blocker、readiness 与 write-scope warning；界面提供分段总进度、动态摘要、Lead→Role/成员派工树和任务标签。
- Lead、Planner/Explore、Executor、Reviewer、QA、设计、文档、数据与 Manager/运维成员使用随包发布的职业鲸鱼插画；右下状态动作图随成员状态切换工作、睡眠或思考动画，`prefers-reduced-motion` 时停止动画。素材来源与 MIT 许可见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
- 任务 DAG 按依赖深度分列并用 SVG 曲线连边；悬停或键盘聚焦高亮完整上下游，点击固定，`Esc` 取消。详情区显示 owner、revision、未满足前置、下游解锁、写入范围与重叠警告。
- 面板默认停靠右侧并让宽屏对话区按实际宽度让位；可切换浮动、拖拽、调整左边缘/底边/右下角并持久化布局。窄屏使用无手势的安全 inset overlay，收起后保留活动徽标。
- DSH Team `ready` 和 `writeScopeWarnings` 只显示官方 Runtime 事实；Sacha readiness、Scope、授权、单写入者和 Reviewer 独立性仍由 Sacha Core/Skill 判断。
- companion 不注册自动调度器，不创建 teammate，不修改 task，不发送 mailbox，也不读取第三方 `.agent-teams` 状态目录。
- 当前 Session 没有活动时每 5 秒探测；发现 Sacha/Team 状态后每 1 秒刷新。切换 Session 后停止旧轮询，只显示当前 Root Session。
- 当前不提供归档 Team 恢复、对话流 Conversation Node 卡片或宿主 locale 实时切换；这些能力分别需要新的历史数据入口、Conversation Node 和 locale 消费边界，不能由当前面板样式推导。

## 构建与验证

```powershell
pnpm install
pnpm verify
```

`pnpm verify` 依次执行 Host/Client typecheck、回放/输入校验/DAG/面板几何/素材映射测试以及 Host/Client bundle 构建。测试只证明源码与 bundle；真实 DSH 仍需验证 Profile 组合、工具 discovery、Session 回放、可选 Agent Teams 状态、Web client bundle、panel 注入和浏览器交互。

## DSH 本地安装

完整使用分为 Agent Plugin、可视化 companion 和官方 Agent Teams 三层。第一层让 DSH 发现 Sacha Skill，第二层提供 `sacha_visual_event` 与 Web 面板，第三层提供 teammate、鲸鱼 Role 树和 task DAG；缺少后两层时分别只失去可视面或 Team 面。

### 1. 准备路径

以下命令面向 DSH 源码 checkout；使用已安装的 `dsh` CLI 时，把后文的 `pnpm dsh` 换成 `dsh`。先在 PowerShell 设置当前机器的绝对路径：

```powershell
$sachaRoot = '<SachaOrchestra 仓库绝对路径>'
$dshRepo = '<deepseek-harness checkout 绝对路径>'
$agentPluginsRepo = '<dsh-agent-plugins checkout 绝对路径>'
$dshHome = if ($env:DSH_HOME) {
    [System.IO.Path]::GetFullPath($env:DSH_HOME)
} else {
    Join-Path $HOME '.dsh'
}
```

后续命令要求 Node 与 pnpm 满足目标 DSH checkout 的版本约束，并且该 checkout 已完成 `pnpm install` 和必要构建。

### 2. 安装 Agent Plugins loader

Sacha 是目录形式的 Agent Plugin，DSH 需要 `@deepseek-ai/dsh-agent-plugins` compatibility loader 才能读取 `plugin.json` 与 `skills/`。独立 loader checkout 推荐运行其安装脚本：

```powershell
powershell -File (Join-Path $agentPluginsRepo 'install.ps1') -DshRepo $dshRepo
```

脚本不会修改 Profile。检查 `$dshHome/profiles/web/cordis.patch.yml`；缺少 loader 行时，把下面这个独立 patch 条目加入现有 YAML 列表，不覆盖其他条目：

```yaml
- insert:
    - id: agent-plugins
      name: '@deepseek-ai/dsh-agent-plugins'
```

### 3. 让 loader 发现 Sacha Agent Plugin

loader 默认扫描 `$DSH_HOME/agent-plugins` 的直接子目录。开发 checkout 推荐建立 junction，使 Sacha 源码更新后无需重复复制；目标已存在时先确认其归属，不覆盖或删除未知目录：

```powershell
$pluginInstallRoot = Join-Path $dshHome 'agent-plugins'
$sachaInstall = Join-Path $pluginInstallRoot 'sacha-orchestra'
$sachaSource = Join-Path $sachaRoot 'plugins/sacha-orchestra'

New-Item -ItemType Directory -Force -Path $pluginInstallRoot | Out-Null
if (Test-Path -LiteralPath $sachaInstall) {
    throw "目标已存在，请先确认现有安装：$sachaInstall"
}
New-Item -ItemType Junction -Path $sachaInstall -Target $sachaSource
```

启用了 workspace filter 时，在 `$dshHome/agent-plugins.yml` 的现有配置中加入 `sacha-orchestra`；`disable` 恒胜于 `enable`：

```yaml
enable:
  - sacha-orchestra
disable: []
```

重启后的 fresh Session 必须在 Skill catalog 中发现 `sacha-orchestra-using-sacha`。只看到磁盘目录或 loader 日志不构成 discovery 证据。

### 4. 构建并安装 visualizer companion

先在 companion 目录执行完整本地验证：

```powershell
$visualizer = Join-Path $sachaRoot 'integrations/dsh/sacha-visualizer'
Push-Location $visualizer
pnpm install
pnpm verify
Pop-Location
```

再从 DSH checkout 把本地 bundle 加入 Web Profile：

```powershell
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

### 5. 启用官方 Agent Teams

需要 roster、成员状态、鲸鱼 Role 树和 task DAG 时，在 `$dshHome/profiles/web/cordis.patch.yml` 的现有 YAML 列表中再加入：

```yaml
- insert:
    - id: agent-team
      name: '@deepseek-ai/dsh-experimental-agent-team'
    - id: tool-agent-team
      name: '@deepseek-ai/dsh-experimental-tool-agent-team'
```

这两个包当前是 DSH 源码树中的 private experimental package，不随正式 npm 发布族分发；npm 版 DSH 无法解析它们时，不要复制包或伪造依赖，继续使用不含 Team 面的 Sacha phase、Gate、Outcome、证据和时间线。

### 6. 启动与验收

先复核最终组合，再启动 Web Profile：

```powershell
Push-Location $dshRepo
pnpm dsh --profile web --dump-config |
    Select-String 'agent-plugins|sacha-visualizer|agent-team|tool-agent-team'
pnpm dsh --profile web
Pop-Location
```

新建 fresh Session 后按层确认成功信号：

- Agent Plugin：Skill catalog 出现 `sacha-orchestra-using-sacha`。
- visualizer：工具面出现 `sacha_visual_event`，产生 Sacha 活动后右侧面板或折叠徽标出现。
- Agent Teams：工具面出现 `spawn_teammate`、`list_agents`、`team_task_create/list/get/update`；创建 teammate 后出现职业鲸鱼、成员状态、派工树和 task DAG。
- Client：浏览器刷新后加载 `/plugins/@sacha-orchestra/dsh-visualizer/client.js`，鲸鱼资源从 `/plugins/sacha-visualizer/assets/<name>.png` 返回。

分层排障：Skill 缺失先查 loader、安装目录和 `agent-plugins.yml`；面板缺失先查 visualizer bundle、`client.js` 与是否已调用 `sacha_visual_event`；Team 区域缺失先查两个 experimental row 与官方 Team 工具；源码已更新但界面仍旧时重新执行 `pnpm verify`、重启 DSH 并刷新浏览器。

安装、复制/链接 Agent Plugin、重启和 Profile 修改属于外部状态动作，不由普通 Sacha 实施或本仓静态验证自动执行。

## Sacha Adapter 配合

安装后的 Sacha Agent Plugin 通过 `adapters/dsh/runtime-adapter.md` 拥有事件映射。主任务只能在真实转换提交后调用 `sacha_visual_event`；记录失败不回滚 Sacha 流程，并须在下一次 Human 进度或最终结果中披露“可视化未同步”。面板颜色、工具成功和 Team task 状态均不能替代源码、包、Runtime 或 Human 验收证据。

