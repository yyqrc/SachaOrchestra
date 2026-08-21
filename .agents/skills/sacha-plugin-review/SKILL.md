---
name: sacha-plugin-review
description: 用于只读评审 SachaOrchestra 插件差异、提交或有界工作树，核对 Owner、发布边界、Role/Skill 职责、真实入口和证据；不修复、不发布，也不替代 Runtime Reviewer Outcome。
---

# Sacha 插件评审

## 功能

从 Sacha 插件开发控制面审查一个精确差异，定位会错误交付的产品、Runtime、发布、自包含或验证问题，并把阻塞问题与非阻塞后续项分开。

## 输入与首查

1. 要求可解析的提交、范围、差异、文件集或有界工作树；核对当前远端基线与精确目标提交，变更目标变化后重新建立范围。
2. 先读[项目规则](../../../AGENTS.md)，再按目标 path 区分开发控制面和发布 Runtime。差异包含 Human 可读文本时完整读取 [Sacha 文档治理](../sacha-doc-governance/SKILL.md)，消费其语言与完整命题检查；涉及提炼术语时读 [`docs/CONTEXT.md`](../../../docs/CONTEXT.md)，涉及入口、流程或职责时读 [`PLUGIN_DESIGN.md`](../../../PLUGIN_DESIGN.md)。
3. 读取差异及足以理解设计的相邻 Owner、直接消费者和真实生产入口；范围报告、校验器和测试结果只提供线索，不替代语义评审。

## 动作顺序

1. 检查 delta 是否落在现有 Core、Skill、Adapter、开发文档、测试或生成器 Owner 内；新增入口、职责、跨节点路线或 Owner 转移必须先有 Human 批准并自上而下同步。
2. 对变更接口追踪声明、实现和当前消费者，核对成功、失败、取消、所有权、清理、恢复和持久化边界；只有单一内部消费者的公共扩张必须有产品依据。
3. 对限制、拒绝和授权路径追到最终副作用，检查直接调用、替代入口、包装层和监听顺序能否绕过。对模型或 Human 可见变化读取实际提示词、schema、结果、诊断和受影响模式。
4. 核对发布 root、manifest 路由和本地引用；开发文档可引用 Runtime Owner，发布文档不得依赖 root 外文件。源码、包/缓存、安装后发现和 Runtime 行为分别裁定。
5. 检查验证是否命中真实加载入口、生成器、Adapter、工具、进程入口或场景；聚焦测试、构建、校验器、Runtime 和 Human 验收不互相替代。断言应在目标回归出现时失败，关键禁止行为需要真实入口负例。
6. 只在问题可能改变交付判断时扩大 path/reference。已由绿色机器 Gate 精确执行且没有语义缺口的事项不重复列为人工问题。

## 输出

- 每个问题给出紧凑位置、缺陷、影响和直接证据；区分阻塞交付的问题与 `Accepted with follow-up` 候选。
- 报告精确评审范围、复用与重跑的证据、未验证 Runtime/安装边界，不输出实现者自检冒充独立裁决。

## 停止与禁止边界

- 本 Skill 只读，不修复、提交、发版、安装、创建任务或修改外部资源。
- 没有会改变交付判断的具体缺口时停止，不追求全历史、全部 Runtime 或无消费者 Owner。
- Runtime Reviewer 的 Baseline、Outcome 和返回路由仍由发布插件的 Assurance Contract 与 Reviewer Skill 拥有；本 Skill 不建立第二套裁决合同。
