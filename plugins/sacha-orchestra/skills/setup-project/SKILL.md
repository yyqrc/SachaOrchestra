---
name: setup-project
description: 显式生成/刷新 Project Integration；按正文评估项目 Skill，以 dry-run、确认、hash、回滚保护写入。
---

1. 显式 project root；否则用 [resolver](scripts/resolve_capability_queries.py) 从 Binding/AGENTS/SCM 定位唯一根；多候选 unresolved。
2. Catalog 只给 id、canonical Skill、副作用。Human 标记项目 Skill root 为 `authority | mirror | independent | ignore`，不得按名称猜能力。
3. 完整读取 authority/independent 的 `SKILL.md` 和必需 locator；按正文评估 goal、入口、证据行和 SHA-256，只映射 Runtime 可见且入口成立项。
4. `project.rules` 只取 Human 明示/本轮已选 provider；canonical Skill 只读 `assets/project-rules.md` 原始字节，以 `--project-rules-file <canonical-skill>::<asset-path>` 传入，不调用生成、转述或临时模板，也不进 Binding。
5. 交给[生成器](scripts/generate_project_integration.py)核对证据、路径和可见性；正文/证据缺失、歧义、冲突或 policy 未确认均不得写入。
6. 需要 Pi 时由[巡检器](scripts/inspect_pi_models.ps1)读 `--list-models`；已有 route 优先，其余按 `glm-5.2 | kimi k3 | deepseek | gpt-5.6 luna` 筛选，Human 用 `--pi-model-binding <route>::<provider/model>` 保存；清空须 `--clear-pi-model-bindings`。
7. 展示 current/recommended。Spec/文档、授权或 Pi 未明确时先展示完整 delta 并等待 Human 明确确认；历史 Binding 不是本轮写入授权。
8. 先读 managed block：保留适用项、同源刷新、新源合并；废弃才传 `--remove-project-rules-skill <canonical-skill>`。旧版无来源/hash 须核对归属并连同 asset 显式 `--replace-legacy-project-rules`，不得静默采信或丢弃。
   dry-run 报告 reconciliation、冲突、warning 和 `planned_delta_sha256`；确认后以 `--confirmed-planned-delta-sha256` 写入。

边界：

- 普通任务不调用；dry-run 不授权写入。marker 外 Project AGENTS byte-for-byte；写入原子并可补偿恢复。
- Spec/文档根独立；外部根标记 non-portable，拒绝文件系统根。
- Provider 变更须显式刷新，policy 由 Setup/Human 确认；项目知识和外部动作各归 owner。
- `project-rules` 按 canonical Skill 分段+SHA-256 合并；AGENTS 仅一个 managed block。未给模板则保留校验，删除显式，正文禁 Sacha marker。
