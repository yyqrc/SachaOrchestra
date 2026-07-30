---
name: setup-project
description: 显式生成或刷新 Sacha Project Integration；发现并按正文评估项目 Skill，以 dry-run、确认、hash 与回滚保护写入。
---

# Setup Project（项目接入）

## 工作流

1. 使用显式路径；否则由 [resolver](scripts/resolve_capability_queries.py) 从 workspace、Binding/Project AGENTS、SCM 解析唯一根；多候选 unresolved。
2. 只用当前 metadata 和已知同 plugin catalog locator。Catalog 只给 id、canonical Skill、副作用上界；其余以 `SKILL.md` 为准。
3. Human 标记项目 Skill root 为 `authority | mirror | independent | ignore`。完整读取 authority/independent 正文及其必需 locator；不按名称猜能力。
4. 从正文识别独立 goal unit，记录 goal、副作用、入口/前置、正文行、SHA-256 和可调度性；只映射 Runtime 可见且入口成立的 unit。
5. 把评估交给 [生成器](scripts/generate_project_integration.py)。生成器拒绝证据过期、只引 frontmatter、不可见或缺入口；load policy 由 Setup/Human 决定。
6. 可能使用 Pi 时运行[巡检器](scripts/inspect_pi_models.ps1)读取 `--list-models`；把既有 route 作为 `-ConfiguredModel` 传入并保持优先。
7. 其余按 `glm-5.2 | kimi k3 | deepseek | gpt-5.6 luna` 模糊筛选。展示候选后，由 Human 以 `--pi-model-binding <route>::<provider/model>` 保存；plugin 不保存完整型号。
8. 从现有配置形成 current/recommended。未明确的 Plan/文档值、授权或 Pi 路由展示一次完整 delta 并等待 Human 明确确认；历史 Binding 不是本轮写入授权。
9. 先 dry-run，报告冲突、warning 和 `planned_delta_sha256`；确认后才用 `--confirmed-planned-delta-sha256` 写入。delta 或旧 hash 变化时拒绝；写后 check，`partial_write` 保留现场。

## 边界

- 普通任务不调用；dry-run 不授权写入。
- marker 外 Project AGENTS byte-for-byte；原子写入并补偿恢复。
- Plan 根和文档根相互独立；外部根标记 non-portable，拒绝文件系统根。
- Provider id/Skill/副作用变化须显式刷新；policy 只由 Setup/Human 确认。
- 既有 Pi 路由默认保留；只有 Human 明确要求才用 `--clear-pi-model-bindings` 清空。精确型号只属于目标项目 Runtime 配置。
- Skill assessment 不写入 Binding；rerun 重新读取正文。
- 项目知识归 Project AGENTS/Domain Skill；安装、Git、发布等外部动作各自授权。
