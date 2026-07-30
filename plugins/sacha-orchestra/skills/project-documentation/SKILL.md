---
name: project-documentation
description: 按项目策略生成自包含 change archive/system guide；不替代 Artifact。
---

# Project Documentation（项目存档）

## 工作流

1. 读取 confirmed Project Integration；`disabled` 不生成，`on-request` 只响应 Human，`required-at-closeout` 仅处理持久产品改动的合法 closeout。
2. 按 `assets/` 示例准备 schema `1` JSON：type 为 `change-archive | system-guide`，提供标题、trigger、持久 delta、相对输出路径及八段自包含正文；Spec/Report/Review 仅作输入。
3. 以 `python -B scripts/generate_project_document.py --project-root <root> --input-json <json>` dry-run。
   `bounded-closeout` 已覆盖时直接写；当前明确请求可满足 `per-write-confirmation` 并增加 `--per-write-confirmed --write`，planned delta 改变时才重新确认。
4. 生产入口校验 Integration、授权、root containment、无覆盖、结构及内部 locator；只在既存 root/父目录中原子新建并写后复核。拒绝时不绕过。
5. 报告类型、目标、transaction、SHA-256、验证与限制；方案正文先讲怎么用，AI 附录只保留公开文件/符号、不变量和风险。

## 边界

- 发布型项目文档不是 Spec Artifact/Execution Report/Review/Handoff，不改变权威或复制任务状态。
- 内部 task/thread ID、缓存路径和不可发布 evidence locator 不进入正文。
- generator 只证明输入、授权、路径与静态结构；Runtime trigger、内容语义质量和真实外部副作用需对应证据。
- 安装、Git、发布、外部消息及根外写入仍需各自授权。
