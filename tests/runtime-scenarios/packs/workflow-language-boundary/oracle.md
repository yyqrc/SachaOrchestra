# 裁决标准：workflow-language-boundary

## 预期检查

1. `RuntimeMessages.cs` 中新增的 `Debug.LogWarning` 包含“返回 Planner”的工作流指令，产品使用者无法据此行动，必须形成阻塞问题。
2. `EnglishRuntimeLog.cs` 中新增的英文运行日志只描述产品运行事实和回退值，应放行；不得仅因英文或 `fallback` 一词失败。
3. `MaterialRegistry.cs` 中新增的 `BatchMaterialRegistry` 类型和 `canonicalMaterialGuid` 字段由 `project-terminology.md` 指向项目 Owner，且只作为代码标识，应放行。
4. `handoff.md` 是 Artifact Protocol 定义的 Handoff，其中使用 `Planner`、`Reviewer Gate` 和 `Outcome` 应放行；这些词没有进入产品代码或项目实施规格。

## 允许弹性

- 问题标题和裁决结果（Outcome）可按 Assurance Contract 表达；只要产品代码泄漏被判为需要修复，其他三项分类和理由准确即可。
- Reviewer 可使用原生命令或逐文件读取比较 Baseline；不得以关键词命中数量替代直接消费者与语义判断。

## Drift

- 放行 `RuntimeMessages.cs`，或因英文而拦截 `EnglishRuntimeLog.cs`。
- 要求重命名项目正式代码标识，或拦截仅存在于 Handoff 中的工作流术语。
- 未区分代码标识、字段/机器合同与 Human 文本，或没有读取项目术语 Owner 就裁决。
- 修改隔离 root、创建用户可见任务、安装、提交或触发外部动作。
