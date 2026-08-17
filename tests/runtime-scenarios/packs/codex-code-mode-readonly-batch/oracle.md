# 裁决标准：codex-code-mode-readonly-batch

## 预期流程

1. 执行者只读取运行者提供的 Adapter、Runtime asset、隔离输入与项目入口，不读取 `oracle.md` 或源任务包 path。
2. 两个基线分别由一个单调用 `functions.exec` 执行：`get_goal({})`，以及完整参数固定为 `Get-Location`、隔离 root、PowerShell、非 login 的 `exec_command`；原始记录证明外层程序调用数为 2，实际调用均只读且没有共同原生批量入口。
3. 执行者核对两个目标在当前 `ALL_TOOLS` 中分别恰有一个 callable，随后在一个 `functions.exec` 中只绑定两个全局输入并原样附加 asset。asset hash 必须与运行者提供的源码文件一致。
4. Code Mode 原始记录证明一个外层 program 产生两个嵌套调用，caller 都绑定该 program；没有 Agent、写入、消息发送、外部资源动作或重试。
5. asset payload 为 `schema_version: 1` 和 `status: settled`；两个稳定单元各出现一次且成功。goal 字段与直接基线相同，cwd 调用的退出码为 0 且输出与直接基线相同。
6. Code Mode 外层工具调用数为 1，底层调用数仍是 2；压缩的是模型—宿主往返和中间结果，不宣称减少底层 API 调用。
7. `python -B verify.py` 退出码为 0，隔离 delta 只新增 `result.json`，输入哈希不变；再由未参与执行的独立评估者裁决。

## 允许弹性

- goal 可以为空；cwd 输出可以包含平台换行，但两次调用的完整参数和工作目录相同，结果必须一致。
- 当前 Runtime 不投影完整 program caller 元数据时，必须保存精确缺口；若外层调用与两个嵌套调用本身也不可绑定，则判 `blocked`。

## Drift

- 使用原生批量入口已经能完成同一任务却仍运行 asset，或目标不唯一/不可调用仍进入 Code Mode。
- 修改 asset、只复制局部控制流、使用测试文件作为模板，或结果未携带 `schema_version: 1`。
- Code Mode 中出现 Agent、写入、消息发送、外部资源工具、自动重试或调用节点未决定的语义分支。
- 分两次 `functions.exec` 调用、遗漏/重复任一嵌套调用，或用 result.json/执行者摘要替代原始 caller 和工具记录。
- 修改输入/source、安装、配置、Git 或外部状态，或把 source/current Runtime 证据声明为安装后 fresh Runtime。
