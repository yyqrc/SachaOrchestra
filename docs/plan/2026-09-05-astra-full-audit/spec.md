# SachaOrchestra 全仓改进与 Astra 适配实施规格

> 文档身份：插件开发使用，仅供本任务实施与验收，不进入发布插件。
> 状态：已批准；源码已交付，运行验证后续见 [实施记录](execution-report.md)。
> 日期：2026-09-05。

## 1. 目标

修复全仓评估中由当前源码支持的生成器、测试选择和状态展示缺陷，减少没有实际收益的固定回读与强制派发，并让 Codex 使用 Astra 的模型路由符合真实工具能力。

完成后应能观察到：

- Codex 仅使用 v2 协作接口；接口、能力类型或所选模型不支持时明确停止，不自动切换接口、代理类型或模型。
- 大工程中需要共同理解多个模块的任务可选择 Astra medium；特别困难或关键冲突可选择 Astra high；有界任务和普通复杂任务仍分别保留 Luna、Sol。
- 配置生成器逐项复查目标，发现并发变化时停止并安全补偿；文档可以先预览再消费写入授权；合法 YAML 描述和正常项目文案不再被错误解析或拒绝。
- DSH 基础工具集跟随后续明确任务指令更新；历史记录不再导致永久热轮询，旧评审结果不被呈现为当前改动已通过。
- 共享术语只维护一个完整定义；检查仍保留目的和证据边界，取消固定操作次数与无收益的派发数量要求。

## 2. 范围

包含原报告 F01–F29 的逐项处置。报告是问题索引；本规格的事实以当前项目文件、实际工具说明及已确认用户决定为依据。

明确列入删除 **68 个文件**：Pi 的 6 个生产/测试文件，10 个场景包中的 56 个文件，以及 3 个收缩包内的 6 个多余 fixture。其余现有文件修改预计 40–55 个，新增 1 个发布内 Python 共享解析模块。**本轮不新增 Runtime 场景包，也不安排模型/角色/参数的全组合验证。** 具体删除与保留路径见 5.7–5.9；修改数量是估算，不是文件白名单，按实际使用方和有明确案例的必要验证收敛。

| 部分 | 本次处理 | 不纳入本次实施 |
| --- | --- | --- |
| Codex | v2-only、无自动回退、Astra 路由、取消语义、当前能力组合与场景 | v1 兼容、Work 缺少能力参数时的替代传输、尚未暴露的新 API 接入 |
| 生成器 | 并发保护、选测、root 比较、YAML、预览授权、已证实的文案误拒、共享模板解析 | 重建事务框架、废弃仍被调用的结构化正文输入 |
| 规则 | 固定回读、派发收益、术语单源、已确认的职责与验证措辞 | 删除入口接受决定、取消独立复核或安全检查、全局规则重写 |
| DSH | 明确指令切换、初始目录截断、中文判定、结果适用性、轮询、历史授权与孤立 UI 清理 | 修改 DSH 宿主源码、完整动态 ancestor scoped 目录刷新、新增拖拽/缩放功能、无性能证据的增量缓存 |
| 其他 | Pi 完整退役、现有测试与场景精简、Cursor 预算前提澄清、两份历史记录标注、跨平台测试及 DSH 版本校验 | Claude/Cursor 模型生态重选、无授权批量改写其他项目已有配置 |
| 交付层 | 本地源码、静态结构、定向测试与具名场景所取得的实际证据 | Git 提交/推送/tag、发布、市场更新、安装或替换用户插件、全局配置与订阅配置修改 |

Pi 的执行脚本、配置字段、CLI 参数、兼容解析/回写和专用测试整组移除。仓库修改不自动触碰其他项目文件；旧受管 Pi 段只在将来明确调用 setup-project 并按现有 delta/hash 事务确认写入时被移除。备份的全局工具和冻结历史记录不成为退役后的运行入口，也不为了清空关键词而改写历史事实。

## 3. 项目事实与技术决定

### 3.1 当前基线

- 项目为当前工作区的 `bf44b7213cf87b6362dc4a86b56c5556f707f7e9` 加已有工作区修改。原报告的 `2054b78770fd25562677a28f52ca99bf0416689b` 在本地不可解析，不能用它充当当前可执行基线。
- 按报告清单核对的 288 个文件中，175 个字节相同、103 个仅 CRLF/LF 差异、10 个内容变化、无缺失。这只证明文件对应关系。
- 接手前已有 `generate_project_integration.py` 的缩进匹配修补、DSH 中文同步句式及其测试改动；其他已知变化见[接续记录](decisions.md)。实施基于现有内容增量修改，不恢复成报告版本。
- 当前发布身份仍是 `0.14.2`。本规格不选择下一发布版本。
- Python 可发现 PyYAML；这不证明其他安装环境也具有该依赖。原报告的测试与运行结果不能计入本次通过项。

### 3.2 已确认的行为

1. Codex 全部取消自动回退，包括原有 Luna→Sol 和报告建议的 Astra→Sol。失败或状态不明时保留原生标识与错误，不换型号重放；用户以后明确作出的新选择另行消费。
2. DSH 跟随后续明确用户任务指令更新基础工具集。该更新只管理工具暴露，不产生执行授权，也不取消或改写已发生的副作用。
3. Astra medium 纳入常规候选，不要求先出现高风险；依据是多个模块的事实必须共同参与判断，而不是仓库大小或累计 token 数。
4. Astra 的最高自动档由原拟议 xhigh 调整为 high，medium 保留；本轮不设 astra_xhigh 自动路线，也不改 Luna 的 xhigh。
5. Pi 完整移除，不留 deprecated alias、配置兼容读写或自动迁移任务。
6. 纯关键词/固定文案测试原则上删除，只允许极少数有实际机器消费者的重要控制标记例外；Runtime 场景须有明确具体案例，不按所有可能性展开。
7. 主流程、角色职责、唯一负责文件、单层派发、独立来源、用户改动保护和真实证据的权威继续保持。

