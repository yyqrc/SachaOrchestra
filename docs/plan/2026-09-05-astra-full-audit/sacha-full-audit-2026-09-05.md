> 接手来源：Work 会话“核查Astra与仓库适配”（2026-09-05）。本文件从该会话已读取的报告预览恢复为 Markdown，保留正文、链接、表格和附录；不是原附件的字节副本。原报告的建议、验证与未验证声明保持其原有证据范围，接手校正另见同目录 decisions.md。
> 原会话：https://chatgpt.com/c/6a9b2e1a-2b28-83e9-807d-ea43f354e2a8

# SachaOrchestra 全仓评估与 Astra 适配建议

评估日期：2026-09-05（UTC）对象：yyqrc/SachaOrchestra，main，2054b78770fd25562677a28f52ca99bf0416689b，源码版本 0.14.2。性质：全仓规则和实现评估；未修改、提交、发布仓库代码，也未修改用户宿主配置。报告中的改动是建议，不能当成已完成修复或已获批准的新产品合同。

## 1. 总体判断

仓库有可保留的清晰骨架：Direct 为默认路线；Core 分别拥有入口、流程、交互、证据、协调、工作记录和术语；Skill 实现角色职责；Adapter 负责宿主调用；DSH Companion 独立构建。升级 Astra 不需要推翻这套分工。 真正需要处理的是四类问题：实际宿主接口与适配器假设不一致；已经可以复现的脚本缺陷；把必要检查写成固定操作次数或强制派发；同一规则在设计、合同、技能、场景之间发生漂移。Astra 路由只是其中一个专题。 建议先修正确性和接口，再统一规则与减少无效步骤，随后接入 Astra 并比较任务结果。不能用更强模型替代并发保护，也不能用更长上下文证明更多历史、更多代理或更多测试都有收益。

## 2. Astra 消息核实

以下区分 Codex/ChatGPT 订阅或积分计费与 Codex 使用 API Key；两者不能合并成一句“Codex 不加价”。公开资料核对截至本报告日期。

