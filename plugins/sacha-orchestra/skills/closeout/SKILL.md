---
name: closeout
description: 用户明确要求把当前 Spec 标为已完成、存档项目文档，或同时执行两项时使用。兼容旧说法“收口”和“收口并存档”。只讨论这些动作时不执行。
---

# 标记 Spec 完成和存档

## 功能

按用户请求把 Spec 标为已完成、存档项目文档，或顺序执行两项。报告实际结果。

## 输入与首查

收到明确请求后，按[工作流规则第 5 节](../../core/workflow-contract.md#5-标记-spec-完成和写入存档)执行。

- 按[Spec 完成规则](../../core/artifact-protocol.md#3-spec-完成)把当前 Spec 标为已完成。
- 存档以 `human-request` 调用 [`document-project`](../document-project/SKILL.md)。同时请求两项时，按上面的工作流顺序处理。

## 输出

分别报告本次请求涉及的 Spec 状态和存档结果，并给出实际路径。状态有变化时说明原状态和新状态。某项未完成时说明原因、影响和继续所需的条件。用户询问命令含义时，说明实际动作。
