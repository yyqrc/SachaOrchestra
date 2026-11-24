---
name: setup-agents
description: 显式配置 Sacha 官方 Codex 自定义 Agent；普通流程不得调用。
---

# Setup Agents（全局 Agent 配置）

## 功能

主流程外的显式配置能力：创建、更新或核对由 Sacha 管理的 Codex Agent 文件，并报告配置层证据。

## 输入与首查

1. 用户明确调用时，可创建、更新或保留本次涉及的 Sacha 配置文件。
2. 配置以对应模板为准。目标是 `CODEX_HOME/agents/` 下的五个 `sacha-*` 文件。未设置 `CODEX_HOME` 时使用当前用户的 `.codex/agents/`：
   - [研究代理](assets/sacha-researcher.toml)只读取代码、资料和运行状态，也可使用项目接入配置已确认的插件技能和 MCP 只读查询。
   - [Reviewer](assets/sacha-reviewer.toml)可执行裁决所需验证并产生已授权的临时状态；[Executor](assets/sacha-executer.toml)实施并验证获授权工作单元。
   - 三类能力 Agent 关闭自动 Skill instructions、bundled Skills、Memory 和权限请求；Researcher 另关闭 Shell 与 Apps。模型和推理强度由 Adapter 每次派发。[DeepSeek](assets/sacha-deepseek-worker.toml)与[DeepSeek Pro](assets/sacha-deepseek-pro-worker.toml)继续使用模板内固定路线。

## 动作顺序

1. 已取得配置授权且目标明确时，直接运行[配置器](scripts/setup_agents.py) `--write`。用户只要检查或需先看具体冲突时，使用 `--dry-run`。
2. 配置器在写入时检查归属和身份、拒绝冲突、回读校验，并在失败时恢复写入前状态。以配置器的实际结果报告安装、更新、移除或保持不变的项目。

## 输出

- 试运行（`dry-run`）冲突、计划变化或最终结果面向 Human 展示时读取 [交互规则](../../core/human-interaction-contract.md)。
- 说明实际创建、更新、移除或保留了哪些 Agent 配置，给出涉及的路径和配置验证结果。只完成预检时说明尚未写入。出现冲突或影响使用的警告时，说明受影响项及下一步。需要核对或排障时，引用工具返回的 `action`、`transaction`、`delta` 或 `warning`。只有结果使用方需要核对时才提供 `per-file`、`planned` 或 `installed` 哈希。
- 单纯配置以写后回读为准。本次也要求检查发现或派发时，按 [Codex 适配器的证据要求](../../adapters/codex/runtime-adapter.md#4-进度与证据边界)核对实际运行。分别报告配置结果和有直接证据的运行结果，并说明影响使用的证据缺口。

## 停止与禁止边界

- 写入授权仅覆盖五个受管文件，以及归属标记和旧身份均匹配的 `sacha-readonly-worker.toml` 迁移。
- 本技能管理用户级 Sacha 代理配置。`setup-project` 管理项目接入配置。两项技能各自由用户明确调用。
- 入口判断和代理派发仍由主任务处理。运行环境是否强制只读，须用当前运行环境的直接证据核实。证据不可达时说明缺口。
