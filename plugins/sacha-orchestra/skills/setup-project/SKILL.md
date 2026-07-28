---
name: setup-project
description: 显式生成或刷新 Sacha Project Integration；发现并按正文评估项目 Skill，以 dry-run、确认、hash 与回滚保护写入。
---

# Setup Project（项目接入）

## 工作流

1. 使用显式路径；否则由 [resolver](scripts/resolve_capability_queries.py) 从 workspace、Binding/Project AGENTS、SCM 解析唯一根；多候选 unresolved。
2. 按 Adapter 只用 context metadata；已知 locator 可定点读同 plugin Schema v2 catalog。Catalog 只拥有 id、canonical Skill、副作用上界，其余读 `SKILL.md`；无效时回退 metadata 并 warning。
3. 发现目标项目的 Skill root，并让 Human 将每个 root 定为 `authority`、`mirror`、`independent` 或 `ignore`。只评估 authority/independent；mirror 复用 authority，不重复入表。
4. 完整读取每个待评估 `SKILL.md` 正文；仅在正文把项目内 locator 声明为调用必需时继续读取。不得用 Skill id、目录名、frontmatter name/description 或关键词猜能力。
5. 从正文拆出零到多个独立 goal unit，逐项记录 goal、`inspect/change/verify/build/operate/coordinate`、副作用、静态入口、运行时前置、reason、覆盖步骤/输出的正文行证据和 `schedulable/support_only/unavailable`。只有正文定义了可独立交付的有界目标、当前 Runtime 可见且必需静态入口存在时才标记 `schedulable`；先完成判定，再分配 capability id。其余只保留评估，不生成 mapping。
6. 按 [Project Skill Evidence](references/project-skill-evidence.md) 把当前 Runtime 可见的项目 Skill 与逐 Skill JSON evidence 传给 [生成器](scripts/generate_project_integration.py)；生成器核对 authority/independent 身份、完整覆盖、正文行、Skill SHA-256、必需路径和可见性。未评估、证据过期、仅引用 frontmatter、不可见或缺必需入口时拒绝；每个 schedulable unit 仍须由 Setup/Human 明确 load policy。
7. 从现有 Binding、Project AGENTS 和项目约定形成当前值与推荐值。Plan 根或项目文档 policy/root/write authorization 未在本轮请求明确给出时，一次展示 current/recommended、取舍与完整 planned delta，并等待 Human 明确确认；历史 Binding 只作默认候选，不是本轮写入授权。
8. Plan 根和文档根可分别使用项目相对或外部绝对路径；外部根标记 non-portable，拒绝文件系统根，不可达只 warning。
9. 运行生成器 dry-run，一次展示项目 Skill assessments/candidates、current/recommended 配置、mapping/load policy、planned content/hash、warning、冲突和 `planned_delta_sha256`；不得创建目录或外写。
10. 本轮请求已明确完整配置与写入授权且 dry-run 一致，或 Human 明确确认该完整 delta 后，才把返回值作为 `--confirmed-planned-delta-sha256` 传给 `--write`。缺失/过期确认值或 delta 变化时拒绝并重新 dry-run/确认；现有文件仍需 expected SHA-256，未管理 workflow 仍需 replace 许可。
11. 写后 dry-run/check，报告 transaction/hash/warning/冲突；`partial_write` 保留现场。

## 边界

- 普通任务不调用；dry-run 不授权写入。
- marker 外 Project AGENTS byte-for-byte；写入使用原子替换与补偿恢复。
- Binding 可分别保存 confirmed non-portable Plan 根和文档根；rerun 未改值时原样保留。
- Provider id/Skill/副作用变化须显式刷新；Binding policy 只由 Setup/Human 确认。
- 项目 Skill assessment 是本轮证据，不写入 Binding；rerun 重新读取正文。Binding 仍只保存 confirmed capability id、Skill 与 policy。
- 项目知识归 Project AGENTS/Domain Skill；安装、refresh、Git、发布及其他外部动作需各自授权。
