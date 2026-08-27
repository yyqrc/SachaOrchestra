# Runtime Surface 与 DSH Continuable Subagent 迭代设计

> 状态：本轮实施设计；只记录当前仍推荐采用的方案。
> 日期：2026-08-28

## 1. 目标

本轮收敛两个问题：

1. Sacha 如何在安装了大量项目 Skill、领域插件 Skill、MCP/工具和 Runtime 内置 Skill 的环境中，继续保持稳定的自动入口与按需能力加载，而不试图接管宿主的整个 Skill/工具目录。
2. DeepSeek Harness 适配如何删除 experimental Agent Teams 依赖，直接使用正式 continuable subagent 能力，并让可视化改为观测 Sacha 流程事件与 continuable child 状态。

本轮不新增 Role、Gate、生命周期、Artifact 或完成定义；Direct-first、Planner/Executor/Reviewer、Manager、Assurance 与 Artifact 权威保持不变。

## 2. 全局能力竞争：Sacha 不能只解决自己的 Skill

### 2.1 问题边界

真实 Runtime 的初始能力面可能同时包含：

- Sacha 自己的 Skill；
- `setup-project` 绑定的领域 Provider canonical Skill；
- 项目本地 Skill；
- 其他插件公开 Skill；
- Codex/Claude/DSH 自带 Skill；
- MCP、原生工具和第三方工具。

因此，单纯把 Sacha 的 Planner/Executor/Reviewer 隐藏起来，只能减少 Sacha 自己制造的竞争，不能消除全局目录竞争。Sacha 也不应为了自动入口而尝试隐藏、重写或接管其他 Provider/项目/宿主拥有的 Skill 和工具。

### 2.2 自动入口的正确责任

`using-sacha` 仍承担自动触发入口，但它的责任是“尽早完成一次低成本 Intake 判断”，不是把 Runtime 变成 Sacha 私有菜单。

采用以下原则：

- 入口元数据保持短、独特、面向“当前可执行目标先判断 Direct 或 Sacha”，避免与领域 Skill 的具体任务描述竞争。
- `using-sacha` 被触发后只读取 Intake Contract 与当前任务完成入口判断；Human 接受 Sacha 后才读取 Workflow Contract 和目标 Role。
- 领域 Provider、项目 Skill 和其他 Runtime Skill 继续由其自己的描述/发现机制存在；Sacha 只在当前 Role 的 load policy 成立时读取已绑定 canonical Skill。
- Sacha 不把“某领域 Skill 可见”视为 Sacha 接受、Planner Gate 或授权证据。
- 清晰任务保持 Direct；不强制所有任务先进入只读研究阶段。

### 2.3 Codex 的可用优化

Codex 当前 Skill catalog 初始暴露的是 Skill 的 `name + description + locator`，选中后才完整读取 `SKILL.md`。因此主要风险是目录候选竞争，而不是所有 Skill 正文同时加载。

对 Sacha 自身可以使用 Codex 原生 `policy.allow_implicit_invocation: false` 隐藏下游 Skill 的初始模型目录，同时保留 Human 通过 `$skill` 显式调用能力。此优化只减少 Sacha 自己的候选，不宣称解决全局 Skill 竞争。

推荐：

- `using-sacha`：保持 implicit 可见；
- Planner/Executor/Reviewer/Explore/Manager/Roadmap/document-project/closeout/feedback/setup-*：Codex 默认 implicit 隐藏，仍允许显式调用；
- `using-sacha`/Workflow 通过稳定相对路径或 Runtime 正式 Skill read 机制读取目标 Role，不依赖目标 Role 必须出现在初始 catalog。

是否实施该 Codex visibility 改动必须由对应 Runtime scenario 验证自动入口召回率没有下降；不能只以目录更短作为正确性证据。

## 3. 渐进披露的跨 Runtime 抽象

不复制固定“理解→规划→开发→验证”四阶段。Sacha 的通用抽象是：

```text
入口需要的最小能力
    ↓
当前 Role / work unit 需要的能力
    ↓
对应 Runtime 原生能力面
```

即两层渐进披露：

1. **Skill disclosure**：只读取当前消费者需要的 Skill/合同；
2. **Tool/capability disclosure**：委派 work unit 时，只给该 child 完成任务需要的能力。

Runtime 映射：

- DSH：多个具名 `dsh-tool-subagent` composition，使用 `toolFilter`、`maxDepth`、persona、child model route；
- Claude Code：subagent `tools`/`disallowedTools`、fresh context，按需 `isolation: worktree`；
- Codex：custom agent sandbox / named agent config；Skill 目录使用 `allow_implicit_invocation`；更强的 tool hook 仅在真实 failure mode 出现后评估；
- Cursor：仅使用当前 Runtime 已验证的原生能力，不为统一接口伪造 enforcement。

Core 只产生 readiness、Role、Scope、授权和路由要求，不写具体工具名。

## 4. DSH：删除 Agent Teams 主路径

### 4.1 原因

Agent Teams 提供 roster、peer mailbox、共享 task board、`blockedBy`、task owner、revision/CAS 和 write-scope warning。这些能力适合普通 Agent 自行组织团队，但 Sacha 已经由 Coordination Contract 拥有：

- 工作单元拆分；
- dependency DAG；
- execution-ready / research-ready；
- 波次与并发判断；
- 单一写入者；
- dispatch / barrier / aggregate；
- Owner、revision 与恢复语义。

