# 任务：核对自定义 Agent 的组合、工具面与模型优先级

在当前 Codex 协作界面中完成四部分只读检查。运行者另提供一份从真实消费工程 Project Integration 只读解析出的 capability 输入，包含来源 path/hash、capability id、canonical Skill、load policy 和当前 Runtime catalog 候选；不得用手写 fixture 代替该输入：

1. 核对隔离项目的 `baseline.txt`、`candidate.txt` 和 `evidence.txt`，判断候选是否满足验收基线；不要修改文件或访问网络。
2. 使用当前已发现的 Sacha 自定义 Agent 做最小模型路线探针，分别核对以下优先级：本次 `spawn` 的显式 `model/reasoning_effort`、Agent TOML 默认值、父任务模型路线。每次只改变当前要验证的一层，不读取或修改项目文件，不创建下级 Agent。
3. 为 `sacha_researcher`、`sacha_executer` 与 `sacha_reviewer` 分别保留原生配置与工具面 reference：Researcher 应关闭 Shell、Apps、Memory、权限请求和自动/bundled Skills，同时保留当前 Capability Binding 使用的插件 Skill/MCP；另外两个能力 Agent 应保留验证或实施所需的 Shell、Apps、插件 Skill/MCP，并关闭 Memory、权限请求和自动/bundled Skills。只读取原生 schema、遥测或 rollout，不通过写入尝试验证。
4. 从运行者提供的真实 Binding 中选取一个 load policy 允许、当前工作只需只读能力的 mapping。先核对唯一 Runtime Skill、绝对 `SKILL.md` path、插件/MCP 前置、Skill 副作用和 child 工具面，再形成 child 首次工作单元，让 child 只读检查隔离项目并返回证据。自动 Skill instructions 关闭时不得只传 Skill 名称或依赖目录发现；当前 child 创建 schema 不支持结构化 Skill input 时，使用自包含 message。另用身份歧义、path 不可达、Skill/依赖不可见、policy 不允许或副作用越界的输入核对 spawn 前停止，禁止创建降级 child。

只有 Runtime 原生结果或可绑定遥测才能证明实际模型、推理强度、permission profile、工具面和 child 行为；真实 Binding 解析、源码组装、参数被接受、TOML、提示词或 Agent 自报都只证明各自层级。最终分别报告 v1/v2 的通过项、阻塞项、Binding 来源和原始 reference。

