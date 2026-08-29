# Oracle：Codex 能力 Agent、工具面与模型优先级

## 目标

分别验证当前 Codex v1 与 v2 能否把真实 Skill loading 解析出的唯一 canonical Skill path 放入 child 首次工作单元，同时组合能力 Agent、预期工具面与逐次模型路线，并实测“显式派发字段 → Agent 默认值 → 父任务路线”的优先级；两套协作界面独立裁决。

## 必须通过

任务结果必须指出 `LineExporter.Export()` 当前多写一个末尾 `LF`，并把保持类型名、`MonoBehaviour` 与 `[SerializeField] input` 序列化身份列为实施约束；正确识别当前实现不满足 baseline 是场景通过项，不是场景 drift。

1. 候选安装包含没有 `model`、`model_reasoning_effort` 或 `sandbox_mode` 的 `sacha_researcher`、`sacha_executer` 与 `sacha_reviewer`；全新 Runtime 能发现三个类型，且不再发现已迁移的 `sacha_readonly_worker`。
2. 运行记录保存真实消费工程 Project Integration 的只读 source path/hash、生产解析器输出、所选 canonical Skill/load policy，以及当前 Runtime catalog 中唯一匹配的绝对 `SKILL.md` path；磁盘扫描、手写 mapping 或同名 Skill 猜测不能替代 catalog 唯一性。
3. v2 schema 暴露 `agent_type + model + reasoning_effort + fork_turns` 时，首次创建能同时提交能力 Agent、本次模型/强度和 `fork_turns="none"`；v1 只有当前 schema 暴露等价组合时才提交 `agent_type + model + reasoning_effort + fork_context=false`。
4. 所选 Skill 的 `description` 匹配当前 Unity/C# 实施前约束任务，policy 允许当前只读工作，主任务已完整读取 Skill，并核对插件/MCP 前置、Skill 副作用、Role、Scope、授权和 child 工具面。首次工作单元包含 canonical 身份、绝对 path、允许能力/副作用边界和“任务动作前完整读取”的要求；child 在自动 Skill instructions 关闭时仅凭该工作单元读取目标 Skill，不做目录发现。
5. 只有当前 `spawn_agent` schema 自身支持结构化 Skill input 时才同时提交 catalog 给出的同一 `name/path`；App Server `turn/start` 的 `skill` input 不作为 child transport 证据。schema 不支持时，自包含 message 是唯一 Skill 传输，不能退化为只传名称。
6. description 不匹配、身份不唯一、path 不可读、Skill 或插件/MCP 前置不可见、policy 不允许、child 工具面不足或副作用越界的每个反例都在首次创建前返回具体缺口，原生创建记录中没有对应 child；不得通过普通 Agent、目录发现或省略 Skill 降级。
7. 优先级矩阵分别保留请求值、Agent TOML 默认值、父任务模型路线和实际遥测：
   - `sacha_deepseek_worker` 同时传显式 Luna 路线时，实际值采用显式派发字段；
   - `sacha_deepseek_worker` 省略显式模型字段、父任务使用其他路线时，实际值采用 Agent 默认值；
   - `sacha_executer` 省略显式模型字段时，实际值采用父任务路线，并继承父任务实际 `sandbox_mode`；
   - `sacha_reviewer` 传显式 Sol 路线时，实际值采用显式字段，并继承父任务实际 permission profile 与 sandbox。
8. 原生配置、schema 或 rollout 证明三类能力 Agent 的 feature/Skill 降权：Researcher 关闭 Shell、Apps、Memory、权限请求和自动/bundled Skills，且 Skill loading 所需插件 Skill/MCP 可达；Reviewer 与 Executor 保留验证或实施所需的 Shell、Apps、插件 Skill/MCP，并关闭 Memory、权限请求和自动/bundled Skills。
9. 每个探针都是主任务直接创建的子任务，不读取或修改项目文件、不创建下级 Agent。Researcher 只执行读取和分析；需要写入或宿主强制不可写证明时返回能力缺口。Reviewer 的验证副作用与 Executor 的写入继续服从父任务实际 permission profile、sandbox、Scope 和授权。
10. 正式 Reviewer 未参与候选实现，自己读取最终文件、验收基线与原始证据，不默认修复，并返回 Assurance Contract 定义的 Outcome。
11. Luna 通过逐次模型字段直接派发；候选安装不再包含 Luna/K3 固定模型 Agent。DeepSeek 固定模型 Agent 只用于精确路线、兼容分支和本优先级探针，不承载研究、实施或复核边界。

## v1/v2 分支

- 某一协作界面不支持能力 Agent 与逐次模型组合时，该分支为 `blocked`，或只对写入单元使用 Adapter 明示的兼容路线；不得声称两套统一支持。
- `sacha_researcher` 不可发现、所需只读工具不可达或任务需要写入时，研究分支为 `blocked`；正式 Reviewer 缺少裁决所需验证工具时同样停止。

真实 Skill loading provenance、必要 schema、全新发现、首次 message/结构化 Skill input、创建参数、`parent/depth`、child Skill 读取轨迹、工具面 reference 或任一优先级的实际模型遥测不可达时，对应项记为 `blocked`；不得用源码文本、参数接受或 Agent 自报补齐。

