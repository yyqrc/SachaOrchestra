# Project Skill Evidence

`--project-skill-evidence` 每次接收一个 JSON object：

```json
{
  "skill": "project-check",
  "skill_path": ".agents/skills/project-check/SKILL.md",
  "skill_sha256": "<64 hex>",
  "units": [
    {
      "goal": "检查当前项目并返回结构化报告",
      "kind": "inspect",
      "admission": "schedulable",
      "side_effect": "read_only",
      "evidence": ["42-68", "91"],
      "required_paths": ["tools/project_check.py"],
      "runtime_prerequisites": [],
      "reason": "正文给出独立入口、步骤和报告输出。",
      "id": "project.check",
      "load_policy": "on-demand"
    }
  ]
}
```

## 字段

- `skill`：当前 Runtime 可见的无 plugin 前缀项目 Skill。
- `skill_path`：目标项目内 authority/independent `SKILL.md` 的项目相对路径。
- `skill_sha256`：本轮完整读取文件的 SHA-256。
- `units`：非空；一个 Skill 可拆零个 capability，但仍须用 `support_only` 或 `unavailable` unit 说明判断。
- `goal`：正文定义的独立交付目标，不是 Skill 名称改写。
- `kind`：`inspect`、`change`、`verify`、`build`、`operate` 或 `coordinate`。
- `admission`：`schedulable`、`support_only` 或 `unavailable`。
- `side_effect`：`read_only`、`project_generated_state`、`project_source_write`、`runtime_state` 或 `external_state`。
- `evidence`：正文的 1-based 行号或闭区间；不得只引 frontmatter/空行。
- `required_paths`：调用必需的项目相对静态入口。`schedulable` 时必须存在；非调用必需的示例、可选 locator 不填。
- `runtime_prerequisites`：设备、进程、授权或输入等调用时检查项；它们不因当前未满足而删除静态 mapping。
- `reason`：为何该 unit 可或不可由 Sacha 独立调度。
- `id`：仅 `schedulable` 必填，且必须在正文判定之后分配。
- `load_policy`：仅 `schedulable` 使用；缺失时 generator 输出 `project_policy_decisions_required` 并拒绝写入。

`support_only`/`unavailable` 不得包含 `id` 或 `load_policy`。若 Skill 当前不可见、正文只有辅助步骤，或缺少调用必需入口，应使用这两种 admission，而不是猜 mapping。
