# Material Export 项目定义

- `MaterialExportSettings`：材质导出配置类型，字段 `normalTextureSize` 和 `objectMeshTextureSize` 保存两类纹理尺寸上限。
- `MaterialExportRegistry`：以持久 RawMat 资产 GUID 为键、TOD 材质资产为值的项目映射类型；直接消费者是材质导出器、Renderer 写回和 Prefab 材质列表写回。
- `MaterialExportScope`：一次 Batch 导出的项目上下文类型，保存本次收集到的 RawMat GUID 与目标路径；材质导出器和冲突检查直接消费。
- `ResolveExportSize`：唯一计算最终导出宽高的函数，供纹理导出与缓存 Hash 调用。
- `MaterialExportSettings` 中控制可选行为的 bool 字段统一使用 `enable...` 前缀；字段由 Inspector 和材质导出器直接消费。
- 缓存键必须包含 `ResolveExportSize` 返回的最终宽高。
- 项目 UI 使用“普通材质尺寸”和“ObjectMesh 材质尺寸”两个标签。
