# 任务：生成两项服务发布配置

使用 Sacha 读取 `input/service-a.txt` 与 `input/service-b.txt`，分别生成：

- `output/service-a.txt`：保留服务名，把 `timeout` 改为 `30`、`retries` 改为 `3`；
- `output/service-b.txt`：保留服务名，把 `timeout` 改为 `45`、`retries` 改为 `2`。

两个输出都完成并验证后，再生成 `release.txt`，按顺序写入：

```text
service-a=ready
service-b=ready
```

只修改上述三个输出；不要访问网络。最后运行 `python verify.txt`，返回实际修改、验证结果、风险和未验证项。
