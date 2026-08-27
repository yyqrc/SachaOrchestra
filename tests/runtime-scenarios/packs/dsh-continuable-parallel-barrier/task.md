# 任务

在当前隔离工作区中完成一次小型数据整理，并给出可直接验证的最终结果。

工作区中有两个彼此独立的输入：`input/accounts.csv` 与 `input/routes.csv`。请分别把它们转换成规范化 JSON：

- `output/accounts.json`：按 `id` 升序；`enabled` 转成布尔值；只保留 `id`、`owner`、`enabled`。
- `output/routes.json`：按 `path` 升序；`methods` 转成大写、去重、字母序数组；只保留 `path`、`methods`。

两个结果都完成后，再生成 `output/manifest.json`，内容只包含：

```json
{
  "accounts": <accounts.json 的记录数>,
  "routes": <routes.json 的记录数>
}
```

约束：

- 使用 Sacha 完成当前目标。
- 不修改 `input/`。
- 不新增依赖，不访问网络。
- `output/accounts.json` 与 `output/routes.json` 是彼此独立的工作单元；`manifest.json` 只能在两者真实完成并核对后生成。
- 最终运行 `python verify.py`，以其退出码和输出作为直接验收证据。