| 原消息 | 结论 | 依据与限制 |
| --- | --- | --- |
| Astra 在 Codex 可用 | 已确认 | 官方模型指南列出 gpt-6-astra 的 Codex 使用方式。见[Codex 模型指南](https://learn.chatgpt.com/docs/models)。 |
| 输入超过 272K，Codex 不收额外长上下文倍率 | 订阅/积分模式未取得明确豁免声明；不能作为所有 Codex 模式的事实 | 公开 Codex 价目表未单列长上下文档位；但 API Key 模式明确按 API 价格。见[Codex 定价](https://learn.chatgpt.com/docs/pricing)。 |
| Codex 不收缓存写入费用 | 订阅/积分表未单列该项，不等于已明确承诺豁免 | API 模型页单列缓存写入收费。不能将订阅表的缺列推广到 API Key。见[API 模型页](https://developers.openai.com/api/docs/models/gpt-6-astra)。 |
| Codex 上下文上限为 872,000 | 未确认 | 官方 API 页列出 1,050,000 上下文和 128,000 最大输出；这些数字不能直接替代 Codex 客户端有效窗口，也不能反推 872,000。 |
| 自动压缩固定为 90% | 未确认，不能视为通用默认 | model_auto_compact_token_limit 未设置时使用模型默认；另有计数范围配置。见[配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)。 |
| 872,000 × 90% = 784,800 | 算术正确，运行时前提未证实 | 只成立于窗口和比例都确实如此的特定环境。 |

API 页明确规定：超过 272K 输入的请求，整次请求输入与缓存价格按 2 倍、输出按 1.5 倍计算；标准 API 单价为每百万 token 输入 $10、缓存输入 $1、缓存写入 $12.50、输出 $50。因此，如果原消息也包括 API Key 模式，它不成立。[API 模型与价格](https://developers.openai.com/api/docs/models/gpt-6-astra)Codex 积分表中 Astra 标准输入/缓存输入/输出为每百万 token 250/25/1250 credits，Sol 为 100/10/500，Luna 为 5/0.5/30。按同样 token 数计算，Astra 的输入与输出消耗均为 Sol 的 2.5 倍；实际任务成本还取决于推理、返工和上下文使用。Astra Fast 的 2.5 倍是独立的速度倍率，不能混作长上下文规则。[Codex 定价](https://learn.chatgpt.com/docs/pricing)本次本地模型缓存并非用户桌面的实时模型目录，也没有给出 Astra 的有效窗口证明。后续确认 872,000，应绑定具体客户端版本、登录/计费模式、该会话实际模型元数据和配置；无需读取凭据或整个配置目录。仓库目前不应增加 872000、784800 或“90% 固定压缩”的默认值。

## 3. 评估范围和证据等级

清单包含全部 288 个 Git 跟踪文件。当前规则全文审查覆盖：根部治理文档、7 份 Core、12 个产品 Skill 及元数据、4 份 Runtime Adapter、4 个开发 Skill 及引用规则；生产脚本、配置生成器、Codex JS asset 和 DSH 服务端/客户端/构建配置均纳入源码审查。22 个运行场景包的任务与裁决规则已核对，其中 21 个属于当前场景，codex-code-mode-v1-batch 已明确为历史场景。 “全仓评估”不等于所有文件都执行过，也不等于图片逐像素审查：历史记录核对身份和取代关系，并详读与当前机制相关的记录；测试核对结构、调用链和关键断言，执行可用套件；图片按资源用途和引用核对。未将未跑的场景、PowerShell 或宿主功能写成通过。附录提供逐文件清单及阅读/验证层级。 证据标签：复现＝在隔离临时目录或纯函数输入上观察到结果；源码＝由当前控制流/规范直接得出；宿主对照＝与本会话实际工具 schema 比较；建议＝产品取舍，仍需要按目标场景评估。 优先级：P1 是建议先处理的正确性、兼容性或误导风险；P2 是效率、维护性、较窄场景问题；P3 是低风险清理。这里的 P1 不表示已在用户生产环境造成事故。

## 4. 逐项发现

### F01 · P1 · Codex Adapter 假定的创建字段不适用于当前 Work 界面

证据：adapters/codex/runtime-adapter.md 第 156、184 行要求组合 agent_type/model/reasoning_effort，并断言当前 v2 具备三个字段。本会话 collaboration.spawn_agent 有 task_name/message/fork_turns/model/reasoning_effort，没有 agent_type。因此“发现 v2”不足以证明该组合成立。宿主对照。建议：按实际字段与能力映射；把角色能力、模型选择、上下文传输分开核对。支持自定义类型的宿主保留现有组合；没有该字段的宿主只能采用已证明满足角色边界的映射，否则准确标为该派发方式不支持。不要仅删除保护后改成通用代理。此项应先于 Astra 路由实施，否则增加型号后仍不能正确创建。

### F02 · P1 · setup-agents 批量写入会覆盖检查之后发生的并发修改

证据：setup_agents.py 先统一检查目标原像，再逐项 os.replace；第 483 行写入前没有逐文件再核对。使用已有 after_replace 测试钩子，在第一个文件替换后修改第二个目标，最终返回 status=ok, transaction=written，并发内容消失。隔离复现。建议：复用同仓 setup-project 中临近替换的原像检查思路；冲突时停止受影响写入，补偿只处理仍匹配本次写入的文件。补一个真实并发插入回归。单纯增加模型 gate 或先问一次用户均不能修复此缺陷。还应明确跨进程写入的保护边界，逐项复查只能缩小检查与替换之间的窗口，不能宣称有原子 CAS 保证。

### F03 · P1 · release.py 没有为现行 JS asset 选择已有回归测试

证据：scripts/release.py 第 239 行只把测试文件自身映射到 test_code_mode_batch_asset；第 263 行机械文件扩展名集合没有 .js。将唯一变更设为 adapters/codex/code-mode-batch.js，narrow_test_modules 返回空，验证命令只剩 release coherence。直接调用真实选择器复现。建议：把生产 asset 加到真实消费者测试映射，并核对 document-project 被消费的 Markdown 模板是否同样漏选。发布入口检查还应覆盖当前实际运行资源；不要把“兼容 Pi 文件存在”当成现行资产完整性的充分证明。这里需要检查选择器产生的命令，不需要用正则锁定 Markdown 说明文字，也不必改成每次全套测试。

### F04 · P2 · Project root 消歧错误合并大小写不同的 POSIX 路径

证据：resolve_provider_queries.py 第 258 行对所有候选路径无条件 casefold()。输入 /tmp/Project、/tmp/project 被合并成一个已解析根。复现。建议：按平台/文件系统身份处理路径比较，保留 Windows 的合理等价处理；POSIX 上不同目录应继续消歧。防止接入写入落到错误工程。这与模型升级无关。

### F05 · P2 · Skill description 的 YAML 读取不完整

证据：generate_project_integration.py 第 1101 行 _parse_skill_identity 使用逐行解析。合法 description: | 的多行描述被解析成字符串 |，后续描述匹配失真。复现。建议：用符合仓库依赖约束的 YAML 解析方式读取 front matter，校验类型和唯一身份；覆盖块标量、引号与注释等真实输入。不要让模型凭名称猜补错误 description。

### F06 · P2 · document-project 对部分只读预览提前要求写入确认

证据：项目采用 per-write-confirmation 时，system-guide 即使 write=False，仍会进入 _authorize 并拒绝；结果连 target/hash 都未返回。Roadmap 分支已有 if write 判断，行为不统一。隔离复现。建议：只读阶段生成候选、目标、差异和原像哈希；真正落盘时再要求已有授权满足写入条件。保留写入边界，取消为了看到可审查结果而先“确认写入”的循环。

### F07 · P2 · 文档词法禁用表误拒合法项目内容

证据：generate_project_document.py 的内部引用过滤使普通项目说明 The project stores implementation specifications in spec.md. 被拒绝。复现。建议：判断内容是否把私有运行资料当作项目产品依据，而不是见到 spec.md、某些目录或 UUID 形式就拒绝。Sacha 自身、工作流工具等项目需要合法讨论这些对象。路径越界保护仍在文件操作层执行；来源真实性和文档语境由语义审查负责。

### F08 · P2 · 文档生成链重复解析与模板承诺不一致

证据：两个生成器重复实现接入/模板目录读取；document-project 消费 required_topics/optional_sections 时与 setup-project 的结构校验深度不同。返回 required topics 不证明正文实际覆盖这些主题。旧结构化正文路线与 profile/rendered Markdown 路线并存。源码。建议：先统一同一合同的解析与报错，保留各 Skill 的职责；再按真实调用者判断旧正文路线能否退役。主题完整性留给文档检查，不新增假装理解正文的正则 gate。24K 字符、64KiB 等上限应说明实际消费者依据；不能因 Astra 窗口大就一起放大。

### F09 · P2 · Intake 的“先选择是否用 Sacha”会阻塞已授权的事实准备

证据：完整 Spec 入口和语义转向场景刻意要求用户先选择 Sacha，再继续流程。它保护不自动接管的边界，但对于“先核对事实、继续澄清并形成规格”这类明确请求，也会增加一次框架选择。规范与场景；建议。建议：保留“不推断用户接受额外流程”；允许在已有授权内继续只读准备。用户已明确选择本流程或同一目标持续推进时复用接受事实。只有是否采用 Sacha 会实质改变时间、任务创建或副作用时才提出选择。修改时必须同步 Intake、using-sacha、设计和两项入口场景，不能只删 Skill 中一句话。

### F10 · P2 · Planner 固定三遍回读可合并

证据：Planner 第 26–29 行规定三遍回读，任一失败重新执行三遍。检查目的分别是格式、来源和项目语境，目的合理，但次数不能证明质量。规范。建议：改为一次完整核对三个维度；修订后只重查被影响的维度和相关消费者。保留不让不自包含的 Spec 提交审批；去掉固定轮数和全量重启。

### F11 · P2 · Planner 到 Explore 的强制切换粒度过细

证据：Planner 第 16 行对冻结前未收口事项要求完整读取并调用 Explore。规范。建议：小型事实核对或一个可直接说明的选择可在当前 Planner 完成；需要持续探索、多候选调查或共同澄清时进入 Explore。保留 Explore 的共享对话、事实/未知项区分和只读边界。这属于节点边界取舍，应先改设计，不应以 Astra 能力强为由悄悄绕过现行流程。

### F12 · P2 · Manager 把“可以并行”写成“必须创建至少两个代理”

证据：Coordination 第 41 行要求至少两个就绪且隔离单元在首次等待前实际创建至少两个代理；第 19 行每单元固定九维评估；第 21 行多数实现工作默认具有上下文污染风险。规范。建议：保留输入自足、依赖、输出隔离、单写入者、完成检查和必要等待；派发还要有实际收益，可由父任务执行一个单元，也可直接完成少量机械步骤。九维应合并为任务相关的简短事实，不强制九项表单。长上下文降低部分隔离需求，但日志噪声和独立判断仍可能值得隔离。不得增加“超过某 token 数就迁移”的第二套生命周期。

### F13 · P1 · 失败影响检查应保留，但“持久数据”措辞应收窄

证据：Codex Adapter 第 140 行把持久数据列为至少 broad；第 142 行进一步限定破坏性覆盖、删除、跨消费者身份和生命周期。这两段约束强度容易被不同读取者理解为“任何文件写入都是 broad”。规范。建议：以第 142 行的实际后果作为判定依据，区分有界可重建输出与会破坏用户状态/身份/兼容性的写入。保留 broad/critical 判断，去掉泛化用词引起的自动升级。文件少、验收明确都不能自动豁免破坏性风险；文件多也不能单独触发高档模型。

### F14 · P1 · 路由缺 Astra，但应扩展现有路由而非替换整个模型池

证据：当前有序路由为 human_exact → sol_xhigh → sol_medium → luna_max → luna_xhigh，没有 Astra。源码与规范。建议：按第 6 节增加 Astra 用途；普通任务继续使用 Luna/Sol。模型名和强度只在 Codex Adapter 拥有，其他 Skill/Core 不复制表。Reviewer 独立性与模型强弱分开判断。精确指定模型不可被自动替换；已启动或状态不明的旧写入者不可因换模型重放。

### F15 · P1 · v2 取消映射没有足够终止语义

证据：Codex Adapter 第 54 行把 interrupt_agent 后等待描述为确认 terminal/cancelled。本会话 interrupt 的定义是中断当前 turn，代理仍可继续收消息；wait 返回通知不等于进程终止证明。宿主对照。建议：区分中断、暂停、代理完成、底层写入进程停止。接管写入前确认相关写入者确实停止；无法证明时只暂停有双写风险的部分，并说明准确缺口。不要将中断成功记录成完全取消，也不要用重复创建来探测。

### F16 · P2 · Skill 的唯一身份合理，绝对本地文件限制过窄

证据：Codex Adapter 第 170–171 行仅接受绝对 SKILL.md path，并要求父子均完整读取。本 Work 界面的 Skill 可由 skill:// 和 provider 读取。宿主对照。建议：保留唯一 canonical 身份、版本/内容来源、权限和依赖核对；允许宿主原生资源标识及其读取方式。父任务读取足以判定工作边界的规范，子任务读取其执行所需的原文；不要传全目录或无关 Skill。Researcher 关闭 Shell 后能否读取所需文件应单独验证，不能仅凭 TOML 自称可用。

### F17 · P2 · Human Interaction 对方案阶段要求过早的逐文件统计

证据：Human Interaction 第 17 行在用户判断修复、方案、调整前要求文件数量、逐文件规则/代码块和可确定行数。规范。建议：方案阶段说明行为、范围、代价和需要决定的事项；具体补丁阶段再给实际文件和差异。未形成补丁时不制造精确行数。保留中文表达、先说明再提问、持续承接纠正、稳定编号和“是否需要回应”；只披露影响当前判断的限制。

### F18 · P2 · 术语存在双重全文维护成本

证据：根规则要求每项事实唯一负责，同时要求 docs/CONTEXT.md 完整镜像共享术语且强双向同步。规范。建议：共享术语由插件内合同唯一维护，开发侧保留链接与开发专用解释；只有实际离线消费者需要全文时才考虑自动投影。保留 Scope、Owner、Baseline、Outcome、授权等确实影响判断的概念；删除纯粹限制措辞的重复约束，不为宿主既有词另造概念。

### F19 · P2 · 根 AGENTS 与设计、开发 Skill 重复承担细节

证据：根规则已约 29KB，包含大量修改顺序、文档身份、同步、角色边界和验证细则；其中“调用新的负责文件”也被列为必须先走顶层设计变化。规范。建议：根部保留项目事实、唯一负责入口、关键授权边界与验证选择；操作过程交给现有开发 Skill。把“读取一个新来源”与“接管该来源的职责/增加产品路线”分开。普通职责内修复无需因多读一个文件增加设计 gate。不要通过新建更多治理文件来做精简。

### F20 · P2 · 验证要求在顶层与具体合同之间漂移

证据：PLUGIN_DESIGN.md 第 209 行按字面要求顶层变更后运行真实场景；根 AGENTS 则明确以行为证明需求等触发条件选择运行验证。设计中 Reviewer “重跑关键验证”也应与 Assurance 的“重跑能改变裁决的检查”统一。规范。建议：统一为按变更及所声称的证据层触发；源码/说明修复不强制所有宿主回归。Baseline 变化使旧裁决不再直接有效，但未受影响的原始证据仍可复用；针对变化给出新裁决，不默认全部重跑。

### F21 · P2 · 场景应避免长期绑定旧路由和强制成本

证据：当前场景中模型路由、Skill 加载和两个小输出的并行场景包含 Luna/Sol 或实际派发数量断言。它们对现行合同有效，但会阻止改变该合同。任务、oracle 与 verifier 核对。建议：一般场景验证用户结果、授权、依赖、单写入者、证据真实性；专门路由场景才绑定当期映射。F12 若获采纳，应修改隔离场景的成本假设。增加真实工作流项目可以合法描述自身 Spec 的语境案例。历史 codex-code-mode-v1-batch 已注明被取代，应保留历史身份，不能误报为当前批量代理规则。

### F22 · P2 · Pi 兼容资产可以退出主维护路线

证据：顶层设计明确 pi_once.ps1/pi_guard.mjs 未接入当前 Skill/Adapter，但仍随插件存在、保留配置处理和测试。源码引用与设计。建议：不要为 Astra 改造这条非活跃路线。先确认真实消费者，再决定保留兼容读取、停止发布执行资产或正式退役。删除应同时处理生成器 Pi 段、探测脚本、对应测试与 release coherence；不能只删两份脚本留下悬空入口。

### F23 · P2 · DSH 工具目录截断和任务分类限制需修正

证据：tool-surface-policy 使用 256 项快照上限；合并只加入新名称，既有名称的元数据不更新。基础 profile 从首条 Human 消息恢复。questionOnly 将结尾感叹号也纳入疑问判断，可能使“请修复……”类中文感叹句停在 inspect。源码；实际宿主行为未复验。建议：保持默认较小工具面，但截断后仍有按名称查询/获取的恢复办法；目录刷新应反映更新和移除。覆盖中文动作请求与否定约束；明确同一目标后续 steering 和显式 control 的优先级。工具隐藏是能力面策略，不拥有用户授权；不得让分类结果自行放宽权限。

### F24 · P2 · DSH 三层防护有具体原因；发布 README 混入历史授权

证据：DSH 实现包含 schema restriction、guidance、执行 guard，历史修复针对 rc.2 的同 scope 继承绕行；README 第 137 行仍称“当前任务只授权迁移 web Profile”。源码与历史。建议：保留仍对应真实宿主缺陷的防护和单层 child 约束，不因文件超过千行就删除。把职责拆为可验证的内部模块即可，不增加另一套授权状态机。将特定历史任务授权移回历史记录；它既不应限制所有以后安装，也不能授权当前安装。

### F25 · P2 · DSH 长会话的状态新鲜度和轮询成本有问题

证据：activity-monitor 只要历史曾有事件或 child，就持续采用 1 秒热轮询；服务端反复折叠事件。网络失败保留旧 snapshot。纯函数复现：先记录旧候选 accepted，再进入新一轮 Executor，折叠结果同时保留旧 accepted，未标记其适用候选。源码与纯函数复现；未实测宿主 UI。建议：以活跃状态决定热轮询，空闲/不可见时退避；按已有事件序号增量处理。为 Review/Evidence 明确现有 Scope/revision 的适用性，新候选不能让旧通过结果呈现为当前通过；不必因此发明跨会话全局注册表。旧快照可展示，但要有新鲜度或历史身份。

### F26 · P3 · DSH UI 有可清理的孤立实现

证据：panel geometry 的移动/缩放函数主要由测试消费，当前组件缺少相应交互调用；部分样式未见当前引用。静态引用审查。建议：若没有承诺拖动/缩放，删除孤立实现和镜像测试；若属于现有用户功能，则接入实际 UI 并验证操作。不要仅因有纯函数测试就认为界面具备该功能。尺寸样式差异作为视觉验证候选，本次未宣称实际布局破损。

### F27 · P2 · Claude/Cursor 的宿主假设与预算不应混入通用合同

证据：Claude 路线较多依赖宿主默认值，不能从文字直接证明有效模型/能力。Cursor Adapter 内嵌固定月预算和型号/付费档位。源码；未查证这些宿主当前价格或运行行为。建议：预算归用户/项目配置，模型可用性由该宿主当期目录确认；Adapter 保留参数、失败与证据映射。Astra 是本次 Codex 适配主题，不应顺手改写其他模型生态。跨宿主源码一致性可以检查，未安装宿主无需阻塞 Codex 源码修复。

### F28 · P2 · 少数历史计划仍像现行操作指南

证据：8 月 28 日的 capability follow-up/DSH design 保留进行中语气和被后续实现取代的路径、角色或 sandbox 描述；8 月 29 日已有后续规范与报告。另一些更早历史文件已经正确注明被取代。历史身份核对。建议：只给仍会误导的记录加最短“已取代”和现行入口；不改写全部历史，也不把历史运行成功、失败或机器路径当成今天的宿主状态。

### F29 · P2 · 跨平台验证基线需要修正

证据：当前 Linux 上运行 117 项 Python 测试，报告 4 处失败，涉及 Windows 分隔符以及 drive/share root 错误消息。拒绝 foreign path 不等于允许越界，其中两项 subtest 是拒绝原因预期不同。实际测试。建议：区分原生路径合同和异平台输入，按平台构造预期；保留拒绝不安全路径的断言。DSH 独立 package 的版本断言应验证声明的一致性，避免固定 0.1.0 阻止正常升级。不要为清除失败而删掉路径检查。

## 5. 全部规则、入口和脚本的处置矩阵

下列路径相对仓库根；产品 Skill/Core/Adapter 简写均位于 plugins/sacha-orchestra/。保留表示当前职责有必要，不表示所有细节均已由宿主验证。

| 编号 | 当前负责文件/入口 | 保留内容 | 建议处置 |
| --- | --- | --- | --- |
| R01 | 根 AGENTS.md | Direct、语义 Scope、同范围修复、按改动验证 | 收拢重复过程；限定真正需要设计决定的变化，F19/F20 |
| R02 | PLUGIN_DESIGN.md | 职责和流程唯一设计、发布边界 | 同步拟改变的入口/协调；去掉无条件运行场景措辞，F09–F12/F20 |
| R03 | docs/AGENTS.md | 开发/发布/历史身份区分 | 保留；全仓评估可审历史，普通任务不默认遍历 |
| R04 | docs/CONTEXT.md | 开发专用术语与导航 | 移除人工维护共享术语全文镜像，F18 |
| R05 | EVOLUTION.md | 成熟度、版本、破坏性边界与未实施方向 | 保留；只在本次真正改变其职责时更新 |
| R06 | 根 README、插件 README | 各自导航与最小使用入口 | 保持短；不复制自动型号表或完整流程 |
| R07 | core/intake-contract.md | 接受/拒绝、抑制重复、授权延续 | 允许已授权只读准备；避免重复框架确认，F09 |
| R08 | core/workflow-contract.md | 同一生命周期、Gate、返修与结束 | Planner/Explore/Manager 触发收窄；不新增 Astra 专用生命周期 |
| R09 | core/coordination-contract.md | DAG、就绪、单写入者、去重、必要等待、Owner 转移 | 删除固定至少两代理和九维表单负担，F12；保留停止旧写入者 |
| R10 | core/assurance-contract.md | 独立来源、原始证据、Baseline、分级裁决 | 增量复核；无具体裁决收益不重跑；不把模型型号当独立性 |
| R11 | core/artifact-protocol.md | 按消费者生成 Spec/决定/Handoff、最小恢复记录 | 保留；长上下文下仍按恢复需要记录，不按传闻 token 数迁移 |
| R12 | core/human-interaction-contract.md | 中文、先说明后提问、用户纠正延续、稳定编号 | 按决策阶段提供粒度，删除早期精确行数负担，F17 |
| R13 | core/terminology-contract.md | Scope、Owner、授权、证据、root/path 等必要区分 | 单源维护，精简只约束措辞的内容，F18 |
| R14 | skills/using-sacha | 唯一自动入口、受控接管 | 与 Intake 同步 F09，元数据继续抑制其他 Skill 自动触发 |
| R15 | skills/explore | 共同澄清、只读事实、冲突/未知项、交回决定 | 保留核心；小事实核对不强制正式切换，F11 |
| R16 | skills/planner | 形成自包含可实施 Spec、冻结关键决定 | 三遍改一次多维检查，按影响重查，F10/F11 |
| R17 | skills/executor | 在当前 Scope 内完成、验证、返修、交付 | 保留；职责内修复直接继续，不把所有实施委派出去 |
| R18 | skills/manager | 同一 Owner 持续推进依赖闭环 | 是否派发按收益判断，保留屏障和聚合，F12 |
| R19 | skills/reviewer | 独立裁决、正式入口到消费者语义链 | 保留；关键 Review 可用 Astra，普通可用 Sol，F14/F20 |
| R20 | skills/roadmap | 分阶段长期规划、只创建已授权文档 | 保留；生成 Roadmap 不自动创建/批准实施；短期 task 不强制 Roadmap |
| R21 | skills/document-project | 按长期消费者与实际产品变化生成文档 | 修复预览授权和语境误拒；统一模板解析，F06–F08 |
| R22 | skills/closeout | 合法 goal_complete 后原位标记唯一 Spec | 保留；不额外造 docs/done 或文档归档副作用 |
| R23 | skills/feedback | 具名目标的有界调查、唯一任务路由、Owner 交接 | 保留去重和交接后来源结束；来源调用不授权目标任意写入 |
| R24 | skills/setup-project | 项目接入归项目、计划差异、确认与有限写入 | 修复解析/根选择，收拢重复格式代码，F04/F05/F08 |
| R25 | skills/setup-agents | 显式配置操作、只管理 Sacha 文件、原像和补偿 | 修复并发覆盖，F02；安装/配置不证明实际发现 |
| R26 | 12 份产品 openai.yaml | 入口可见性与显式 Skill 调用边界 | 保留当前产品区分；只随入口语义变更同步，不注入型号表 |
| R27 | Codex runtime-adapter.md | 模型、调用参数、能力、失败与证据的宿主归属 | 先接口和取消，再 Astra 和 Skill 资源读取，F01/F13–F16 |
| R28 | Codex code-mode-batch.js | 原始逐项结果、独立只读批处理与投影 | 保留；补发布测试映射 F03；不恢复旧代理批量传输 |
| R29 | Claude Code Adapter | 本宿主调用与能力边界 | 显式说明默认继承和未证明项，F27 |
| R30 | Cursor Adapter | 本宿主参数与可用路线 | 预算从静态规则移到用户配置，F27 |
| R31 | DSH Adapter | continuable child、Role/能力映射与证据层 | 保留；只在声称实际行为时验证对应宿主 |
| R32 | 5 份 setup-agents TOML | Research/Execution/Review 能力及兼容 agent 定义 | 自动路由不靠把每份 TOML 默认都改 Astra；宿主真实工具面需另证 |
| R33 | setup_agents.py | 管理范围、dry-run、差异、补偿 | F02 优先修复；共享事务抽象有第二个明确消费者才提取 |
| R34 | generate_project_integration.py | 接入合同与真实写入计划 | F05/F08；保留已存在的原像复查和按配置授权 |
| R35 | resolve_provider_queries.py | provider 候选排序与工程根消歧 | F04；歧义继续返回歧义，不让模型猜写入根 |
| R36 | generate_project_document.py | 模板/路径/原像与文档目标管理 | F06–F08；语义与机械校验各负责实际能证明的内容 |
| R37 | 文档 JSON/Markdown assets | 项目语境与最小文档骨架 | 按直接消费者保留；模板变更选中真实生成测试 F03 |
| R38 | inspect_pi_models.ps1 | 现存 Pi 配置消费者的兼容探测 | 随 Pi 真实使用情况退役，不扩展 Astra，F22 |
| R39 | pi_once.ps1 / pi_guard.mjs | 旧执行通道的必要兼容保护 | 非 active；成组决定退役，F22 |
| R40 | scripts/release.py / docs/release.md | 窄验证、版本一致、发布步骤与明确授权 | 修补选测遗漏 F03；源码验证、发布、安装分层 |
| R41 | 部署 manifest / marketplace | 版本、发布 root、入口身份 | 保持无流程语义；校验所有实际消费入口的一致性 |
| R42 | docs/integrations/capability-provider-guide.md、project-skill-evidence.md | 项目 provider/Skill 证据输入与消费边界 | 保留；支持合法 YAML 和宿主资源读取，F05/F16 |
| R43 | sacha-doc-governance 开发 Skill 及 reference | 身份、信息归属、规则密度审查 | 保留操作价值，根部不再复制完整过程 |
| R44 | sacha-plugin-review 开发 Skill | 关键消费者、失败与证据判断 | 保留；按风险选择验证，不新增全面证明门槛 |
| R45 | sacha-simplification-audit 开发 Skill | 识别真实低效、唯一负责者、删除替代副本 | 保留；用于本次取舍，不把检查清单写入产品运行流程 |
| R46 | sacha-runtime-scenario 开发 Skill | 真实任务、执行者与 evaluator 分离、原始轨迹 | 保留；有触发才运行，只在相关宿主证明对应声明 |
| R47 | DSH src/index/types/normalize/snapshot | 原生事件、已提交事实与状态投影 | F25，明确 Review/Evidence 适用候选和新鲜度 |
| R48 | DSH tool-surface-policy.ts | 小工具面、catalog/help/unlock/reset、执行 guard | F23/F24；内部解耦不改变权限语义 |
| R49 | DSH client activity-monitor / ActivityPanel | 展示既有状态，不裁决任务完成 | 轮询退避、旧结果标识与错误恢复，F25 |
| R50 | DSH manager-graph / geometry / visibility | 图形投影、可见性和有消费者的布局 | 保留图形纯函数；清理孤立代码 F26 |
| R51 | DSH cats/artwork/status-art/CSS/图片/preview | 界面资产与独立预览 | 不因 Astra 变更；只清理真实无消费者资产，未做视觉验收 |
| R52 | DSH package/lock/patch/tsconfig/build | 可重复构建与单包安装边界 | 依赖缺失补齐后做相应构建；去掉 README 历史授权，F24/F29 |
| R53 | Python/Node/PowerShell 测试和验证器 | 检测生成器、写入保护、选择器与真实边界 | 修正跨平台预期 F29；增加已复现缺陷回归，避免说明文本锁死 |
| R54 | 21 个当前运行场景 | 用户目标、入口、语义链、证据与副作用边界 | 随被批准的规则变化更新直接相关 oracle，F21 |
| R55 | v1 历史运行场景、16 份历史工作记录 | 历史证据与设计原因 | 保留历史身份；只修仍误导的入口 F28 |

## 6. Astra 路由与长上下文方案

### 6.1 最小路由改动

根据后续讨论，路由方案同时纳入 astra_medium 和 astra_xhigh。大工程中需要持续联合理解多个模块的工作，应将 Astra medium 作为默认候选，不必等到 critical 才使用。切换型号时先保留同等 effort，随后用结果、耗时和整任务用量校准。下表是修订后的评估方案，尚未写入仓库运行规则。

| 优先级 | 任务事实 | 建议 route | 参数 |
| --- | --- | --- | --- |
| 1 | 用户或 Scope 精确指定 | human_exact | 原样使用已支持的型号/强度；不可悄悄降级 |
| 2 | broad + critical；或关键独立 Review | astra_xhigh | gpt-6-astra, xhigh |
| 3 | 非 critical，但需要持续联合理解较大有效上下文：全仓评估、跨模块调用/数据链、多消费者联合改动，或相应独立 Review | astra_medium | gpt-6-astra, medium |
| 4 | 其余 broad + standard；普通独立 Review | sol_medium | gpt-5.6-sol, medium |
| 5 | bounded + nontrivial | luna_max | gpt-5.6-luna, max |
| 6 | bounded + light | luna_xhigh | gpt-5.6-luna, xhigh |

sol_xhigh 可先保留为明确兼容路线；Astra 在创建前确实不可用时，只有原任务允许该替代且能力、授权、质量要求不变，才允许一次回退。用户精确指定 Astra 不允许自动换 Sol。超时、busy、执行失败、取消和不明启动状态均不是创建前不可用。astra_medium 已纳入方案，无需先证明“高风险”才能选用。触发依据是多个部分必须共同参与判断，不能只因仓库体积、文件数量或累计 token 多而升级：大仓库的一项局部机械改动仍可使用 Luna/Sol。该判断留在 Codex Adapter，沿用既有上下文/依赖事实，不新增 Core gate、必填枚举或固定 token 阈值。与 sol_medium 的对照用于校准这条路线的适用范围，不再作为是否允许加入该路线的前置条件。 同样，astra_xhigh 的价值来自更困难的推理、关键冲突或高返工代价；上下文长本身不要求 xhigh。medium 与 xhigh 是推理强度，不能据此假定二者有不同的窗口上限或每 token 价目。 主任务由用户选择 Astra，与每个子任务都使用 Astra 是两个决定。不要改写用户选择的主模型；子任务在宿主和上位约束允许显式选型时才应用路由。已有模型继承/override 限制必须尊重。

### 6.2 应改变的上下文使用方式

- 先读现行负责文件与当前目标相关证据。全仓评估当然可以全量读；普通局部修改不应把全仓历史作为固定前置。
- 大工程中需要同时理解的接口、调用链、数据结构和约束可保留在 Astra 主任务的有效上下文中。这样可能减少跨代理摘要损失、重复取证和返工；这是待任务对照检验的收益判断。独立、耗时、噪声较大的调查或必须独立的 Review 仍可隔离。
- 持久记录保留已确认目标、Scope、授权、关键决定、有效证据与下一步。不要把每段日志复制进 Handoff，也不要等到压缩边缘才记录不能重建的决定。
- 使用宿主提供的模型窗口与压缩默认值。若要覆盖，记录具体版本、计数范围与实测原因，保持可撤销；该值不应进入模型无关 Core。
- “无额外倍率”即使最终获确认，也不等于 tokens 免费、延迟不变或质量不随噪声变化，不能作为无条件全读和满窗口运行的理由。

官方 Astra 使用指南提示应检查旧提示/Skill 叠加的冲突，关注多余确认、过量格式与重复验证等行为。这支持先简化现有指令，但不证明本仓任何具体 gate 可以自动删除。[Astra 使用指南](https://developers.openai.com/api/docs/guides/latest-model)

### 6.3 最小迁移验证

只运行能区分新旧行为的任务：有界低风险工作仍走 Luna；破坏性覆盖不能被误判为 light；大工程联合推理可走 astra_medium；困难/关键任务走 astra_xhigh；普通复杂任务保留 Sol；用户精确选型不被覆盖；创建前不可用与已启动失败分开；当前 Work schema 可映射或正确报不支持。再用一个真实的大范围任务比较 Sol medium/Astra medium 的结果、人工纠正、返工、时间和用量。 不要求先跑所有宿主、不要求每个任务都记录完整九维表，也不因没拿到私有模型遥测而否定已经直接观察到的文件结果；但不能将文件正确声称成实际模型/权限配置已被验证。

### 6.4 官方迁移实践如何落到 Sacha

上轮已参考官方使用/迁移指南，本次再次核对其中的 Prompting best practices 和 Migration quickstart。官方要求迁移时保留原有效推理强度（none/minimal 改从 low 起步）；强调检查 Skill/AGENTS 冲突、减少不必要确认、明确委派策略与控制过量验证。以下 Sacha 调整是本仓评估建议，并非官方要求 Sacha 必须采用某一流程。[Astra 迁移与提示指南](https://developers.openai.com/api/docs/guides/latest-model)

| 实践 | 对本仓的具体调整 | 判断依据 |
| --- | --- | --- |
| 先同强度迁移，再调优 | Sol medium 对照 Astra medium，Sol xhigh 对照 Astra xhigh；避免把型号收益和 effort 变化混在一起 | 官方迁移基线；本次 astra_medium 选择 |
| 规则的优先级与适用条件明确 | 清理同一授权下的重复确认；Skill 因何阻断必须能定位到当前有效规则 | F09、F17、F19；不能靠模型自行猜哪份规则应失效 |
| 用完成条件替代操作次数 | Spec 核对格式、来源、自包含性，不要求固定三遍；测试覆盖已知风险后停止扩展 | F10、F20；保留检查目标，减少循环 |
| 明确有收益的委派，而非一律少派发 | 父任务持有耦合上下文；独立研究/长耗时任务有收益时委派；有 gate 的独立 Reviewer 继续保持独立 | F12；Astra 可能较少主动委派，不应把去掉数量硬约束写成禁止委派 |
| 控制常驻提示和无效格式 | 根部保留长期原则与负责入口；局部规则按任务加载；无需每次给九维表或精确行数 | F17–F19；不削减当前任务确实需要的项目事实 |

这次大工程任务的改进方向是让 Astra medium 同时持有足够完整、相关的工程事实，减少传递中丢失的约束；仍继续清理相互冲突的指令和无关日志。上下文容量与指令质量分别优化。

### 6.5 新能力与宿主边界

| 已确认的 API 能力 | 对 Sacha 的意义 | 接入限制 |
| --- | --- | --- |
| 异步工具调用（async tool calling） | 长工具运行期间继续推进无依赖工作，沿用当前依赖屏障原则 | 应用仍负责执行和关联 call_id；不是给普通 MCP 调用加 async:true 就能启用。见[异步工具指南](https://developers.openai.com/api/docs/guides/async-tool-calling)。 |
| 运行中纠正（mid-turn steering） | 用户补充或改向后保留已完成工作，更新受影响的计划、在途任务与证据 | 接收成功仅表示排队，不证明模型已执行纠正；底层工具结果和副作用仍需处理。见[Steering 指南](https://developers.openai.com/api/docs/guides/steering)。 |
| configuration_update 调整 effort 并保留缓存前缀 | 自管请求层可研究同模型 medium→xhigh 的按需调整 | 官方迁移说明限定受支持的 standard、single-agent 请求；不能推断 Codex 的已有子代理可通过消息原地改 effort。见[官方迁移说明](https://developers.openai.com/api/docs/guides/latest-model)。 |

若将来直接维护 Astra API 请求层，工具调用需采用 Responses，并清理不支持的采样参数；这是该请求层的迁移工作，不应写成当前 Markdown 插件必须实现的新运行机制。[官方迁移说明](https://developers.openai.com/api/docs/guides/latest-model)本次确认的是官方 API 能力，不是 Sacha、Codex、DSH 已全部暴露这些能力。新接口的适配应留在实际宿主 Adapter 或请求实现中，不新增第二套协调、取消或授权合同。

### 6.6 大工程按整任务成本评估

上轮用同 token 数的 2.5 倍价差解释模型分工，描述了单价，但不足以判断大工程的最终成本。应比较达到同一验收结果所花费的输入、缓存、输出/推理、重复调查与返工；同时记录耗时与人工纠正。官方称部分评估里 Astra 用更少输出取得更好结果，估算每任务 API 成本低于旧模型；这不能直接外推为 Sacha 已经节省同样比例。[Astra 官方说明](https://developers.openai.com/api/docs/guides/latest-model)对于“长上下文费用接近 Sol”，分三层记录：

- 已确认：当前 Codex 标准积分单价中，同等输入/缓存/输出 token 的 Astra/Sol 比例为 2.5；这不等于整任务成本比例。[Codex 定价](https://learn.chatgpt.com/docs/pricing)
- 条件计算：如果某计费模式确实对 Sol 长输入收 2 倍而对 Astra 不收倍率，输入价差会变成 2.5 ÷ 2 = 1.25；若 Sol 输出为 1.5 倍，输出价差则是 2.5 ÷ 1.5 ≈ 1.67。这是一组条件算式，本次尚未确认该 Codex 模式的非对称倍率前提。Sol API 确实有长输入倍率，但不能把一边 API 倍率和另一边订阅单价混算成实际账单。[Sol API 价格](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- 合理推断、未实测：Astra 在复杂工程中若减少重复读取、摘要损失、过量推理和返工，整任务费用可能接近 Sol，甚至更低。用相同任务对照确认即可，不应因此继续把 Astra 限在 critical，也不能提前写成普遍价格承诺。

因此本方案提高 Astra medium 在大工程联合推理中的优先级。实际成本校准是后续选择依据，不是增加每个任务的计费审批 gate。

## 7. Gate 的保留、合并与删除

无法仅凭当前仓库证明某条规则是哪个模型亲自引入，因此以下按它解决的失败模式判断，不把“Sol 时代”当作删除理由。

| 检查 | 处置 | 理由 |
| --- | --- | --- |
| 真实权限、安全、破坏性或不可逆副作用 | 保留 | 模型强弱不改变用户授权 |
| 文件原像、冲突、路径边界、单写入者 | 保留并修复 | F02/F04 已证明会影响真实数据 |
| 失败影响 broad/critical | 保留并精确化 | 实施边界清楚不等于失败影响小 |
| 关键未知会改变方案时澄清 | 保留 | 只问真正改变实现的事项 |
| 有条件的 Planner/Spec | 保留 | 批准、交接、恢复或破坏性变化有真实消费者 |
| 每个未收口小事实都切 Explore | 缩小触发 | 不需要完整节点切换的事项当前上下文可处理 |
| 每个 Spec 固定三遍回读，失败全重来 | 合并 | 保留检查维度，删除固定轮数 |
| 两个就绪单元必须创建两个代理 | 删除数量硬约束 | 就绪与隔离是可派发条件，收益才决定是否派发 |
| 每次派发固定九维逐项填表 | 合并 | 保留相关事实，去掉无关模板项 |
| 所有真实实现默认上下文污染 | 收窄 | 自包含输出与父任务认知收益应具体判断 |
| 独立 Reviewer | 按现有关键风险保留 | 必须独立时保留来源隔离，不能以 Astra 自检代替 |
| Reviewer 必须固定 Sol 型号 | 解除型号绑定 | 独立性不由型号定义；具体模型留给 Adapter |
| Review 默认重跑所有关键验证 | 改为按裁决收益 | 已有原始证据可复用，变化需新裁决 |
| 源码改动一律真实宿主场景 | 删除无条件要求 | 按行为声明和交付层触发 |
| 只读文档预览前确认写入 | 删除提前阻断 | 应先形成可审查候选，再在实际写入处消费授权 |
| 用户已批准同一目标后重复确认 | 删除重复 | 只对新增决定或未授权副作用提问 |
| 严格任务去重与 Owner 交接 | 保留 | 避免重复任务、双写和来源/目标同时接管 |
| 固定 token 阈值强制迁移 | 不新增 | 宿主压缩与产品任务迁移是不同机制 |

## 8. 验证结果与实际限制

| 检查 | 结果 | 能证明什么 |
| --- | --- | --- |
| python -B -m unittest discover -s tests -p 'test_*.py' | 117 项；4 处失败 | 当前 Python 套件运行情况；不能写成全绿 |
| node --test tests/test_pi_guard.mjs | 通过 | Pi guard 当前 Node 断言；不是 Pi PowerShell 端到端 |
| python -B tests/validate_release_coherence.py --version 0.14.2 --phase candidate | pass，0 failures | 该校验器覆盖的版本/入口一致性；F03 仍存在 |
| 6 个隔离探针 | 均产生第 4 节描述的结果 | F02–F07 对应并发覆盖、选测、根消歧、YAML、预览和词法误拒 |
| DSH snapshot 纯函数输入 | 新 Executor 与旧 accepted 同时保留 | 当前状态折叠没有自动失效；未验证实际 UI 展示 |
| DSH 离线依赖安装 | 缺少 @deepseek-ai/dsh-scope@0.1.1-rc.2 离线包而失败 | 本次无法继续完整 typecheck/Vitest/build/pack |
| PowerShell、21 个当前原生任务场景、Codex 自定义 agent 发现、Claude/Cursor/DSH 安装 | 本次未执行 | 明确未验证，不能用源码代替 |
| 工作区 | Git tracked 工作区保持干净 | 没有把建议伪装成已实施修复 |

Python 失败详情：test_external_storage_bases_are_derived_independently、test_spec_storage_defaults_is_separate_and_preserved 的路径分隔符预期；test_project_documentation_refuses_unreachable_escape_and_root_boundaries 有 drive/share 两个 subtest 的错误原因预期差异。不是四个独立功能都允许不安全路径，也不能直接归为 Astra 兼容失败。 8 月 29 日历史报告记载的宿主/Windows/DSH 结果只证明当时运行，不计入本次通过项。本次没有开展依赖供应链审计、真实账户计费实验、用户桌面配置检查或图片视觉验收。

## 9. 建议实施顺序

| 工作包 | 对应发现 | 具体结果 | 最小验证 |
| --- | --- | --- | --- |
| W1 正确性修复 | F02–F07、F29 | 并发修改不被覆盖；JS/模板选测正确；根与 YAML 正确；预览可审查；合法项目文案可生成 | 对应缺陷回归及相关现有套件；保留完整失败输出 |
| W2 当前 Codex 能力映射 | F01、F15、F16 | 当前 schema 能正确映射或准确报告不支持；资源读取与取消语义成立 | 只读能力探针；受控生命周期证据；不靠写入试探权限 |
| W3 全仓规则减负 | F09–F12、F17–F21 | 同一目标少重复确认、少固定回读、少无收益派发；负责文件无冲突 | owner review；只跑被改变的入口、协调、Spec 场景 |
| W4 Astra 路由 | F13、F14 | 保留 Luna/Sol，加入大工程 astra_medium 与关键任务 astra_xhigh；精确指定与安全回退明确 | 专门路由场景加 Sol medium/Astra medium 的真实大任务对照 |
| W5 DSH 当前缺口 | F23–F26 | 目录可恢复、状态不误导、空闲不热轮询、发布说明无历史授权 | 依赖齐备后定向 Vitest/typecheck/build；对应 DSH runtime 场景 |
| W6 兼容和历史清理 | F22、F27、F28 | Pi 去留按消费者决定；预算外置；历史不再冒充当前规则 | 引用/发布可达性与受影响宿主源码校验 |

W1 与 W2 可分别设计和审查；W4 依赖 W2 的实际调用能力。W3 涉及入口和节点职责的部分属于产品取舍，应形成具体差异后按仓库现有设计规则实施。当前请求是全量评估，因此本报告没有把这些建议直接写成新的强制规则。 本次评估无需用户补充输入即可成立；仍未确认的计费与上下文数字已保留为未确认，而不是交给用户代查或用假设填补。

## 10. 关键源码证据索引

以下链接固定在本次评估 commit，避免后续 main 更新改变引用内容。

- [根治理规则](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/AGENTS.md)
- [顶层设计](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/PLUGIN_DESIGN.md)
- [Codex Adapter](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/plugins/sacha-orchestra/adapters/codex/runtime-adapter.md)
- [Coordination Contract](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/plugins/sacha-orchestra/core/coordination-contract.md)
- [Planner Skill](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/plugins/sacha-orchestra/skills/planner/SKILL.md)
- [setup-agents 实现](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/plugins/sacha-orchestra/skills/setup-agents/scripts/setup_agents.py)
- [release 选择器](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/scripts/release.py)
- [项目接入生成器](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/plugins/sacha-orchestra/skills/setup-project/scripts/generate_project_integration.py)
- [provider 与 root 解析](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/plugins/sacha-orchestra/skills/setup-project/scripts/resolve_provider_queries.py)
- [文档生成器](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/plugins/sacha-orchestra/skills/document-project/scripts/generate_project_document.py)
- [DSH 工具策略](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/integrations/dsh/sacha-companion/src/tool-surface-policy.ts)
- [DSH 状态折叠](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/integrations/dsh/sacha-companion/src/snapshot.ts)
- [DSH 轮询](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/integrations/dsh/sacha-companion/src/client/activity-monitor.ts)
- [运行场景目录及历史身份](https://github.com/yyqrc/SachaOrchestra/blob/2054b78770fd25562677a28f52ca99bf0416689b/tests/runtime-scenarios/README.md)

## 附录 A：隔离探针原始摘要

以下为本次实际调用真实模块后得到的结果；临时目录和用户宿主配置隔离。{

## 附录 B：288 个跟踪文件的覆盖清单

层级说明：全文＝当前规则或生产源码全文静态审查；测试＝结构/调用链/关键断言审查，实际执行以第 8 节为准；场景＝task/oracle 全文，fixtures 按归属和相关断言核对，未执行原生任务；历史＝身份与取代关系核对，涉及当前判断的记录详读；资源＝引用和用途核对，未做视觉验收。清单不把哈希核对等同语义审查。

| 文件 | 覆盖层级 | SHA-256 前 12 位 |
| --- | --- | --- |
| .agents/plugins/marketplace.json | 全文 | ecf6076d3cc4 |
| .agents/skills/sacha-doc-governance/SKILL.md | 全文 | 72ec2c585675 |
| .agents/skills/sacha-doc-governance/agents/openai.yaml | 全文 | b523805c9bb1 |
| .agents/skills/sacha-doc-governance/references/skill-and-adapter-text.md | 全文 | 17f7627f17c0 |
| .agents/skills/sacha-plugin-review/SKILL.md | 全文 | ae562033b151 |
| .agents/skills/sacha-plugin-review/agents/openai.yaml | 全文 | abff7bd37674 |
| .agents/skills/sacha-runtime-scenario/SKILL.md | 全文 | 50948b0cbb71 |
| .agents/skills/sacha-runtime-scenario/agents/openai.yaml | 全文 | 670df67a13c4 |
| .agents/skills/sacha-simplification-audit/SKILL.md | 全文 | d995b2b93d1b |
| .agents/skills/sacha-simplification-audit/agents/openai.yaml | 全文 | dd44b96b4cfc |
| .claude-plugin/marketplace.json | 全文 | 5dd3c460b4d5 |
| .cursor-plugin/marketplace.json | 全文 | 44199a8606a0 |
| .gitattributes | 配置归属核对 | 17bc4093d2c6 |
| .gitignore | 配置归属核对 | f6904ad4d4a6 |
| AGENTS.md | 全文 | 1bfa2ba52ca8 |
| EVOLUTION.md | 全文 | c8fd86b592a3 |
| PLUGIN_DESIGN.md | 全文 | d72e424d42be |
| README.md | 全文 | 4317ba18f7cf |
| docs/AGENTS.md | 全文 | e299f90b9a41 |
| docs/CONTEXT.md | 全文 | fbfd1eeba3f2 |
| docs/integrations/capability-provider-guide.md | 全文 | c91e1c6dfc64 |
| docs/plan/2026-07-30-spec-artifact-storage-repair/spec.md | 历史 | 9c0603e969b0 |
| docs/plan/2026-08-04-domain-provider-planning-support/spec.md | 历史 | 509afc9e49ab |
| docs/plan/2026-08-04-planner-alignment-executable-spec/spec.md | 历史 | d4f9ef2b7147 |
| docs/plan/2026-08-06-executor-task-migration/execution-report.md | 历史 | b627f8fe1559 |
| docs/plan/2026-08-06-executor-task-migration/review.md | 历史 | d81d9ebc5890 |
| docs/plan/2026-08-06-executor-task-migration/spec.md | 历史 | 42054c4f8320 |
| docs/plan/2026-08-07-feedback-owner-transfer/spec.md | 历史 | e4aab3b0c401 |
| docs/plan/2026-08-07-flow-first-skill-boundaries/spec.md | 历史 | f5cc60193ca2 |
| docs/plan/2026-08-12-single-level-manager-dispatch/spec.md | 历史 | 56fd1fe5d1c4 |
| docs/plan/2026-08-14-codex-code-mode-orchestration/spec.md | 历史 | 5a09ff37d5fb |
| docs/plan/2026-08-19-closeout-aliases/spec.md | 历史 | 4bc48c221c8c |
| docs/plan/2026-08-28-runtime-capability-followup/feature.md | 历史 | 3e5a8bbb72a2 |
| docs/plan/2026-08-28-runtime-surface-and-dsh-subagents/design.md | 历史 | 30a93d71532e |
| docs/plan/2026-08-29-dsh-adapter-full-chain/execution-report.md | 历史 | 05b3b24f3ed4 |
| docs/plan/2026-08-29-dsh-adapter-full-chain/review.md | 历史 | c7fe10254374 |
| docs/plan/2026-08-29-dsh-adapter-full-chain/spec.md | 历史 | 749b988b590f |
| docs/release.md | 全文 | 85802faea97f |
| integrations/dsh/sacha-companion/.gitignore | 配置归属核对 | b787d94b14b4 |
| integrations/dsh/sacha-companion/CAT_ART_PROMPT.md | 资源 | 5e189cfd5234 |
| integrations/dsh/sacha-companion/README.md | 全文 | f748549ca6f9 |
| integrations/dsh/sacha-companion/artwork-source/cats/00-original-svg-screenshot.png | 资源 | 7cc0cf3543d2 |
| integrations/dsh/sacha-companion/artwork-source/cats/01-sacha-conductor-concept.png | 资源 | 882d6cc36df8 |
| integrations/dsh/sacha-companion/artwork-source/cats/02-jojo-scalloped-ruff-rejected.png | 资源 | 6f6695b2ea32 |
| integrations/dsh/sacha-companion/artwork-source/cats/03-jojo-round-shoulder-concept.png | 资源 | a4140b6b6528 |
| integrations/dsh/sacha-companion/artwork-source/cats/04-jojo-reviewer-clipboard-concept.png | 资源 | 6323f89cf166 |
| integrations/dsh/sacha-companion/artwork-source/cats/05-svg-full-iteration-preview.png | 资源 | 76f6cdb22a10 |
| integrations/dsh/sacha-companion/artwork-source/cats/06-svg-base-v1-comparison.png | 资源 | cccb7d075046 |
| integrations/dsh/sacha-companion/artwork-source/cats/generated/cat-jojo-base-source.png | 资源 | f33d6c9bcc42 |
| integrations/dsh/sacha-companion/artwork-source/cats/generated/cat-sacha-base-source.png | 资源 | 95dbfb4588a7 |
| integrations/dsh/sacha-companion/assets/cats/cat-jojo-base.png | 资源 | 1e22781c0bd6 |
| integrations/dsh/sacha-companion/assets/cats/cat-sacha-base.png | 资源 | 469da7b1a3e5 |
| integrations/dsh/sacha-companion/cordis.patch.yml | 全文 | c8175d2d42f1 |
| integrations/dsh/sacha-companion/package.json | 全文 | 74ad6634ddc3 |
| integrations/dsh/sacha-companion/pnpm-lock.yaml | 全文 | 4d403405b4fe |
| integrations/dsh/sacha-companion/pnpm-workspace.yaml | 全文 | ac02d9636861 |
| integrations/dsh/sacha-companion/preview/index.html | 全文 | 1977f845fff2 |
| integrations/dsh/sacha-companion/preview/src/main.tsx | 全文 | 845d09c7ec4d |
| integrations/dsh/sacha-companion/preview/src/scenarios.ts | 全文 | 1db239a3b213 |
| integrations/dsh/sacha-companion/preview/src/styles.css | 全文 | 92c4d6a1fde0 |
| integrations/dsh/sacha-companion/preview/vite.config.ts | 全文 | d18f9e0283f3 |
| integrations/dsh/sacha-companion/src/client/ActivityPanel.module.css | 全文 | 113294bf6889 |
| integrations/dsh/sacha-companion/src/client/ActivityPanel.tsx | 全文 | 844c26dc531c |
| integrations/dsh/sacha-companion/src/client/activity-monitor.ts | 全文 | eed016c92dc4 |
| integrations/dsh/sacha-companion/src/client/artwork.ts | 全文 | 389b50f882c7 |
| integrations/dsh/sacha-companion/src/client/cats.tsx | 全文 | ef48794dd9c6 |
| integrations/dsh/sacha-companion/src/client/index.tsx | 全文 | c5c373ce01e7 |
| integrations/dsh/sacha-companion/src/client/manager-graph.ts | 全文 | 5f71a1be1d3d |
| integrations/dsh/sacha-companion/src/client/panel-geometry.ts | 全文 | 5e6b601d2494 |
| integrations/dsh/sacha-companion/src/client/panel-visibility.ts | 全文 | a47bde26f4ba |
| integrations/dsh/sacha-companion/src/client/status-art.tsx | 全文 | f25457273bff |
| integrations/dsh/sacha-companion/src/css-modules.d.ts | 全文 | 977a7f55de28 |
| integrations/dsh/sacha-companion/src/index.ts | 全文 | 05c51cc20aa6 |
| integrations/dsh/sacha-companion/src/normalize.ts | 全文 | a05305a8ae90 |
| integrations/dsh/sacha-companion/src/snapshot.ts | 全文 | d112d12dd7ff |
| integrations/dsh/sacha-companion/src/tool-surface-policy.ts | 全文 | 6dec8e4f6079 |
| integrations/dsh/sacha-companion/src/types.ts | 全文 | 47369a4e56ba |
| integrations/dsh/sacha-companion/tests/activity-monitor.spec.ts | 测试 | 02abbd4fddec |
| integrations/dsh/sacha-companion/tests/artwork.spec.ts | 测试 | 08694ceee108 |
| integrations/dsh/sacha-companion/tests/fixtures/sacha-llm.mjs | 测试 | 75ec02ff530f |
| integrations/dsh/sacha-companion/tests/manager-graph.spec.ts | 测试 | 0d67fa576932 |
| integrations/dsh/sacha-companion/tests/normalize.spec.ts | 测试 | d32219cfb2f9 |
| integrations/dsh/sacha-companion/tests/panel-geometry.spec.ts | 测试 | e256f808a253 |
| integrations/dsh/sacha-companion/tests/panel-visibility.spec.ts | 测试 | 9c7037349ad3 |
| integrations/dsh/sacha-companion/tests/snapshot.spec.ts | 测试 | ee40ab611df3 |
| integrations/dsh/sacha-companion/tests/tool-surface-policy.spec.ts | 测试 | 286246df4ebf |
| integrations/dsh/sacha-companion/tsconfig.client.json | 全文 | 1be0c120e28d |
| integrations/dsh/sacha-companion/tsconfig.json | 全文 | 5af08c623503 |
| integrations/dsh/sacha-companion/tsconfig.preview.json | 全文 | 1d998e6b8cc6 |
| integrations/dsh/sacha-companion/tsdown.config.ts | 全文 | 211d1f118fd8 |
| plugins/sacha-orchestra/.claude-plugin/plugin.json | 全文 | e5d35dad8ead |
| plugins/sacha-orchestra/.codex-plugin/plugin.json | 全文 | 5c62748002bd |
| plugins/sacha-orchestra/README.md | 全文 | e6f58c0d9878 |
| plugins/sacha-orchestra/adapters/claudecode/runtime-adapter.md | 全文 | cbac8f34c752 |
| plugins/sacha-orchestra/adapters/codex/code-mode-batch.js | 全文 | 2862e321e42b |
| plugins/sacha-orchestra/adapters/codex/runtime-adapter.md | 全文 | 21b8171e9652 |
| plugins/sacha-orchestra/adapters/cursor/runtime-adapter.md | 全文 | 59670b60373b |
| plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md | 全文 | 7d6f24a3b0be |
| plugins/sacha-orchestra/core/artifact-protocol.md | 全文 | 1b2ce81438fd |
| plugins/sacha-orchestra/core/assurance-contract.md | 全文 | 043bc262bf40 |
| plugins/sacha-orchestra/core/coordination-contract.md | 全文 | c6bfec4542bb |
| plugins/sacha-orchestra/core/human-interaction-contract.md | 全文 | dc07ccf6871a |
| plugins/sacha-orchestra/core/intake-contract.md | 全文 | bc4ae87201dc |
| plugins/sacha-orchestra/core/terminology-contract.md | 全文 | bdcb709e5f08 |
| plugins/sacha-orchestra/core/workflow-contract.md | 全文 | f9c2d9a9ad44 |
| plugins/sacha-orchestra/plugin.json | 全文 | 47cfd8f88530 |
| plugins/sacha-orchestra/scripts/pi_guard.mjs | 全文 | 9257c0e8f6e1 |
| plugins/sacha-orchestra/scripts/pi_once.ps1 | 全文 | 6e34723b115e |
| plugins/sacha-orchestra/skills/closeout/SKILL.md | 全文 | 1ccee352e2b4 |
| plugins/sacha-orchestra/skills/closeout/agents/openai.yaml | 全文 | 081a1b784862 |
| plugins/sacha-orchestra/skills/document-project/SKILL.md | 全文 | bb20392c6fb1 |
| plugins/sacha-orchestra/skills/document-project/agents/openai.yaml | 全文 | 44fb57152759 |
| plugins/sacha-orchestra/skills/document-project/assets/change-archive.md | 全文 | ecd6d0c226e8 |
| plugins/sacha-orchestra/skills/document-project/assets/project-context.json | 全文 | 62b4aefaaae4 |
| plugins/sacha-orchestra/skills/document-project/assets/roadmap.json | 全文 | 2f8a32e3ce25 |
| plugins/sacha-orchestra/skills/document-project/assets/roadmap.md | 全文 | 6559a28779ad |
| plugins/sacha-orchestra/skills/document-project/assets/system-guide.md | 全文 | d8a2c29080b5 |
| plugins/sacha-orchestra/skills/document-project/scripts/generate_project_document.py | 全文 | 52c2aeef6216 |
| plugins/sacha-orchestra/skills/executor/SKILL.md | 全文 | df629ced4e28 |
| plugins/sacha-orchestra/skills/executor/agents/openai.yaml | 全文 | b10fb638c301 |
| plugins/sacha-orchestra/skills/explore/SKILL.md | 全文 | a8b9f2ad17bc |
| plugins/sacha-orchestra/skills/explore/agents/openai.yaml | 全文 | beaaba0ed0d0 |
| plugins/sacha-orchestra/skills/feedback/SKILL.md | 全文 | f603f48ecc37 |
| plugins/sacha-orchestra/skills/feedback/agents/openai.yaml | 全文 | 507f05022d3f |
| plugins/sacha-orchestra/skills/manager/SKILL.md | 全文 | 0979cf237c3d |
| plugins/sacha-orchestra/skills/manager/agents/openai.yaml | 全文 | e0f0504e878e |
| plugins/sacha-orchestra/skills/planner/SKILL.md | 全文 | c808948f0a82 |
| plugins/sacha-orchestra/skills/planner/agents/openai.yaml | 全文 | 7fe3bd8ccc37 |
| plugins/sacha-orchestra/skills/reviewer/SKILL.md | 全文 | e78f0370a3ce |
| plugins/sacha-orchestra/skills/reviewer/agents/openai.yaml | 全文 | a78de52788dd |
| plugins/sacha-orchestra/skills/roadmap/SKILL.md | 全文 | a885275c54f9 |
| plugins/sacha-orchestra/skills/roadmap/agents/openai.yaml | 全文 | e538e96c07d8 |
| plugins/sacha-orchestra/skills/setup-agents/SKILL.md | 全文 | d6900a76e5e8 |
| plugins/sacha-orchestra/skills/setup-agents/agents/openai.yaml | 全文 | af778fdbea7b |
| plugins/sacha-orchestra/skills/setup-agents/assets/sacha-deepseek-pro-worker.toml | 全文 | d2cf00500181 |
| plugins/sacha-orchestra/skills/setup-agents/assets/sacha-deepseek-worker.toml | 全文 | 9fa1d30554a2 |
| plugins/sacha-orchestra/skills/setup-agents/assets/sacha-executer.toml | 全文 | e710fa12e9fc |
| plugins/sacha-orchestra/skills/setup-agents/assets/sacha-researcher.toml | 全文 | 27cb28b379bf |
| plugins/sacha-orchestra/skills/setup-agents/assets/sacha-reviewer.toml | 全文 | 2a0e6f5f3ef5 |
| plugins/sacha-orchestra/skills/setup-agents/scripts/setup_agents.py | 全文 | 7762245d4c08 |
| plugins/sacha-orchestra/skills/setup-project/SKILL.md | 全文 | 5d2947f4a2ca |
| plugins/sacha-orchestra/skills/setup-project/agents/openai.yaml | 全文 | e87ce930840f |
| plugins/sacha-orchestra/skills/setup-project/references/project-skill-evidence.md | 全文 | b265456593d2 |
| plugins/sacha-orchestra/skills/setup-project/scripts/generate_project_integration.py | 全文 | f05f1dbb99e5 |
| plugins/sacha-orchestra/skills/setup-project/scripts/inspect_pi_models.ps1 | 全文 | 2ce590edc2a7 |
| plugins/sacha-orchestra/skills/setup-project/scripts/resolve_provider_queries.py | 全文 | 1374759ad5f5 |
| plugins/sacha-orchestra/skills/using-sacha/SKILL.md | 全文 | f1dfd492aa66 |
| plugins/sacha-orchestra/skills/using-sacha/agents/openai.yaml | 全文 | 5bf97d39ace9 |
| scripts/release.py | 全文 | b4fd0c99b080 |
| tests/project_test_support.py | 测试 | 1f23e4127844 |
| tests/runtime-scenarios/README.md | 全文 | a01eda1f0505 |
| tests/runtime-scenarios/assets/workspace-AGENTS.md | 测试 | c97d05b6db79 |
| tests/runtime-scenarios/packs/closeout-command/fixture/current/spec.md | 场景：fixture/验证入口归属 | b8b1823f83ee |
| tests/runtime-scenarios/packs/closeout-command/fixture/verify.py | 场景：fixture/验证入口归属 | 212a6b342d29 |
| tests/runtime-scenarios/packs/closeout-command/oracle.md | 场景：task/oracle 全文 | e3741b9bcb9b |
| tests/runtime-scenarios/packs/closeout-command/task.md | 场景：task/oracle 全文 | 3d2c17f32220 |
| tests/runtime-scenarios/packs/codex-agent-skill-loading-routing/fixture/LineExporter.cs | 场景：fixture/验证入口归属 | 45b120b601e7 |
| tests/runtime-scenarios/packs/codex-agent-skill-loading-routing/fixture/baseline.txt | 场景：fixture/验证入口归属 | d7de59c8f53c |
| tests/runtime-scenarios/packs/codex-agent-skill-loading-routing/fixture/evidence.txt | 场景：fixture/验证入口归属 | ae10853596aa |
| tests/runtime-scenarios/packs/codex-agent-skill-loading-routing/oracle.md | 场景：task/oracle 全文 | ee867a844cbf |
| tests/runtime-scenarios/packs/codex-agent-skill-loading-routing/task.md | 场景：task/oracle 全文 | 0f91c2e7fa1b |
| tests/runtime-scenarios/packs/codex-code-mode-readonly-batch/fixture/probe.json | 场景：fixture/验证入口归属 | 43dc7da8d3a8 |
| tests/runtime-scenarios/packs/codex-code-mode-readonly-batch/fixture/verify.py | 场景：fixture/验证入口归属 | 59f0a10b6490 |
| tests/runtime-scenarios/packs/codex-code-mode-readonly-batch/oracle.md | 场景：task/oracle 全文 | 4100b7e18372 |
| tests/runtime-scenarios/packs/codex-code-mode-readonly-batch/task.md | 场景：task/oracle 全文 | c88d8e11133d |
| tests/runtime-scenarios/packs/codex-code-mode-v1-batch/fixture/alpha.json | 场景：fixture/验证入口归属 | 83d71701f81a |
| tests/runtime-scenarios/packs/codex-code-mode-v1-batch/fixture/beta.json | 场景：fixture/验证入口归属 | 506f8a297db4 |
| tests/runtime-scenarios/packs/codex-code-mode-v1-batch/fixture/probe.json | 场景：fixture/验证入口归属 | 742d65e7b3ba |
| tests/runtime-scenarios/packs/codex-code-mode-v1-batch/fixture/verify.py | 场景：fixture/验证入口归属 | a3578aa31f89 |
| tests/runtime-scenarios/packs/codex-code-mode-v1-batch/oracle.md | 场景：task/oracle 全文 | 02ebc19e9b23 |
| tests/runtime-scenarios/packs/codex-code-mode-v1-batch/task.md | 场景：task/oracle 全文 | 0c5a4786a071 |
| tests/runtime-scenarios/packs/codex-context-isolation-execution/fixture/input/service-a.txt | 场景：fixture/验证入口归属 | def1286a2cd0 |
| tests/runtime-scenarios/packs/codex-context-isolation-execution/fixture/input/service-b.txt | 场景：fixture/验证入口归属 | e113cf7c4683 |
| tests/runtime-scenarios/packs/codex-context-isolation-execution/fixture/verify.txt | 场景：fixture/验证入口归属 | 9e55b68be65e |
| tests/runtime-scenarios/packs/codex-context-isolation-execution/oracle.md | 场景：task/oracle 全文 | d8cb09302db4 |
| tests/runtime-scenarios/packs/codex-context-isolation-execution/task.md | 场景：task/oracle 全文 | 89a328792b10 |
| tests/runtime-scenarios/packs/codex-context-isolation-research/fixture/logs/build-summary.txt | 场景：fixture/验证入口归属 | 3cd8f66b15f4 |
| tests/runtime-scenarios/packs/codex-context-isolation-research/fixture/logs/compile-and-tests.txt | 场景：fixture/验证入口归属 | e6520e9cd63b |
| tests/runtime-scenarios/packs/codex-context-isolation-research/fixture/logs/environment.txt | 场景：fixture/验证入口归属 | 51acd2586bca |
| tests/runtime-scenarios/packs/codex-context-isolation-research/fixture/logs/package-worker.txt | 场景：fixture/验证入口归属 | 63fab1e61622 |
| tests/runtime-scenarios/packs/codex-context-isolation-research/oracle.md | 场景：task/oracle 全文 | 7131697ce626 |
| tests/runtime-scenarios/packs/codex-context-isolation-research/task.md | 场景：task/oracle 全文 | b7c13037dc82 |
| tests/runtime-scenarios/packs/codex-model-routing-failure-radius/fixture/input/source/alpha.txt | 场景：fixture/验证入口归属 | 28b1c53710e5 |
| tests/runtime-scenarios/packs/codex-model-routing-failure-radius/fixture/input/source/nested/beta.txt | 场景：fixture/验证入口归属 | f2c82decdd71 |
| tests/runtime-scenarios/packs/codex-model-routing-failure-radius/fixture/input/target/alpha.txt | 场景：fixture/验证入口归属 | cd66ab615c8b |
| tests/runtime-scenarios/packs/codex-model-routing-failure-radius/fixture/input/target/obsolete.txt | 场景：fixture/验证入口归属 | abdcccf4a6a5 |
| tests/runtime-scenarios/packs/codex-model-routing-failure-radius/fixture/verify.py | 场景：fixture/验证入口归属 | 6e7bd3aae5b6 |
| tests/runtime-scenarios/packs/codex-model-routing-failure-radius/oracle.md | 场景：task/oracle 全文 | 01c7498bd6e2 |
| tests/runtime-scenarios/packs/codex-model-routing-failure-radius/task.md | 场景：task/oracle 全文 | aaaea07366d1 |
| tests/runtime-scenarios/packs/codex-skill-entry-visibility/fixture/.agents/skills/domain-copy-editor/SKILL.md | 场景：fixture/验证入口归属 | 66dde6b01dc8 |
| tests/runtime-scenarios/packs/codex-skill-entry-visibility/fixture/.agents/skills/project-fact-check/SKILL.md | 场景：fixture/验证入口归属 | cea4399dfd12 |
| tests/runtime-scenarios/packs/codex-skill-entry-visibility/fixture/product-note.md | 场景：fixture/验证入口归属 | b374d5cd9eda |
| tests/runtime-scenarios/packs/codex-skill-entry-visibility/oracle.md | 场景：task/oracle 全文 | 87e3be212438 |
| tests/runtime-scenarios/packs/codex-skill-entry-visibility/task.md | 场景：task/oracle 全文 | de765e2cc436 |
| tests/runtime-scenarios/packs/dsh-companion-root-surface-routing/fixture/README.md | 场景：fixture/验证入口归属 | 9ca093817169 |
| tests/runtime-scenarios/packs/dsh-companion-root-surface-routing/oracle.md | 场景：task/oracle 全文 | 6520bbf47273 |
| tests/runtime-scenarios/packs/dsh-companion-root-surface-routing/task.md | 场景：task/oracle 全文 | cb3a5d27ba0c |
| tests/runtime-scenarios/packs/dsh-continuable-parallel-barrier/fixture/input/accounts.csv | 场景：fixture/验证入口归属 | 75be0b313c25 |
| tests/runtime-scenarios/packs/dsh-continuable-parallel-barrier/fixture/input/routes.csv | 场景：fixture/验证入口归属 | ab07daf0d833 |
| tests/runtime-scenarios/packs/dsh-continuable-parallel-barrier/fixture/verify.txt | 场景：fixture/验证入口归属 | 4377046592ec |
| tests/runtime-scenarios/packs/dsh-continuable-parallel-barrier/oracle.md | 场景：task/oracle 全文 | 50abbc1cf6ee |
| tests/runtime-scenarios/packs/dsh-continuable-parallel-barrier/task.md | 场景：task/oracle 全文 | f24dc502325d |
| tests/runtime-scenarios/packs/dsh-continuable-review-isolation/fixture/token_mask.txt | 场景：fixture/验证入口归属 | f84f3945facf |
| tests/runtime-scenarios/packs/dsh-continuable-review-isolation/fixture/verify.txt | 场景：fixture/验证入口归属 | b3f769abb17c |
| tests/runtime-scenarios/packs/dsh-continuable-review-isolation/oracle.md | 场景：task/oracle 全文 | bee95751e61c |
| tests/runtime-scenarios/packs/dsh-continuable-review-isolation/task.md | 场景：task/oracle 全文 | 172b80d6d45e |
| tests/runtime-scenarios/packs/executor-only/fixture/input.json | 场景：fixture/验证入口归属 | 2ac2e0a29a2f |
| tests/runtime-scenarios/packs/executor-only/fixture/verify.py | 场景：fixture/验证入口归属 | d5f12a76daae |
| tests/runtime-scenarios/packs/executor-only/oracle.md | 场景：task/oracle 全文 | 4b798ec505ac |
| tests/runtime-scenarios/packs/executor-only/task.md | 场景：task/oracle 全文 | 575292ba96cc |
| tests/runtime-scenarios/packs/explore-handoff-continuation/fixture/consumer-facts.md | 场景：fixture/验证入口归属 | 5b9a0f20fa2b |
| tests/runtime-scenarios/packs/explore-handoff-continuation/fixture/control-facts.md | 场景：fixture/验证入口归属 | 85e017d292f8 |
| tests/runtime-scenarios/packs/explore-handoff-continuation/fixture/decisions.md | 场景：fixture/验证入口归属 | 015c8cb40613 |
| tests/runtime-scenarios/packs/explore-handoff-continuation/fixture/probe-facts.md | 场景：fixture/验证入口归属 | 88b3267e3d04 |
| tests/runtime-scenarios/packs/explore-handoff-continuation/fixture/verify.py | 场景：fixture/验证入口归属 | fff023f0da10 |
| tests/runtime-scenarios/packs/explore-handoff-continuation/oracle.md | 场景：task/oracle 全文 | 13aa1f9d04d5 |
| tests/runtime-scenarios/packs/explore-handoff-continuation/task.md | 场景：task/oracle 全文 | f8fb7b79ba18 |
| tests/runtime-scenarios/packs/explore-shared-context-loop/fixture/runtime-facts.md | 场景：fixture/验证入口归属 | 229e5d24cde1 |
| tests/runtime-scenarios/packs/explore-shared-context-loop/fixture/verify.py | 场景：fixture/验证入口归属 | f54fd789d5f7 |
| tests/runtime-scenarios/packs/explore-shared-context-loop/oracle.md | 场景：task/oracle 全文 | 17eee0dee1bd |
| tests/runtime-scenarios/packs/explore-shared-context-loop/task.md | 场景：task/oracle 全文 | 17bf0e33d5d3 |
| tests/runtime-scenarios/packs/planner-explore-manager-reviewer/fixture/consumer-alpha.py | 场景：fixture/验证入口归属 | df3e478478ba |
| tests/runtime-scenarios/packs/planner-explore-manager-reviewer/fixture/consumer-beta.py | 场景：fixture/验证入口归属 | 773ac6191c79 |
| tests/runtime-scenarios/packs/planner-explore-manager-reviewer/fixture/service-alpha.json | 场景：fixture/验证入口归属 | 57413f23c796 |
| tests/runtime-scenarios/packs/planner-explore-manager-reviewer/fixture/service-beta.json | 场景：fixture/验证入口归属 | e3253e0aa16c |
| tests/runtime-scenarios/packs/planner-explore-manager-reviewer/fixture/verify.py | 场景：fixture/验证入口归属 | 8e13972d4200 |
| tests/runtime-scenarios/packs/planner-explore-manager-reviewer/oracle.md | 场景：task/oracle 全文 | 0a0fd9283727 |
| tests/runtime-scenarios/packs/planner-explore-manager-reviewer/task.md | 场景：task/oracle 全文 | 365808bf93e8 |
| tests/runtime-scenarios/packs/project-facing-spec/fixture/handoff.md | 场景：fixture/验证入口归属 | a02b1bc8bbc6 |
| tests/runtime-scenarios/packs/project-facing-spec/fixture/project-brief.md | 场景：fixture/验证入口归属 | c7ec5e5d9b42 |
| tests/runtime-scenarios/packs/project-facing-spec/fixture/project-source.md | 场景：fixture/验证入口归属 | fd23c3030e14 |
| tests/runtime-scenarios/packs/project-facing-spec/oracle.md | 场景：task/oracle 全文 | fdef31a60dac |
| tests/runtime-scenarios/packs/project-facing-spec/task.md | 场景：task/oracle 全文 | 7d676eeb30e2 |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/fixture/baseline/cli.py | 场景：fixture/验证入口归属 | d6d440b34dab |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/fixture/baseline/exporter.py | 场景：fixture/验证入口归属 | 02a2804da9ec |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/fixture/candidate/cli.py | 场景：fixture/验证入口归属 | d6d440b34dab |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/fixture/candidate/exporter.py | 场景：fixture/验证入口归属 | 04d6d16e3acc |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/fixture/candidate/test_exporter.py | 场景：fixture/验证入口归属 | 6b962f711cb2 |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/fixture/verify.py | 场景：fixture/验证入口归属 | 264b9eb771b2 |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/oracle.md | 场景：task/oracle 全文 | 1ba146f2e904 |
| tests/runtime-scenarios/packs/reviewer-semantic-chain/task.md | 场景：task/oracle 全文 | 1f61f1c8b7dd |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/docs/archive/.gitkeep | 场景：fixture/验证入口归属 | a8b6ce519e15 |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/docs/plan/2026-08-10-depth-fetch-baseline/spec.md | 场景：fixture/验证入口归属 | 2104a20f79e1 |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/docs/roadmap/.gitkeep | 场景：fixture/验证入口归属 | cbbd63ca5f94 |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/docs/workflow-rule.md | 场景：fixture/验证入口归属 | 200365b49375 |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/project-facts.md | 场景：fixture/验证入口归属 | 255bfc7d119c |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/templates/profiles.json | 场景：fixture/验证入口归属 | c63fd4d95464 |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/templates/roadmap-project-roadmap-v1.md | 场景：fixture/验证入口归属 | 423458c03d11 |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/fixture/verify.py | 场景：fixture/验证入口归属 | 68fe9c87dd4a |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/oracle.md | 场景：task/oracle 全文 | 0fc55f4561e3 |
| tests/runtime-scenarios/packs/roadmap-self-contained-document/task.md | 场景：task/oracle 全文 | a3192a006d3d |
| tests/runtime-scenarios/packs/roadmap-spec-task-handoff/fixture/project-facts.md | 场景：fixture/验证入口归属 | ec8bf19df52c |
| tests/runtime-scenarios/packs/roadmap-spec-task-handoff/fixture/roadmap.md | 场景：fixture/验证入口归属 | 39d6e4fcc698 |
| tests/runtime-scenarios/packs/roadmap-spec-task-handoff/fixture/verify.py | 场景：fixture/验证入口归属 | 3a7990e907bb |
| tests/runtime-scenarios/packs/roadmap-spec-task-handoff/oracle.md | 场景：task/oracle 全文 | d3a9e2c91f8e |
| tests/runtime-scenarios/packs/roadmap-spec-task-handoff/task.md | 场景：task/oracle 全文 | 0aa97d2eb873 |
| tests/runtime-scenarios/packs/using-sacha-semantic-turn/fixture/project-facts.md | 场景：fixture/验证入口归属 | 522e551ce10d |
| tests/runtime-scenarios/packs/using-sacha-semantic-turn/fixture/verify.py | 场景：fixture/验证入口归属 | 8fa594f76763 |
| tests/runtime-scenarios/packs/using-sacha-semantic-turn/oracle.md | 场景：task/oracle 全文 | 6577e67828cc |
| tests/runtime-scenarios/packs/using-sacha-semantic-turn/task.md | 场景：task/oracle 全文 | ed7a8a908e54 |
| tests/runtime-scenarios/packs/using-sacha-spec-intake/fixture/project-facts.md | 场景：fixture/验证入口归属 | 6a4b6ecf9e68 |
| tests/runtime-scenarios/packs/using-sacha-spec-intake/fixture/verify.py | 场景：fixture/验证入口归属 | abcd97ba27fb |
| tests/runtime-scenarios/packs/using-sacha-spec-intake/oracle.md | 场景：task/oracle 全文 | 96b2fd59a27f |
| tests/runtime-scenarios/packs/using-sacha-spec-intake/task.md | 场景：task/oracle 全文 | fc1be2bd5d65 |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/baseline/Editor/MaterialExport/EnglishRuntimeLog.cs | 场景：fixture/验证入口归属 | 970958c5f3d1 |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/baseline/Editor/MaterialExport/MaterialRegistry.cs | 场景：fixture/验证入口归属 | 37b30a88d8b2 |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/baseline/Editor/MaterialExport/RuntimeMessages.cs | 场景：fixture/验证入口归属 | f609664ba7a3 |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/baseline/handoff.md | 场景：fixture/验证入口归属 | d96557c144ad |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/candidate/Editor/MaterialExport/EnglishRuntimeLog.cs | 场景：fixture/验证入口归属 | 72e28c0f5952 |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/candidate/Editor/MaterialExport/MaterialRegistry.cs | 场景：fixture/验证入口归属 | 87597205655d |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/candidate/Editor/MaterialExport/RuntimeMessages.cs | 场景：fixture/验证入口归属 | fb742c192c46 |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/candidate/handoff.md | 场景：fixture/验证入口归属 | 82b5234ae324 |
| tests/runtime-scenarios/packs/workflow-language-boundary/fixture/project-terminology.md | 场景：fixture/验证入口归属 | 6b7552b81dd8 |
| tests/runtime-scenarios/packs/workflow-language-boundary/oracle.md | 场景：task/oracle 全文 | 5fb590da8f44 |
| tests/runtime-scenarios/packs/workflow-language-boundary/task.md | 场景：task/oracle 全文 | bbf62cd07302 |
| tests/test_code_mode_batch_asset.py | 测试 | f8f837a413d4 |
| tests/test_document_project.py | 测试 | 735b89b9fc40 |
| tests/test_dsh_companion.py | 测试 | 6dee27e484fe |
| tests/test_inspect_pi_models.ps1 | 测试 | afab46ea45fb |
| tests/test_pi_guard.mjs | 测试 | b77e2f7a92cb |
| tests/test_pi_once.ps1 | 测试 | 5ba3599ec114 |
| tests/test_release.py | 测试 | d42548935cd1 |
| tests/test_runtime_scenario_verifiers.py | 测试 | 5a68a9f2ec7e |
| tests/test_setup_agents.py | 测试 | c431e1cf3a5e |
| tests/test_setup_project.py | 测试 | 56b6ee2b42dc |
| tests/test_skill_loading.py | 测试 | 5514c6312673 |
| tests/validate_dsh_companion.py | 测试 | d5adb203b805 |
| tests/validate_release_coherence.py | 测试 | d93c6005cda2 |

清单数：288。原生场景包数：22（21 当前，1 历史）。本报告的 29 项发现与 55 项处置矩阵覆盖当前规则及实现；历史和资源的不同审查深度已单独标出。
