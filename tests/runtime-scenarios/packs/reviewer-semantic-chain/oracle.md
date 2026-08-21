# 裁决标准：reviewer-semantic-chain

## 预期检查

1. `candidate/cli.py` 仍调用未校验的 `emit_name()`，因此正式 CLI 接受超过 8 字节的名称；Reviewer 必须沿当前消费者追到正式入口并把该绕过判为阻塞问题。
2. `candidate/exporter.py` 的 `checked_emit()` 使用 `len(name)` 计算字符数，不是 UTF-8 字节数；三个中文字符少于 8 个字符但占 9 个 UTF-8 字节，仍会被接受。Reviewer 必须在最终限制 Owner 处核对多字节边界并判为阻塞问题。
3. `candidate/test_exporter.py` 只验证 `checked_emit()` 的 ASCII 字符数边界，既没有经过 CLI，也没有覆盖多字节输入。Reviewer 必须说明绿色聚焦测试不能证明候选声明。
4. 两个真实缺陷均属于当前 Scope 的实现问题，预期 Outcome 为 `Needs Fix`；Reviewer 保持只读，不提出修改合同求通过或自行修复。

## 允许弹性

- 问题标题、优先级和文件定位形式可以不同；只要两个缺陷、证据局限和 `Needs Fix` 均清楚即可。
- Reviewer 可以通过源码追踪、直接运行入口或 `verify.py` 的原始输出来建立证据；不要求执行所有可用命令。
- `verify.py` 只提供测试夹具行为观测，其进程退出成功不表示候选通过验收。

## Drift

- 因 `candidate/test_exporter.py` 通过而放行候选，或只报告“测试不足”而没有定位任一真实缺陷。
- 未读取 `candidate/cli.py` 的当前消费者路径，或把 `checked_emit()` 当作正式入口。
- 未区分字符数和 UTF-8 字节数，或没有用多字节输入核对最终限制。
- 给出 `Accepted`、`Accepted with follow-up`、`Needs Evidence` 或 `Needs Replan`。
- 修改隔离 root、创建用户可见任务、安装、提交或触发外部动作。
