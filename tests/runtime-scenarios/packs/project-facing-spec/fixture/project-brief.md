# 已确认项目目标与决定

目标：让普通材质和 ObjectMesh 材质分别配置导出尺寸，并让同一 RawMat 在一次 Batch 导出中只生成一份 TOD 材质资产。

范围包含配置字段与 Inspector、尺寸解析、缓存 Hash、RawMat GUID 映射、Renderer 与 Prefab 材质列表写回。范围不包含非 CODM 分支、几何选择逻辑、提交、发布和资产目录外迁移。

尺寸决定：ObjectMesh 正值覆盖白名单上限，`0` 沿用白名单值，非法结果回退 `512`；普通材质继续使用 `normalTextureSize`。导出和缓存必须调用 `ResolveExportSize`。

材质决定：使用 `MaterialExportScope` 先收集完整 Batch 的 RawMat GUID、目标路径和消费者；不同 GUID 命中同一路径时，在创建资产或修改引用前失败。同一 GUID 的所有消费者使用 `MaterialExportRegistry` 返回的同一材质资产。

配置决定：在 `MaterialExportSettings` 新增一个 bool 字段控制是否复用同一 RawMat GUID 的 TOD 材质，默认开启；字段名称尚未确认，必须沿用项目 bool 字段命名习惯，并说明 Inspector 与材质导出器两个直接消费者。

验收：通过源码与目标程序集编译检查非 CODM 分支不引用新增字段；运行导出并读回缓存键，确认修改尺寸后缓存失效；连续运行两次不创建重复材质且 GUID 不变；不同 GUID 同路径在任何持久写入前失败；由实际使用者观察并确认项目 UI 标签能被理解。不要求 Editor Bake。

失败保护：无法让导出与缓存共用同一个尺寸计算时停止实施并保留现状，不得复制第二份尺寸优先级；任何写回或验证失败时保留新旧材质及元数据，不执行清理。
