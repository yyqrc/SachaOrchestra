# Runtime 控制事实

- 全局 Uniform 可以控制共享 Shader 核心中的动态分支，并覆盖消费该核心的目标 Draw。
- LOD100 keyword 需要在目标 ShaderLab Pass 中声明，并由 Shader stripping、编译产物与包体证据确认实际组合。
- Engine Probe 状态与 Shader 输出控制属于两个直接 consumer；C# 画质应用链可以作为两者的共同 Apply 入口。
- 当前产品范围同时包含 LOD120 与 LOD100；选择 LOD100 keyword 会改变第一期覆盖范围。
