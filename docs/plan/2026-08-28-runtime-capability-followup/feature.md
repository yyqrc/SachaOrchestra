# Runtime 能力面后续迭代

> 状态：进行中  
> 基线：Sacha Orchestra 0.12.11  
> 用途：跨会话继续迭代 Codex、Claude Code、Cursor 与 DSH 的子 Agent 能力边界和验证方式。

## 1. 当前基线

当前主线已经完成以下改造：

- `using-sacha` 保持 Codex 默认入口，其他 Sacha Skill 默认不参与隐式调用竞争。
- Codex 自定义 Agent 已拆成能力载体，不再把 Agent 类型和模型绑定在一起；当前受管能力 Agent 为 `sacha_readonly_worker`、`sacha_executer`、`sacha_reviewer`。
- Codex Adapter 按工作单元逐次选择模型和推理强度，能力 Agent 本身不拥有 Role、授权或工作流状态。
- Coordination 已正式支持“为了隔离高噪声中间过程而派发单个 fresh child”；这条路线不要求并行，也不打开 Manager Gate。
- DSH 已切换到 continuable subagent；Visualizer 已能显示 Manager 依赖图、工作单元与真实 child 的绑定关系。
- Codex 和 DSH 已有对应运行场景，但部分行为仍只有静态实现或配置证据，尚未经过目标 Runtime 实测。

这些既有语义保持不变：Direct-first、三个生产 Role、Manager Gate、Assurance、Artifact 权威和单写入者规则都不因本轮能力面优化而改变。

## 2. 当前最高优先级风险

### Codex 的 `sandbox_mode` 不能继续默认认为有效

当前 `sacha_readonly_worker` 和 `sacha_reviewer` 的 TOML 中都声明了：

```toml
sandbox_mode = "read-only"
```

但 Codex 最新 custom role 是否仍会把这个字段真正作用到 spawned child，需要重新按目标 Runtime 验证。后续统一区分四层事实：

```text
配置中声明
≠ 创建时请求
≠ Runtime 实际生效
≠ 行为已经验证
```

在真实行为验证完成前：

- 不把 TOML 中的 `sandbox_mode` 当成只读证据；
- 不把 Reviewer 称为“硬只读”；
- 文件写入能力只能标为“已验证 / 部分验证 / 未验证”；
- 不能用提示词中的“不要写文件”代替权限控制。

这是下一轮首先要解决的问题。

## 3. 剩余工作

| 优先级 | 项目 | 目标 | 完成标准 |
| --- | --- | --- | --- |
| P0 | 验证 Codex 文件写入边界 | 确认 `sandbox_mode` 是否真的作用于 child | 对 readonly worker 和 reviewer 做真实写入探针 |
| P1 | 关闭 child 自动 Skill 目录 | child 不再重新看到整个 Skill catalog | Runtime 证明自动 Skill 目录没有进入 child |
| P1 | 利用 Codex 原生能力缩减 | 减少无关 Shell、Apps、Plugins、Memory、权限请求等能力 | 形成真实能力矩阵，并区分请求值与实际值 |
| P1 | Capability Binding 直达 child | 父任务先选好 canonical Skill，child 不再重新发现 | child 只收到当前工作单元所需 Skill/reference |
| P1 | 单独验证 MCP / App | 文件只读不能代表外部系统只读 | 分别记录外部工具可见性和副作用能力 |
| P1 | Claude Code 能力 Agent | 为 researcher / worker / reviewer 建真正的工具边界 | 使用原生 `tools` / `disallowedTools` 并实测 |
| P2 | 强化入口竞争测试 | 验证大量 Skill 共存时 `using-sacha` 的召回和误触发 | 同时测 precision 和 recall |
| P2 | Cursor 能力收窄 | Cursor 不只做模型路由，也按能力缩小子 Agent 工具面 | 只映射当前 Runtime 能证明的能力 |

## 4. Codex 能力面目标

