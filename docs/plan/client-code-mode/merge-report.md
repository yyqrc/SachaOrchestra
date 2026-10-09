# 主干整合验证记录

2026-10-01，用户在完成本地实现后要求“合到主干”，授权提交、推送并合入远端 main；不包含发版、安装、强推或绕过分支保护。早先执行报告的“未提交/未推送”描述保留为当时事实。

独立 clone 从 GitHub 拉取 main `d1b8794cef6a60ccc7c86c11c9c9fc2674931968`，其相对实施基线新增的 7 个 DSH 文件与本次改动无重叠。最终去包装改动已无冲突地 rebase 到该提交，未恢复被取代的投影方案，未修改 DSH；原 checkout 的未跟踪 `.plugins-cache.json` 未写入。

整合后验证：

- `python -X utf8 -B -m unittest tests.test_release tests.test_runtime_scenario_verifiers -v`：34/34，通过，10.437 秒；见[原始日志](merge-unit-tests.log)。
- 活跃旧包装引用 0；228 个本地 Markdown 链接，缺失 0；3 个 plugin JSON 可解析；见[审计结果](merge-audit.json)。
- `tests/validate_release_coherence.py --version 1.0.16 --phase candidate`：pass，failures=0。版本不变，未执行发版。
- 与最新 main 的 `git diff --check` 通过；DSH 差异为空。

标准 `validate_plugin.py` 仍不在当前技能安装中，因此未执行；可用机器入口、JSON、链接检查不是该标准校验器的替代通过声明。未运行全仓单测、真实 Desktop 性能实验或插件安装验收，本版没有新的独立 review。

推送前，远端 main 的 branch API 显示 `protected=false`、required status checks 为空；仓库未提交 `.github/workflows`，Actions runs API 返回 `total_count=0`。远端更新成功与最终提交 CI 状态须由推送后的原始结果核实，不能仅据本地提交或本文声称完成。
