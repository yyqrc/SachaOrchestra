---
name: document-project
description: 按项目策略生成 change archive/system guide，或在 closeout 复核候选并维护项目 CONTEXT；不替代 Artifact。
---

# Project Documentation（项目存档）

## 工作流

1. 只在 Human 明确请求，或 [Workflow Contract](../../core/workflow-contract.md) closeout candidate 成立时读取 confirmed Project Integration。候选检查只用当前任务最终事实，不扫历史；`disabled` 或无配置静默跳过。
2. 先选生命周期和目标：
   - Execution Report 是任务 Artifact/证据索引，留在 Spec/任务约定位置，本 Skill 不生成；
   - `change-archive`/done 文档记录已交付持久变化，`system-guide` 解释长期使用与维护，均写 Project Documentation root；
   - `project-context` 只收有跨任务消费者的稳定术语/约束，写 Project Context path 指定的 `CONTEXT.md` managed 区。
3. `on-request` 候选只向 Human 询问一次是否生成，肯定答复才形成 `human-request`；`required-at-closeout` 候选使用 `goal-closeout`。纯问答、无持久 delta、仅任务报告，或没有新增持久知识的一行/局部修复不询问。
4. 若 Project Integration 绑定 template catalog，运行时读取该 path 下当前 `profiles.json`：先按 `document_type` 过滤，再用 `primary_purpose`、`primary_question`、`choose_when`、`avoid_when` 选择唯一最高相关 Profile；选择完成前不读模板正文，选定后只读并校验该 Profile 的 `template`，其他模板独立变化不使项目绑定失效。正文必须回答 `required_topics`，但模板章节只是候选结构：按 `generation_policy` 删除、合并、改名或重排没有独立信息价值的可选章节，不为编号、目录、修订记录、字数或篇幅填充内容。并列或主要意图不清时只向 Human 展示候选差异，不随机选择、不混合模板。未绑定 catalog 时按文档类型回退插件内 `canonical-change-archive-v1` 或 `canonical-system-guide-v1` bundled 模板。禁止扫描 Documentation root、历史正文或相邻文件猜文风。`project-context` 不使用 catalog，以最终 Spec、真实证据、Review 和现有 `CONTEXT.md` 复核当前任务候选。
5. 以 `python -B scripts/generate_project_document.py --project-root <root> --input-json <json>` dry-run。
   `required-at-closeout + bounded-closeout` 覆盖当前持久 delta 时可直接写；`on-request` 或 `per-write-confirmation` 必须先取得本次 Human 明确请求/确认，再增加 `--per-write-confirmed --write`，目标或 planned delta 改变时重新确认。
6. 入口校验 Integration、授权、root containment、结构、preimage 与 path；catalog 模式校验当前 manifest 的选择合同、所选 Profile 的类型/版本/template path、选中模板的当前 SHA-256 与 `generation_policy`，不校验或冻结未选模板。输出拒绝残留占位符、模板作者说明和无实质正文的标题；不要求复刻完整 heading skeleton。发布文档只原子新建。Context 只写 managed 区；修改既有定义须 per-write confirmation，并发变化拒绝。
7. 报告类型、目标、transaction、验证与限制；只有确认并发 preimage、恢复或用户明确需要内容指纹时才展示对应 SHA-256，不把内部模板/中间结果 hash 堆进普通收尾。候选未满足事实、冲突、消费者或授权条件时留在任务记录。

## 回归场景

- 已批准复杂 Spec + 持久代码变化 + 实际 Runtime 验证：必须形成一次候选检查；`on-request` 询问一次，`required-at-closeout` 按授权进入 writer。
- 没有新增持久产品知识的一行修复、纯问答、无持久 delta：静默跳过，不加载 writer、不询问 Human。
- 消费项目 setup 显式绑定自己的 template catalog 后，由 manifest 在多个 change archive/system guide Profile 中选唯一最相关模板；项目名称、绝对路径和领域文风不得进入 Sacha Core 或默认 Skill。

## 边界

- 发布文档和 `CONTEXT.md` 不替代 Artifact/Handoff、不复制任务状态；writer 不替 Human 发明业务定义。
- 内部 task/thread ID、缓存路径和不可发布 evidence reference 不进入正文。
- generator 只证明输入、授权、路径与静态结构；Runtime trigger、内容语义质量和真实外部副作用需对应证据。
- 安装、Git、发布、外部消息及根外写入仍需各自授权。
