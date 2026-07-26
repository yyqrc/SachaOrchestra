---
name: setup-project
description: 当 Human 显式调用 `$setup-project`，或明确要求初始化、刷新、检查 Sacha Project Integration 时使用；通过 dry-run、候选确认、hash 冲突保护和回滚生成当前 Schema v3 Binding。不得隐式触发。
---

# Setup Project（项目接入）

## 工作流

1. 把显式路径作为目标；否则使用 [resolver](scripts/resolve_capability_queries.py) 从 active workspace、适用 Project AGENTS/confirmed Binding 和最近 SCM root 中解析唯一项目。多候选保持 unresolved。
2. 只使用当前 Runtime context 已暴露的 plugin/Skill metadata 构造 task-local catalog；不得扫描 cache、marketplace、网络或任意磁盘。宽松 query 只产生候选，最终保存 canonical Skill。
3. 运行 bundled [生成器](scripts/generate_project_integration.py) 的默认 dry-run。它只检查有界规则引用、直接 Skill 根和根级 SCM；现有 managed Binding 非 Schema v3 时拒绝。
4. 集中展示项目、候选、SCM/rule/Skill-root 决策、capability reconciliation、冲突、planned diff/content 和 preimage/planned hash。未决或冲突时不写入。
5. Human 确认后才使用 `--write`，并为现有文件传入 matching expected SHA-256；未管理 workflow rule 还需显式 replace 许可。生成器不得猜测或覆盖并发变化。
6. 写入后再次 dry-run/check，报告 transaction、discovery、reconciliation、hash、冲突和恢复步骤。`partial_write` 必须保留现场并逐文件恢复。

## 边界

- 普通任务不调用本 Skill；只读 dry-run 不扩大写入授权。
- marker 外 Project AGENTS 内容保持 byte-for-byte；生成器只承诺单文件原子替换和跨文件补偿恢复。
- Binding 只保存项目相对定位和已确认关系，不保存正文、绝对路径、扫描 hash、版本或模糊 query。
- 项目命令、领域知识和验证规则仍归 Project AGENTS 或 Domain Skill。
- 安装、refresh、Git、发布和其他外部动作需要各自明确授权。
