# 已核实项目事实

- Remote Debugger 当前把所选贴图打入 AssetBundle，通过 PlayerConnection 发送到 Player，并按贴图名称替换场景资源。
- 路径或名称包含 `_custom` 的贴图会跳过当前 AssetImportProcessor 的自动限制。
- Remote Debugger 的贴图列表支持同时选中多张贴图，并在同一次发送操作中提交。多选界面目前只负责发送，没有修改导入参数的控件。
- 多选发送时，每张贴图按自己的平台导入设置打包。例如同一次 Android 发送可包含最大分辨率分别为 1024 和 256 的两张贴图。
