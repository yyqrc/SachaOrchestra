---
name: project-documentation
description: 按项目策略生成 change archive/system guide，或在 closeout 复核候选并维护项目 CONTEXT；不替代 Artifact。
---

# Project Documentation（项目存档）

## 工作流

1. 读取 confirmed Project Integration；`disabled` 不生成，`on-request` 只响应 Human，`required-at-closeout` 仅处理持久产品改动的合法 closeout。
2. `change-archive | system-guide` 按 `assets/` 示例提供标题、trigger、持久 delta、输出路径及八段正文。`project-context` 只收当前任务候选，并以最终 Spec、真实证据、Review 和现有 `CONTEXT.md` 复核，不扫历史任务。
3. 以 `python -B scripts/generate_project_document.py --project-root <root> --input-json <json>` dry-run。
   `bounded-closeout` 已覆盖时直接写；当前明确请求可满足 `per-write-confirmation` 并增加 `--per-write-confirmed --write`，planned delta 改变时才重新确认。
4. 入口校验 Integration、授权、root containment、结构、preimage 与 locator；发布文档只原子新建。Context 只写指定 `CONTEXT.md` managed 区；修改既有定义须 per-write confirmation，并发变化拒绝。
5. 报告类型、目标、transaction、preimage/result SHA-256、验证与限制。候选未满足事实、冲突、消费者或授权条件时留在任务记录。

## 边界

- 发布文档和 `CONTEXT.md` 不替代 Artifact/Handoff、不复制任务状态；writer 不替 Human 发明业务定义。
- 内部 task/thread ID、缓存路径和不可发布 evidence locator 不进入正文。
- generator 只证明输入、授权、路径与静态结构；Runtime trigger、内容语义质量和真实外部副作用需对应证据。
- 安装、Git、发布、外部消息及根外写入仍需各自授权。
