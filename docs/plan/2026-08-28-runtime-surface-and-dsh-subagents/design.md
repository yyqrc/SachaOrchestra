# Runtime Surface 与 DSH Continuable Subagent 迭代设计

> 状态：本轮实施设计；只记录当前仍采用或仍待验证的方案。
> 日期：2026-08-28

## 1. 目标

本轮收敛两个问题：

1. Sacha 如何在项目 Skill、领域插件 Skill、MCP/工具和 Runtime 内置 Skill 同时存在时保持稳定自动入口与按需能力加载，而不接管宿主整个能力目录。
2. DeepSeek Harness（DSH）如何删除 experimental Agent Teams 依赖，直接使用 continuable subagent，并让可视化完整观察 Sacha Manager DAG、work unit 到真实 child 的映射和 child Runtime 状态。

本轮不新增 Role、Gate、生命周期、Artifact 或完成定义；Direct-first、Planner/Executor/Reviewer、Manager、Assurance 与 Artifact 权威不变。

## 2. 全局能力竞争：不只看 Sacha 自己的 Skill

真实 Runtime 初始能力面可能同时包含：

- Sacha Skill；
- `setup-project` 绑定的领域 Provider canonical Skill；
- 项目本地 Skill；
- 其他插件公开 Skill；
- Codex/Claude/DSH 内置 Skill；
- MCP、原生工具和第三方工具。

因此只隐藏 Sacha 的 Planner/Executor/Reviewer，只能减少 Sacha 自己制造的竞争，不能解决全局目录竞争。Sacha 也不应为了自动入口而隐藏、重写或接管其他 Provider、项目或宿主拥有的能力。

### 2.1 `using-sacha` 的责任

`using-sacha` 继续承担自动触发入口，但目标是**尽早完成一次低成本 Intake 判断**，不是把 Runtime 变成 Sacha 私有菜单：

- 入口元数据保持短、独特，聚焦“当前可执行目标应 Direct 还是进入 Sacha”；
- 触发后先读 Intake Contract；Human 接受后才读 Workflow 与实际消费者 Role；
- Domain Skill/项目 Skill 仍按 `setup-project` 的 Binding/load policy 和当前 Role 需要加载；
- 某 Skill 可见不等于 Sacha 已接受，也不构成 Planner Gate、授权或验证事实；
- 清晰任务保持 Direct，不强制统一的 read-first 阶段。

### 2.2 Codex 的可用优化

Codex 初始 Skill catalog 主要暴露 `name + description + locator`，选中后再完整读取 `SKILL.md`。风险主要是**候选描述竞争**，不是所有 Skill 正文同时加载。

对 Sacha 自身可评估 Codex 原生：

```yaml
policy:
  allow_implicit_invocation: false
```

推荐候选：

- `using-sacha` 保持 implicit 可见，继续承担自动入口；
- Planner/Executor/Reviewer/Explore/Manager/Roadmap/document-project/closeout/feedback/setup-* 默认从 implicit catalog 隐藏，但保留 Human `$skill` 显式调用；
- `using-sacha`/Workflow 通过稳定 locator 或 Runtime 正式 Skill read 机制读取目标 Skill。

**当前未直接实施。** 必须先用 Runtime scenario 比较自动入口召回与误触发；目录更短本身不是正确性证据。

## 3. 渐进披露的跨 Runtime 抽象

不复制固定“理解→规划→开发→验证”四阶段。Sacha 采用两层按需披露：

1. **Skill disclosure**：只读当前消费者需要的 Skill/合同；
2. **Tool/capability disclosure**：委派 work unit 时，只给 child 完成该单元所需的 Runtime 能力。

```text
using-sacha / 当前入口
        ↓
当前 Role / work unit
        ↓
Runtime-native capability surface
```

Runtime 映射：

- DSH：多个具名 `dsh-tool-subagent` surface，使用 `toolFilter`、`maxDepth`、persona 与 continuable child；
- Claude Code：subagent `tools`/`disallowedTools`、fresh context；独立写入场景再按事实使用 worktree；
- Codex：custom agent sandbox / named agent config；Skill catalog 可用 `allow_implicit_invocation`；更强 hook 只在真实 failure mode 出现后评估；
- Cursor：只使用当前 Runtime 已验证的原生能力，不伪造统一 enforcement。

Core 只产生 readiness、Role、Scope、授权与路由要求，不写具体工具名。

## 4. DSH：continuable subagent 直接承载 Sacha 调度

### 4.1 删除 Agent Teams 的理由

Agent Teams 提供 roster、peer mailbox、共享 task board、`blockedBy`、task owner、revision/CAS 与 write-scope warning。Sacha 已经由 Coordination Contract 拥有：

- work-unit 拆分；
- dependency DAG；
- execution-ready / research-ready；
- wave/并发判断；
- single writer；
- dispatch / barrier / aggregate；
- Owner 与恢复语义。

再映射一份 Team task DAG 会形成重复调度状态。Sacha 又要求 child 不拥有 Manager/派发权，因此 peer-to-peer Team 协作不是目标能力。

### 4.2 主路径

```text
Sacha Manager 形成 ready work unit / DAG
        ↓
DSH Adapter 选择 continuable delegation surface
        ↓
Runtime 返回 durable child id
        ↓
Root 继续其他 ready work
        ↓
settlement / report
        ↓
Root 消费结果并重算同一份 Sacha DAG
```

DSH 只拥有 child 生命周期、消息、interrupt、列表、settlement 与真实 child route；依赖图只有 Sacha 一份权威。

### 4.3 `sacha-subagents` companion

仓库已新增：

```text
integrations/dsh/sacha-subagents/
├─ package.json
├─ cordis.patch.yml
└─ README.md
```

