# Codex × Antigravity ACP 跨模型协作

状态：已完成

## 目标与范围

在 Codex 中保留原生 V2 子代理和精确选型，通过官方 Antigravity CLI 为探索和独立评审增加第二种模型视角。重要方案可以用同一 Gemini 会话多轮质询，正式 Spec 在提交审阅前接受独立方案评审，实施后的独立评审按影响选择覆盖。只实现 Codex 主宿主。Antigravity 提供只读探索与评审代理，实施与现有迁移继续走 Codex 路径。

基线为 `main` 的 `0a3181824a8d745aced72ebaeacdae314711c631`，插件版本 `1.0.27`。本次批准范围是源码改动和本地验证。官方 CLI 安装、用户配置写入、外部认证、调用费用和项目资料外发按各自授权执行。

## 实施

1. 先在 [顶层设计](../../../PLUGIN_DESIGN.md) 中说明应使用正式方案评审的步骤、Reviewer 的两种评审对象和显式配置范围。再在 [工作流](../../../plugins/sacha-orchestra/core/workflow-contract.md) 中接入原有批准和返修，在 [验收规则](../../../plugins/sacha-orchestra/core/assurance-contract.md) 中定义评审基线和独立性。接入这些能力的宿主使用分级安排。已有有效批准与原路径继续适用。
2. [Explore](../../../plugins/sacha-orchestra/skills/explore/SKILL.md) 按输入选择脑暴、质询、调查比较。主任务把影响取舍的观点转交原会话，双方核对需要保留的约束。正式 Spec 和实施结果分别交独立 Reviewer。双模型结果评审采用同一基线和原始证据，独立收集首轮发现。不降低既有独立评审要求，不自动替换用户明确指定的模型或覆盖。
3. [Codex 适配器](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md#32-antigravity-acp) 调用发布目录内的 [Python ACP 客户端](../../../plugins/sacha-orchestra/adapters/codex/scripts/agy_acp.py)。从已核对的绝对路径启动官方 CLI，每次只执行一次初始化探测或一次会话操作。按 setup 保存的认证方式建立会话。本机选择复用现有 CLI 登录，由官方 CLI 在会话调用时处理，登录错误不切换认证方式。按服务端声明建立会话或按原会话标识续接，确认当前模型与推理选项，再发送 UTF-8 输入。严格区分协议终态、文本、工具事件、直接子进程退出及独立评审结论。超时或中断发出取消并等待终态。未知状态保留原标识，不重复派发。
4. 扩展 [setup-agents 配置器](../../../plugins/sacha-orchestra/skills/setup-agents/scripts/setup_agents.py) 的目标选择。Antigravity 两份模板安装到 `~/.gemini/config/agents/<name>/agent.md`，只开放读文件和搜索，关闭命令执行。复用原归属标记、冲突保护、写后回读和回滚。setup 当场验证角色发现和 ACP 握手，再保存本机 CLI 路径与认证选择。后续派发直接从保存的配置启动，一次调用内完成协议握手和会话动作。

## 验收

- 在隔离目录检查 Codex、Antigravity 和两者组合。观察 dry-run、写入、重跑、冲突和回滚。正式 setup 须由 `agy agents` 发现两份用户级角色，并经 ACP 握手后保存连接。确认后续派发直接读保存的连接，缺少配置时原生 Codex 仍可用。
- 从 Codex 本地命令调用官方 CLI，记录版本、握手、角色、工作目录、实际认证方式、模型和原生会话标识。对同一探索目标连续发送三轮，包含一次新用户决定。重启 CLI 后按原标识续接，另开独立会话验证上下文隔离。在授权范围内尝试写入和有副作用的命令，检查工作区与实际工具权限。取消后确认回合、直接子进程和相关活动均已停止。
- 用同一真实规划任务比较纯 GPT 和跨模型的质询与方案评审。独立核对删掉了哪些无必要机制、必要约束是否保留、发现了哪些设计问题及实际耗时和调用。用来源隔离、Spec 修订和工作区差异证明未批准时只有规划。实施结果分别验证自检、一个独立评审和两个模型独立评审的覆盖与返修。用明确额度错误及未知调用状态分别核对选路，沿用原生 V2 和原来的实施授权条件。

## 联调前提

本机已安装并完成官方 `agy` 1.5.18 的 ACP v1 握手，正式用户配置中的两份角色可以被发现。模型会话需使用获准的认证方式。首轮外发范围只包含隔离的合成测试文本与代码。Google 消费订阅对第三方应用封装有使用限制。 [Google FAQ](https://antigravity.google/docs/faq)
