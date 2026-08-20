# Forward consumer 事实

- 生产 Shader 中有 115 个 Standard consumer 和 4 个外部 CODM consumer 直接使用共享 Forward core。
- 88 个 consumer 同时提供 `EDITOR_VISUALIZATION` 对照入口；另外 31 个 consumer 提供共享 Forward core 的 Runtime 路径。
- 基础 Standard 的 `ForwardAdd` 只存在于 LOD300 及以上；目标低画质使用 LOD120 或 LOD100 的 Forward Base。
- 当前事实来源是静态源码统计；实际编译变体、Player 包与目标设备 Draw 仍需要对应层的证据。