它是 DSH profile bundle，只组合官方 `@deepseek-ai/dsh-tool-subagent`，暴露：

- `sacha_research`
- `sacha_worker`
- `sacha_review`

共同特征：

- `backgroundMode: continuable`
- `provider: spawn`
- `maxDepth: 1`
- 自包含 child persona
- 不拥有 Sacha Gate、DAG、readiness、Scope、授权或 Outcome

能力边界：

- **research**：移除 `write/edit`、当前平台 shell 与 standard `workflow/subagent/subagent_fork`；适合调查型 work unit；
- **worker**：保留实施/验证工具，移除 standard delegation tools；
- **review**：移除 `write/edit` 与 standard delegation tools，但保留 shell 做测试/diff；因此不是硬 read-only sandbox。

三个 sibling `sacha_*` 名字故意不互相写进 `toolFilter` deny-list。DSH 会对未知 filter 名响亮失败，互相引用会引入注册顺序耦合；单层派发的真正 Runtime guard 是 `maxDepth=1`。Runtime scenario 必须证明没有 depth>1 child。

当前 bundle 面向 standard coding preset 或真实工具面等价的组合；自定义 preset 不满足显式 tool 前提时应失败或不安装，不静默削弱限制。

### 4.4 barrier

DSH 主路径不依赖 Team `wait_agent`：

- 还有 ready work：继续推进；
- 没有 ready work 且有未满足 child 依赖：Root 停止主动推进；
- settlement/report 到达后恢复；
- 每次只消费新增结果并重算 DAG；
- 只收到部分依赖时不得进入后续 Role 或根终态。

这必须由真实 Runtime scenario 验证。

## 5. DSH Visualizer：完整观察 Sacha，而不是替代 Sacha

Visualizer 继续只观测，不拥有流程语义或调度。

### 5.1 数据源

1. `sacha_visual_event` 成功 tool call/result：
   - `phase`
   - `gate`
   - `manager_wave`
   - `delegation`
   - `review`
   - `evidence`
2. `ctx.subagents.listChildren(rootSessionId)` + live Agent registry：
   - durable child id
   - label
   - `running | idle | ready`
   - `hasChildren`

### 5.2 Manager DAG

`manager_wave` 不再只保存一组 unit id，而是保存**当时已由 Manager 决定的 DAG 快照**：

```text
wave_id
wave_state
manager_units[]:
  id
  label
  state
  blocked_by[]
```

Visualizer 由这些 Sacha 已提交事实画依赖图。它不是 Team task board，也不取得 DAG ownership。

### 5.3 work unit ↔ child

continuable child 真正发布并返回 durable id 后，DSH Adapter记录：

```text
event_type = delegation
unit_id
child_id
delegation_state
role?              # 已有 Sacha 事实
surface?           # sacha_research/worker/review
requested_route?
effective_route?   # 只有 Runtime 直接证据存在才写
```

Visualizer 因此可以显示：

```text
Manager unit ──blocked_by──> Manager unit
     │
     └──delegation──> durable child
                         ├─ label
                         ├─ running/idle/ready
                         └─ hasChildren
```

不再从 child label 猜 work unit/Role；label 只允许做猫咪道具等纯展示选择。

若 `hasChildren=true`，只显示“需要复核单层派发”的 Runtime warning，不自行裁决任务失败。

### 5.4 删除的 Team 面

现行源码不保留：

- Agent Teams roster；
- Team task DAG；
- task revision/CAS；
- Team `blockedBy`/owner/readiness；
- `writeScopes`；
- peer mailbox UI；
- Team fallback/兼容分支。

历史实现由 Git 保存，不在当前产品代码中保留废弃路径。

## 6. 验证

### 6.1 静态验证

Visualizer 仍运行其 `pnpm verify`（typecheck、Vitest、bundle、preview build）。新增测试覆盖 Manager DAG layout、event normalization 和 replay folding。

`sacha-subagents` 新增：

```text
tests/validate_dsh_subagents.py
tests/test_dsh_subagents.py
```

验证：

- 三个 surface 名称；
- official `dsh-tool-subagent`；
- continuable + `maxDepth=1`；
- research 平台 shell 过滤；
- reviewer `write/edit` 过滤；
- Agent Teams 不回流；
- sibling deny-list 不产生注册顺序耦合；
- release.py 对 companion machine files 有最窄测试映射。

### 6.2 Runtime task pack

#### `dsh-continuable-parallel-barrier`

验证：

- 至少两个 Root direct continuable child；
- 首个 child 启动后继续推进另一个 ready unit；
- child 不产生 grandchildren；
- barrier 由 settlement 驱动恢复；
- 部分 settlement 不导致提前完成；
- 最终产物只在所有前置依赖满足后生成；
- child id、direct-parent、settlement、最终工作区和 verifier 原始输出可核对。

#### `dsh-continuable-review-isolation`

验证：

- Reviewer 是新的 Root direct continuable child；
- 输入自包含且来源独立；
- Reviewer 未参与前序实现；
- 自己核对最终实现与原始 evidence；
- 无下级 child；
- 能力/sandbox 只按 Runtime 直接证据声称；
- Outcome 回到现有 Assurance 路线。

## 7. 当前文件边界

本轮实施涉及：

- `plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md`
- `integrations/dsh/sacha-subagents/**`
- `integrations/dsh/sacha-visualizer/**`
- `PLUGIN_DESIGN.md`
- `tests/runtime-scenarios/**` 的 DSH 场景
- `tests/validate_dsh_subagents.py`
- `tests/test_dsh_subagents.py`
- `scripts/release.py` 的 companion 最窄测试映射

Codex Skill visibility、Claude native subagent surface 与更强 DSH Reviewer sandbox 仍是后续 Runtime-specific 增强；在各自真实 scenario 通过前不作为当前已验证能力。
