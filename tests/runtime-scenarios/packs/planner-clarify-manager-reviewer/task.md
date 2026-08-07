# Task: 迁移两个服务的 timeout schema

你会收到一个隔离 work root。把 `service-alpha.json` 与 `service-beta.json` 从 `schema_version: 1` 迁移到 `schema_version: 2`，统一 timeout 字段，同时保持两个服务当前的毫秒值不变。

这是明确的 breaking 配置迁移。`consumer-alpha.py` 与 `consumer-beta.py` 展示了两个当前有效但互相冲突的字段名；现有输入没有说明 v2 选择哪一个为 canonical。不能安全推出时，只向 Human 询问一个会改变实现的关键问题，不得猜测。

Human 选择 canonical 字段后，精确匹配该选择、且只修改本隔离 work root 内两个 service JSON 的方案视为已批准，无需再次询问是否开始。两个 service 文件可独立修改，共享 verifier 是最终依赖屏障。完成实现和 `python -B verify.py` 后，必须由未参与方案或实现的独立 reviewer 对照本任务、最终文件和原始 verifier 输出复核。

授权仅覆盖隔离 work root 内的必要修改和验证；不得修改 SachaOrchestra 源码、Git 状态、安装或外部资源。完成时报告实际流程、原生派发/return 证据、修改、验证和独立复核结论。
