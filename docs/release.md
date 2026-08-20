# Sacha Orchestra 发版与安装指南

> 文档身份：插件开发使用；不进入发布插件。仅在 Human 显式要求快速发版、普通发版、安装、重装或 cache parity 验收时读取。

## Owner 与授权

- [`EVOLUTION.md`](../EVOLUTION.md) 拥有当前 release、当前待发布源码版本、breaking boundary、成熟度和尚未实施的长期方向；三个 deployment manifest 拥有当前源码版本，Git annotated tag 标识已发布版本。
- [`scripts/release.py`](../scripts/release.py) 只执行现有 Owner 已决定的机械步骤；失败后停止，不替代版本决定、Review、commit/tag/push 授权、安装授权或 Runtime 验收。
- 发布执行者保护发布范围外的 working/untracked 内容，不执行 stash、reset、clean、rebase、强制 checkout 或历史改写。

## 快速发版

Human 说“快速发版”时默认递增 patch 版本；只人工核对 Evolution 的当前 release 与当前待发布源码版本状态，并机器核对三个 deployment manifest、annotated tag 到 `HEAD` 的指向及 push 后远端分支/tag。跳过普通回归、Skill/Plugin validator、完整 release coherence、安装/cache parity、fresh discovery 和 Runtime。

快速发版授权 commit、annotated tag 和 push，不授权安装、refresh、cache 修改或 Runtime 验收；跳过项必须在交付中明确标记。

## 普通发版

Human 说“发版”时，运行风险对应的普通验证与完整 metadata coherence；安装和 Runtime 仍按明确授权与发布目标决定。

- Scope、版本和 Review 结论稳定时优先使用 `scripts/release.py prepare|publish|install`；脚本不可用时才使用下文的定向 fallback。
- 执行者发现同一 Scope 已有仍有效的独立 Review，且精确暂存发布内容、验收输入和证据边界未超出该 Review 时复用原结论；发版本身不触发重审。任一项变化时只审原结论后的精确暂存变化及其影响，按风险选择最低充分模型与推理强度，不因发布动作默认提高强度。实施收尾本应完成但缺失的 Review 只补未审 staged delta，不得借发版重启完整调查。
- 执行者先精确暂存当前待发布源码版本对应的发布内容并取得唯一 staged tree；需要增量 Review 时立即以该 tree、精确 diff、受影响 Owner/消费者和已有证据派发独立 Reviewer，同时在主任务运行 `release.py prepare`，不得等待一方结束后才启动另一方。
- `prepare` 返回的同一 tree JSON 是 Reviewer 可复用的验证回执：Reviewer 仍在运行时由主任务立即补发；Reviewer 已终态时由主任务核对回执 tree 与 Review tree 一致且无失败，不新开 Review。除非 tree 不同、输出缺少退出状态/结果摘要/失败计数，或存在会改变 Outcome 的具体冲突，Reviewer 不得重跑其中命令，也不得为恢复背景重新读取完整根 `AGENTS.md`、`PLUGIN_DESIGN.md`、历史或无直接消费者 Owner。
- `prepare` 与 Review 通过后，维护者才把 Evolution 从待发布状态切换为当前 release，并依次执行 commit、annotated tag、发布阶段一致性检查、原子 push 和远端核对。tag 建立前不得向 Human 宣称当前待发布源码版本已成为 release，发布授权不得写入原实施 Scope。
- 实施收尾时若 Reviewer Gate 已有事实依据，当前 Owner 应完成必要 Review；发布阶段只核对精确暂存发布内容是否仍在该 Review 的 Scope、验收输入和证据边界内。发布脚本允许精确暂存发布范围外存在无关工作区改动，但 `--candidate-path` 指定文件暂存后又变化、存在冲突或 index 验证失败时必须停止。
- `release.py publish` 返回 `status=pass` 且携带 commit、tree、branch、tag、remote 与 `remote_verified=true` 后，执行者直接消费这些机器结果，只再运行一次 `cprobe summary` 确认任务外工作区边界并交付；不得例行重复查询 manifest、Evolution、HEAD/tag、远端 branch/tag、cache parity 或完整 plugin list。只有脚本缺少上述字段、结果冲突/失败、Human 明确要求安装或当前 Scope 包含 fresh Runtime 验收时才定向补查。

普通发版先对当前待发布源码版本的精确暂存内容运行；`prepare` 从 Git index 导出隔离快照，验证不读取精确暂存发布范围外的 working/untracked 内容：

```powershell
python -B scripts/release.py prepare --version <version> --candidate-path <path> [--candidate-path <path> ...]
```

复用仍有效的 Review 或完成必要的增量 Review 后，维护者把 Evolution 从待发布状态切换为当前 release 并精确暂存；再运行：

```powershell
python -B scripts/release.py publish --version <version> --review reused|accepted --message <commit-message> --candidate-path <path> [--candidate-path <path> ...]
```

脚本不可用时，待发布与发布两个机器阶段分别运行 metadata coherence：

```powershell
python -B tests/validate_release_coherence.py --version <version> --phase candidate
python -B tests/validate_release_coherence.py --version <version> --phase release
```

`candidate`（待发布阶段）只核对当前待发布源码版本的机器可解析部署身份和生产入口；`release`（发布阶段）在 commit、annotated tag 已建立且 Evolution 已人工切换为当前 release 后运行，并额外核对 annotated tag 精确指向 `HEAD`。该脚本不读取 README、Core、Adapter、Skill 或 Evolution 的说明文字。

## 安装与 cache parity

- Marketplace 注册、安装、refresh、removal/reinstall 需要 Human 明确授权；实施或发布批准不隐含安装授权。
- `codex plugin list` 显示已启用插件的 `PATH` 直接指向当前 repo-local plugin `root` 时，视为源码直连加载；版本变化本身不触发安装或 refresh。需要安装/cache 证据时先核对当前 `PATH`、生效版本和 source/cache parity，只有明确安装授权才调用安装 CLI。
- 使用 `read_marketplace_name.py` 从 `.agents/plugins/marketplace.json` 读取 marketplace 名称；不得根据目录名猜测。
- 授权后按目标 Adapter 执行并验证 marketplace/plugin list；Scope、版本、目标、branch/remote 未变化时不重复询问。
- 安装前关闭本次发布创建且已终态的辅助 Agent；安装返回拒绝访问或 cache 已创建但登记未完成时停止并报告，不删除、覆盖或手改 cache，待占用解除后再用同一 CLI 恢复并核对。
- manifest 使用批准的精确 semantic version，不加 cachebuster；不得编辑 cache、应用权限或系统 PATH。

只有 Human 明确要求安装、重装或 cache parity 验收时运行：

```powershell
python -B scripts/release.py install --version <version>
```

安装证据只覆盖目标 Runtime 的实际安装、发现和 source/cache parity；源码校验、发布成功或 repo-local 直连不能替代安装后 fresh discovery 与 Runtime 行为。