把 Sacha DAG 再映射为 Team task DAG 会形成第二份调度状态和重复权威。Sacha 又要求 child 不拥有 Manager/派发权，因此 peer-to-peer Team 协作不是目标能力。

### 4.2 新主路径

使用正式 continuable subagent：

```text
Manager / 主任务形成 ready work unit
    ↓
DSH Adapter 选择一个具名 Sacha delegation tool
    ↓
continuable subagent 返回 durable child id
    ↓
主任务继续其他不冲突工作
    ↓
child settlement / report 到达
    ↓
主任务消费结果并重算 Sacha DAG
```

依赖图只留在 Sacha。DSH Runtime 只拥有 child 生命周期、消息、interrupt、列表、settlement 和真实 child route。

### 4.3 DSH 需要的三个 delegation surface

部署组合建议暴露三类官方 `dsh-tool-subagent` 实例；名称是 Adapter 合同的一部分，具体工具过滤以目标 DSH 版本真实工具目录验证后配置：

- `sacha_research`：fresh、continuable、只读调查型 child；
- `sacha_worker`：fresh、continuable、普通 implementation child；
- `sacha_review`：fresh、continuable、独立 Reviewer child。

共同要求：

- `maxDepth=1` 或等价运行时限制，保持 Sacha 单层派发；
- child 输入必须自包含；
- child 不取得工作流 Owner、Manager 或根终态责任；
- 主任务只消费 child 的结果、证据、风险、协调请求和必要 reference；大 search/test dump 留在 child transcript；
- DSH 支持逐 child provider/model/reasoning 时按 Adapter 路由；不支持时报告能力缺口，不静默伪造实际模型。

`toolFilter` 是 child 能力/注意力缩小的 Runtime 机制；更强文件只读如仍需要，应使用 DSH sandbox 的真实 enforcement，并记录 full/partial/unknown，而不是把提示词或 writeScopes 当安全边界。

### 4.4 barrier 语义

continuable subagent 没有 Agent Teams `wait_agent`。DSH Adapter 将 Core 的“dependency barrier → wait”映射为：

- 没有其他 ready work 时停止主动推进/park 当前 Activation；
- 依赖 child 的 settlement/report 唤醒主任务；
- 每次唤醒只消费新结果并重算剩余依赖；
- 未满足全部阻塞依赖时不得提前进入后续 Role 或根终态。

此路径必须由真实 Runtime scenario 验证，不能由静态文档推断。

## 5. DSH Visualizer

Visualizer 继续只观测，不拥有流程语义或调度。

删除全部 Agent Teams 依赖和兼容代码，改为两类数据源：

1. `sacha_visual_event` 成功 tool call/result：Sacha phase、Gate、Manager wave、Review、Evidence；
2. `ctx.subagents.listChildren(rootSessionId)` + live Agent registry：当前 root 的 continuable direct child id、label、running/idle/ready、是否存在下级。

UI 不再显示 Team task board、task revision、blockedBy、writeScopes 或 Team peer 状态。Manager wave 仍由 Sacha 事件展示调度进度；child 卡只展示 Runtime child 事实。若发现 `hasChildren=true`，以“违反 Sacha 单层派发的 Runtime 观测”作为 warning 展示，但不自行裁决任务失败。

## 6. Runtime 场景验收

新增 DSH Adapter 任务包至少覆盖：

### 6.1 `dsh-continuable-parallel-barrier`

真实 failure mode：两个独立 child 并发后，主任务不能立即等待其中一个而浪费可用工作，也不能在只收到一个 settlement 时提前完成。

验收：

- 主任务实际启动至少两个 direct continuable child；
- child 都是 root 的直接子级且没有 grandchildren；
- 首个 child 启动后，主任务继续推进另一个 ready unit；
- 到达 barrier 后由 settlement 驱动恢复；
- 只收到部分结果时重算依赖并继续等待剩余依赖；
- 全部结果消费后才进入下一转换；
- 原始 child id、启动调用、settlement、最终工作区与验证器输出可核对。

### 6.2 `dsh-continuable-review-isolation`

真实 failure mode：实现 child 和 Reviewer child 共享历史或 Reviewer 自行修改实现，导致独立性失真。

验收：

- Reviewer 是新的 direct continuable child；
- Reviewer 输入只包含 Scope/Baseline/原始 evidence/reference 等自包含材料；
- Reviewer 未参与前序方案/实现；
- Runtime 能力面/沙箱按当前 DSH 能力如实记录；若无法证明只读则标记对应 enforcement 未验证，不用自报替代；
- Reviewer Outcome 返回 Core 合法路线。

## 7. 文件级实施边界

本轮应修改：

- `plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md`
- `integrations/dsh/sacha-visualizer/**` 中所有 Team 专用 Host/Client/type/test/README 内容
- `PLUGIN_DESIGN.md` 中 visualizer/DSH transport 描述
- `tests/runtime-scenarios/README.md`
- 新增上述 DSH runtime scenario pack
- `scripts/release.py` / `tests/test_release.py` 的最窄验证映射（如新增 machine files）

本轮不保留 Agent Teams fallback、Team task type、Team UI、Team 安装说明或废弃注释。历史 git 提交本身即保留旧实现，不在现行源码中留兼容分支。
