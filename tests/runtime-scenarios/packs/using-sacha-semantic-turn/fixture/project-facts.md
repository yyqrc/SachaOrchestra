# 已核实项目事实

- Remote Debugger 当前把所选贴图打入 AssetBundle，通过 PlayerConnection 发送到 Player，并按贴图名称替换场景资源。
- 路径或名称包含 `_custom` 的贴图会跳过当前 AssetImportProcessor 的自动限制。
- Human 要求首次副本继承全部导入参数，后续只由界面更新目标平台的压缩格式和最大分辨率。
- 当前请求包含多张目标贴图，但尚未决定每个平台使用一组批量设置，还是每张贴图分别保存设置。
