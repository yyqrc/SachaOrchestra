# 删除 Codex Code Mode 包装：执行报告

2026-10-01。已按最新决定完成本地去包装，当前方案见 [spec](spec.md)。独立 clone 保持 `codex/code-mode-projection / 482019606584db9afd187a2c9a2447821d3cfc1c`；原 checkout 保持 `main / d1b8794cef6a60ccc7c86c11c9c9fc2674931968`，本任务没有写入它。

## 删除与修改

| 路径 | 结果 |
| --- | --- |
| `plugins/sacha-orchestra/adapters/codex/code-mode-batch.js` | 删除整个包装，包括昨天新增的嵌套投影、状态保留和预算包络实现。 |
| `tests/test_code_mode_batch_asset.py` | 删除整个专用测试模块；昨天的 18 项通过只保留为历史，不是本版验收。 |
| [Codex adapter](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md) | 只使用客户端 `functions.exec` / `tools`；删除 asset 加载、专用输入/输出协议、最少调用数、投影字段、预算、唯一解析及包装证据要求。保留权限、工具发现、direct-only Agent 生命周期限制、原始结果判断、长任务收取和未知结果不自动重放。 |
| [release.py](../../../scripts/release.py) | 删除包装器和已删除测试的选择映射；不新增退役路径特判。既有未知已删除 producer 处理与资源删除结构校验选择继续有效。 |
| [test_release.py](../../../tests/test_release.py) | 清理旧模块断言，通用 staged deletion 用仍存在的 setup-agents 测试作输入；增加一项真实目录/验证命令回归，确认 Codex adapter 文档仍存在且没有可执行辅助包装，纯文档变更不选择包装生产测试。不用 Markdown 词句断言规则行为。 |
| 历史计划与报告 | 昨天的 spec/报告和 2026-08-14 包装 spec 顶部增加已取代链接，原正文、路径和日志保持历史身份；其他历史审计与实验保留。 |

DSH PTC/run_code、companion、其他 Runtime、型号目录、feature flags、全局配置和已安装插件均未修改；没有引入新包装、DSL、job manager 或测试框架。

## 实际验证

- `python -X utf8 -B -m unittest tests.test_release tests.test_runtime_scenario_verifiers -v`：最终 **34/34 通过**，10.306 秒；[完整原始日志](unit-tests.log)。release 测试中的 Git/安装操作只在隔离测试目录或 mock 中执行，未发布或安装本项目。
- 仓库现有测试选择函数对实际 tracked diff 只选择 `tests.test_release`；Runtime verifier 额外核对既有语义场景不依赖被删包装。
- 全仓 tracked 内容搜索并分类：活跃旧实现/测试名称、专用全局输入与投影协议引用为 0。当前 Code Mode 字样仅出现在原生 adapter 说明和既有 Explore 词义场景；docs/plan 中剩余命中是历史方案、审计或实验。新 spec 中删除路径仅描述本次删除，不是执行依赖。
- 活跃 tracked Markdown：113 文件、228 个本地链接目标，缺失 0；其中发布 root 为 142 个本地链接目标，缺失 0。3 份插件 JSON 可解析，打包清单未指向旧包装。
- `python -X utf8 -B tests/validate_release_coherence.py --version 1.0.16 --phase candidate`：pass，failures=0。版本/清单未变；只执行只读机器检查，未执行 release。
- `git diff --check` 通过；有界 `cprobe summary` 完整，adapter、release.py、test_release.py 的 `whitespace.errors=0`。已阅读最终生产差异和测试变更，自查未发现本范围阻塞缺陷。
- 原 checkout 末次只读核对仍为上述 HEAD，只有原 `.plugins-cache.json` 未跟踪；独立 clone 对 DSH 的 diff 为空，无关改动受到保护。

## 校验限制

`requires_plugin_validation=True`，因为删除了发布资源。标准 `validate_plugin.py` **未执行**：仓库选择的个人路径 `C:\Users\shifengzhou\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py` 不存在；个人 skills、相关已安装缓存检索及完整 executor Skill catalog 中未找到可用入口。上面的现有 release coherence、JSON 和全量活跃链接检查是已完成的可用检查，不冒充标准插件结构校验。没有为此安装插件或修改全局配置。

本轮没有新的独立审阅结论；昨天的审阅针对已经被替换的包装方案，不能复用为本版裁决。未运行全仓测试、真实 Desktop 场景、性能实验、安装缓存验收或发版。当前结果不包含性能或 token 收益承诺。

## 替换关系与交付

[昨天的执行报告](../code-mode-projection/execution-report.md)及测试日志继续记录当时行为；今天的决定是完整撤掉该包装，不能把昨天的投影协议换名保留。原 `code-mode-review.patch` 继续作为历史 diff；本版 tracked 最终 diff 导出为 `client-code-mode-review.patch`（non-portable：`C:\Users\shifengzhou\Documents\Codex\2026-09-30\task-5\client-code-mode-review.patch`）。本次 spec、报告和日志作为独立任务材料保留，可供父任务复核。

没有对项目 checkout 暂存、提交、推送、合并、发版或安装。标准结构校验缺口如上，其余本轮已授权实施与可用验证均完成。
