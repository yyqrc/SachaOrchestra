---
name: setup-agents
description: 显式配置 Sacha 官方 Codex 自定义 Agent；普通流程不得调用。
---

# Setup Agents（全局 Agent 配置）

## 功能

主流程外的显式配置能力：创建、更新或核对由 Sacha 管理的 Codex Agent 文件，并报告配置层证据。

## 输入与首查

1. 入口为 Human 显式调用；该调用授权本次创建、更新或保持由 Sacha 管理的文件。
2. 目标为 `CODEX_HOME/agents/` 下的五个 `sacha-*` 受管文件；未设置时使用当前用户 `.codex`。[只读调查](assets/sacha-readonly-worker.toml)与[独立 Reviewer](assets/sacha-reviewer.toml)固定 `sandbox_mode="read-only"`；[实施验证](assets/sacha-executer.toml)不设置 `sandbox_mode`，沿用父任务实际边界。三者的模型与推理强度均由 Adapter 每次派发；[DeepSeek](assets/sacha-deepseek-worker.toml)与[DeepSeek Pro](assets/sacha-deepseek-pro-worker.toml)继续作为固定模型 Agent。对应模板是唯一 Owner。

## 动作顺序

1. 运行[配置器](scripts/setup_agents.py) `--dry-run`，取得五个目标的 `create | update | no-op | conflict` 计划。
2. Owner 标记与预期命名空间标识同时成立时允许自动更新；非 Sacha 文件或标识冲突会停止整批写入。已退出受管集合的 Luna/K3 文件和旧 `luna-worker*.toml` 保持原状。
3. 无 `conflict` 时在同一调用中执行 `--write`。写入前重读全部写入前内容（preimage），全部临时 TOML 校验后原子替换。
4. 写后按完整字节、共同必填字段和各 Agent 类型回读：固定模型 Agent 必须匹配模型与强度；能力 Agent 必须没有固定模型，只读类型还须匹配 `sandbox_mode`；任一失败时整批补偿恢复。

## 输出

- 试运行（`dry-run`）冲突、计划变化或最终结果面向 Human 展示时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
- 返回 `action`、`transaction`、目标 path、`delta`、`warning` 和配置层验证；省略无消费者的 `per-file`/`planned`/`installed` hash。
- Runtime 证据分别报告发现（`discovery`）、具名传输选择（`named transport selection`）、`spawn`/`join` 和实际模型/推理强度；宿主无遥测时标记未验证。

## 停止与禁止边界

- 写入授权仅覆盖上述带命名空间的受管安装。
- 本 Skill 只管理用户级 Sacha Agent；`setup-project` 只管理 Project Integration，二者不互调或静默触发。
- Sacha 接受与 Agent 派发由正式入口和主任务处理；配置层证据与 Runtime 发现/使用证据分别报告。
