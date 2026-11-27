# Codex × Antigravity ACP 验收记录

2026-11-27。A1–A9 对应用户提供的原方案第 9 节，实施范围见[本仓库的批准规格](spec.md)。基线为 `main` 的 `0a3181824a8d745aced72ebaeacdae314711c631`，本记录覆盖 Codex 候选源码和真实宿主调用。Antigravity 使用官方 `agy` 1.5.18 与已保存的 `cached-login`。`.temp` 链接指向本机原始回执。

**A4 和 A7 的补验通过。A6 已用正式结论规则补验。Neon Mid 复审确认两处源码交付阻塞已修复，最终校验和实机选型回执见文末。**

## A4 取消正在运行的只读工具

真实 `agy` 使用已保存的 `cached-login`。客户端收到获准隔离文件 `records.txt` 的只读工具进入 `in_progress`，随即走原有中断路径发送 `session/cancel`。同一工具调用 `call_11941958079448845691` 随后返回终态 `failed`，回合终态为 `cancelled`，无正文，CLI 自行退出，退出码为 `0`。文件哈希未变。使用相同角色、文件和提示且不中断时，读取返回 `completed` 并取得预期尾行，确认文件可以正常读取。[原生事件顺序](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a4-direct-proof.json) · [取消原始回执](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a4-file-raw.json) · [正常读取对照](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a4-file-control.json)

首次搜索探测选中了夹具外的配置路径。观测器发送取消，回执没有返回文件正文，该轮未计入通过证据。此结论覆盖指定读取工具的取消。只读角色的写入、命令限制和未启动工具时的取消沿用已有证据。[首次探测回执](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a4-raw.json) · [角色配置与权限探测](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/reused-and-capability-evidence.json) · [早期取消回执](../../../.temp/agy-adapter-document-review-1826d053/neon-cancelled.json)

## A7 处理 L2 的单方发现

换用日结订单 CSV 样例。GPT 和 Gemini 独立评审同一初始基线，均发现四处功能问题。Gemini 还单独指出账户配置值为 `null` 时的回退风险。这个分支在读取账户默认值时触发，和两人共同发现的「订单显式空标签被默认值覆盖」是两个行为。[初始基线](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-baseline.json) · [GPT 独立评审](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-native-review.json) · [Gemini 独立评审](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-gemini.json)

主任务按批准要求在正式导出入口复现。订单未设置标签且账户的标签为 `null` 时，实际 CSV 行是 `A-1,,201`，预期是 `A-1,sample,201`。主任务采纳该发现，修正了回退逻辑并处理两路共同发现。修复后六项定向检查与冒烟均通过，GPT 和 Gemini 独立接受同一最终基线。两轮的原生读取与 ACP 输入已逐文件核对。[主任务裁决](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-adjudication.md) · [修复前输出](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-targeted-before.json) · [修复后输出](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-targeted-after.json) · [最终基线](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-final-baseline.json) · [Gemini 复评](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-gemini-final.json) · [两路输入核对](../../../.temp/runtime-scenarios/codex-agy-a4-a7-1c39bcf3/evidence/a7-compare-inputs.json)

L0 自检、L1 独立评审和此前 L2 主路径沿用既有运行记录。[分级评审的原生记录](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/native-runtime-evidence.json) · [此前 L2 返修验证](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/result-fixed-verifier.json)

## A9 原生自动选型补验

上轮记录有五次由验收主任务直接发起的手工派发省略 `model` 和 `reasoning_effort`。子代理实际使用 `gpt-6.2-sol / xhigh`。同批显式传入 `medium` 的两次调用均按请求运行。[上轮原生调用](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/native-runtime-evidence.json)

