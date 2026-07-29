---
name: setup-project
description: 显式生成或刷新 Sacha Project Integration；发现并按正文评估项目 Skill，以 dry-run、确认、hash 与回滚保护写入。
---

# Setup Project（项目接入）

## 工作流

1. 使用显式路径；否则由 [resolver](scripts/resolve_capability_queries.py) 从 workspace、Binding/Project AGENTS、SCM 解析唯一根；多候选 unresolved。
2. 只用当前 context metadata 和已知同 plugin catalog locator。Catalog 只提供 capability id、canonical Skill 和副作用上界；其余以 `SKILL.md` 为准。
3. 找到项目 Skill root 后，让 Human 标记 `authority | mirror | independent | ignore`。完整读取 authority/independent 的 `SKILL.md` 及其声明为调用必需的项目内 locator；不按名称或关键词猜能力。
4. 从正文识别可独立交付的 goal unit。记录 goal、动作类型、副作用、必需入口/前置、正文行证据和 `schedulable | support_only | unavailable`；只有当前 Runtime 可见且入口成立的 unit 才能映射。
5. 把完整评估和 Skill SHA-256 交给 [生成器](scripts/generate_project_integration.py)。生成器拒绝未评估、证据过期、只引用 frontmatter、不可见或缺入口的能力；每个 schedulable unit 的 load policy 仍由 Setup/Human 决定。
6. 从现有 Binding、Project AGENTS 和项目约定形成 current/recommended。未由本轮请求明确的 Plan/文档根、policy 或 write authorization 只展示一次完整 planned delta 并等待 Human 明确确认；历史 Binding 不是本轮写入授权。
7. 先 dry-run，报告配置、mapping、warning、冲突和 `planned_delta_sha256`。只有本轮已明确完整配置与写入授权，或 Human 确认该 delta 后，才用 `--confirmed-planned-delta-sha256` 写入；delta 变化、旧 hash 不符或 replace 未授权时拒绝。
8. 写后 check 并报告 transaction/hash/warning/冲突；`partial_write` 保留现场。

## 边界

- 普通任务不调用；dry-run 不授权写入。
- marker 外 Project AGENTS byte-for-byte；写入使用原子替换与补偿恢复。
- Plan 根和文档根相互独立；外部根标记 non-portable，拒绝文件系统根。
- Provider id/Skill/副作用变化须显式刷新；Binding policy 只由 Setup/Human 确认。
- Skill assessment 不写入 Binding；rerun 重新读取正文。
- 项目知识归 Project AGENTS/Domain Skill；安装、refresh、Git、发布及其他外部动作需各自授权。
