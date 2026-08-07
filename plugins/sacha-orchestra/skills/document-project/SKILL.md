---
name: document-project
description: 仅在 Workflow closeout candidate 成立后按项目策略生成存档/指南或维护项目 CONTEXT；不能作为用户入口，不替代 Artifact。
---

# Project Documentation（项目存档）

## 功能

在 [Workflow Contract](../../core/workflow-contract.md) closeout candidate 成立后，按 confirmed Project Integration 和 Human 授权生成长期消费的项目文档或维护 Project Context。

## 输入与首查

1. 入口为 [Workflow Contract](../../core/workflow-contract.md) closeout candidate 成立后的 workflow owner 路由；随后读取 confirmed Project Integration。候选检查只使用当前任务最终事实；`disabled` 或无配置静默跳过。
2. 从当前任务最终事实选择生命周期和目标：
   - Execution Report 作为任务 Artifact/证据索引，留在 Spec/任务约定位置；
   - `change-archive`/done 文档记录已交付持久变化，`system-guide` 解释长期使用与维护，均写 Project Documentation root；
   - `project-context` 只收有跨任务消费者的稳定术语/约束，写 Project Context path 指定的 `CONTEXT.md` managed 区。
3. `on-request` 只在 candidate 成立后询问一次；`required-at-closeout` 使用 `goal-closeout`。纯问答、无持久 delta、仅任务报告或没有新增持久知识的局部修复静默跳过。

## 动作顺序

1. Project Integration 绑定 template catalog 时读取当前 `profiles.json`：
   - 按 `document_type` 过滤，再用 `primary_purpose`、`primary_question`、`choose_when`、`avoid_when` 选择唯一最高相关 Profile。
   - 选定后只读取并校验该 Profile 的 `template`；正文覆盖 `required_topics`，可按 `generation_policy` 删除、合并、改名或重排可选章节。
   - Profile 并列或主要意图不清时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)，向 Human 展示候选差异并请求选择。
   - 未绑定 catalog 时按文档类型使用插件内 `canonical-change-archive-v1` 或 `canonical-system-guide-v1` bundled 模板。
2. `project-context` 使用最终 Spec、真实证据、Review 和现有 `CONTEXT.md` 复核当前任务候选，不使用 template catalog。
3. 运行 `python -B scripts/generate_project_document.py --project-root <root> --input-json <json>` dry-run。
4. `required-at-closeout + bounded-closeout` 覆盖当前持久 delta 时直接写入；`on-request` 或 `per-write-confirmation` 在 Human 确认后增加 `--per-write-confirmed --write`。目标或 planned delta 改变时重新确认。
5. 校验 Integration、授权、root containment、结构、preimage 与 path。catalog 模式校验当前 manifest、所选 Profile 的类型/版本/template path、选中模板的 SHA-256 与 `generation_policy`。正文必须清除占位符和模板作者说明，只保留有实质内容的标题。
6. 发布文档原子新建；Context 只写 managed 区。修改既有定义需要 per-write confirmation，并发变化停止写入。

## 输出

- 向 Human 提问、确认或报告结果时读取 [Human Interaction Contract](../../core/human-interaction-contract.md)；报告文档类型、目标 path、transaction、验证与限制。
- SHA-256 只在并发 preimage、恢复或 Human 明确需要内容指纹时展示。
- 未满足事实、消费者或授权条件的候选，以及发生冲突的候选，保留在任务记录。

## 停止与禁止边界

- 本 Skill 只写 Project Documentation root 或 Project Context managed 区；任务 Artifact/Handoff 由 [Artifact Protocol](../../core/artifact-protocol.md) 管理。
- 正文只使用可发布事实，不包含内部 task/thread ID、缓存 path 或不可发布 evidence reference。
- template catalog 是唯一文风来源；文风只读取所选 Profile。
- generator 的证据范围为输入、授权、path 与静态结构；Runtime trigger、内容语义和外部副作用分别验证。
- 安装、Git、发布、外部消息及 root 外写入使用各自授权。
