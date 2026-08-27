# Sacha DSH Subagents

> 文档身份：DeepSeek Harness companion bundle；不进入 `plugins/sacha-orchestra` 的 Agent Plugin 发布 root。

`@sacha-orchestra/dsh-subagents` 是一层很薄的 DSH **profile bundle**。它不实现 Sacha Workflow，也不维护第二份任务板；它只用 DSH 官方 `@deepseek-ai/dsh-tool-subagent` 组合出三个 Sacha Adapter 可识别的 continuable delegation surface：

- `sacha_research`：调查/研究型 direct child；
- `sacha_worker`：实施型 direct child；
- `sacha_review`：独立复核型 direct child。

Sacha 的 Gate、Manager DAG、readiness、Scope、授权、Reviewer Outcome 和根终态仍由 `plugins/sacha-orchestra` 的 Core/Adapter 拥有。

## 为什么是 bundle，而不是新的 subagent runtime

DSH 官方 `dsh-tool-subagent` 已经支持同一组合挂多个实例，每个实例可独立设置 `toolName`、`persona`、`toolFilter`、`backgroundMode` 与 `maxDepth`。本 companion 只把这些官方能力组合成 Sacha 需要的三个入口，不复制 child 生命周期、settlement、send_message、interrupt 或持久化实现。

## Profile 前提

当前 `0.1.0` 面向 DSH **standard coding preset 或与其工具面等价的组合**。目标 Profile 必须已经提供：

- `@deepseek-ai/dsh-subagent`；
- `spawn` in-process provider；
- `send_message`、`interrupt_agent`、`list_agents` 控制工具；
- standard 文件工具 `read/write/edit`；
- standard delegation 工具 `subagent`、`subagent_fork` 与 `workflow`；
- 平台对应 shell：Windows 为 `pwsh`，其他平台为 `bash`。

这是有意的响亮失败边界：DSH 的 `toolFilter` 对未知工具名会拒绝装配，因此本 bundle 不声称可无条件装到任意自定义 preset。

## 三个 surface

### `sacha_research`

- `backgroundMode: continuable`
- `maxDepth: 1`
- 去掉 `write`、`edit`、当前平台 shell、workflow 和所有 delegation surface
- 保留读取、搜索、Web、`skill` 等当前 standard preset 中未被 deny 的能力

因此它适合 Sacha 的 `research-ready` / Explore 型 work unit。由于 shell 被移除，它不能通过 shell 绕过 `write/edit` 做项目变更。

### `sacha_worker`

- `backgroundMode: continuable`
- `maxDepth: 1`
- 保留正常实施/验证工具
- 去掉 workflow 与所有 delegation surface

它能实施当前 work unit，但不能把 Sacha 的 Manager 权继续向下传。

### `sacha_review`

- `backgroundMode: continuable`
- `maxDepth: 1`
- 去掉 `write/edit`、workflow 和所有 delegation surface
- 保留平台 shell，便于运行测试、diff、静态检查等验证

因此 **它不是硬 read-only sandbox**：shell 仍可能产生文件副作用。Sacha Adapter/Assurance 只能把它记录为“直接写工具已移除”；若任务要求文件级只读 enforcement，仍必须使用目标 DSH 的真实 sandbox 能力并记录 `full | partial | unknown`，不能把 persona 当权限边界。

## 模型路由边界

`0.1.0` 不为三个 surface 同时开启 `modelSelectionSettings`。DSH 当前一个工具作用域只能有一个实例拥有共享 `list_subagent_models` 选择面；在没有更干净的官方多实例路由接口前，本 bundle 默认使用 spawn provider 的当前 child route。

Sacha Adapter 如果发现目标 Runtime 提供了可核实的等价 surface，且它能逐 child 接受 `provider/model/reasoning_effort`，可以优先使用该 Runtime 原生能力。请求值和实际模型仍必须分开记录。

## 安装

从 DSH Profile 安装本地 bundle：

```powershell
$dshRepo = '<deepseek-harness checkout>'
$sachaRoot = '<SachaOrchestra checkout>'
$bundle = Join-Path $sachaRoot 'integrations/dsh/sacha-subagents'

Push-Location $dshRepo
pnpm dsh plugin --profile web add $bundle
pnpm dsh --profile web --dump-config
Pop-Location
```

`dsh plugin` 会依据 package.json 的 `dsh.bundle.patch` 把本包加入该 Profile 的 bundle 层；直接 `pnpm add` 只安装包，不会自动应用 patch。

## Fresh Runtime 验收

安装后新建 fresh Root Session，至少验证：

1. 工具目录同时出现 `sacha_research`、`sacha_worker`、`sacha_review`；
2. 三个工具默认返回 durable continuable child id，而不是前台吞掉结果；
3. `list_agents(scope="children")` 能看到这些 direct child；
4. `sacha_research` 无 `write/edit` 和当前平台 shell；
5. `sacha_worker`/`sacha_review` 无继续 delegation 能力，且 depth 证据没有出现大于 1 的 child；
6. child settlement 能重新驱动 Root 继续处理；
7. `sacha_review` 的 shell 能运行验证，但若没有 sandbox 证据，不声称文件只读。

对应 Sacha Runtime task pack：

- `tests/runtime-scenarios/packs/dsh-continuable-parallel-barrier`
- `tests/runtime-scenarios/packs/dsh-continuable-review-isolation`

配置文件、bundle 已安装、工具 schema 存在都不等于上述行为已经验证。
