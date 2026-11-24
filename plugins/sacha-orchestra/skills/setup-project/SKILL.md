---
name: setup-project
description: 用户明确要求配置或更新项目接入时使用。核对项目规则、技能加载策略和文档位置，再生成接入配置。
---

# Setup Project（项目接入）

## 功能

按用户明确请求生成或刷新项目接入配置。项目接入、规范技能和项目上下文见[术语定义](../../core/terminology-contract.md)。项目实施、文档正文和用户级代理配置由对应技能处理。

## 输入与首查

1. 用户提供项目起始目录时沿用。否则由[解析器](scripts/resolve_provider_queries.py)根据项目接入配置、`AGENTS.md` 和版本控制信息确定唯一项目根目录。仍有多个候选时保留 `unresolved`。
2. 刷新时读取并沿用已有的项目规则绑定、技能加载策略、技能根目录策略、文档位置和写入策略。核对新发现或实际变化的技能时，用运行环境目录核实 `name`、`description` 与 `path`，必要时用 Provider 资料核对副作用。按[工作流规则](../../core/workflow-contract.md)确认适用的加载策略。完整读取 `authority`/`independent` 正文和调用必需路径，只映射运行环境可见且可独立使用的技能。
3. `project.rules` 使用用户明示或本轮已选 Provider 的正式资源原始字节。

已选技能依赖独立项目数据绑定时，通过 Provider 的只读入口核对，复用有效绑定和已有禁用决定。缺失或失效时先核对现有授权，在授权内由 Provider 的配置技能处理。确实需要用户决定时按动作顺序第 6 步处理。普通项目接入不授权修改用户级配置。Provider 数据绑定由 Provider 管理，不复制到项目接入配置。

## 动作顺序

1. [生成器](scripts/generate_project_integration.py)用 PyYAML 校验本地技能元数据，并核对正文、SHA-256、路径和可见性。项目接入配置只保存规范技能身份和加载策略。发现缺口或冲突时，先用已有配置和可读证据解决。仍不满足生成器要求时保留原配置，按第 6 步处理。缺少 PyYAML 时报告错误，不自动安装依赖。
2. 配置文档位置：
   - 首次 Spec storage root 默认 `docs/plan`。
   - 沿用已配置的 Spec base、Roadmap root 和 Project Documentation root。需要新增或改变位置时使用已明确的项目约定或用户决定。Setup 派生 `<spec-base>/plan` 和 `<spec-base>/CONTEXT.md`，原样保存 Roadmap root，并生成 `<YYYY-MM-DD>-<short-slug>-roadmap.md` 文件模式。
   - 外部 path 标记 `non-portable`；文件系统根无效。
3. 模板目录可选。生成器校验 `profiles.json`，项目接入配置只保存其目录类型和路径。模板选择见 [`document-project`](../document-project/SKILL.md#动作顺序)。
4. 读取受管块，按归属标记保留适用项、刷新同源资源、合并新来源。替换来源不明的旧段须有用户明确指定的来源，并核对原始资源。旧 `SOURCE SHA-256` 随对应内容刷新移除。
5. 刷新时让生成器复用已有配置，只提供本次需要更改的设置。必须整组提交的绑定列表保留原有的其他项。试运行取得 `delta` 和 `planned_delta_sha256` 后，在已有授权内将该值传给 `--confirmed-planned-delta-sha256` 写入。
6. 计划变化时重新试运行。只有变化会影响权限、写入位置或实际行为，而且从已有配置、项目规则和用户决定中仍无法确定做法时，才询问需要用户决定的部分。

## 输出

- 需要用户决定时，按第 6 步询问实际缺项。提问和报告按[交互规则](../../core/human-interaction-contract.md)处理。
- 说明本次新增、更新、移除或保留了哪些项目配置，并给出相应的验证结果。只完成预检时说明尚未写入。出现冲突或影响使用的警告时，指出受影响的配置和下一步。给出本次涉及的 `non-portable` 路径，说明换环境时需要核对什么。需要核对具体配置或排障时，引用工具返回的 `reconciliation`、`transaction` 或 `warning`。

## 停止与禁止边界

- 普通任务不调用；写入只来自本轮显式配置/刷新授权。标记外的 AGENTS 保持不变，写入原子且可恢复。
- 技能提供方可选。没有提供方时，仍检查当前运行环境能读取的项目技能。没有可用的技能绑定时，按项目规则使用已有工具。
- `workflow-rule.md` 只记录该项目的运行差异，状态文件供接入配置恢复使用。
- Spec base、Roadmap root、Project Documentation root 和 template catalog root 各自独立；Project Context path 由 Spec base 派生。
- 模板目录的 Profile 选择和正文生成由 `document-project` 处理。
- `project-rules` 按规范技能的归属和资源完整内容合并。项目规则文件只保留一个受管区，删除须由用户明确决定。