### 4.1 关闭 child 自动 Skill 目录

主任务已经完成 Skill 路由后，child 不应再次浏览全部 Skill。目标流程：

```text
主任务判断当前工作单元
→ 解析所需 capability
→ 选择 canonical Skill / reference
→ 创建 fresh child
→ child 只消费明确给出的能力输入
```

优先验证 Codex 当前是否真正支持 role-local 的 Skill suppression，例如：

```toml
[skills]
include_instructions = false
```

只有 Runtime 证明生效后才加入三个 Sacha 能力 Agent。这样隔离的不只是日志、搜索结果和被淘汰方案，还包括无关 Skill 带来的注意力竞争。

### 4.2 使用 Codex 已支持的能力缩减

Custom role 更适合做“只减能力”，而不是承担所有权限配置。下一轮重点核对当前版本是否真的能对 child 关闭：

- 自动 Skill 指令；
- Shell；
- Apps；
- Plugins；
- Memory；
- 权限请求工具。

建议目标：

- **Research**：关闭自动 Skill 目录、Shell、无关 Apps / Plugins / Memory，只保留调查所需读取和搜索能力。
- **Reviewer**：关闭自动 Skill 目录、Apps、Memory、权限请求；是否保留 Shell 取决于是否需要自己执行测试。即使保留 Shell，也不能据此声称文件只读。
- **Executor**：保留实施和验证能力，关闭自动 Skill 目录和无关外部能力，不允许取得新的调度权。

具体字段必须以当前 Runtime 实际 schema 和行为为准，不根据旧版本或配置文件存在性推断。

## 5. Project Capability Binding 要接到 child

当前 `setup-project` 已经能保存：

```text
Capability
→ canonical Skill
→ load policy
```

下一步要把这条链真正接到委派过程：

```text
工作单元需要 Capability B
→ Project Integration 解析 canonical Skill B
→ 主任务确认当前 load policy 允许使用
→ child 收到 Skill B 的明确 reference
```

边界：

- Core 只表达“当前工作单元需要 Capability B”；
- Project Integration 负责 canonical Skill 与 load policy；
- Runtime Adapter 负责把已确定的 reference 传给 child；
- child 不重新执行全局 Skill discovery，也不自行改写 Binding。

不要把项目所有绑定 Skill 一次性塞给 child，只传当前消费者需要的能力。

## 6. 能力证据要拆成多维

以后不再用一个模糊的“readonly”描述 Agent。至少分别记录：

| 能力 | readonly worker | executor | reviewer |
| --- | --- | --- | --- |
| 自动 Skill 目录 | 目标关闭 | 目标关闭 | 目标关闭 |
| 明确指定 Skill/reference | 允许 | 允许 | 允许 |
| 本地文件写入 | 待实测 | 允许 | 待实测 |
| Shell | 目标关闭 | 允许 | 按任务决定 |
| Apps / Plugins | 目标关闭 | 按任务决定 | 目标关闭 |
| MCP | 单独验证 | 单独验证 | 单独验证 |
| 权限升级 | 目标关闭 | 按任务决定 | 目标关闭 |
| Memory | 目标关闭 | 优先关闭 | 目标关闭 |
| 创建下级 Agent | 必须禁止 | 必须禁止 | 必须禁止 |
| 实际模型 / 推理强度 | Runtime 证据 | Runtime 证据 | Runtime 证据 |

每一项都要区分：

```text
配置值 → 请求值 → 实际值 → 行为证据
```

其中任一层缺失，都不能用后一层的措辞声称已经证明。

### 外部副作用单独处理

即使 Reviewer 不能修改本地文件，如果还能使用 GitHub MCP、数据库 MCP、部署工具或可写 App，仍然可能产生外部副作用。因此至少把以下三类能力分开：

```text
本地文件
外部系统 / MCP / Apps
下级 Agent 创建
```

