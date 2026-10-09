# 仅使用客户端原生 Code Mode

状态：已完成

## 目标与范围

按 2026-10-01 最新明确决定，删除 Sacha 自己的 Codex Code Mode 包装，只使用客户端 `functions.exec` / `tools` 能力。此决定取代昨天的可选包装及嵌套投影方案；不保留替代包装、输入/输出协议、专用加载、校验或路由要求。

保留通用工具发现、权限与读写边界、Agent direct-only/单层生命周期限制，以及长任务原目标收取和未知结果禁止自动重放。DSH 客户端 PTC/run_code 与 companion、型号目录、feature flags、全局配置和安装缓存均不在范围内。初次实施仅授权本地修改和测试；2026-10-01 用户随后要求“合到主干”，授权在独立 clone 整合最新远端 main、提交并推送合入 main，核实远端提交和 CI。不得强推、绕过分支保护、发版或安装；原 checkout 的无关改动保持不动。

## 精确实施方案

1. 删除 `plugins/sacha-orchestra/adapters/codex/code-mode-batch.js` 与 `tests/test_code_mode_batch_asset.py`，包括昨天的投影实现和 18 项专用测试。已有历史 diff 和测试日志保留，不能把已删除实现的历史通过数当作当前验证。
2. `plugins/sacha-orchestra/adapters/codex/runtime-adapter.md` 第 2.7 节（锚点 `### 2.7 Code Mode`）改为简短客户端原生用法：按实际宿主 schema 用 `functions.exec` / `tools` 完成读取、并发和结果处理，不加载 Sacha asset、不设置专用全局输入、不使用自有结果包络。并发仅用于已就绪且独立的调用，依赖或语义判断仍按需串行。权限/只读研究边界和 direct-only Agent 工具约束继续服从宿主及现有合同，不复制专用最少调用数、字段表、预算或日志协议。
   - 原 2.7.2 长任务两段保留，移为 2.7.1；明确 `cell_id` / `session_id` 的当前宿主收取方式，yield/running/timeout 不代表完成或取消，不盲目重放未知调用。
   - 2.8 删除包装器 `ALL_TOOLS` 唯一解析要求，仅沿用实际客户端工具面和原生搜索。第 4 节移除 asset hash、单元 ID、自有 schema 等包装证据字段；保留原生调用、参数、结果和来源的通用证据要求。
3. `scripts/release.py` 的 `narrow_test_modules`（当前约 255、282 行）删除包装器及已删除测试的映射，不新增退役路径特判或另一套调度。现有未知已删除 producer 的通用处理仍负责本次删除；插件资源删除继续触发结构校验。
4. `tests/test_release.py` 删除专用 asset 验证断言和 Runtime test 集合中的已删除模块。现有真实 staged deletion 案例改用仍存在的 `tests/test_setup_agents.py`，保留“删除 producer 和自身测试不选择已删除模块”的通用行为。补一项轻量当前发布内容回归：实际 Codex adapter 目录不存在可执行辅助器；纯 adapter 文档变更不选择插件侧 Code Mode 生产测试。观察目录/验证命令，不用 Markdown 固定词句证明规则语义。
5. 在 `docs/plan/code-mode-projection/spec.md`、其执行报告和 `docs/plan/2026-08-14-codex-code-mode-orchestration/spec.md` 顶部加最短“已取代”链接，原正文、日志和事实不改写。其他历史审计/实验仅作为历史，不扫除所有 Code Mode 词语；既有 Explore Runtime 词义场景保留，因为它不调用或依赖包装器。

## 验收

- 发布 root 无 Codex JS 包装和专用协议；脚本、当前测试、活跃文档与打包配置无旧实现/已删除测试依赖。全仓搜索按当前内容、历史记录和无关客户端能力逐项分类。
- Adapter 用法与当前客户端 schema 一致，不改变 Agent 权限、direct-only 限制、其他运行环境或通用恢复规则；发布 root 中链接目标存在。
- 运行现有 `tests.test_release` 及相关轻量回归，并核对 Runtime 场景 verifier；运行可用 plugin 结构/机器入口检查和 `git diff --check`。缺失 validator 时报告具体缺口，并运行现有可用等价检查，不伪报结构通过。
- 差异限定为上述实现、消费者和必要历史标记；原 checkout 与无关改动不受影响。交付最终 diff、真实日志和实现者自查结果，不复用昨天独立审阅作为本版裁决。

## 验证限制

源码、发布内容和单测只能证明本次依赖移除及保留的机器行为，不证明客户端运行性能、token 收益或已安装插件行为。本轮不新增 Desktop 性能验收债。
