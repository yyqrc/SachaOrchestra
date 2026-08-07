# Flow-first 与 Skill 职责边界 Spec

> 状态：Human 已批准实施
> 日期：2026-08-07

## 目标

停止用 Markdown 语句测试维持合同，把 README 流程图设为高层流程骨架；Core 解释图中判断，Skill 只实现自己的节点或主流程外功能，使后续迭代先判断职责归属，不再逐文件打补丁。

## Scope

- 删除读取 README、Core、Adapter 或 Skill 后做正则、marker、整句存在/缺失和段落顺序断言的测试。
- release coherence 只核对机器可解析部署身份、生产入口、可解析配置与 Git release identity。
- 先校对 README 流程图，再使 Workflow、Intake、Assurance、Coordination 与直接 Adapter 映射一致。
- Planner、Executor、Reviewer 明确职责、工作流和边界；其他 Skill 明确功能、概略工作流和副作用边界。
- 由上述流程和职责重新整理 AGENTS 产品边界，不为现状硬凑消费者表或 validator 规则。

## Non-goals

- 不改变 Runtime transport、模型选择、安装状态或外部授权。
- 不新增 Role、Gate、Artifact、Hook、Registry、MCP、app 或外部服务。
- 不用静态 source test 声明 Runtime 路由已经验证。

## 决定

1. README 流程骨架拥有高层节点、先后关系、分支和回路；改变这些内容先改图，再改 Core 和消费者。
2. 节点内部条件与语义仍由对应 Core owner 定义；流向未变时不为同步而修改 README。
3. Role Skill 只在已声明输入、输出和禁止边界内演进；新增职责、输出 owner 或跨节点路线先按流程变化处理。
4. 支持/控制 Skill 映射图中节点或闭环；setup 等具体 Skill 在主流程外声明独立功能、工作流和副作用。
5. 测试调用真实生产入口并检查行为或机器状态；Markdown 语义由 owner review 与真实 scenario/runtime 证据负责。

## Acceptance

- 测试目录不存在以产品 Markdown 为被测对象的静态语义测试，release coherence 不使用正则或读取说明文档。
- README 图能完整表示 Direct、Planner/Clarify/Human、Executor、Reviewer、Documentation、Feedback 和 Manager 协调闭环。
- Core 不新增图外 lifecycle；Runtime Adapter 映射声明与 Workflow schema 一致。
- 三个生产 Role Skill 都有清晰职责；其余 Skill 都能从正文直接看出功能与工作流。
- AGENTS 产品边界从流程和职责推导，明确 flow-first 次序、Skill 变更判定和测试边界。
- 生产脚本行为测试、官方 Skill/Plugin validator、candidate coherence 与有界变更审计通过；Runtime 行为仍明确为未验证。
