# Executor task migration Execution Report

## 实际 delta

- Workflow Contract 15 只保留 Role/Gate、高层 lifecycle、single writer、普通批准与明确迁移语义；readiness、派发和 return 指向 Coordination。
- Coordination Contract 7 成为 Manager 唯一 Core owner：统一评估、拆分、依赖波次、execution/research readiness、逐单元 route requirement、派发/等待/取消、去重归并、return 与 migration owner transfer。
- 普通同-task Executor、迁移 target 与 Clarify research 共用同一 Manager 算法。当前 owner 只需识别多个候选/依赖/恢复协调，不必先完整拆分或宣布 ready；串行结论只约束当前波次，本波完成后回到同一 Task/Scope revision 重算剩余图，后续波次满足至少两个 ready 且隔离时仍须在该波次首次 wait 前实际并行派发。
- `using-sacha`、Planner、Executor、Manager、Clarify 只保留 Role-local 调用与消费步骤，不再复制 readiness、spawn、模型或 Runtime 参数。
- Codex Adapter 只映射 transport：assessment 收敛为“任务形态 broad/bounded × 负荷 critical/standard 或 nontrivial/light”，不再维护九种重叠难度类别。
- 自动 route 只有 Sol xhigh、Sol medium、Luna max、Luna xhigh；Human exact 可指定其他 model/effort，但 Adapter 不主动选择 Terra 或 Sol high/max/ultra。
- 自动 fallback 至多一次：named Luna 未启动即失败时只尝试 Sol medium；Sol、Human 精确配置、可能已启动/写入、旧 writer 未终止或独立性不明时停止。
- 两个 Luna named definition 同时接受 `execution-ready` 与只读 `research-ready`；Clarify research 不再被错误要求冻结实施 Scope/验收，也不取得写入、架构、跨 owner 或独立 Review 权限。
- 明确“批准并新开执行任务”才 create/reuse 一个用户可见 target；target 接管完整剩余 lifecycle，Source 最小 handoff 后结束，不 wait/join。普通批准仍在当前 task 立即执行。
- 显式 Feedback 使用独立的 `list_threads`/有界 `read_thread`、唯一 `create_thread` 和 `wait_threads` terminal join；repair target 因有上游 return consumer 保持 owner 到根终态，不再嵌套 migration。
- Codex Adapter active surface 不再暴露 Pi one-shot；Pi 脚本、Setup 配置和历史记录按 Scope 保留。
- README 从冻结需求反推主流程，不再作为规范来源；图中 Manager 自己评估 ready。
- 文本预算继续只输出 advisory warning，不进入 failure，也不驱动语义压缩。
- prompt/migration source tests 从 16 项逐句文案测试收缩为 7 项结构与分支不变量；Spec/Artifact 测试删除中文整句与旧合同版本硬锁。完整 `test_*.py` 数量从 31 降至 22。

## 验证

- `python -B -m unittest discover -s tests -p 'test_*.py'`：22/22 passed。
- `python -B tests/validate_project_setup.py`：45/45 passed；Pi Setup 保留行为仍通过。
- `python -B -m unittest tests.validate_spec_artifact_contract`：3/3 passed；删除无行为 consumer 的 Documentation 中文整句锁定。
- `python -B tests/validate_release_coherence.py --version 0.8.0 --phase candidate`：pass，0 failures，4 advisory warnings。
- `using-sacha`、`planner`、`executor`、`manager`、`clarify` official quick validator：全部通过。
- official plugin validator：通过。
- Setup Agents：13/13 passed；既有幂等测试同时核对两个实际 TOML 的 execution/research readiness 接受边界。
- 本次真实使用了一个 Sol/xhigh Planner 与两个隔离的 Luna/max 实施 subagent；这证明当前宿主可调用这些 route，不证明插件安装后的自动路由行为。
- 独立 Sol/xhigh Reviewer 的 R8 找到 Evolution 旧 Manager owner 与 Documentation 文案测试两项阻塞；修复后的 R9 source/static re-review Accepted，0 blocking finding。
- R9 后按 Human 要求进一步把自动模型从多档 Sol/Terra/Luna 收敛为上述四种组合；本轮 route 4/4、完整 unit 22/22、candidate coherence 0 failure。该后续 delta 未冒充 R9 的独立 Review。
- Project AGENTS 新增唯一 owner、改动顺序、删除旧副本、Adapter-only 模型参数、测试和历史 superseded 纪律。Evolution `0.3.0` 表格/§4.20 与 2026-08-04 旧 Spec 入口已标明历史 Baseline、替代版本和当前 owner，保留事实但不再伪装现行规则。
- 依赖波次回环 delta 经独立 Sol/xhigh Reviewer 复核为 `Accepted`、0 blocking finding：串行结论只约束当前波次，结果回到同一 Task/Scope revision 后重算；该裁决只覆盖 source/static，不证明真实两波 Runtime 派发。
- 最终 release Reviewer 的 R10 发现 Clarify research 与 Luna named definition 接受条件冲突；修复模板和 active-consumer 测试后，R11 scoped re-review 为 `Accepted（source/static Scope）`、0 blocking finding。
- 候选安装后的 fresh Feedback dry-run 发现 Adapter 在语义压缩时遗漏 Feedback task 查询/创建/等待映射，并使 repair target 是否还能再次 migration 产生 return consumer 冲突。现已恢复独立 Feedback transport，并以“存在上游 return consumer 时不得迁移”关闭双 owner/丢 return 分支；等待 R13 scoped re-review。
- R13 独立 Sol/xhigh scoped re-review 为 `Accepted（source/static Scope）`、0 blocking finding；targeted 3/3、完整 unit 22/22、Project Setup 45/45、candidate coherence 0 failure/4 advisory、Feedback quick validator、plugin validator 与 scoped `cprobe` 均通过。

## 剩余边界

- source/static 只证明 owner、结构、参数和禁止分支已表达；候选安装、cache parity 与 fresh dry-run 已产生独立证据，但尚未验证真实 context/compaction signal、Codex `create_thread`/`wait_threads` 去重与 owner transfer、实际自动模型选择、fallback、wait/cancel 或 migrated target 的完整 Execute→Review→closeout。
- 字符/行数 advisory 当前仍报告 Workflow、Coordination、Direct active surface 与 README 超建议值；不会限制迭代或改变退出码。
- 未修改 `E:\cpTools`、`G:\COD` 或 Marketplace。已创建 source candidate commit并安装过候选 `0.8.0`；本次 Feedback 修复后的最终提交、重装、tag、push 与 release coherence 尚待完成。
