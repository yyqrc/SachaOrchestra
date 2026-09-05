# 第三阶段：Sacha 安装后运行流程精简

> 状态：已完成；2026-09-06 按批准范围实施与验证，见 [实施记录](execution-report.md)。
> 日期：2026-09-06。本文以当前源码为修改对象；本轮规划使用已安装 0.14.2，二者不等同。

## 目标

以 GPT-6 Astra 为主要使用对象，使入口、探索、批准、执行、独立评审和完成记录能够在已有授权内连续推进。删除没有独立保护作用的固定前奏、重复展示和过宽冲突检查，保留授权、来源独立、原像复查、失败补偿、持久格式兼容与证据边界。

可观察结果：成熟方案可直接检查前提和反例；可完成的补证先由当前执行者处理；批准实施后无需再单独要求收口 Spec；无变化的 AGENTS 不再要求一个不会用于替换它的 Hash；模板目录中的无关合法变化不再阻断选中模板的写入。

## 范围

具体正文与脚本提案见 [proposed.patch](proposed.patch)。补丁基于当前工作区原文生成，只供审查，未应用。拟修改 14 个现有文件；实施时另在两个现有测试文件补充行为用例，不新增测试体系。

| 负责位置（相对仓库根） | 本次差异 |
| --- | --- |
| plugins/sacha-orchestra/core/intake-contract.md | 补齐已有 Roadmap 调用 Explore 的入口描述 |
| plugins/sacha-orchestra/skills/explore/SKILL.md | 按实际缺口选择起始工作意图，取消固定 brainstorm/research 前奏 |
| plugins/sacha-orchestra/core/human-interaction-contract.md | 文件数、行数和重复编号摘要按审查价值提供 |
| plugins/sacha-orchestra/core/artifact-protocol.md | 按用途区分项目来源与当前任务编排信息；消费实施批准中的 Spec 状态写入授权 |
| plugins/sacha-orchestra/skills/planner/SKILL.md | 同步 Spec 来源筛选 |
| plugins/sacha-orchestra/skills/executor/SKILL.md | 区分 Spec 的目标产品行为与当前任务的路由和授权 |
| plugins/sacha-orchestra/core/workflow-contract.md | 明确先完成可完成的补证；迁移不强制 Review；正常完成时收口 Spec；明确文档确认的消费条件 |
| plugins/sacha-orchestra/skills/closeout/SKILL.md | 保留显式入口，消费已有状态收口和具体文档写入授权 |
| plugins/sacha-orchestra/skills/document-project/SKILL.md | 对已覆盖的同一次具体写入不重复提问；同步模板冲突范围 |
| plugins/sacha-orchestra/core/assurance-contract.md | 新基线重新形成裁决时复用有效检查；阻塞标准对应本次交付 |
| plugins/sacha-orchestra/core/coordination-contract.md | 研究服务当前决定和实际消费者；父任务核对关键原始证据，避免重走完整调查 |
| PLUGIN_DESIGN.md | 同步正常实施后收口 Spec 的路线及补证说明 |
| plugins/sacha-orchestra/skills/setup-project/scripts/generate_project_integration.py | 临时文件原字节比较；仅真正改写已有 AGENTS 时强制要求 expected_agents_sha256 |
| plugins/sacha-orchestra/skills/document-project/scripts/generate_project_document.py | 比较选中 Profile、生成策略与模板指纹，替代整个 manifest 的指纹比较 |
| tests/test_setup_project.py、tests/test_document_project.py | 在既有测试入口补充下述验收，不以文字匹配证明规则语义 |

不改阶段一、二的已确认决定，不修改部署身份、模型路由、其他适配器、技能元数据、安装缓存或 DSH 配套包；不提交、推送、发版或安装。不增加节点种类、状态机、Hash 回执、跨会话注册表或全组合场景。既有角色和术语名称保留。源码已取消的固定三遍回读和固定两个代理要求不重做。

## 项目事实与技术决定

