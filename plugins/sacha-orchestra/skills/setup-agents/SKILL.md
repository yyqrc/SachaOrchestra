---
name: setup-agents
description: 显式配置 Sacha 官方 Codex 自定义 Agent；普通流程不得调用。
---

# Setup Agents（全局 Agent 配置）

## 功能

主流程外的显式配置能力：创建、更新或核对 Sacha-owned Codex Agent 文件，并报告配置层证据。

## 输入与首查

1. 入口为 Human 显式调用；该调用授权本次创建、更新或保持 Sacha-owned 文件。
2. 目标为 `CODEX_HOME/agents/sacha-luna-worker.toml` 和 `sacha-luna-worker-xhigh.toml`；未设置时使用当前用户 `.codex`。对应 [max](assets/sacha-luna-worker.toml) 与 [xhigh](assets/sacha-luna-worker-xhigh.toml) 模板是唯一 owner。

## 动作顺序

1. 运行[配置器](scripts/setup_agents.py) `--dry-run`，取得两个目标的 `create | update | no-op | conflict` 计划。
2. owner marker 与预期 namespaced identity 同时成立时允许自动更新；非 Sacha 文件或 identity 冲突停止整批写入。旧 `luna-worker*.toml` 保持原状。
3. 无 conflict 时在同一调用中执行 `--write`。写入前重读两个 preimage，全部临时 TOML 校验后原子替换。
4. 写后按完整字节、必填字段和两个 Agent identity 回读；任一失败时整批补偿恢复。

## 输出

- dry-run 冲突、计划变化或最终结果面向 Human 展示时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
- 返回 action、transaction、目标 path、delta、warning 和配置层验证；省略无消费者的 per-file/planned/installed hash。
- Runtime 证据分别报告 discovery、named transport selection、spawn/join 和 effective model/reasoning；宿主无遥测时标记未验证。

## 停止与禁止边界

- 写入授权仅覆盖上述 namespaced managed installation。
- 本 Skill 只管理用户级 Sacha Agent；`setup-project` 只管理 Project Integration，二者不互调或静默触发。
- Sacha 接受与 Agent 派发由正式入口和 workflow owner 处理；配置层证据与 Runtime discovery/使用证据分别报告。
