---
name: setup-agents
description: 显式配置 Sacha 官方 Codex 自定义 Agent；普通流程不得调用。
---

# Setup Agents（全局 Agent 配置）

## 工作流

1. 仅在 Human 显式调用后运行[配置器](scripts/setup_agents.py)的 `--dry-run`。
   目标为 `CODEX_HOME/agents/luna-worker.toml` 和 `luna-worker-xhigh.toml`；未设置时使用当前用户 `.codex`。对应 [max](assets/luna-worker.toml) 与 [xhigh](assets/luna-worker-xhigh.toml) 模板是唯一 owner。
2. 展示两个目标各自的 `create | update | no-op | conflict`、合并后的完整 `delta` 和 `planned_delta_sha256`。全为 `no-op` 才结束；任一 `conflict` 默认拒绝整批写入。
3. 等待 Human 对同一 delta/hash 的明确确认。写入使用 `--write --confirmed-planned-delta-sha256 <hash>`；替换 conflict 还须明确批准 `--replace-conflict`。
4. 配置器重读两个 preimage 并核对 hash，全部临时 TOML 校验后才替换。写后回读内容/hash、必填字段和两个 Agent identity；任一失败则整批补偿恢复。
5. 返回 action、transaction、目标/hash 和 warning。文件存在或 parse 成功不代表 Runtime 已发现。

## 边界

- 安装本 Skill 或插件不授权写入。本 Skill 只管理用户级 Sacha Agent，`setup-project` 只管理 Project Integration；二者不得互调或静默触发。
- `agents/openai.yaml` 仅是 Skill metadata，不是自定义 Agent TOML。
- Runtime 证据分别报告 discovery、named transport selection、spawn/join、effective model/reasoning；宿主无遥测时保持未验证，不用模板、任务名或自报补齐。
