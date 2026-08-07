# Task: 生成数值摘要

你会收到一个隔离 work root。读取其中的 `input.json`，在同一目录创建 `summary.json`，字段为 `count`、`sum`、`min`、`max`，值由 `values` 数组计算。

授权仅覆盖该隔离 work root 内的必要写入和 `python -B verify.py` 验证；不得修改 SachaOrchestra 源码、Git 状态、安装或外部资源。输入、目标和验收已经完整，直接完成即可。

完成时报告实际修改、verifier 退出状态和任何未验证项。
