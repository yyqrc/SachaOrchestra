# 会话驱动的维护工具方向

> 状态：Codex 本地检查已收敛到 FastCtx、`diff_digest.ps1` 和项目具名验证；其余为后续方向
> 位置边界：被 Runtime/Role 直接消费的通用 helper 随 plugin 部署；项目或领域工具归对应项目/Provider；Core 不拥有脚本

## 1. 会话规律

2026-07-28 对本机现有 JSONL 会话做结构统计，只读取 cwd、回合、工具名、调用参数中的命令类别、输出长度和 compaction，不消费其他项目业务正文。

重点样本为 LookDevProject 18 个、UnitySource 9 个、Client 6 个会话：

| 现象 | 结果 | 对应方向 |
| --- | --- | --- |
| 模型与工具往返 | 319 个模型回合、3075 次工具调用 | 合并同一阶段的机械调用 |
| `functions.exec` 聚合不足 | 2380 次 `exec` 中 92.6% 只调用一个内部工具 | 独立步骤并行调用；重复且稳定的项目动作再脚本化 |
| 读与搜索高频 | 读文件占 46.3%，搜索占 38.9%；`read + search` 组合出现 244 次 | FastCtx 先 grep，再局部 read |
| 大输出集中 | 超过 6000 字符的输出占 30.5%，却占 86.7% 输出字符 | 默认摘要，原文落 `.temp/` 并返回 locator |
| 项目侧重复 | LookDev/Client 频繁重复 status、diff、Unity 状态和同步检查 | `diff_digest.ps1`、领域 Unity probe 和 compact sync 各自处理 |

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

### 2.2 当前本地检查

- 文件定位和读取：FastCtx `grep → read 30～100 行 → 必要时全文`。
- Git/SVN 状态和 patch：全局 `diff_digest.ps1`。
- 测试、validator、build 和 runtime：Project AGENTS/Domain Skill 选择最窄入口。

不再用第二层聚合脚本包装这些已有入口。

### 2.3 Unity `state_probe`

LookDevProject 和 Client 的 Unity 状态查询由 cgame-unity 或项目工具拥有，不在 Sacha 复制 C#。

一次 `eval_cs` 接受 JSON query，按需读取：

- Editor/PlayMode 与编译状态；
- Scene、对象、组件字段和资源绑定；
- Renderer、Material、LightProbe/TOD 等指定领域状态；
- 过滤后的日志计数与最高信号项。

默认只读、不 Refresh、不切 PlayMode、不改对象。stdout 返回有界 JSON；完整日志、截图和对象清单只返回 locator。固定查询成熟后再落为项目 Editor helper。

### 2.4 `sync_to_client.py` compact mode

复用 LookDevProject 已有脚本，不另建同步实现。增加：

- `--format json`：stdout 只输出 copied/skipped/deleted/error 计数和目标根；
- `--details-file <path>`：逐文件记录落盘；
- `--max-items`：终端只展开少量异常；
- dry-run 保持默认安全入口，真实复制/删除语义不变。

该模式只减少输出；不自动执行 SVN add/delete/commit，也不把格式差异误报为功能漂移。

### 2.5 `task_handoff.ps1`

在调查已结束、目标和 locator 已冻结后生成短交接，供新 task 使用。

输入只接受 Human/模型已经确认的目标、Scope、关键文件、已知事实、剩余动作和风险，不自行推断方案。默认输出不超过 20 行 / 3500 字符；超出内容写入 locator。

## 3. 实现顺序

1. 已完成：FastCtx 负责本地 read/search，`diff_digest.ps1` 负责 VCS diff。
2. 下一项：`sync_to_client.py --format json` 在现有安全同步路径上直接减输出。
3. Unity `state_probe` 由 cgame-unity/消费项目根据真实重复 query 固化。
4. `session_usage_digest.py` 与 `task_handoff.ps1` 分别用于持续发现高频模式和阶段切换。

每个工具只在步骤已经稳定且跨会话重复时实现。仍需模型判断的方案、Scope、风险和授权不写进脚本。
