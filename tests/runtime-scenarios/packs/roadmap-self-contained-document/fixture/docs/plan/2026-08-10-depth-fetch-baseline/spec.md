# Depth Fetch 静态 Owner 调查

## 目标

定位当前工程中 Depth Attachment、RenderPass 生命周期和 capability query 的静态 Owner。

## 范围

只调查当前工程源码，不形成生产实现或设备支持结论。

## 验收标准

主要 Owner、直接消费者和未验证 Runtime 边界均有项目源码依据。
