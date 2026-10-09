# CodeMode 投影优化执行报告

> 历史记录：包装方案已被 2026-10-01 的[客户端原生 Code Mode 方案](../client-code-mode/spec.md)取代；以下正文、路径与验证仅描述当时状态，不是当前执行依赖。

2026-09-30；实施基线 `482019606584db9afd187a2c9a2447821d3cfc1c`；独立 clone 分支 `codex/code-mode-projection`。本次实施与验证已完成，依据为 [spec](spec.md)、真实 asset 文件入口的 [单测原始日志](unit-tests.log) 和以下差异/检查记录。

## 实际改动

| 文件 | 最终行为 |
| --- | --- |
| [code-mode-batch.js](../../../plugins/sacha-orchestra/adapters/codex/code-mode-batch.js) | 保持旧必填字段和 schema 1；可选 result/reference/required 路径投影限制为每类 32 条、每条 8 段。自身属性读取；缺失和 undefined 显式报告，null/false/0 保留。自动保留已存在的错误、状态、退出码和 session/cell ID，并支持调用方明确所需状态路径。限额先省略普通值，保留引用、必需状态、缺失与拒绝信息；无法容纳时明确 unknown。同步抛错进入逐项拒绝，不跳过后续调用或重放。 |
| [runtime-adapter.md](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md) | 普通独立读取优先最小宿主 CodeMode；包装器仅服务确有统一结果/投影/逐项错误需求的调用。明确 Manager/Explore/researcher 边界、工具发现与 shell 限制；区分 cell_id 与 session_id，yield/running/timeout 不视为结束或取消，不自动重放。 |
| [test_code_mode_batch_asset.py](../../../tests/test_code_mode_batch_asset.py) | 沿用读取真实 asset 的 Node wrapper。原 9 项保留，增加 9 项接口回归，其中非法输入包含 39 个 subtest。覆盖嵌套小值/固定数组索引、引用、缺失与假值、状态/业务错误/运行 ID、prototype 自身属性、边界输入、预算回退、同步与异步失败、旧输入兼容。 |

消费方可继续使用旧 `result_fields`/`reference_fields`。输出新增字段为加法；状态/缺字段会增加输出长度，因此原来刚好可容纳的预算可能转入明确的省略或 unknown，不能据此推断完成。自动状态列表不理解所有业务 schema；调用方仍须用 `required_paths` 保留实际需要的字段，并检查 domain 状态。

## 验证与独立复核

- `python -X utf8 -B -m unittest tests.test_code_mode_batch_asset -v`：18/18 通过，3.151 秒；日志见上方链接。原 9 项先单独通过，最终 18 项包含原有覆盖。
- Node `v22.23.1`，Python `3.14.2`。每个测试执行真实 asset 源码，不在测试中维护其副本；所有成功输出额外核对 UTF-16 长度不超过设置的上限。
- Adapter 的 8 个本地 Markdown 链接目标全部存在，发布 root 内所需引用可达。
- 对实际 3 个修改路径调用仓库 `scripts/release.py` 的只读选择函数：最窄模块为 `tests.test_code_mode_batch_asset`；`requires_plugin_validation=False`，`changed_skill_metadata_roots=[]`。未修改部署清单、技能元数据或目录结构，不运行不适用的 plugin/skill 结构校验，不执行 release。
- `cprobe summary` 对 adapter 目录和测试文件均 `budget.complete=true`、`whitespace.errors=0`。CRLF 归一化提示不属于错误；未重复执行 diff --check。源码和全部新增测试已由实现者阅读核对。
- 父任务提供的独立只读审阅任务 `01a0f1fa-5585-742d-84b4-7fa055a24029` 已完成，覆盖兼容、错误/状态/session、缺字段、prototype、嵌套/预算/引用和规则，当前快照无可行动缺陷；它未运行测试。交付前回读的源码 hash 与其 11:04Z 快照完全相同：asset `882471CFC997CC0A37A6E43E65722ACFF6DCF02618A08B1D95B7E2C76B02DCDB`；adapter `573FC6B8CA1F5A1E44E129C9AA5DE137C883714983F71C25D643F95DC39CE6BD`；test `12DDE82ADF13600FC4185D000983678DC8FE2C6CC6BD92601E98DFFEAE8C9782`。审阅后只增加交付记录、原位更新 spec 状态，未改源码或测试。

没有运行全仓单测、真实 Desktop 配对实验、安装缓存验收或发版。Node 入口测试证明上述接口在模拟工具返回下的行为，不证明 Desktop 宿主、真实工具权限、端到端时延或 token 收益；长任务收取规则依据当前宿主 schema 核对，本版没有新增收取管理器。

## 工作区与交付边界

本任务只写独立 clone。原 checkout 在执行期间从 `4820196` 推进到 `d1b8794cef6a60ccc7c86c11c9c9fc2674931968`；只读核对表明新增差异全部是最初观察到的 DSH 文件，本次 3 个源码/测试路径与原基线仍一致。本任务没有修改原 checkout、已安装 Sacha、全局 Codex 配置或外部资源，也没有暂存、提交、推送、合并、安装或发版。

最终 tracked diff 已导出为本任务目录的 `code-mode-review.patch`（non-portable：`C:\Users\shifengzhou\Documents\Codex\2026-09-30\task-5\code-mode-review.patch`）；源文件、规格和测试日志保留在独立 clone，可由父任务据实际文件复核和决定后续集成。

## 优化项是否仍成立

仍成立且本版已实施：普通读取减少不必要包装；按实际 schema 精选嵌套小值；保留状态、引用、缺失与省略；同步失败逐项隔离；明确长任务原目标收取和禁止重放。

暂缓：DAG/分页框架、job manager、自动 instant_interrupt、型号/agent_type 改动、放宽 fastctx/researcher 限制、多层 Agent 生命周期、重写调度器。当前证据不支持这些扩张。

后续收益实验建议把两个因素分开：先固定全部调用/参数/返回内容，仅比较最小宿主程序与无额外缩减的包装器；再固定调用比较整段输出与本版精确投影。沿用相同任务、Desktop/插件版本、型号/强度、缓存口径，交错重复多对，记录答案正确性、失败/遗漏、补读、outer calls、嵌套耗时、端到端耗时和 input/cached/output token。缓存不匹配或数据不足时保留不确定性；既有单 pair 不构成包装器提速或省 token 的因果证据。
