---
name: setup-project
description: 显式生成或刷新 Sacha Project Integration；dry-run、确认、hash 与回滚保护写入。
---

# Setup Project（项目接入）

## 工作流

1. 使用显式路径；否则由 [resolver](scripts/resolve_capability_queries.py) 从 workspace、Binding/Project AGENTS、SCM 解析唯一根；多候选 unresolved。
2. 按 Adapter 只用 context metadata；已知 locator 可定点读同 plugin Schema v2 catalog。Catalog 只拥有 id、canonical Skill、副作用上界，其余读 `SKILL.md`；无效时回退 metadata 并 warning。
3. 从现有 Binding、Project AGENTS 和项目约定推断 Plan 根与文档策略；无约定时推荐项目内 `docs/plans` 与 `on-request` 文档。只有多个选择会实质改变路径、可移植性或授权时询问，并一次展示推荐与取舍。
4. Plan 根和文档根可分别使用项目相对或外部绝对路径；外部根标记 non-portable，拒绝文件系统根，不可达只 warning。
5. 运行 [生成器](scripts/generate_project_integration.py) dry-run，一次展示配置、mapping/load policy、planned content/hash、warning 和冲突；不得创建目录或外写。
6. 显式请求已包含完整 planned delta 的写入授权且未扩大范围时直接 `--write`；否则只对完整 delta 确认一次。现有文件需 expected SHA-256，未管理 workflow 还需 replace 许可；delta 变化后重新确认。
7. 写后 dry-run/check，报告 transaction/hash/warning/冲突；`partial_write` 保留现场。

## 边界

- 普通任务不调用；dry-run 不授权写入。
- marker 外 Project AGENTS byte-for-byte；写入使用原子替换与补偿恢复。
- Binding 可分别保存 confirmed non-portable Plan 根和文档根；rerun 未改值时原样保留。
- Provider id/Skill/副作用变化须显式刷新；Binding policy 只由 Setup/Human 确认。
- 项目知识归 Project AGENTS/Domain Skill；安装、refresh、Git、发布及其他外部动作需各自授权。
