# 中文收口与存档触发词

> 状态：Human 已批准实施

## 目标与冻结决定

- “存档”只作为 `document-project` 的 `human-request` 语义别名；不修改 Spec，也不改变正常 `goal-closeout` 自动候选。
- “收口”路由到新增支持 Skill `closeout`，只把当前任务唯一 Spec Artifact 原位标记为“已完成”。
- “收口并存档”先分别预检两个动作及授权，再按 Spec 完成 → `document-project` 顺序执行；后者失败不回滚已合法完成的 Spec。
- `closeout` 由 Skill description 按 Human 请求语义选择；只讨论或引用动作词不执行。

## Owner

- `closeout` 只拥有预检、顺序和结果聚合。
- Artifact Protocol 拥有 Spec 完成条件、原位更新与失败关闭。
- `document-project` 继续独占项目文档；两类内容和写入授权不得互相替代。

## Scope

- 顶层设计、Intake、Workflow、Artifact、术语同步视图、入口 Skill、`document-project`、发布插件 README。
- 新增 `closeout` Skill、元数据、Spec 完成辅助脚本、行为测试与 Runtime 场景任务包。

## 非目标

- 不移动、改名或归档 Spec，不创建或推导 `docs/done`。
- 不让项目文档替代 Spec，不让 Spec 完成自动生成项目文档。
- 不修改安装缓存、版本、manifest、Git 或远程状态。

## 验收

- Skill description 能区分动作请求与普通讨论；Runtime 场景核对自然语言请求的实际路由。
- 缺少/多份当前 Spec、非 `goal_complete`、必需检查未满足、未批准 Spec、只读上下文和状态行异常均无写入。
- 合法收口只原位修改唯一 `spec.md` 状态行；不创建 `docs/done` 或项目文档。
- 组合动作分别保留 Spec 显式命令授权与项目策略写入授权，`per-write-confirmation` 不被别名绕过。
- 最窄行为测试、相关完整单元测试、Skill/Plugin 结构校验、Runtime source-scenario 与独立 Review 均按证据边界报告。
