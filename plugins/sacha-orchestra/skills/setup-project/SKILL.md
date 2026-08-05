---
name: setup-project
description: 显式生成/刷新 Project Integration；评估项目 Skill，以 dry-run、hash 和回滚保护写入。
---

## 工作流

1. 使用显式 project root；否则由 [resolver](scripts/resolve_capability_queries.py) 从 Binding/AGENTS/SCM 定位唯一根，多候选保持 unresolved。
2. Catalog 只给 id、canonical Skill 和副作用。Human 标记 Skill root policy；完整读取 authority/independent 正文和调用必需 path，只映射 Runtime 可见且可独立交付的 goal。
3. `project.rules` 只取 Human 明示或本轮已选 provider 的 canonical asset 原始字节，不生成、转述或写入 Binding。
4. [生成器](scripts/generate_project_integration.py)核对正文证据、SHA-256、路径和可见性；缺失、歧义、冲突或 policy 未确认均不写入。
5. 需要 Pi 时由[巡检器](scripts/inspect_pi_models.ps1)执行 `--list-models`，按 `glm-5.2 | kimi k3 | deepseek | gpt-5.6 luna` 筛选；Human 用 `--pi-model-binding <route>::<provider/model>` 保存，清空用 `--clear-pi-model-bindings`。
6. 首次 Spec storage root 默认 `docs/plan`；Human 独立提供 Spec base 与 Project Documentation root。Setup 派生 `<spec-base>/plan`，并把 Project Context path 定位为 `<spec-base>/CONTEXT.md`；Project Documentation root 原样保存，不追加目录。两项输入不要求同根也不互相推导。Setup 不创建正文。
7. 读取 managed block 后保留适用项、同源刷新、新源合并；废弃或替换无来源/hash 的旧段必须显式指定并核对 asset。
8. dry-run 返回 reconciliation、冲突、warning、完整 delta 和 `planned_delta_sha256`；Human 以 `--confirmed-planned-delta-sha256` matching hash 写入。历史 Binding 不授权本轮写入。

## 边界

- 普通任务不调用；dry-run 不授权写入。marker 外 AGENTS 不变；写入原子且可恢复。
- Provider 可选；无 Provider 时仍评估 Runtime 可见的项目 Skill，无 mapping 时由 Role 使用项目规则和原生路线。
- `workflow-rule.md` 只保留 Runtime 项目差异；state 文件只供 Setup 恢复，普通 Role 不读取。
- Spec base 与 Project Documentation root 独立；外部路径标记 non-portable，拒绝文件系统根。Project Context path 复用 Spec base，不扫描历史任务推断内容。
- Provider 变更须显式刷新，policy 由 Setup/Human 确认；项目知识和外部动作各归 owner。
- `project-rules` 按 canonical Skill 和 SHA-256 合并；AGENTS 仅一个 managed block，删除必须显式。
