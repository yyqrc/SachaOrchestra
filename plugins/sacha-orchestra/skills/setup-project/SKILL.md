---
name: setup-project
description: 显式生成/刷新 Project Integration；评估项目 Skill，通过 `dry-run`、hash 和回滚保护写入。
---

# Setup Project（项目接入）

## 功能

主流程外的显式配置能力：发现并生成或刷新一个 Project Integration，使 Role 能定位项目规则、Capability Binding、Spec/Documentation/Context 位置。项目实施、文档正文和用户级 Agent 配置由对应 Skill 处理。

## 输入与首查

1. 接收 Human 显式 project base；未提供时由[解析器](scripts/resolve_capability_queries.py)从 Binding、AGENTS 和 SCM 定位唯一 project root。多候选保持 `unresolved`。
2. Catalog 提供 `id`、规范 Skill（canonical Skill）和副作用；Human 确认 Skill root 策略。完整读取 `authority`/`independent` 正文和调用必需 path，只映射 Runtime 可见且可独立交付的目标。
3. `project.rules` 使用 Human 明示或本轮已选 Provider 的规范 asset 原始字节。

## 动作顺序

1. [生成器](scripts/generate_project_integration.py)核对正文证据、SHA-256、path 和可见性。缺失、歧义、冲突或策略未确认时停止写入。
2. 需要 Pi 时由[巡检器](scripts/inspect_pi_models.ps1)执行 `--list-models`，按 `glm-5.2 | kimi k3 | deepseek | gpt-5.6 luna` 筛选；使用 `--pi-model-binding <route>::<provider/model>` 保存 Human 选择，使用 `--clear-pi-model-bindings` 清空。
3. 配置文档位置：
   - 首次 Spec storage root 默认 `docs/plan`。
   - Human 分别提供 Spec base 与 Project Documentation root；Setup 派生 `<spec-base>/plan` 和 `<spec-base>/CONTEXT.md`，原样保存 Project Documentation root。
   - 外部 path 标记 `non-portable`；文件系统根无效。
4. 项目可选绑定一个模板目录 root（template catalog root）。Setup 校验固定名 `profiles.json`、`manifest-ranked`/`tie-ask-Human`/`no-merge`/`no-ad-hoc` 选择合同、`generation_policy`，以及各 Profile 的 `required_topics`、`optional_sections`、类型、意图、template 的相对 path 和版本；Integration 只保存目录的 path kind/path。
5. 读取受管块，按规范 Skill 标记的归属规则：保留适用项、刷新同源 asset 完整内容、合并新源。无来源旧段需要 Human 显式指定并核对 asset；旧 `SOURCE SHA-256` 行在本次确认刷新时删除。
6. 试运行（`dry-run`）返回 `reconciliation`、冲突、`warning`、完整 `delta` 和 `planned_delta_sha256`。显式配置/刷新已授权且无待决策略、范围或高影响变化时，在同一流程把当前值传给 `--confirmed-planned-delta-sha256` 后写入。
7. 目标、变更或关键决定变化时重新试运行，只就变化请求 Human 确认。

## 输出

- 向 Human 请求策略/路径决定、确认计划变更或报告结果前读取 [Human Interaction Contract](../../core/human-interaction-contract.md)。
- 报告 `reconciliation`、写入 `transaction`、冲突、`warning`、验证和 `non-portable` path。

## 停止与禁止边界

- 普通任务不调用；写入只来自本轮显式配置/刷新授权。标记外的 AGENTS 保持不变，写入原子且可恢复。
- Provider 可选；无 Provider 时仍评估 Runtime 可见的项目 Skill，无映射时由 Role 使用项目规则和原生路线。
- `workflow-rule.md` 只保存 Runtime 项目差异；状态文件只供 Setup 恢复。
- Spec base、Project Documentation root 和 template catalog root 各自独立；Project Context path 由 Spec base 派生。
- 模板目录的 Profile 选择和正文生成由 `document-project` 处理。
- `project-rules` 按规范 Skill Owner 和 asset 完整内容合并；AGENTS 仅一个受管块，删除需要 Human 显式决定。
