---
name: setup-agents
description: 用户明确要求配置或检查 Sacha 管理的 Codex 或 Antigravity Agent 时使用。
---

# Setup Agents（全局 Agent 配置）

## 功能

创建、更新或核对用户选定工具的 Sacha Agent 文件，并报告配置层证据。

## 输入与首查

1. 沿用用户明确选择的 Codex、Antigravity 或两者。选择会改变获准写入的配置范围，目标仍不明确时先确认。只要求检查时使用试运行。
2. Codex 使用 `CODEX_HOME/agents/` 下的五个 `sacha-*` 文件。未设置 `CODEX_HOME` 时使用当前用户的 `.codex/agents/`。
   - [研究代理](assets/sacha-researcher.toml)只读取代码、资料和运行状态，也可使用项目接入配置已确认的插件技能和 MCP 只读查询。
   - [Reviewer](assets/sacha-reviewer.toml)可执行裁决所需验证并产生已授权的临时状态；[Executor](assets/sacha-executer.toml)实施并验证获授权工作单元。
   - 三类能力 Agent 关闭自动 Skill instructions、bundled Skills、Memory 和权限请求；Researcher 另关闭 Shell 与 Apps。模型和推理强度由 Adapter 每次派发。[DeepSeek](assets/sacha-deepseek-worker.toml)与[DeepSeek Pro](assets/sacha-deepseek-pro-worker.toml)继续使用模板内固定路线。
3. Antigravity 使用 `~/.gemini/config/agents/<name>/agent.md`。参考 [Explorer](assets/agy/sacha-explorer/agent.md) 和 [Reviewer](assets/agy/sacha-reviewer/agent.md) 模板。只开放读文件和搜索，关闭命令执行，省略固定模型。Reviewer 将需要副作用的验证交回主任务。

## 动作顺序

1. 为[配置器](scripts/setup_agents.py)选择参数。
   - **目标和操作。** 用 `--target codex|agy|both` 选择目标，省略时用 Codex。已有写入授权时用 `--write`，只检查时用 `--dry-run`。
   - **CLI 路径。** 配置 Antigravity 时沿用已保存的路径或使用官方安装位置。其他安装位置用已核对的 `--agy-executable <绝对路径>`。
   - **认证方式。** 已在 CLI 登录且明确选择复用时，用 `--agy-auth cached-login`。已选择并获准使用 API Key 时，用 `--agy-auth gemini-api-key`。省略认证参数时沿用已保存的选择，首次可只验证本机连接。
2. 配置器检查归属、身份和冲突。配置 Antigravity 角色或连接发生变化时，在用户配置目录核对两份角色的发现、ACP 握手及相应认证能力。通过后保存 `~/.gemini/config/sacha-acp.json`。连接配置只记录可执行文件路径和认证选择。复用登录时由官方 CLI 在建立会话时读取自己的登录状态。失败按现有事务恢复，配置相同且回读一致时复用结果。
3. 隔离验证可用 `--codex-home` 和 `--agy-config`。用 `--agy-config` 在指定目录准备模板时，角色发现和派发连接仍以正式 setup 为准。

## 输出

- 试运行（`dry-run`）冲突、计划变化或最终结果面向 Human 展示时读取 [交互规则](../../core/human-interaction-contract.md)。
- 说明实际创建、更新、移除或保留了哪些 Agent 配置，给出涉及的路径和配置验证结果。只完成预检时说明尚未写入。出现冲突或影响使用的警告时，说明受影响项及下一步。需要核对或排障时，引用工具返回的 `action`、`transaction`、`delta` 或 `warning`。只有结果使用方需要核对时才提供 `per-file`、`planned` 或 `installed` 哈希。
- 分别报告文件回读、角色发现、握手及是否保存了可用于派发的认证方式。真实会话按 [Codex 适配器的证据要求](../../adapters/codex/runtime-adapter.md#4-进度与证据边界)核对。

## 停止与禁止边界

- 写入授权限于选定工具的受管文件。选中 Antigravity 时包含本机派发配置。选中 Codex 时包含归属标记和旧身份均匹配的 `sacha-readonly-worker.toml` 迁移。
- 本技能管理用户级 Sacha 代理配置。`setup-project` 管理项目接入配置。两项技能各自由用户明确调用。
- 入口判断和代理派发仍由主任务处理。运行环境是否强制只读，须用当前运行环境的直接证据核实。证据不可达时说明缺口。
