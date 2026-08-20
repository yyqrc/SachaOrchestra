# Runtime DirectAndSkyOnly 探索决定

> 状态：上一轮需求澄清已形成决定；当前 task 继续探索，尚无 Spec。

## 目标

- 为低画质 Runtime 形成 DirectAndSkyOnly 方案，并保留 SceneView 对照入口。
- 当前阶段只读探索源码事实、方案边界与验收输入。

## 已确认决定

1. 产品状态由全局画质应用链驱动，场景生命周期内保持稳定。
2. 第一期覆盖 Forward 主路径，资源释放属于后续阶段。
3. 静态 Renderer 保留 Lightmap 身份；动态 Renderer 的 Probe 语义需要独立核对。

## 当前关注点

1. 生产 Shader、Pass 与 LOD 的共享 Forward consumer 覆盖范围。
2. SceneView 与 Runtime 下动态 Renderer 的局部 Probe 退化语义和状态传播。
3. Runtime 输出控制在全局 Uniform 与 LOD100 keyword 之间的适用边界。

## 事实来源

- `consumer-facts.md`
- `probe-facts.md`
- `control-facts.md`

## 当前边界

- 本轮保持现有文件和外部状态不变。
- 探索结果返回 Planner 消费；Spec、实施、构建和 Runtime 验收分别沿用各自 Owner。
