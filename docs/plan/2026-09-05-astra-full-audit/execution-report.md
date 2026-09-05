# 全仓改进与 Astra 适配实施记录

> 状态：源码交付完成；独立复核 Accepted with follow-up。
> 批准规格：[spec.md](spec.md)。未提交、发布、安装或修改用户全局配置。

## 实际变更

当前相对 HEAD `bf44b7213cf87b6362dc4a86b56c5556f707f7e9` 的任务相关跟踪文件为 125 个：68 删除、57 修改；另新增发布内 `plugins/sacha-orchestra/scripts/template_catalog.py`。统计不含本任务规划/报告文件，包含受保护的既有局部改动，不能把整份 diff 都归为本次从零产生。

| 范围 | 结果 |
| --- | --- |
| Pi | 删除 3 个生产文件、3 个专用测试；移除配置字段、解析/回写、CLI 和现行说明。旧项目文件只有在以后正常获授权的 setup 事务中才会更新。最终补齐提供方指南中遗漏的配置行。 |
| 场景与测试 | 删除 10 包及多余夹具共 62 文件；收缩 3 包，现存 12 包。仅保留具体案例，不默认新增包或按模型/角色/参数全组合验证；删除大量固定文案与夹具包装镜像，保留真实入口和安全行为。 |
| Codex | 仅支持实际可用的 v2 组合；取消接口、能力类型和模型自动回退；增加 Astra medium/high，最高自动档 high；区分回合中断与写入进程停止。 |
| 生成器 | 逐目标临近替换复查和安全补偿；宿主路径比较；安全 YAML 与依赖错误；共享目录解析；预览与写入授权分离；修复普通 spec.md、cache、UUID 已确认误拒。 |
| 规则 | 顶层设计、核心合同、技能与直接使用方对齐；共享术语单源；取消固定三遍回读和固定两个代理数量，保留检查目的、独立来源及安全/证据边界。 |
| DSH | 明确后续指令更新、临时解锁清空、旧控制晚到隔离、事件恢复；初始/追加目录不丢 256 项之后的已知工具；评审修订关联、旧状态与连接提示、热冷轮询；清理孤立 UI 实现。 |
| 发布验证 | 补齐真实生产资源选测，消费真实暂存 D 状态；删除 Pi 入口要求；DSH 版本/包身份按机器字段核对。验证器不再隐含安装依赖。 |

接手前的 `policy_match(..., line)` 修补、Skill loading 17 行回归、DSH 中文同步句式和代表测试均保留。另有两个范围外未跟踪历史记录未纳入本次、未修改。

## 验证证据

| 验证 | 直接结果 | 原始证据 |
| --- | --- | --- |
| 4 个生成器模块 | 71 项；退出 0；失败/错误/跳过均 0。独立复核补齐了命令与退出状态，不以实施者摘要代替。 | [generator-tests.json](../../../.temp/astra-review/generator-tests.json) |
| release、DSH 机器校验、JS asset、保留的语义 fixture | 49 项；退出 0；失败/错误/跳过均 0。 | [remaining-unit-tests.json](../../../.temp/astra-validation/remaining-unit-tests.json) |
| DSH 定向 Vitest | 6 文件、36 项通过；退出 0，无失败或跳过。 | [vitest.log](../../../.temp/astra-dsh/vitest.log)、[退出状态](../../../.temp/astra-dsh/vitest.exit.txt) |
| Explore 元数据 | 当前 quick_validate 退出 0；只覆盖结构。 | [explore-structure.json](../../../.temp/astra-validation/explore-structure.json) |
| 发布插件结构 | 当前 validate_plugin 退出 0。 | [plugin-structure.json](../../../.temp/astra-validation/plugin-structure.json) |
| 主插件版本/入口一致性 | 明确使用 0.14.2；pass，0 failures，退出 0。 | [release-coherence.json](../../../.temp/astra-validation/release-coherence.json) |
| 一次性 Pi 退役输入 | dry-run/未确认写入保留原字节；确认及原像满足后删除旧段；旧 CLI 参数退出 2。 | [pi-retirement-final.log](../../../.temp/astra-generators/pi-retirement-final.log) |
| DSH typecheck/build/preview | 退出均 0；每次 build 有 1 条 CommonJS/ESM 建议警告。 | [typecheck.log](../../../.temp/astra-dsh/typecheck.log)、[build.log](../../../.temp/astra-dsh/build.log)、[preview-build.log](../../../.temp/astra-dsh/preview-build.log) |
| 干净隔离包 | `@sacha-orchestra/dsh-companion@0.1.0`，35 文件；源码/隔离输入及构建/包字节核对通过。 | [package-check.json](../../../.temp/astra-dsh/package-check.json)、[隔离包](../../../.temp/astra-dsh/sacha-orchestra-dsh-companion-0.1.0.tgz) |
| 范围与空白 | cprobe 各范围空白错误 0；测试明细分两页读取，汇总完整。部分文件有 Git 行尾归一化提示，未据此额外重写。 | [final-cprobe.json](../../../.temp/astra-validation/final-cprobe.json)、[测试明细末页](../../../.temp/astra-validation/cprobe-tests-page-2.json) |

以上 Python 共 120 项、DSH 36 项。没有把结构、包或单元测试结果外推为安装后的宿主行为。原始日志位于本机 .temp，保留供复核，未提交。

实施者曾把 DSH 包版本 0.1.0 误写成主插件 coherence 命令的版本，已撤回；本表只使用主任务实际执行的 0.14.2 记录。

## 现有规格案例

复用现有 Material Export 案例，没有新增测试包或型号矩阵。

- [初稿](../../../.temp/runtime-scenarios/astra-20260905/case-1/spec.md)：独立内容裁决 drift。把未定义的旧导出路径当成事实，使用未定义类型简称；五份输入哈希不变，仅新增 spec.md。
- [有反馈修订](../../../.temp/runtime-scenarios/astra-20260905/correction-1/spec.md)：同一执行者、同一目标、模型未切换；修订后独立内容裁决 pass。恢复完整类型名，移除无来源旧路径与缓存映射依赖，收窄 512 回退范围；五份输入未变，只有 spec.md 修改。
- 初稿保留，不称首轮通过。当前协作接口未提供可恢复的子任务工具轨迹，无法确认其 Planner 读取与起草核对过程；完整原生运行过程仍 blocked。不能把内容通过当作完整流程通过，也不据初稿偏差臆断应增加生产规则。

## 独立复核与边界

[独立复核记录](review.md)为 Accepted with follow-up；未发现阻塞当前源码交付的缺陷。

仍未验证：安装、Profile 部署、宿主 UI、完整动态 scoped 工具目录一致性、未实际观察的模型分支及 POSIX 宿主行为。资源式 Skill 和新 API 未预建接入；独立 API 验证创建请求仍缺真实任务标识和完成证据，不重复创建、不计为已验证。

DSH 工作区旧 lib 中的两个 activity-model 产物未删除，工作区直接 pack 会有 37 文件；本次干净隔离包为 35 文件。两者不能混作同一包证据，后续部署前应采用经核对的干净产物。

保留的 SO-、execution-report.md/review.md 等既有词法限制未顺带放宽；本次只修复批准范围内的已知误拒。临近替换检查不宣称跨进程原子 CAS。主插件仍为 0.14.2，下一发布版本待定。