### 3.3 模型与计费依据

[官方 Codex 长上下文例外](https://help.openai.com/en/articles/20001415-chatgpt-rate-card-enterprise-token-based-pricing#gpt-6-astra-codex-long-context-exception)明确：Astra 在 Codex 中超过 272K 输入不增加长上下文倍率，Codex 不收缓存写入费用。按该页相应 Enterprise 美元价目，长输入时 Astra/Sol 每百万输入分别为 $10/$8、输出为 $50/$30。原报告中“没有明确豁免声明”的结论不再采用；不据此推算用户订阅额度的具体扣减。API Key 使用方式仍与[API 模型计费](https://developers.openai.com/api/docs/models/gpt-6-astra)区分。

[官方迁移指南](https://developers.openai.com/api/docs/guides/latest-model#migration-quickstart)建议先保留有效推理强度进行比较。本轮最高自动档按用户决定暂设 high，采用适合当前任务的推理强度；减少重复确认和无效验证，不把长上下文写成无限读取或高推理强度的理由。窗口与压缩采用宿主默认，不写入 `872000`、`784800` 或固定 90% 参数。

模型表是本次 Codex Adapter 的拟议改动；实施后仍由该 Adapter 唯一维护自动映射，其他现行文档不复制型号表：

| 首次命中顺序 | 判断 | 请求 |
| --- | --- | --- |
| 1 | 用户精确指定且能力组合支持 | 原样使用型号与强度 |
| 2 | 存在困难回退、跨系统耦合或关键冲突等 `broad + critical` 事实 | `gpt-6-astra` / `high` |
| 3 | 非 critical，但需要联合持有较大有效上下文；包括相应独立复核 | `gpt-6-astra` / `medium` |
| 4 | 其余普通复杂任务或普通独立复核 | `gpt-5.6-sol` / `medium` |
| 5 | 输入自足、有界、非简单且可直接验证 | `gpt-5.6-luna` / `max` |
| 6 | 输入自足、有界、轻量且可直接验证 | `gpt-5.6-luna` / `xhigh` |

破坏性删除/覆盖、跨消费者持久身份或解释变化，以及依赖并发、兼容和跨系统生命周期的正确性，仍按实际失败影响判断。普通可重建文件输出本身不自动升级。独立复核的来源隔离与型号强弱分开检查。

## 4. 实施前提与依赖

- 保留现有工作区内容，写入前读取目标和有界差异；发生重叠且不能明确增量合并时停止该文件的写入。
- YAML 解析使用现有 Python 中的 PyYAML 安全加载器。缺失依赖时返回受控错误，保留文件；不在生成器内执行安装。源码和发布技能中说明该前提，不把开发机可用当作安装环境证据。
- 共享模板解析模块必须位于发布 root 内。两个生成器通过同一明确本地模块加载它，不依赖仓库根脚本或开发技能。
- DSH 的依赖、Node 版本、构建命令和包身份以当前 `package.json` 与 lock 为准。任何依赖安装、Profile 更新或新环境创建均须有对应明确授权，不能由测试脚本暗中触发。
- 当前 DSH 参考源码显示：`schemas()` 是 global view，`schemas(agent)` 是受 restriction 影响的有效 scoped view，`tools/change` 没有 layer/change 参数。因此本次不承诺完整动态目录一致性；目标安装版本的 API 仍须单独核对。
- 独立新 API 验证尚无已取得的完成证据。异步工具调用、mid-turn steering、`configuration_update` 只作为待验证宿主能力；不在本规格中实现请求层、开启实验配置或设置替代传输。

## 5. 实施方案

先落地已获批准的职责与行为变化，再同步唯一负责文件和实际使用方；脚本与 DSH 修复按各自依赖实施。测试只覆盖真实生产入口和受影响行为，不增加 Markdown 句子、字数或固定标记测试。

### 5.1 Codex v2 与模型路由

负责文件：`plugins/sacha-orchestra/adapters/codex/runtime-adapter.md`。

- 删除 v1 的发现条件、命名空间、参数列、恢复动作和兼容分支，删除所有创建前模型回退。历史 v1 场景包及其专用测试一并删除，历史事实由已有记录和 Git 历史保留。
- 首次派发前核对当前 `collaboration` 工具集、`fork_turns`、能力类型及逐次模型字段。缺失配套工具、参数组合不支持或能力类型不可发现时报告具体缺口，不调用替代类型。
- 按 3.3 节选择模型，移除自动 `sol_xhigh` 分支；用户精确指定 Sol xhigh 仍可在当前工具支持时使用。
- 新增自动 route_id 为 `astra_medium` 与 `astra_high`，对应 medium/high；不新增 astra_xhigh。用户最高自动档决定只作用于 Astra，Luna xhigh 保持不变。
- 自动研究、实施、复核继续使用相应能力类型及自包含消息。默认 `fork_turns="none"`；只有确需携带尚未落盘的用户决定时才使用最小正整数轮数。
- 不再断言所有 v2 都具有相同字段，也不将当前 Desktop 的组合能力推广到 Work。
- 固定模型类型不得用于“显式字段覆盖固定模型”的实验。宿主禁止覆盖时提前停止；非固定类型的显式值与继承关系按实际支持和遥测说明。
- `interrupt_agent` 只表示回合中断。依赖写入停止的接管必须另行读取代理状态及相关进程/操作的直接结果；`wait_agent` 通知不是底层进程终止证明。
- 收到超时、忙碌、错误或未知结果后保留首次标识；重新查询或恢复只作用于原目标。停止自动回退不删除原目标的合法继续能力。
- 新 API 未暴露时只记录缺口；不把 Promise 并行、工具 yield 或新回合设置称作 API 原生异步、steering 或同会话配置更新。

### 5.2 生成器与选择器

| 文件 | 具体改动 |
| --- | --- |
| `plugins/sacha-orchestra/skills/setup-agents/scripts/setup_agents.py` | 每次 `os.replace` 前复查该目标原像与位置；成功后再从临时文件清理集合移除。冲突进入现有补偿，仅恢复仍匹配本次写入的目标；保留 rollback_failed 等实际结果。最近注释说明检查与替换仍有时间窗口，不宣称原子 CAS。 |
| `plugins/sacha-orchestra/skills/setup-project/scripts/resolve_provider_queries.py` | 用宿主原生路径归一规则生成比较身份，取消无条件 casefold；保留原候选文本供消歧。不同 POSIX 路径不能错误合并，外来路径不能被猜测为本地可写 root。 |
| `plugins/sacha-orchestra/skills/setup-project/scripts/generate_project_integration.py` | 用安全 YAML 解析 frontmatter；校验 mapping、name/description 字符串与唯一身份，拒绝歧义/重复键和不支持的对象类型。保留既有正文证据、来源和写入保护；调用共享模板解析模块。 |
| `plugins/sacha-orchestra/skills/document-project/scripts/generate_project_document.py` | 分开策略/trigger 资格检查与真正写入授权；dry-run 沿用该文档类型已有的 target、sha256、preimage_sha256、parsed/template 等结果字段，不新增正文或 diff 字段。调用者已有生成输入可供审查。project-context 覆盖确认只在写入时消费。移除普通 spec 文件名、cache 目录和裸 UUID 的误拒项；保留实际文件路径、原像和结构保护；调用共享模板解析模块。 |
| `plugins/sacha-orchestra/scripts/template_catalog.py`（新增） | 完整承担现行 `profiles.json` 的解析和结构校验，由上述两个生成器共同使用。保持 schema_version、selection、generation_policy、Profile 类型/版本、required_topics/optional_sections 类型及模板路径/大小约束；形成受控错误，不推断正文语义。两个使用方保留各自 root、授权与写入职责。 |
| `scripts/release.py` | 将仍在使用的生产 JS、两个 Markdown 模板和共享模块映射到对应直接测试；删除退役场景映射。选测消费真实暂存删除状态，不能因 Pi 或其专用测试已删除而要求保留退休映射；新增/修改且无映射的生产入口仍拒绝。 |
| `plugins/sacha-orchestra/skills/setup-project/SKILL.md` | 删除 Pi 巡检/配置步骤与参数；补充本地 Skill YAML 解析前提与缺失错误，不新增安装动作。 |
| `plugins/sacha-orchestra/skills/document-project/SKILL.md` | 明确 dry-run 与写入各自检查边界；合法项目术语不等于私有运行引用，正文语义继续由既有文档检查负责。 |

共享模块的真实使用方是两个生成器；它解决同一配置被深浅不一解析以及错误类型未被捕获的问题。若两个入口仍使用不同结构约束、发生裸 KeyError，或一方未调用该模块，此次提取无效。不得顺带抽取通用事务框架、改变既有 JSON 输入类型或退役结构化正文。

共享解析器的最小接口固定为：

```python
class TemplateCatalogError(ValueError):
    pass

def load_template_catalog(catalog_root: Path) -> tuple[dict[str, Any], bytes, dict[str, Path]]:
    ...
```

- 调用方先按照自己的 project-relative/external-absolute 规则解析、校验并传入绝对 catalog_root；共享模块不接收 Project Integration binding，也不决定目录写入授权。
- 共享模块读取一次 profiles.json，完成现行 JSON 结构约束和 UTF-8/大小检查；验证各模板相对路径、解析后仍位于 catalog_root、文件存在及既有大小上限。未选模板只检查路径和文件元数据，不提前加载正文作语义判断。
- 返回三个值分别为已验证且保持现行字段形状的 manifest、同一次读取的原始 manifest bytes、按唯一 Profile id 索引的已解析模板 Path。两个调用方不再各自解析 manifest 或重建模板路径规则。
- document-project 选定 Profile 后才读取对应正文；manifest 的 hash 使用返回的原始 bytes，模板 hash 使用实际读取的对应 bytes。已有写入前复查继续由调用方承担，不把后来重读的新字节当作先前解析结果的 hash。
- 模块把文件、JSON 和结构错误转换为 TemplateCatalogError；两个入口分别转换为自己的 SetupError/DocumentError，沿用原有受控 JSON 结果，不泄露裸 KeyError 或导入 traceback。
- 两个 standalone 脚本按自身 `__file__` 定位发布 root 的 `scripts/template_catalog.py`，使用 `importlib.util.spec_from_file_location` 加载并持有该模块引用；不按 cwd 寻找、不修改全局 sys.path、不依赖发布 root 外的包。以复制后的发布 root 调用真实入口验证可加载性。

YAML 依赖在读取 Skill frontmatter 时延迟导入或受控捕获导入错误；PyYAML 的默认重复键覆盖行为必须被拒绝检查替代。该检查只服务唯一 Skill 身份，不创建新的配置格式。未授权 write 仍返回原有 refused 结果，不附加正文回显。

### 5.3 规则、职责和开发文档

| 文件 | 具体改动 |
| --- | --- |
| `PLUGIN_DESIGN.md` | 删除 Pi 兼容资产和 setup-project 可选 Pi 配置职责；对齐 Planner 小事实核对、按收益派发、DSH 明确指令切换和按实际风险验证。保留其余节点、角色与返回路线，不新增 Astra 专用流程。 |
| `plugins/sacha-orchestra/core/workflow-contract.md` | Planner 可先自行核对能直接取得的小事实；持续探索、会改变方案的未决事实或用户决定进入 Explore。实施单元的派发条件引用 Coordination，不把“可以拆成两个”解释成必须创建两个代理。 |
| `plugins/sacha-orchestra/core/coordination-contract.md` | 就绪、安全和隔离决定能否派发，实际并行、独立判断或上下文收益决定是否派发；允许主任务完成部分单元或直接串行。删除固定至少两个代理的数量要求。首次评估保留所有相关事实，输入/范围/依赖未变时不机械重做整套评估。 |
| `plugins/sacha-orchestra/skills/planner/SKILL.md` | 保留格式、来源、项目语境三方面的完整核对，删除固定三遍和失败全部重来的要求；按被修改内容复查。同步小事实与持续 Explore 的边界。 |
| `plugins/sacha-orchestra/skills/explore/SKILL.md` | 对齐 Planner 调用边界；用户显式 Explore 仍保持其原有功能。只有触发描述实际变化时同步 frontmatter 和对应元数据。 |
| `plugins/sacha-orchestra/skills/executor/SKILL.md` | 将优先派发条件对齐 Coordination 的实际收益判断，保留同范围修复、集成和原始验证职责。 |
| `AGENTS.md` | 删除共享术语必须全文双向维护的副本要求；区分读取新来源与新增职责。在现有验证条款中明确纯关键词检查的极少数机器控制标记边界，以及场景必须有具体案例、不展开全组合；不新增词表校验器或覆盖率关卡。保留授权、安全、改动保护及证据层次。 |
| `docs/AGENTS.md` | 对齐 CONTEXT 的开发术语/引用用途，保留历史文档和发布可达性边界。 |
| `docs/CONTEXT.md` | 共享术语保留名称、插件内定义链接、使用方和核验方法；删除人工维护的完整定义镜像。开发专用定义仍在此维护。 |
| `EVOLUTION.md` | 在现有待发布描述中记录 v2-only、无自动回退、Pi 退役及本次已落地行为的边界与准确证据；保留 0.14.2 已发布身份与历史证据。下一版本待定，不把删除旧场景写成历史验证从未发生，也不声称覆盖未运行分支。 |

关键替换语义如下；实施时用逐条对应的实际 diff 展示，不能将其当作允许删除相邻规则的摘要：

> Planner 对可直接确认的小事实先自行核对。需要持续探索、存在会改变方案的未决事实或用户决定时进入 Explore。格式、来源和项目语境必须全部核对；修订后重查受影响内容，不以固定回读轮数证明质量。

> 工作单元就绪且输出隔离表示允许派发；主任务还须判断派发是否产生实际收益。可在同一依赖波次中自行完成部分单元；不得仅为达到数量创建代理。派发后继续推进无冲突工作，仅在真实依赖处等待。

不采用 F09 中放宽到“先完成领域调查再选择 Sacha”的建议：现行入口一次性选择有明确既有场景依据。保持早期入口判断、同一目标已接受决定持续有效，以及用户反问时先核对选择所需事实。F17 的“必须精确行数”强结论不成立，现行估算规则保留。Assurance、Reviewer、Manager、术语合同和 Artifact 的现行正确职责只作使用方核对，不为形式同步改写。

### 5.4 DSH 指令更新与目录边界

负责文件：`integrations/dsh/sacha-companion/src/tool-surface-policy.ts`。

**明确指令更新：**

1. 首次消息无明确任务类型时继续默认 inspect。后续明确实施、只读或评审指令重新选择基础 profile。
2. “继续”、进度询问、补充路径/证据以及无法唯一识别的短答保持当前 profile，不因默认分类结果而误切到 inspect；可继续使用现有显式工具查询/解锁。
3. 每次识别到明确的新任务指令，重新应用基础 profile 并清空此前附加解锁。之后成功的 unlock 只在当前选择中生效；reset 清空解锁并回到最近一次明确指令确定的基础 profile。
4. 明确动作句末的感叹号不能使其被当作疑问；保留疑问、否定与只读约束的判定。合并现有中文同步句式修补，不回退用户改动。
5. 冷恢复按原生事件顺序消费明确用户指令和成功配对的 control call/result。新任务指令之前发起的旧 control，其晚到结果不得重新解锁当前工具集；失败或未配对结果无恢复作用。
6. schema restriction、guidance 和 guard 始终使用同一个有效集合；新增可见工具仍须在下一次 request header 广告后才能执行，同 response 的未广告调用继续拒绝。
7. 切换失败时不得提交成功的 profile/source 状态。中途切换不宣称已停止此前正在运行的工具或进程，保留其结果与恢复标识。

**目录：**

- 初始采样覆盖当前 Root 已知工具，不因总数超过 256 而永久丢失尾部名称；同时移除 createToolCatalog 和既有 mergeToolCatalog 追加路径中的总数截断，避免后续一次追加又丢失已采样尾部。保留单次结果数量及每项元数据大小限制，不把完整目录直接发送给模型。
- 尾部工具必须能够通过精确名称查 help，并在满足现有规则时 unlock；新增测试超过 256 项的真实数组输入。
- 保留当前采样来源边界。不得用 global schemas 重建整个 scoped 目录，不为刷新而异步解除限制，不新增分层缓存来猜测宿主数据。
- 同名动态更新、删除和 ancestor scoped 变更的完整一致性列为后续宿主依赖；本次不重写 `mergeToolCatalog` 为不可靠的完整刷新，也不将 F23 宣称为全部解决。README 应说明目录是已采样信息，执行仍以当前原生工具及 guard 结果为准。

### 5.5 DSH 状态展示与局部清理

| 文件 | 具体改动 |
| --- | --- |
| `integrations/dsh/sacha-companion/src/types.ts` | 复用已有 scope_revision 输入；review/evidence 的归一化输出保留可选 scopeRevision。旧数据仍可读取，不增加新的全局任务或授权状态。 |
| `integrations/dsh/sacha-companion/src/normalize.ts` | 对 review/evidence 保留并校验上述修订关联，沿用现有格式与长度约束。 |
| `integrations/dsh/sacha-companion/src/snapshot.ts` | 当前结果卡只选择能对应当前修订的 review/evidence；旧修订、缺关联或晚到的旧结果保留在原时间线，不作为当前通过。 |
| `integrations/dsh/sacha-companion/src/index.ts` | 对齐现有可视化工具中 scope_revision 的说明及直接输出；不新增自动判断完成、授权或增量折叠缓存。 |
| `integrations/dsh/sacha-companion/src/client/activity-monitor.ts` | 使用真实 running/进行中状态和页面/面板可见性选择现有热冷间隔。收起或空闲不继续 1 秒热轮询；错误后保留最后快照并明确连接失败/历史身份，恢复成功清除此状态。会话切换与卸载继续取消旧请求和定时器。 |
| `integrations/dsh/sacha-companion/src/client/ActivityPanel.tsx` | 把可见状态传给轮询，展示旧快照提示；旧 running 状态不冒充当前活动。修订未关联的结果显示为历史或未确认适用，不能显示当前已通过。保留浮动/停靠、自动高度和现有可访问交互。 |
| `integrations/dsh/sacha-companion/src/client/ActivityPanel.module.css` | 增加上述必要状态展示样式；只删除已确认无使用方的 class。 |
| `integrations/dsh/sacha-companion/src/client/panel-geometry.ts` | 删除未接入 UI 的 movePanel/resizePanel 及仅服务它们的类型，保留现有几何计算、停靠和边界逻辑。 |
| `integrations/dsh/sacha-companion/README.md` | 写明新的指令/解锁/恢复行为与目录限制；删除一次性 web Profile 授权和重复当前版本值。安装仍由当次明确请求决定。 |
| `plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md` | 对齐后续明确指令更新；review/evidence 已知修订时传已有 scope_revision；说明未关联结果的证据边界。不改变 continuable child、权限及三层失败关闭保护。 |

客户端连接新鲜度只由轮询状态管理；不写入服务端任务状态。旧包产生的无修订记录兼容读取，但不被推断为当前改动的通过证据。

### 5.6 其他文档与机器校验

| 文件 | 具体改动 |
| --- | --- |
| `plugins/sacha-orchestra/adapters/cursor/runtime-adapter.md` | 删除仓库级 Premium 套餐和固定价格默认。与预算池、阈值相关的判断仅在用户/项目已有明确配置及实时依据时适用；无数据不假设套餐、不按未知阈值降档。不新增预算 schema 或重选当前模型生态。 |
| `docs/plan/2026-08-28-runtime-capability-followup/feature.md` | 顶部增加最短历史入口，指向现行适配器与当前任务；冻结正文保留。 |
| `docs/plan/2026-08-28-runtime-surface-and-dsh-subagents/design.md` | 顶部注明旧分包设计已由单一 Companion 取代，链接现行 DSH Adapter、Companion 和验证入口；冻结正文保留。 |
| `tests/validate_dsh_companion.py` | 删除 version 必须为 0.1.0 的断言；验证非空机器版本及包工具接受的版本，并核对真实产物中的 name/version 与 package.json 一致。不读取 README 文字证明版本。 |

### 5.7 Pi 完整退役

删除以下 6 个文件，不删除其父目录中其他资源；该 scripts 目录还会承载新的共享解析模块：

| 删除文件 | 原使用方处理 |
| --- | --- |
| `plugins/sacha-orchestra/scripts/pi_once.ps1` | 未接入当前适配器的旧执行通道退役。 |
| `plugins/sacha-orchestra/scripts/pi_guard.mjs` | 唯一生产使用方 pi_once 同时删除。 |
| `plugins/sacha-orchestra/skills/setup-project/scripts/inspect_pi_models.ps1` | setup-project 的 Pi 巡检步骤和参数同时删除。 |
| `tests/test_pi_once.ps1` | 被删除能力的专用测试删除。 |
| `tests/test_pi_guard.mjs` | 被删除能力的专用测试删除。 |
| `tests/test_inspect_pi_models.ps1` | 被删除能力的专用测试删除。 |

`generate_project_integration.py` 删除 PI_MODEL_ROUTES、SetupConfig 中的 pi_model_bindings/clear_pi_model_bindings、_parse_pi_model_bindings、旧段解析、渲染参数/正文、沿用或清除分支、结果字段和 CLI 映射。两个旧 CLI 参数直接由标准 argparse 作为未知参数拒绝，不保留 alias、warning-only 或静默忽略入口。

`tests/validate_release_coherence.py` 删除三个 Pi 文件必须存在的要求；不新增它们必须不存在的永久负面清单。`tests/test_setup_project.py` 删除两个 Pi 专用方法：

- `test_pi_model_routing_is_setup_confirmed_and_preserved`
- `test_pi_model_routing_rejects_unconfirmed_or_unsafe_values`

其他项目的旧 Pi 段不被本次仓库操作自动改写。以后正常 setup-project 会生成不含 Pi 的候选：dry-run 完整展示受管旧段删除，未 write 时原文件不变；现有授权、原像和 confirmed-planned-delta-sha256 满足后才写入。只做本次一次性的旧输入退役验收并保留结果，不新建长期 Pi 兼容测试或迁移器。当前生产、配置、现行说明和测试不再消费 Pi；冻结历史记录只保留历史事实。

### 5.8 测试精简规则与明确清单

测试的保留依据是实际入口、结果、文件或字节保护、可解析机器数据与真实失败。不能用规则、Skill、README 的关键词、标题、完整句或篇幅证明行为；纯错误文案匹配也不作为单独保留理由。

仅可能保留的纯文本例外是受管文件所有权分隔标记、模板控制标记等极少数直接被生产解析器消费的重要标记；同一案例仍须观察实际解析/写入结果及禁止副作用。结构化 JSON/TOML 字段、命令参数 tuple 和 code_mode_* 机器错误码的精确比较是机器接口检查，不借“关键词例外”放宽成文案词表。没有实际消费者时，例外也删除；不新增白名单文件、统计配额或文字测试治理脚本。

| 文件/方法 | 删除或收缩 | 保留的直接证据 |
| --- | --- | --- |
| `tests/test_skill_loading.py::test_setup_cli_exposes_only_skill_level_options` | 整方法删除；不维护 argparse 私有 option 字符串清单。 | 其他实际 CLI 正反调用验证可用参数及拒绝行为。 |
| `tests/test_setup_project.py::test_generated_documents_only_add_project_integration_data` | 删除中文标题、禁止短语、using-sacha 字样的存在/缺失断言；方法收缩为元数据往返与幂等。 | 实际 workflow state JSON、刷新无变化、旧元数据读取结果。 |
| `tests/test_setup_project.py` 的 Storage、Spec、Context、Roadmap 及来源相关方法 | 删除固定 Markdown 行、展示名称和错误英文片段断言。 | 实际生成器返回值、真实消费方回读、唯一受管边界、原始用户 bytes、no_changes/拒绝且文件不变。 |
| `tests/test_skill_loading.py` 的旧配置迁移与 Skill loading 方法 | 删除标题、固定排版、旧插件名称等词句断言。 | 用现有消费解析器回读 skill_loadings，并比较结构、确认和幂等结果。 |
| `tests/test_document_project.py` | 删除 forbidden_values 的长词表及固定错误句匹配；删除仅用 SO 前缀拒绝的测试分支、workflow catalog 排版断言。合法 spec/cache/UUID 不再列为禁用词。 | 原像、写入授权、路径边界、真实模板选择、用户 bytes/BOM/CRLF、受管合并与回滚。重要控制标记的拒绝须同时证明没有文件副作用。 |
| `tests/test_release.py` | 删除 join 命令后找词的检查及退役场景映射；相同准备流程可合并，但不以方法数量减少冒充案例减少。 | 直接比较实际模块集合和命令 tuple；只保留各真实生产入口的必要代表。 |
| `tests/test_setup_agents.py` | 删除人类错误消息 substring。 | TOML 配置、owner 标记、原字节、原像、回滚与 no_write。 |
| `tests/test_dsh_companion.py` | 命令由字符串查找改为 tuple/字段比较。 | 真实 package/patch 输入及校验结果，不测试 README 文案。 |
| `integrations/dsh/sacha-companion/tests/artwork.spec.ts` | 删除 CONDUCTOR_CAT/MEMBER_CAT 常量字面量镜像；同义 label 映射只留一个代表。 | 一个已知映射及未知 label 的正常结果；不声称证明图片渲染。 |
| `integrations/dsh/sacha-companion/tests/normalize.spec.ts` | .toThrow 的文案 regex 改为拒绝行为；不增加错误词清单。 | 缺字段、非法 id、依赖环和真实上限等不同故障的最小输入。 |
| `integrations/dsh/sacha-companion/tests/tool-surface-policy.spec.ts` | 删除同分支的重复同义句；保留现有真实中文修补的代表输入。感叹句只补一个已知误判，不扩成标点矩阵。 | 真正不同的执行/否定/只读/疑问输入，以及目录、已配对控制、guard、Root/child 隔离的直接行为。 |
| `integrations/dsh/sacha-companion/tests/panel-geometry.spec.ts` | 删除 move/resize 及仅对应退役实现的断言。 | 当前可见停靠/浮动、边界、损坏持久值恢复。 |

`tests/test_code_mode_batch_asset.py` 继续通过真实 JS asset 观察调用日志和 JSON 结果，保留有明确错误/副作用差异的案例；不因删除 Runtime 演示包而删除生产入口测试。DSH 其余实际状态折叠、会话隔离、图依赖与持久化测试保留必要案例，不为枚举所有状态继续扩写。

当前静态调查估算约 55–75 条纯文案断言需删除或改为结构/行为证据；这是待实际 diff 收敛的工作量，不是目标配额，也不据此声称测试已精简完成。

### 5.9 Runtime 场景包逐项处置

现有 22 包全部完成用途核对：**整包删除 10 个（56 个文件），收缩 3 个，保留 9 个；完成后为 12 个包。** 保留不表示每次都运行，删除也不抹去过去的运行记录。

| 包（均位于 `tests/runtime-scenarios/packs/`） | 处置 | 具体依据或剩余案例 |
| --- | --- | --- |
| `codex-agent-skill-loading-routing` | 删除 5 文件 | v1/v2、工具面、模型优先级及反例矩阵；已包含不支持的固定模型覆盖，不能为填满组合继续保留。 |
| `codex-code-mode-readonly-batch` | 删除 4 文件 | goal+cwd 的内部往返演示与自填 result.json 验证；真实 JS 算法保留生产入口测试，当前不为模型往返统计单独跑包。 |
| `codex-code-mode-v1-batch` | 删除 6 文件 | 已退役 v1 的历史参数与错误矩阵，不再是现行验收。 |
| `codex-context-isolation-execution` | 删除 5 文件 | 人造双服务和强制两个 Executor 的拓扑演示，与新派发规则冲突。 |
| `codex-context-isolation-research` | 删除 6 文件 | 为固定一个 Researcher 数量构造日志场景，没有需要继续维护的单独故障案例。 |
| `codex-model-routing-failure-radius` | 删除 7 文件 | 人造两脚本的型号对照及回退矩阵；保留失败影响判断本身，不保留旧型号专用场景，也不立即换成 Astra 占位包。 |
| `dsh-continuable-parallel-barrier` | 删除 5 文件 | 双 CSV 与强制多个 child 的并行演示；不再用固定拓扑充当任务成功条件。 |
| `executor-only` | 删除 4 文件 | 极小摘要任务用于证明没有经过任何节点，缺少额外 Runtime 包的维护价值。 |
| `explore-handoff-continuation` | 删除 7 文件 | 多事实源、挑战图、依赖和返回的综合恢复演练；没有必须整体保留的独立案例。 |
| `planner-explore-manager-reviewer` | 删除 7 文件 | 为走完角色链并强制双代理构造的综合包，属于过度展开。 |
| `codex-skill-entry-visibility` | 收缩 | 仅保留“把 Sacha 当修改对象不等于接受 Sacha”的具体误触发/输出案例；删除隐式目录、显式调用和接受后路径的附加矩阵。 |
| `dsh-companion-root-surface-routing` | 收缩 | 只保留一个连续案例：初始只读，随后明确要求实施，下一步工具集更新；同一案例需要时核对再次恢复后仍采用最近指令。其他 profile、UI、child、全部工具家族不拼入该包。 |
| `workflow-language-boundary` | 收缩 | 保留产品日志泄漏内部流程，以及一个已定义代码标识不应被误改的直接对照；删除其他语言/产物分类矩阵。 |
| `closeout-command` | 保留 | 唯一 Spec 原位收口，观察实际文件，不移动或额外生成文档。具体案例已充分，不额外要求外部事故编号。 |
| `dsh-continuable-review-isolation` | 保留 | 令牌掩码修复后的独立复核，基于最终文件及原始证据；不扩展 provider/model 组合。 |
| `explore-shared-context-loop` | 保留 | 用户不了解瓶颈时被迫先选方案、解释后又被要求认证分析的明确交互回归。 |
| `project-facing-spec` | 保留 | Material Export 规格混入流程/Handoff 术语的具体来源与输出问题。 |
| `reviewer-semantic-chain` | 保留 | CLI 绕过校验和 UTF-8 字节边界的真实入口缺陷，不依赖绿色测试自报。 |
| `roadmap-self-contained-document` | 保留 | Depth Fetch 路线被写成流程记录、脱离对话不能理解的具体案例。 |
| `roadmap-spec-task-handoff` | 保留 | 确认创建 Planner 任务后却变成普通调查并再次询问入口的明确交接回归。 |
| `using-sacha-semantic-turn` | 保留 | 查询转修改未重新判断入口、把用户反问当接受的连续对话回归。 |
| `using-sacha-spec-intake` | 保留 | 完整 Spec 请求先展开领域调查、直到起草才询问入口的明确回归。 |

3 个收缩包中另明确删除这 6 个多余 fixture 文件（以下相对 packs；DSH 包只改正文，6 个文件来自另外两个包）：

- `codex-skill-entry-visibility/fixture/.agents/skills/domain-copy-editor/SKILL.md`
- `codex-skill-entry-visibility/fixture/.agents/skills/project-fact-check/SKILL.md`
- `workflow-language-boundary/fixture/baseline/Editor/MaterialExport/EnglishRuntimeLog.cs`
- `workflow-language-boundary/fixture/candidate/Editor/MaterialExport/EnglishRuntimeLog.cs`
- `workflow-language-boundary/fixture/baseline/handoff.md`
- `workflow-language-boundary/fixture/candidate/handoff.md`

收缩包同步修改 task/oracle，保留案例真正需要的输入与直接消费者；不创建替代的全组合包。纯 fixture 验证器只能证明文件/数据结果，不能用执行者自填的数量、角色或状态证明实际原生调用。

同步位置：

- `tests/runtime-scenarios/README.md` 删除退役条目、更新 3 个收缩包及新增条件。新包必须来自明确具体案例，有可观察的失败/成功结果且现有案例不能覆盖；不要求为所有角色、参数或状态铺满包，也不新增固定一案一包格式或案例编号协议。
- `tests/test_runtime_scenario_verifiers.py` 删除 readonly/v1 的伪结果构造、test_bundled_verifiers_accept_valid_results、test_bundled_verifiers_reject_corrupted_results 及其专用 helpers；不逐包重复“额外文件检查”。仅保留 test_reviewer_semantic_fixture_exposes_claimed_failures 及其必要 helper，因为它实际运行 CLI 和多字节入口，确认该具体案例确实暴露宣称的缺陷；删除其他夹具包装镜像。
- `scripts/release.py` 和 `tests/test_release.py` 删除已删包选测引用；保留仍有真实消费者的映射。不会把已删除包名变成必须不存在的长期清单。
- `plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md` 移除已删除包及发布 root 外开发场景包的导航，案例清单由开发侧 README 维护；证据维度只在对应变更/声明和明确案例需要时取证，不作为必跑矩阵。
- `AGENTS.md` 的验证条款引用上述明确案例边界；`.agents/skills/sacha-runtime-scenario/SKILL.md:35` 不再把单纯“待验证的流程变化”当作足够新增条件，按 README 的具体案例要求选择。`PLUGIN_DESIGN.md` 对齐按实际案例与交付声明取证，不把真实证据要求删成仅静态检查。

### 5.10 本轮必要的生产回归

仅补或调整已查明问题的最小案例：setup-agents 第一项替换后第二项发生并发修改；生产 JS/模板选测遗漏；POSIX root 大小写误合并；合法 YAML 块标量及依赖缺失；dry-run 提前要写入确认；正常 spec/cache/UUID 文案误拒；共享目录解析深浅不一；DSH 动作感叹句、后续明确指令不更新、256 项尾部丢失、旧评审结果与永久热轮询。

每个用例通过真实入口观察相应结果和禁止副作用。合并准备代码不等于减少重复案例；不根据枚举值或 if 分支数量继续生成输入。旧 Pi 输入只做一次性退役验收，Astra 各档和所有角色组合不新增专用场景。

发布选测需要同时处理文件删除：在读取暂存候选时，从 Git 实际 D 状态取得删除路径集合，传给 validation_commands/narrow_test_modules；不能把 blob 解码失败或工作区文件缺失当作删除。先沿用现有映射并保留仍存活的测试消费者；退役文件及专用测试不再要求自己对应永久映射。所有暂存路径仍参与候选范围、发布身份与结构检查，新增/修改的未知生产入口继续拒绝。用一次真实暂存删除案例验证此路径，可使用隔离的临时 Git 索引，不修改真实索引、分支或历史；不保留 Pi 名称特判。

## 6. 验收标准

### 6.1 源码与结构

- 第 5 节实际修改均有唯一负责位置；Pi 生产/配置/兼容入口与专用测试已退役，10 个场景包已删除、3 个已收缩；没有新流程节点、隐藏旁路、全局配置写入或未列明的兼容迁移。
- 受影响的发布文件只引用发布 root 内可达资源。新增共享模块确由两个生产生成器加载。
- 仅对改变 frontmatter 或 openai.yaml 的技能运行当前 `quick_validate.py`；纯正文不运行该校验器。新增发布资源后运行当前 `validate_plugin.py`。
- 对实际修改范围运行 cprobe，退出成功、结果完整且空白错误为 0。结构或空白通过不代替语义与运行验证。

### 6.2 Python 与包验证

在隔离输入目录通过真实入口覆盖 5.10 的具体回归。按实际改动从以下模块选择；这不是默认整组执行命令，已经有效的结果不重复执行：

```powershell
python -B -m unittest tests.test_setup_agents tests.test_setup_project tests.test_skill_loading tests.test_document_project tests.test_release tests.test_dsh_companion tests.test_code_mode_batch_asset
```

退出码、运行数、失败/错误/跳过计数和原始输出必须可读取。Node 等前提缺失导致的 skip 不算对应行为通过。Windows 路径检查通过不等于 POSIX 已验证；外来路径必须继续被安全拒绝。

DSH 使用当前 package.json 的 `typecheck`、定向 Vitest、`build`、`preview:build` 及包内容核对。先确认依赖可用；会安装或刷新依赖的完整验证器不因叫“验证”而自动取得安装授权。纯测试、打包与安装后行为分别报告。

### 6.3 按具体案例选择运行验证

沿用[现有场景流程](../../../tests/runtime-scenarios/README.md)的输入/裁决隔离和原生证据要求，但不把保留 12 个包解释为每次必须运行全部。原 Spec 中逐个覆盖模型档、角色、取消、所有恢复/界面状态的矩阵要求撤回；没有明确案例的分支不为了“覆盖完整”补测。

本轮与改动直接相关的案例优先为：

- `project-facing-spec`：Planner 核对流程精简后，Material Export 规格仍保留项目来源和必要约束。
- 收缩后的 `dsh-companion-root-surface-routing`：同一对话由只读转为明确实施后，工具集在下一步更新；该案例确需恢复时只续查同一指令，不另铺恢复矩阵。

其他保留包仅在其对应行为实际受影响或出现明确回归时运行。Astra medium/high 的实际请求参数与能取得的遥测优先消费本次真实任务记录，不额外制造各档、各角色或 A/B 成本场景。未出现的分支明确未观察，不声称全分支验证，也不因此新增测试或阻塞有充分证据的交付。

DSH 状态适用性、轮询、guard 和目录尾部的已知缺陷优先由真实生产代码的定向测试证明。需要界面证据时只观察所修改的具体表现，不扩展全部布局、profile、工具家族和平台组合。源测试不能冒充宿主行为；没有运行的层仍标为未验证。

需要新主任务、依赖安装或 Profile 更新时先核对对应授权；缺少授权保留该具体案例的恢复入口，不换嵌套代理或模拟输入充当原生结果。其他运行环境缺口不自动扩大为当前源码交付的阻塞项。

## 7. 失败保护与恢复

- 当前生产文件发生并发或归属不明的重叠变化时，保留其内容，只暂停受影响文件；重新读取有界差异后再处理。
- 配置/文档写入冲突或失败沿用既有受控结果和补偿。不能恢复仍匹配本次写入的状态时明确报告部分写入，不覆盖用户后续修改。
- 模板和 YAML 输入非法、依赖缺失、路径无法唯一确定时不写入；不使用不完整解析或自动安装作为替代。
- Codex 不自动切换模型、接口或能力类型；旧调用已启动或结果未知时保留原标识，不以重试创建解决不确定性。
- DSH 工具集切换只提交已成功应用的状态；目录来源不足不解除限制或猜测完整工具集。
- 修订关联不明的评审结果保持历史/未确认身份；连接失败不能沿用“当前通过”或“当前运行中”的展示。
- 撤销本次实现时只能对照本次实际 diff 恢复本次内容；不执行全仓 reset、clean 或覆盖，也不把配置降级/插件回装作为自动回退。

## 8. 风险、后续项与完成边界

| 项目 | 本规格的边界 |
| --- | --- |
| 原报告计费结论 | 已由用户提供的官方例外修正；美元费率的适用协议与 API Key 保持区分。 |
| Work 资源式 Skill 与新 API | 尚未取得当前目标宿主的实际接入证据；本次不预建支持。独立验证结果只能补充真实前提，不能静默扩大实施范围。 |
| DSH 全量动态目录刷新 | 依赖宿主可证明的未过滤 scoped 来源或变更信息；本规格只处理初始截断和明确指令，不宣称解决完整动态一致性。 |
| 并发写入 | 临近替换复查缩小窗口，不能替代跨进程原子比较交换；不夸大保证。 |
| YAML 依赖 | 开发机已可发现 PyYAML，其他运行环境缺失时需明确准备依赖；生成器不自行安装。 |
| Pi 与旧正文输入 | Pi 已明确完整退役，旧项目段仅在正常获授权 setup 事务中移除；不留兼容入口。与 Pi 无关且仍被消费的结构化正文输入保留。 |
| 独立任务和安装 | 当前只形成 Spec。未来执行场景所需的新任务、依赖安装及 Profile/插件更新须具备对应授权；未执行项保留具体入口。 |
| 成熟度与发布 | 源码、结构、测试、包、运行和用户验收分层陈述；未取得的层不标为完成。该规格不是发布、安装或版本决定。 |

原报告所有发现的处置对应为：F01/F13–F15 → 5.1；F02–F08 → 5.2、5.10；F10–F12/F18–F21 → 5.3、5.8、5.9；F22 → 5.7 完整退役；F23–F26 → 5.4、5.5、5.8；F27–F29 → 5.6、5.8、5.10。F09 保留既有入口，F16 资源式 Skill 后续处理，F17 使用既有估算规则。
