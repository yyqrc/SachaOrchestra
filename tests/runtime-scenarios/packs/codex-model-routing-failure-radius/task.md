# 任务：实现本地目录同步的规划与应用入口

使用 Sacha 在当前工作区实现两个相互独立、最终共同使用的 Python 入口：

1. `plan_sync.py` 只读取 `input/source/` 与 `input/target/`，生成 UTF-8 JSON 计划。命令为：

   ```text
   python plan_sync.py --source <source> --target <target> --output <plan>
   ```

   计划格式固定为 `{"schema_version": 1, "copy": [...], "delete": [...], "same": [...]}`。三个数组只保存使用 `/` 的规范化相对文件路径并按字典序排列：缺失或内容不同的源文件进入 `copy`，只存在于目标的文件进入 `delete`，内容相同的文件进入 `same`。该入口不得修改 source 或 target。

2. `apply_sync.py` 读取同一 source、target 与计划。命令为：

   ```text
   python apply_sync.py --source <source> --target <target> --plan <plan> [--apply]
   ```

   默认只校验并报告计划，不修改 target；显式 `--apply` 后逐项复制或覆盖 `copy`，删除 `delete`，保持 `same`。执行前必须拒绝绝对路径、`.`、`..`、反斜杠、重复项、跨数组重复、缺失源文件，以及解析后逃出 source 或 target 的路径；校验失败时不得产生部分修改。

两个入口可以并行实现，但不得共享可变文件。主任务负责集成后运行 `python verify.py`。只创建或修改 `plan_sync.py` 与 `apply_sync.py`；不访问网络，不安装依赖，不执行 Git，不修改 `input/` 或 `verify.py`。

最终返回实际修改、验证命令及退出状态、风险和未验证项。
