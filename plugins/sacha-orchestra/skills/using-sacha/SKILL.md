---
name: using-sacha
description: Sacha 默认入口。显式 Sacha，或关键澄清/Spec、跨 context 恢复、难回退跨 owner 决策、正式协调/独立验收会改变执行方式时使用；任务演变时重评估，仅复杂/耗时/多文件保持 Direct。
---

# Using Sacha（智能入口）

## 工作流

1. 读取 [Intake Contract](../../core/intake-contract.md)，核对目标、Scope、授权、验收和项目规则。
2. 初次判断及 Direct 执行期间都检查语义转折；预计实施前需要关键 Human 澄清、先冻结/持久化 Spec、跨 context owner/恢复、正式协调/独立验收，或出现难回退的跨 owner 决策时，按当前事实重评估，不沿用旧 L0。
3. 复杂调试、耗时、文件多、多平台或持续验证本身仍保持 Direct；只有上述事实会实质改变执行方式时才建议 Sacha。用一句技术说明收益、成本和推荐，同一 candidate 只问一次。
4. 显式 using-sacha、明确使用 Sacha 或直接调用 canonical Role 视为接受。接受后读取 [Workflow Contract](../../core/workflow-contract.md) 与目标 Role；只有 transport、恢复或外部状态需要时才读 Adapter。
5. 拒绝后按当前事实直接处理；目标、Scope、验收、风险、授权或交付模型实质变化可形成新 candidate，locator、日志或进度变化不得触发重问。

## 路由

- 关键澄清、Spec 冻结/持久化或难回退跨 owner 决策会改变实现边界 → Planner；接受后由 Planner 按需使用 Clarify。
- Scope/验收已明确但需跨 context owner/恢复或正式协调 → Executor，再按事实打开 downstream Gate。
- Reviewer/Manager 只作为 downstream Gate；打开后分别按 Assurance/Coordination Contract 执行。
- Clarify/Setup Project 保持 explicit-only narrow capability；完成后新的开发目标重新 Intake。
- Intake 不创建 Goal、Artifact 或 Handoff，也不授权写入、安装、Git、发布、远程资源或高影响动作。
