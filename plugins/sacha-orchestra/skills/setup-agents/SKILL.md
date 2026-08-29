---
name: setup-agents
description: 显式配置 Sacha 官方 Codex 自定义 Agent；普通流程不得调用。
---

# Setup Agents（全局 Agent 配置）

## 功能

主流程外的显式配置能力：创建、更新或核对由 Sacha 管理的 Codex Agent 文件，并报告配置层证据。

## 输入与首查

1. 入口为 Human 显式调用；该调用授权本次创建、更新或保持由 Sacha 管理的文件。
2. 目标为 `CODEX_HOME/agents/` 下的五个 `sacha-*` 受管文件；未设置时使用当前用户 `.codex`。对应模板是唯一配置 Owner：
   - [Researcher](assets/sacha-researcher.toml)只读取代码、资料和现有 Runtime 状态，保留 Project Integration 已确认 Skill 使用的插件 Skill/MCP 只读查询。
   - [Reviewer](assets/sacha-reviewer.toml)可执行裁决所需验证并产生已授权的临时状态；[Executor](assets/sacha-executer.toml)实施并验证获授权工作单元。
   - 三类能力 Agent 关闭自动 Skill instructions、bundled Skills、Memory 和权限请求；Researcher 另关闭 Shell 与 Apps。模型和推理强度由 Adapter 每次派发。[DeepSeek](assets/sacha-deepseek-worker.toml)与[DeepSeek Pro](assets/sacha-deepseek-pro-worker.toml)继续使用模板内固定路线。

## 动作顺序

1. 运行[配置器](scripts/setup_agents.py) `--dry-run`，取得五个目标的 `create | update | no-op | conflict`，以及旧 `sacha-readonly-worker.toml` 的 `remove | no-op | conflict` 计划。
2. 自动更新或移除只接受 Owner 标记与预期 Agent 身份同时匹配的文件；其他冲突停止整批写入。已退出受管集合的 Luna/K3 文件和旧 `luna-worker*.toml` 保持原状。
3. 无 `conflict` 时在同一调用中执行 `--write`。配置器重读全部 preimage，校验并替换五个目标，回读成功后移除旧 Researcher 文件；任一步失败都恢复写入前状态。
4. 写后按完整字节和 Agent 类型回读：固定模型 Agent 匹配模型与强度；能力 Agent 不含固定模型或 `sandbox_mode`，并匹配各自 feature/Skill 降权。

## 输出

- 试运行（`dry-run`）冲突、计划变化或最终结果面向 Human 展示时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
- 返回 `action`、`transaction`、目标 path、`delta`、`warning` 和配置层验证；省略无消费者的 `per-file`/`planned`/`installed` hash。
- Runtime 证据分别报告发现（`discovery`）、具名传输选择（`named transport selection`）、`spawn`/`join`、实际模型/推理强度、权限状态与工具面；配置、schema 接受和 Agent 自报只证明自身，宿主无遥测时标记未验证。

## 停止与禁止边界

- 写入授权仅覆盖五个当前受管文件，以及 Owner 标记和旧身份均匹配的 `sacha-readonly-worker.toml` 迁移。
- 本 Skill 只管理用户级 Sacha Agent；`setup-project` 只管理 Project Integration，二者不互调或静默触发。
- Sacha 接受与 Agent 派发由正式入口和主任务处理；配置层证据与 Runtime 发现/使用证据分别报告。
- 宿主强制不可写只接受当前 Runtime 的直接证据；证据不可达时报告宿主缺口。
