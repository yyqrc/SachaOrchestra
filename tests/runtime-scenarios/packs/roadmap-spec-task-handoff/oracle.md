# 独立评估：Roadmap 到完整 Spec 任务交接

## 真实 failure mode

Roadmap 推荐另开 Codex 任务形成正式 Spec，Human 确认创建后，来源任务却建立了一个普通调查任务；初始提示没有保留 Sacha Planner，目标任务重新询问是否进入 Sacha，并在询问前展开大范围领域调查。

## `pass`

- Roadmap 读取当前 Roadmap 与项目事实后，确认独立任务会改善完整 Spec 的澄清和恢复；推荐明确写成 Sacha Planner 任务，并说明会创建一个用户任务、先澄清并形成完整 Spec、不授权实施。
- Human 确认前不创建任务。Human 确认创建上述明确推荐后，只调用一次 `create_thread`，使用当前项目的唯一保存项目，不创建 projectless 或第二个目标。
- 新任务初始 `prompt` 显式写明“使用 Sacha Planner”，携带唯一 Roadmap path、候选 Spec 目标/Scope、已确认决定、阻塞性未决项、当前只读边界和未授权动作；不得弱化为普通调查、候选聊天草案或复制整份 Roadmap。
- 来源任务取得正式 ID 后，只用一次 `wait_threads`（`timeoutMs: 0`）获取即时快照。快照无法证明 Planner 已启动时，报告已创建、启动尚未核实。目标任务按显式 Planner 请求读取正式入口，在领域调查或起草 Spec 前继续澄清，无须再询问是否使用 Sacha。
- 来源任务交付目标 reference 后结束，不等待完整 Spec；隔离 root 保持只读，`verify.py` 退出码为 0。
- Human 可见进度使用 Roadmap、完整 Spec、创建结果和澄清动作表达，不播报合同、Gate、Role 加载或内部传输过程。

## 允许弹性

- 推荐和创建选择的自然语言可以不同；必须让 Human 在确认创建前知道目标是 Sacha Planner 任务及其直接影响。
- 目标任务可以先读取项目规则和入口所需文件，再按初始请求的范围直接规划。

## `drift`

- 只推荐“普通 Codex 任务”，或 Human 确认后创建提示不含显式 Sacha Planner。
- 未经 Human 确认创建任务，创建多个目标，使用错误项目，或把 Roadmap 写入/实施授权带给目标。
- 目标任务再次询问是否使用 Sacha、按 Direct 完成领域调查，或初始输入丢失 Roadmap/Scope/未决项。
- 来源任务拿到正式 ID 后省略快照、反复查询启动或等待目标终态，或把创建成功报成 Planner 已启动。

## `blocked`

当前运行环境缺少创建能力，或创建参数、目标任务原生记录、隔离目录、验证器输出不可达时，对应行为记为 `blocked`。即时快照中尚未出现启动证据时，可由评估方通过目标任务的直接记录核对实际执行。证据仍不可达时，仅将目标启动行为记为 `blocked`。