不能因为其中一个维度被限制，就把整个 Agent 描述成“只读”。

## 7. Claude Code 下一步

Claude Code 当前主要还是“Role + Agent + 提示词”的映射。后续应建立真正的能力载体，并优先使用 Claude 原生工具限制：

- **researcher**：允许 Read / Glob / Grep / 必要 Web，禁止 Write / Edit 和下级 Agent。
- **worker**：保留实施和验证能力，禁止继续委派。
- **reviewer**：允许读取、diff 和必要测试，禁止 Write / Edit 和继续委派。

模型继续由 Claude Adapter 根据当前工作单元选择，不写死进 Agent 定义。是否使用 worktree 或更强文件系统隔离，按真实任务和 Runtime 能力决定。

## 8. 运行验证

### 8.1 扩展 `codex-agent-capability-routing`

从“参数组合场景”升级为真实能力探针，至少记录：

```text
请求的 agent_type
实际 Agent
请求模型 / 实际模型
推理强度
自动 Skill 目录是否存在
Shell 是否存在
Apps / Plugins / Memory 是否存在
MCP 是否存在
是否能创建下级 Agent
文件写入是否成功
```

不能让 child 自己报告“我没有这些能力”；必须使用原生工具 schema、Runtime 结果、工作区变化或受控外部 fixture 作为证据。

### 8.2 文件写入探针

分别对 `sacha_readonly_worker` 和 `sacha_reviewer` 执行安全的测试文件写入。结果只允许：

```text
已确认阻止
意外允许
无法验证
```

如果写入实际成功，当前 read-only 声明必须同步降级。

### 8.3 Skill 目录隔离

构造父任务拥有大量 Skill 的场景，创建 `sacha_readonly_worker`，验证：

- child 没有自动 Skill catalog；
- parent 明确传入的目标 Skill/reference 仍然可以使用。

### 8.4 Capability Binding

构造项目有 A/B/C 三项 capability，但当前工作单元只需要 B。验证 child 只收到 B，不重新发现 A/C。

### 8.5 Claude 能力边界

至少验证：

- researcher 不能写；
- reviewer 不能写、不能继续派发；
- worker 能执行已授权写入；
- 三者都使用 fresh context，并只返回压缩结果和必要 reference。

## 9. 实施顺序

严格按以下顺序推进：

1. 验证 Codex `sandbox_mode` 和真实写入边界；
2. 按实测结果修正文档、Agent 描述和证据口径；
3. 验证并关闭 child 自动 Skill 目录；
4. 使用 Codex 已证实可用的能力缩减；
5. 接通 Project Capability Binding → 精确 child 输入；
6. 补 MCP / Apps / 外部副作用证据；
7. 为 Claude Code 增加能力 Agent；
8. 最后扩展 Skill 竞争压力测试和 Cursor 能力收窄。

## 10. 明确不做

本轮不新增：

- Context Gate 或 Context Role；
- 固定“研究 → 规划 → 开发 → 验证”阶段；
- 第二份任务 DAG；
- 通用 memory / engram 权威；
- 根据 token 数自动打开 Manager Gate；
- 强制所有任务先派研究 Agent；
- 用 Agent 名称同时表示 Role、模型和权限；
- 用提示词代替 Runtime 权限；
- 在没有真实失败模式前建设复杂 PreToolUse 策略系统。

## 11. 下一会话启动方式

下一会话先读取当前 `main` 和本文件，再处理表格中最高优先级的未完成项。

不要默认本文记录的 Codex 实现细节仍然有效；涉及 custom role、Skill suppression、能力缩减、`spawn_agent` schema、MCP 继承和 sandbox 的内容，都必须重新核对目标 Runtime。

每完成一项，只更新：

- 当前状态；
- Runtime 证据；
- 新发现；
- 剩余待办。

不要重复扩写已经完成的背景，也不要把配置存在、schema 可解析或 Agent 自报当成行为已经通过。