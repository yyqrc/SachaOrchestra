# CodeMode 只读结果投影优化

> 历史记录：包装方案已被 2026-10-01 的[客户端原生 Code Mode 方案](../client-code-mode/spec.md)取代；以下正文、路径与验证仅描述当时状态，不是当前执行依赖。

状态：已完成

## 目标与范围

普通独立并发读取优先使用宿主最小 CodeMode 程序；只有消费者需要统一逐项结果、受控字段投影或逐项错误处理时，才使用现有 canonical asset。解决顶层 `content`/`output` 选择仍返回整段文本、缺字段静默消失、输出省略后不足以判断结果的问题。

保持现有只读边界、一次调用、输入顺序、`schema_version: 1`、旧 `result_fields`/`reference_fields` 字符串数组和三个包络状态。新增输出仅为可选/加法字段；`settled` 与 `fulfilled` 只说明传输，不说明业务成功。

本版不实现 DAG、分页框架、表达式或文本解析 DSL、job manager、Agent 调度重写，不修改型号表、agent_type、fastctx 限制、researcher shell 权限或 instant_interrupt，不以单样本或单测声称耗时/token 收益。

## 共同前提与决定

基线为本机源码 `482019606584db9afd187a2c9a2447821d3cfc1c`。安装后必需语义只放在发布 root `plugins/sacha-orchestra`；任务材料及测试留在仓库既有目录。

宿主工具返回结构因工具而异；投影路径必须由调用方依据实际 schema 指定。只读取已有对象自身属性，不解析 `content`/`output` 文本，不过滤、排序或遍历任意集合。业务含义仍由消费者判断。

## 精确实施方案

1. 修改 `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md` 第 2.7 节（当前约第 102 行，锚点 `### 2.7 Code Mode`）。区分宿主 CodeMode 和 canonical 包装器：原生批量入口优先；普通独立读取用最小宿主程序；确有统一输出、投影或逐项错误处理需求才选包装器。明确主任务 Manager/Explore 的本地只读工具可适用，Agent 生命周期不适用；researcher 仅可通过当前已暴露且已确认只读的工具使用宿主能力，不通过包装器获得 shell、写入、未发现工具或下级调度权限。保留各自能力核对，按此区分修正第 2.8 节及第 4 节的 asset 证据适用范围。

2. 在同节说明本版接口；修改 `code-mode-batch.js` 的输入循环、`pickFields`、结果映射及限额处理（当前约第 14、70、81、107 行，以函数及变量为稳定锚点）：
   - 旧 `result_fields`/`reference_fields` 保持必填。每项新增可选 `result_paths`、`reference_paths`、`required_paths`，缺省为 `[]`。每类最多 32 条路径，每条 1–8 段；段只允许非空、最多 256 个 UTF-16 单元的字符串或非负安全整数。不接受表达式、通配符或字符串点路径解析。校验失败在全部调用前抛出 `code_mode_projection_paths_invalid:<unit_id>:<field>`。
   - 路径例：`["structuredContent", "items", 0, "title"]`。数字段只读取数组自身索引；字符串段读取对象自身属性。不存在或值为 `undefined` 都算缺失，`null`/`false`/`0` 保留。不会读取继承属性或修改原对象。
   - 旧字段继续进入 `value`/`references`。存在的嵌套值进入可选 `value_paths`/`reference_paths`，每项为 `{path, value}`，不重建部分对象。任何请求字段缺失时，新增 `missing_fields: [{kind, path}]`，kind 分别为 `result_fields`、`reference_fields`、`result_paths`、`reference_paths`、`required_paths`。
   - `required_paths` 用来保留当前 schema 中不可省略的状态或错误信息，存在的值进入 `required: [{path, value}]`；显式缺失进入 `missing_fields`，消费者暂停依赖该信息的判断。asset 同时保留顶层及 `structuredContent` 下已存在的 `isError`、`error`、`errors`、`status`、`success`、`ok`、`exit_code`、`session_id`、`cell_id`，同一路径去重。不存在的自动字段不产生缺失告警。未知业务 schema 必须由调用方补充 `required_paths`；不凭这些字段自动生成业务成功状态。
   - `pickFields` 使用无原型字典，保留合法的 `__proto__` 自身字段。工具调用使用 async 映射进入 `Promise.allSettled`，同步抛错与异步拒绝都成为对应 `rejected`，不打断其他项、不重放。
   - 第一层限额压缩仅移除 `value` 与 `value_paths`，保留已有引用、`reference_paths`、`required`、`missing_fields`、拒绝错误、单元标识及 transport status，并标记 `value_omitted: true`。仍超限时沿用最小 `outcome_unknown` 包络和原 reason；不得把丢失证据视为完成。上限沿用 `JSON.stringify(...).length` 的 UTF-16 长度定义，不宣称字节或 token 上限。保留原最小包络预检。

3. 在 Adapter 第 2.7 节追加短的宿主长任务映射。外层 `functions.exec` 返回 `Script running with cell ID ...` 后才用 `functions.wait(cell_id=...)`；嵌套 shell 的 `session_id` 则按当前 schema 用 `write_stdin` 收取。保留两个标识及已发起调用，yield、running、timeout 不等于完成或取消，禁止自动重放。`terminate`/interrupt 仅在已有取消决定下使用，并确认底层状态。这里只说明现有工具，不实现管理器或新增后台任务。

4. 扩展 `tests/test_code_mode_batch_asset.py` 的既有 Node wrapper，始终从真实 asset 文件载入源码。支持模拟同步抛错并测试它与异步拒绝逐项隔离。新增用例覆盖嵌套对象和固定数组索引、保留旧字符串字面字段名、非法/越界投影在调用前拒绝、缺失/undefined 与 null/false/0 区分、自身属性、自动状态/显式 required 路径、限额下引用和必需信息保留、最终未知包络、一次调用和旧输入兼容。规则语义通过直接使用方和当前宿主 schema 核对，不增加 Markdown 关键词测试。

## 验收

- 原有 9 项真实 asset 单测继续通过；新增接口覆盖上述成功、失败、缺失、压缩和旧输入兼容，所有已发起项都只调用一次。
- 返回的错误、缺失、仍运行和超限信息可被消费者区分；选小嵌套字段不返回未选择的大文本；引用和必需信息在可容纳的限额中先于普通值保留，无法容纳时明确未知。
- Adapter 决策与当前宿主 schema 一致，不改变 Agent 能力、原生 v2 路由、权限或核心生命周期；发布 root 内链接完整。运行针对接口及既有消费者的单测、相关静态检查和有界 diff/空白检查。
- 原 checkout 用户改动、已安装 Sacha、全局 Codex 配置与外部资源不受影响；本轮不提交、推送、合并、安装或发版。

## 验证限制

本轮源码/Node 入口测试不证明真实 Desktop 性能或 token 收益。后续可用相同命令、参数、返回数据和任务，固定版本/型号/缓存条件，对比最小宿主程序与按需求使用的包装器，记录正确性、遗漏、补读、outer calls、耗时及 token；分别评估投影策略与包装器开销，不把二者混为一因果结论。
