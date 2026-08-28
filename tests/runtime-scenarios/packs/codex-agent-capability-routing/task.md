# 任务：核对自定义 Agent 的组合与模型优先级

在当前 Codex 协作界面中完成两部分只读检查：

1. 核对隔离项目的 `baseline.txt`、`candidate.txt` 和 `evidence.txt`，判断候选是否满足验收基线；不要修改文件或访问网络。
2. 使用当前已发现的 Sacha 自定义 Agent 做最小模型路线探针，分别核对以下优先级：本次 `spawn` 的显式 `model/reasoning_effort`、Agent TOML 默认值、父任务模型路线。每次只改变当前要验证的一层，不读取或修改项目文件，不创建下级 Agent。

只有 Runtime 原生结果或可绑定遥测才能证明实际模型与推理强度；参数被接受、TOML、提示词或 Agent 自报都只作为配置证据。最终分别报告 v1/v2 的通过项、阻塞项和原始 reference。

