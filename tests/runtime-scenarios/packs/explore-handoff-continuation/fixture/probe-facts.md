# 动态 Probe 事实

- 动态 `BlendProbes` 与 Explicit Probe 当前使用局部 Probe 结果；Probe Off 使用全局 `ambientProbe`。
- SceneView 的 `EDITOR_VISUALIZATION` 与 mode 值进入 Shader 上下文，Probe 类型选择入口当前只接收 Renderer 与 LightProbe 上下文。
- 主线程 Forward 与 render-thread Forward 分别准备目标 Draw 的 SH，两处 consumer 需要取得同一模式结果。
- 全局 `ambientProbe` 的选择会改变 `unity_SH*` 来源；Shader 最终颜色重组属于后续独立步骤。