- 当前发布插件目录的 cprobe 摘要为 complete=true、无跟踪或未跟踪变化、无冲突、whitespace.errors=0。阶段二仍有未提交工作，本次补丁对 PLUGIN_DESIGN.md 使用其当前内容作原文，不覆盖阶段二。
- [入口合同](../../../../plugins/sacha-orchestra/core/intake-contract.md) 第 3 节未列 Roadmap→Explore，但同文件显式 Roadmap 授权、[工作流合同](../../../../plugins/sacha-orchestra/core/workflow-contract.md)及[顶层设计](../../../../PLUGIN_DESIGN.md)已有该路线。本次只补齐描述，不赋予新的入口授权。
- [Explore](../../../../plugins/sacha-orchestra/skills/explore/SKILL.md) 已定义可组合的 brainstorm/research/grill，却要求显式讨论先用前两种。本次允许按当前缺口选择；事实不足仍先调查，真正的用户决定仍须收口。
- 用户已明确选择：实施批准同时覆盖满足完成条件后原位完成本次 Spec；项目文档继续按原有策略授权。该决定仅确定本提案的行为，未批准产品实施。
- [工作记录协议](../../../../plugins/sacha-orchestra/core/artifact-protocol.md) 允许项目源码定义事实，同时绝对排除 Sacha Core/Skill/Adapter。目标项目正是 Sacha 时两者冲突。本次按用途区分：产品规范可以作为项目来源，当前这次编排的状态和命令不能伪装成项目需求。
- [Executor](../../../../plugins/sacha-orchestra/skills/executor/SKILL.md) 已负责验证和同范围补证；无需新增补证节点。关键缺口有争议、证据冲突、补证安全路径耗尽而需正式裁决，或其他 Reviewer Gate 事实存在时，仍执行独立评审。
- setup-project 在计算 agents_action 前要求已有 AGENTS 的 expected 值；但只有 action 非 unchanged 才加入写目标。document-project 的 manifest_sha256 来自完整 profiles.json，两次解析间任何字节变化都会冲突。以上为源码推演，未运行复现。
- [用量报告](../usage-report.md)指出提前调查后续阶段、后期携带长历史和评审重复调查的成本。该报告是固定截止点的累计请求用量，不是订阅账单，没有 A/B 节省比例；本轮不重新统计，也不把报告中的 Token 数作为运行时阈值。

## 实施方案

1. 先更新 PLUGIN_DESIGN.md 中正常完成后的 Spec 收口路线，再更新 Workflow、Artifact、交互及验收合同，最后同步直接技能使用方。其余职责内调整直接写入相应负责文件。
2. 正常实施、适用评审及项目文档候选处理结束，本次全部阻塞验收已满足并进入 goal_complete 后，消费实施批准中的状态收口授权，按既有局部编辑机制只修改本次唯一已批准 Spec 的状态行；无 Spec 或用户要求保留状态时跳过。显式 closeout 继续可用。阻塞性文档未完成时不提前收口；非阻塞文档失败不阻止满足完成条件后的状态写入。状态编辑失败如实报告，保留实现完成证据，不生成替代 Spec。
3. 文档仍按 Project Integration 策略和具体写入授权执行。用户只说“存档”而目标、正文或写入范围尚未明确时，仍需获得具体确认；同一次具体写入已经明确获批时不再因 per-write-confirmation 参数名追加一次提问。组合动作保留双动作预检、先 Spec 后文档，以及文档失败不回滚合法 Spec 状态的顺序。
4. Review 前由现有 Executor 完成可完成且无争议的必需验证；其他 Gate 事实仍成立时，不以补证代替独立 Review。基线变化后旧裁决不能当作当前通过，但未失效的检查与原始证据可复用；复核新增差异、直接影响与失效证据。Accepted 等结果按本次交付的阻塞检查判定，不将源码交付自动扩大成发布验收。
5. setup-project 的 _prepare_temp 只把双 SHA 比较改成 bytes 比较，保留写入、flush、fsync、读回和异常清理。将“existing + write + expected 缺失”的检查移入 agents_action 非 unchanged 分支；调用方显式提供的 expected 值仍作为断言，过期时继续拒绝，哪怕本轮 AGENTS 不变。其余目标与计划确认不变。
6. document-project 两次解析之间保留所选 manifest_profile 的完整结构化值，并比较该值、generation_policy 及选中模板 SHA-256。内部 manifest_sha256 不再使用；公开生成文档 sha256、输入 expected_target_sha256 和所有目标原像检查不变。继续二次完整校验目录，因而无关 Profile 的合法变化可继续，但目录变为非法、重复身份或引用文件缺失仍拒绝。该检查只覆盖同一次调用的验证到写入阶段，不声称独立 dry-run 与 write 调用共享快照。
7. 在两个现有测试文件中补充有明确输入、返回值和文件副作用断言的用例；不新增生产包装、字段版本或配置开关。测试具体组织沿用现有夹具，补丁不预先冻结测试代码行数。
8. 在 Coordination 的既有 research-ready 判断中补充当前决定和直接消费者；沿用现有问题、范围、证据、停止条件和精简返回，不复制到其他合同。父任务按关键原始证据确认结论，只有冲突或直接依赖会改变结论时扩大；未来阶段没有当前依赖的研究只留候选引用。
9. 迁移保留当前术语定义、Spec 审阅推荐顺序、明确创建授权及最小 Handoff。首次具备既有推荐条件时及时交付，不继续无关调查以积累更长历史；已明确在当前任务继续的选择不重问。不扩展到 Spec 前迁移，不按固定 Token 阈值或阶段自动创建任务。

本次追加的 Token 优化中，增量评审已由第 4 项覆盖；Codex Adapter 当前已有 fork_turns="none"、自包含消息，以及按难度、有效上下文和失败影响选档，本次不改动或复制。源码定义不代表所有旧任务均已落实，也不因单个 Luna/max 研究用量高而普遍降档。全局 AGENTS.md 与 features.context_management.experimental_mode 配置由来源任务负责，不属于本提案。统计继续留在已有开发诊断，不新增预算表、用量 Gate、监控流程或统计脚本。