本次由独立 Codex 主任务从候选源码的 `using-sacha` 入口读取正式规则，任务输入只要求本地独立评审，未指定型号和强度。主任务运行在 `gpt-6.2-sol / xhigh`，从 [Codex 适配器的自动选型规则](../../../plugins/sacha-orchestra/adapters/codex/runtime-adapter.md#b-按顺序选择模型和强度)自行选择，唯一一次 `collaboration.spawn_agent` 请求包含以下字段。

```json
{
  "agent_type": "sacha_reviewer",
  "model": "gpt-6.2-sol",
  "reasoning_effort": "medium",
  "fork_turns": "none",
  "task_name": "selection_review"
}
```

原生调用 `call_47c6e72a0d194ed19ff55778ae9ad6c5` 返回 `/root/selection_review`。子代理的实际运行配置为 `gpt-6.2-sol / medium`，直接隶属该主任务，`depth=1`。Reviewer 用验证器复现等于阈值的条目被漏掉，退出码为 `1`，按预期返回 `Needs Fix`。主任务完成，五个夹具文件的哈希均与运行前一致。独立评估确认普通独立评审这一分支通过。[原生调用与遥测](../../../.temp/runtime-scenarios/codex-native-auto-selection-db80f8c6/evidence/native-trace.json) · [主任务终态](../../../.temp/runtime-scenarios/codex-native-auto-selection-db80f8c6/evidence/terminal.json) · [运行前哈希](../../../.temp/runtime-scenarios/codex-native-auto-selection-db80f8c6/evidence/before.json)

A9 的原生 V2、直接处理、单层派发、单一写入者、返修与复评沿用既有证据。独立迁移目标收到批准后接管，验证器退出码为 `0`，随后将 Spec 原位标为「已完成」。无 Antigravity 配置时允许的原生路径见 A8。[原生运行记录](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/native-runtime-evidence.json) · [迁移记录](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/migration-native-evidence.json) · [收尾回执](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/closeout-native-verifier.json)

## 其余证据与结论范围

- **A1–A3 配置和会话。** 隔离测试覆盖试运行、写入、幂等、冲突和回滚。正式 setup 发现两角色并验证握手，派发直接使用保存的认证。Explorer 在三个 CLI 进程中沿用同一会话完成三轮正文，第三轮接上补充决定。独立会话未带入第一轮的观测编号。[配置测试](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/setup-and-controlled-errors.txt) · [正式 setup](../../../.temp/agy-acp-preflight-b57a06f3/setup-result.json) · [保存登录派发](../../../.temp/agy-acp-preflight-b57a06f3/saved-login-dispatch.json) · [会话索引](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/direct-observations.json)
- **A5、A6 和 9.2 质询、方案评审及质量对照。** 两路独立质询都建议去掉跨批缓存、失效事件和阶段管理器。质询时依据验证器纠正了冲突漏报。纯 GPT 的独立规格也得出了正确规则。纯 GPT 规划回合约 28.8 秒，跨模型路线额外使用的三个 Gemini 探索回合和一个方案评审回合合计约 134.5 秒。此样例支持质询能纠错，额外质量收益和额度消耗没有可比数据。[原生对照](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/native-runtime-evidence.json) · [输入哈希和耗时](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/direct-observations.json)
- **A6 的结论取值。** 原测试提示列出了 `Needs Fix`，漏掉 `Needs Replan`。Neon Mid 在新方案评审会话中直接读取同一缺陷规格、原始需求、源码、验证器及当前验收规则，指出跨调用缓存和冲突判定两处问题，按正式规则返回 `Needs Replan`。规格修订及通过仍采用原 Planner 修订后 Reviewer 续接复评为 `Accepted` 的记录，原规划阶段的源码和验证器哈希一致。[原测试提示](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/plan-negative-review.md) · [原退回回执](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/plan-negative-review.json) · [结论取值补验](../../../.temp/runtime-scenarios/gemini-full-review-da7b715e/evidence/a6-plan-decision.json) · [方案复评](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/plan-re-review.json)
- **A8 额度与未知状态。** 原方案允许模拟服务端确定错误。受控 `429` 返回终态且原进程退出后，已批准替代的 L1 实际派出原生 GPT。明确指定 Gemini、缺一路的 L2 和终态未知的调用均保留原安排。缺配置返回 `not_configured`，未启动 CLI。[受控 ACP 回执](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/controlled-acp-responses.json) · [选路记录](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/routing-observed.md)
- **9.3 仓库检查。** 已有定向脚本测试通过记录，`setup-agents` 技能结构与插件校验均通过，后者的原生调用为 `call_98dfcaece0c84a96994c70bd8e0e4f0e`。本记录采用源码场景，也与原方案允许的交付范围一致。[定向检查](../../../.temp/runtime-scenarios/codex-agy-acceptance-20261127/evidence/setup-and-controlled-errors.txt)

## 源码复审与最终检查

Neon Mid 沿原结果评审会话复审修订后的源码。主任务提供获准读取的目录及文件清单，原始回执记录了 13 次成功的文件读取，全部位于该目录。两处阻塞问题已解决，单路自动选型在 Gemini 未启用或资料未获准外发时可直接走原生路径，同时保留明确指定 Gemini 或双模型评审的条件。Gemini 返回 `Accepted with follow-up`，建议补记静态校验和实机选型证据。复审和 A6 的 ACP 回执均确认 `gemini-4-neon / medium`、`cached-login`、`end_turn` 及退出码 `0`。[修订基线](../../../.temp/runtime-scenarios/gemini-full-review-da7b715e/evidence/follow-up-baseline.json) · [原始复审回执](../../../.temp/runtime-scenarios/gemini-full-review-da7b715e/evidence/neon-mid-follow-up.json) · [模型与文件读取核对](../../../.temp/runtime-scenarios/gemini-full-review-da7b715e/evidence/review-run-verification.json)

`python -B -m unittest tests.test_agy_acp tests.test_setup_agents tests.test_release` 的 72 项测试全部通过，插件结构校验通过，改动的发布内 Markdown 引用可达。本次交付覆盖候选源码和上述实际 ACP 调用。[测试结果](../../../.temp/runtime-scenarios/gemini-full-review-da7b715e/evidence/targeted-tests.txt) · [插件校验](../../../.temp/runtime-scenarios/gemini-full-review-da7b715e/evidence/plugin-validation.txt) · [工作区检查](../../../.temp/runtime-scenarios/gemini-full-review-da7b715e/evidence/final-cprobe.json)

Explore 的后续复评为 `Accepted with follow-up`。Neon Mid 复核了脑暴实测和同一 ACP 会话中的两轮质询。脑暴给出不同做法、先试方向及观察标准。质询先问发送方式，再按用户选定的方式追问数据延迟和提醒规则。调查比较与对话收口依据源码核对。第 3 节三项工作流的适用提示随后按复评建议补齐。正式 `setup-agents` 同步了 Explorer 模板，角色发现和握手通过，沿用 `cached-login`。[最终复评](../../../.temp/runtime-scenarios/explore-grill-brainstorm-review-0a31818/evidence/explore-final-review.json) · [脑暴](../../../.temp/runtime-scenarios/explore-dialogue-fix-0a31818/evidence/brainstorm.json) · [质询首轮](../../../.temp/runtime-scenarios/explore-dialogue-fix-0a31818/evidence/grill-recheck-1.json) · [质询续接](../../../.temp/runtime-scenarios/explore-dialogue-fix-0a31818/evidence/grill-recheck-2.json) · [Explorer 同步](../../../.temp/agy-explorer-sync-0a31818/setup-result.json)
