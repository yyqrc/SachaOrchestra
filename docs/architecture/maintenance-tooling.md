# 会话驱动的维护工具方向

> 状态：`context_probe.ps1`、`change_closeout.ps1` 已随 `0.2.3` 发布；其余为后续方向
> 位置边界：被 Runtime/Role 直接消费的通用 helper 随 plugin 部署；项目或领域工具归对应项目/Provider；Core 不拥有脚本

## 1. 会话规律

2026-07-28 对本机现有 JSONL 会话做结构统计，只读取 cwd、回合、工具名、调用参数中的命令类别、输出长度和 compaction，不消费其他项目业务正文。

重点样本为 LookDevProject 18 个、UnitySource 9 个、Client 6 个会话：

| 现象 | 结果 | 对应方向 |
| --- | --- | --- |
| 模型与工具往返 | 319 个模型回合、3075 次工具调用 | 合并同一阶段的机械调用 |
| `functions.exec` 聚合不足 | 2380 次 `exec` 中 92.6% 只调用一个内部工具 | 用脚本一次完成稳定步骤，而不是只给单命令套 `exec` |
| 读与搜索高频 | 读文件占 46.3%，搜索占 38.9%；`read + search` 组合出现 244 次 | 首先实现查询、计数、anchor 展开一体化 |
| 大输出集中 | 超过 6000 字符的输出占 30.5%，却占 86.7% 输出字符 | 默认摘要，原文落 `.temp/` 并返回 locator |
| 项目侧重复 | LookDev/Client 频繁重复 status、diff、Unity 状态和同步检查 | 分别提供 change closeout、Unity probe 和 compact sync |

另取最近 18 个 Sacha 会话作为维护流程对照：188 个模型回合、2300 次工具调用、27 次 compaction；`read + search` 组合 80 次，`diff + validate` 组合 77 次。Sacha 的首要重复项是候选版本收尾，不是再增加流程文档。

这些数字用于选择高频步骤，不作为 token 计费或工具收益承诺。cached token 仍可能计入 gross telemetry。

## 2. 工具设计

### 2.1 `session_usage_digest.py`

持续从会话结构中找高频行为，避免依靠单次体感设计工具。

输入：

- session 根、时间范围和 cwd glob；
- 是否包含 archived session；
- 只统计结构的默认隐私模式。

输出：

- session、模型回合、工具调用和 compaction 计数；
- 工具频率、单工具 `exec` 比例、常见调用组合；
- 输出长度分布和大输出来源；
- JSON 摘要；不输出用户消息、代码正文或命令原文。

### 2.2 `context_probe.ps1`

把项目摸底阶段反复出现的 list、search、count、read anchor 和 VCS 状态合成一次只读调用。

实现：[plugin script](../../plugins/sacha-orchestra/scripts/context_probe.ps1)。默认输出与显式 `-Summary` 使用同一 summary 路径；`-Details` 才返回逐文件与逐 match 数组，两者不得同时指定。

输入：

- `-Root`；
- `-Query`、`-Path`、`-Anchor`；
- include/exclude；
- `-MaxLines`、`-MaxChars`。

行为：

- 并行执行文件清单、命中计数、目标符号搜索和 VCS 摘要；
- 只有命中唯一或调用方指定 anchor 时才展开行段；
- 适用 `AGENTS.md`、Skill 和规则文件只返回 locator，仍由模型按要求完整读取；
- 原始结果写入 `.temp/context-probe/<run-id>/`。

stdout 只返回一个 JSON：

```json
{
  "status": "ok",
  "files": 12,
  "matches": 37,
  "changed": 3,
  "snippets": [],
  "warnings": [],
  "raw_dir": ".temp/context-probe/<run-id>"
}
```

### 2.3 `change_closeout.ps1`

把修改后的 status、diff 摘要、格式检查、链接检查和既有 validator 合成一次收尾。

实现：[plugin script](../../plugins/sacha-orchestra/scripts/change_closeout.ps1)。默认输出与显式 `-Summary` 使用同一 summary 路径；`-Details` 才展开逐检查信息，两者不得同时指定。

输入：

- `-Root`；
- `-Profile docs|plugin|unity|engine`；
- `-ChangedPath`；
- 可选的明确 build wrapper，不自行猜测构建命令。

行为：

- 复用 `diff_digest.ps1 -Mode Summary`；
- 批量运行互不依赖的只读/static checks；Markdown 链接始终扫描全仓入链；
- 完整日志写 `.temp/change-closeout/<run-id>/`；
- 返回每项 `passed|failed|skipped`、退出码、失败摘要和 locator；存在跳过项时顶层为 `partial`；
- 不执行 stage、commit、push、安装、Unity Refresh 或构建，除非调用方显式选择对应动作且已有授权。

### 2.4 Unity `state_probe`

LookDevProject 和 Client 的 Unity 状态查询由 cgame-unity 或项目工具拥有，不在 Sacha 复制 C#。

一次 `eval_cs` 接受 JSON query，按需读取：

- Editor/PlayMode 与编译状态；
- Scene、对象、组件字段和资源绑定；
- Renderer、Material、LightProbe/TOD 等指定领域状态；
- 过滤后的日志计数与最高信号项。

默认只读、不 Refresh、不切 PlayMode、不改对象。stdout 返回有界 JSON；完整日志、截图和对象清单只返回 locator。固定查询成熟后再落为项目 Editor helper。

### 2.5 `sync_to_client.py` compact mode

复用 LookDevProject 已有脚本，不另建同步实现。增加：

- `--format json`：stdout 只输出 copied/skipped/deleted/error 计数和目标根；
- `--details-file <path>`：逐文件记录落盘；
- `--max-items`：终端只展开少量异常；
- dry-run 保持默认安全入口，真实复制/删除语义不变。

该模式只减少输出；不自动执行 SVN add/delete/commit，也不把格式差异误报为功能漂移。

### 2.6 `task_handoff.ps1`

在调查已结束、目标和 locator 已冻结后生成短交接，供新 task 使用。

输入只接受 Human/模型已经确认的目标、Scope、关键文件、已知事实、剩余动作和风险，不自行推断方案。默认输出不超过 20 行 / 3500 字符；超出内容写入 locator。

## 3. 实现顺序

1. 已实现：`context_probe.ps1` 覆盖三个重点项目最高频的 read/search 往返。
2. 已实现：`change_closeout.ps1` 覆盖 Sacha 与 Client 的 diff/status/validate 收尾。
3. 下一项：`sync_to_client.py --format json` 在现有安全同步路径上直接减输出。
4. Unity `state_probe` 由 cgame-unity/消费项目根据真实重复 query 固化。
5. `session_usage_digest.py` 与 `task_handoff.ps1` 分别用于持续发现高频模式和阶段切换。

每个工具只在步骤已经稳定且跨会话重复时实现。仍需模型判断的方案、Scope、风险和授权不写进脚本。