## 验收标准

| 验证范围 | 必须观察到的结果 |
| --- | --- |
| 入口与探索静态语义 | Roadmap 仍不接受 Sacha；Explore 返回原调用节点；成熟方案可直接 grill，事实未知时仍调查，关键决定不足不得冻结 Spec |
| Spec 来源静态语义 | 修改 Sacha 自身产品规则时可引用对应合同；普通项目的 Spec 仍不能被本次编排角色、路由或自报替代项目事实 |
| 收口静态语义与直接消费者 | 普通/迁移实施批准均覆盖唯一 Spec 完成状态；必需证据不足、未批准、状态不唯一、用户要求保留状态时不改；阻塞性文档未完成不改，非阻塞文档失败而其余完成条件满足时可收口；项目文档的原有确认策略保留 |
| Review 静态语义 | 无争议可完成补证不先做空转评审；高风险、冲突及用户明确要求仍有独立裁决；新基线复用检查不等于复用旧最终通过结论 |
| 研究与迁移静态语义 | 后续阶段研究没有当前决定消费者时不展开，有直接依赖时可调查；父任务核对关键原始证据，无冲突、无直接依赖缺失且影响明确时不重走完整研究；存在冲突、直接依赖缺失或影响不明时才扩大到最窄相关调查。首次具备既有 Spec 审阅推荐条件即交付；已明确选择当前任务且事实未变时不重问。不新增 Spec 前迁移、固定阈值或自动新任务 |
| setup-project 真实入口测试 | 已有 AGENTS unchanged 且未传 expected：纯 no_changes、仅其他目标变化均可按原计划授权完成；已有 AGENTS 真变化缺 expected 或显式 stale expected 拒绝且无文件写入 |
| setup-project 临时文件与事务 | 原字节相同返回临时文件；不一致或读回异常清理本次临时文件；既有多目标失败补偿与并发原像保护仍通过 |
| document-project 两次解析间变化 | 合法无关 Profile/JSON 排版变化继续；选中 Profile、generation_policy 或模板字节变化拒绝；覆盖 Roadmap 和一般发布文档两条比较分支，检查返回 transaction 与目标原像未变 |
| document-project 兼容与原子写入 | 内置模板无 catalog 时保持可用；无效 catalog 仍拒绝；旧 SOURCE SHA-256 兼容读取、公开输出 sha256、目标并发修改与失败恢复用例保持通过 |
| 有界差异 | cprobe 完整且 whitespace.errors=0；提案原文仍匹配，阶段二及无关工作保留；纯正文不运行结构校验器 |

实施后运行两个生成器对应的现有测试入口：`python -B -m unittest tests.test_setup_project tests.test_document_project`，读取实际退出状态、失败和跳过项。测试只在既有隔离临时目录产生文件，不能修改真实项目接入配置。

授权含义与正常收口路线的变化应有一次隔离真实行为验证：提供已批准的模拟项目 Spec 和真实完成/未完成证据，观察正常收口、证据不足不写、已有具体文档确认不重问、阻塞性项目文档未完成时不写 Spec 状态，以及非阻塞项目文档失败而其余完成条件满足时仍可收口。使用现有场景机制和原始轨迹，复用有效证据，不扩成角色/型号组合矩阵。需要新用户任务、安装或外部操作才能获得该证据时，先明确该具体动作再取得授权；未取得时只交付源码与本地测试证据，不声称安装后行为已验证。

## 失败保护与回退

- 不因 GPT-6 Astra 能力降低授权、唯一写入者、独立 Reviewer 或原始证据要求。既有接受与批准直接消费；发生实质范围、授权或验收变化时只暂停依赖该决定的部分。
- 保留 setup-project 的计划确认、批量及临近替换原像复查、写后校验、只在目标仍是本次产物时补偿恢复。保留旧 SOURCE SHA-256 标记的兼容解析，不新增该旧格式的写方。
- 保留 document-project 的路径包含、mode、模板合法性、目标原像、原子提交及写后失败恢复；不把无关 Profile 变化容忍扩大为忽略非法目录。
- 拟议差异与当前原文不匹配时只重新核对相关变动，不覆盖阶段二或他人内容。需要回退时只撤回本阶段具体差异；不 reset、stash 或清理无关内容。
- Spec 不是批准证据。实施批准前只维护本任务的提案与决定记录，不写产品目标文件。

## 风险与未验证项

本轮只证明当前源码关系及提案可解析性；没有运行生产脚本、测试或安装后场景，未声明候选已经复现。Hash 的变化会改变冲突拒绝条件，自动 Spec 收口会改变批准含义，均作为本次明确行为调整审查。

现有入口接受/拒绝、显式迁移选择、Manager 协调、探索决定记录与恢复载体继续保留；没有证据证明它们可整体删除。无可靠迁移信号时是否展示迁移选项不在本次提案中调整。固定三遍回读、代理数量与模型路由已由当前源码处理，不把安装缓存差异当作本轮源码缺陷。
