# 2026-10-16 本地验证记录

结果：隔离评审场景 **pass**，独立评估首处偏移为“无”。测试中的错误合并候选被执行者判为 Changes requested；本记录不把错误候选当成本次产品修改，也不重做已发布的合同修复。

## 改动与依据

现有 sacha-plugin-review 只给指定差异建立基线，未具体要求共同祖先、两侧有效决定与最终结果联合比较。实际 `469ea11` remerge diff 证实，旧规则回流既在冲突处理内，也在同文件的冲突标记外；`c6a9e2c` 的文件变更交付另属合法新增。

本次在现有技能增加按合并输入读取的参考，明确两侧到结果的比较、冲突外核对和直接消费者追踪，区分回流、新缺陷与有效新增。文档治理已有语义核对，不重复添加方法；运行时合同、职责与版本均未调整。

## 实际运行

- [重放入口](replay.py) 从八份固定快照生成隔离输入、十项机械比较及原始命令记录。Workflow 自动合并退出码 2，表示两个冲突区；Artifact 为 0；差异命令为 0 或 1。它们只证明输入和比较可重放。
- 执行评审会话 `01a143d6-a747-7152-9177-aae2352e2769` 使用 `fork_turns="none"`，未获 oracle、历史修复或补漏消息。首次结果识别强制拆分、过度尝试、Spec 自主权/设计范围及 Reviewer 条件回退，明确发现冲突区外内容，并保留文件变更交付新增。
- 独立评估会话 `01a143d9-9649-79b0-afb3-d4390b090a88` 重算输入哈希、核对原生读取轨迹与实际比较，裁决 pass。八份快照未被修改。
- 已有输出目录的重放负例退出码 2，拒绝覆盖；`quick_validate.py` 返回 Skill is valid；任务范围 `cprobe` 完整、空白错误为 0。
- 提交前发现 `core.autocrlf=true` 会将检出样例转为 CRLF，使固定哈希失效；在 fixture 内用 `.gitattributes` 固定 Markdown 为 LF，并核对暂存内容经实际检出过滤后的八份样例哈希均匹配，再运行一次机械重放。
- 首次历史片段提取因旧版本没有新版 Spec 段落边界而失败，退出码 1；改为取实际首段后成功，失败输出保留。没有失败的评审运行被覆盖。

## 原始证据与边界

本地隔离输入和差异在 [运行目录](../../../.temp/development-scenarios/20261016-merge-review-01/)，不随插件发布。

- [执行者工具轨迹](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/executor-trace.jsonl)、[最终评审](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/executor-final.md)
- [独立评估工具轨迹](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/evaluation-trace.jsonl)、[独立裁决](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/evaluation-final.md)
- [派发原始记录](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/dispatch.jsonl)、[输入完整性](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/input-integrity.json)、[历史核对与拒绝覆盖负例](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/preflight.jsonl)、[首次提取失败](../../../.temp/development-scenarios/20261016-merge-review-01-evidence/preparation-failure.jsonl)

固定被测技能副本保留在运行目录；试跑后源参考将共同祖先示例明确为 `git merge-base --all`，并删除“缺失决定/复用有效决定”与“文本比较不能代替语义裁决”两处通用规则重述，保留合并专属方法。该命令的真实输出已在 preflight 留存，本案例行为走四快照比较路径；未为上述去重重跑场景。

这是历史取样加合法新增的隔离组合，具体来源与允许变化见 [oracle](oracle.md) 和 [provenance](fixture/provenance.json)。场景通过仅证明本案例，不能证明后续真实合并或安装后的 Runtime 已稳定正确。场景验证完成时尚未提交、发布或安装；原有 `.plugins-cache.json` 未纳入改动。
