---
name: setup-agents
description: 显式配置 Sacha 官方 Codex 自定义 Agent；普通流程不得调用。
---

# Setup Agents（全局 Agent 配置）

## 工作流

1. 仅在 Human 显式调用后运行[配置器](scripts/setup_agents.py)。显式调用授权本次创建、更新或保持 Sacha-owned 文件；先用 `--dry-run` 展示计划，若无 conflict 就在同一调用流程继续 `--write`，不等待第二次 hash 确认。
   目标为 `CODEX_HOME/agents/sacha-luna-worker.toml` 和 `sacha-luna-worker-xhigh.toml`；未设置时使用当前用户 `.codex`。对应 [max](assets/sacha-luna-worker.toml) 与 [xhigh](assets/sacha-luna-worker-xhigh.toml) 模板是唯一 owner。
2. 配置器计划两个目标的 `create | update | no-op | conflict`。只有 owner marker 与预期 namespaced identity 同时成立才可自动更新；非 Sacha 文件或身份冲突一律拒绝整批写入，不提供强制覆盖。旧 `luna-worker*.toml` 不自动改名、覆盖或删除。
3. 写入前重读两个 preimage，全部临时 TOML 校验后才原子替换。写后按完整字节、必填字段和两个 Agent identity 回读；任一失败则整批补偿恢复。
4. 返回 action、transaction、目标、delta 和 warning；不输出无消费者的 per-file/planned/installed hash。文件存在或 parse 成功不代表 Runtime 已发现。

## 边界

- 安装本 Skill 或插件不授权写入；只有显式调用本 Skill 才授权上述 namespaced managed installation。本 Skill 只管理用户级 Sacha Agent，`setup-project` 只管理 Project Integration；二者不得互调或静默触发。
- `agents/openai.yaml` 仅是 Skill metadata，不是自定义 Agent TOML。
- Runtime 证据分别报告 discovery、named transport selection、spawn/join、effective model/reasoning；宿主无遥测时保持未验证，不用模板、任务名或自报补齐。
- Codex 原生精确 spawn 可验证地支持 Luna model/effort、effective route 与失败 fallback 后，移除这项兼容安装能力；仅有文档声明不算验证。
