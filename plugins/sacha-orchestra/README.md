# Sacha Orchestra

跨运行环境的项目工作流插件。Git 发布版本、源码候选和验证层级以[版本演进](../../docs/architecture/evolution.md)为唯一权威。

## 唯一默认入口

直接调用 `$sacha-orchestra:using-sacha`，或让运行环境在初次接收任务及 Direct 执行中的语义转折点重新判断。清晰任务直接执行；只有预计需要关键澄清、先冻结/持久化 Spec、跨 context owner/恢复、难回退跨 owner 决策、正式协调或独立复核会实质改变执行方式时才建议进入 Sacha。同一 candidate 只询问一次；复杂、耗时、多文件或多平台本身不触发。

```mermaid
flowchart TD
    U["用户目标 / 任务演变"] --> S["初次与语义转折重评估<br/>using-sacha"]; S --> L["清晰任务直接处理"]; S --> Q["执行方式需要改变<br/>说明影响并询问一次"]; Q -->|"拒绝"| L; Q -->|"接受"| PG{"是否需要先规划？"}
    PG -->|"否"| E["进入执行阶段"]; PG -->|"是"| P["规划<br/>确认任务范围和完成标准"]; P --> E; E --> EQ{"能否拆成互不冲突的任务？"}; EQ -->|"不能"| SE["单个执行者完成"]; EQ -->|"可以"| M["Manager<br/>组织安全并行"]
    M --> A["执行任务 A"]; M --> B["执行任务 B"]; A --> I["集成负责人汇总"]; B --> I; SE --> IV["整体验证"]; I --> IV; IV --> RG{"是否需要独立复核？"}; RG -->|"否"| C["负责人收尾 / 交接"]; RG -->|"是"| R["复核"]
    R --> V{"复核结果"}; V -->|"通过，可附后续事项"| C; V -.->|"需要返修"| E; V -.->|"范围或完成标准需调整"| P
    P -.->|"目标或完成标准不清"| CL["需求澄清<br/>Clarify"]; CL -.->|"澄清结果返回"| P; CL -.->|"需要独立研究"| RM["Manager<br/>协调独立研究"]; RM -.->|"研究结果返回"| CL
```

实线是默认处理流程，虚线是按需辅助或返修。单个有界 helper 由当前 owner 直接管理；多个独立单元才交给 Manager。共享工作树不并行写同一文件，隔离 patch/候选实现可并行并由集成负责人串行应用；Git 和整体验证仍串行。详细进入条件见[入口规则](core/intake-contract.md)和[工作流规则](core/workflow-contract.md)，复核见[验收规则](core/assurance-contract.md)，任务协调见[协调规则](core/coordination-contract.md)。

高级用户可直接调用 `planner`、`executor`、`reviewer`、`manager` 或 `feedback`；这表示同意使用 Sacha，但不会扩大写入、安装、Git 或发布授权。显式 `feedback` 在修复 owner 唯一时会创建或复用其真实 workspace task并等待终态，不以 Source-local 调查 helper 或报告代替。`clarify` 与 `setup-project` 只在明确调用时运行。正式跨 context dispatch 由目标 Runtime Adapter 按 Role、风险和能力选择模型；Codex 还可把低返工、自包含工作交给本地 Pi 单次执行，具体型号由 setup-project 巡检后保存在项目内，未配置则使用 Pi 默认值。具体映射见 [Codex](adapters/codex/runtime-adapter.md) 与 [Claude Code](adapters/claudecode/runtime-adapter.md)。

## 项目接入与运行环境

`setup-project` 先预演改动；无 provider catalog 的项目 Skill 只有在完整正文证明可独立调用、当前 Runtime 可见且依赖成立后，才成为待确认的 capability mapping。确认选择并核对预期文件指纹后，它以回滚保护生成项目接入配置；`project-documentation` 根据已确认的策略输出自包含的变更存档或系统指南，不替代正式任务记录。项目命令和领域规则仍由项目规则与领域能力所有。

```mermaid
flowchart TD
    SP["项目接入 setup-project"] --> PI["已确认的项目接入配置"]; PI --> PS["规划存储<br/>独立根目录"]; PI --> DP["项目存档<br/>策略 / 根目录 / 写入授权"]
    PS -->|"需要保存规划文件"| PL["持久规划文件"]; PS -->|"无需保存规划文件"| WF["执行 / 复核 / 合法收尾"]; PL --> WF
    WF --> EV["实际改动 / 验证 / 风险 / 公开证据"]; EV --> EX{"是否产生值得沉淀的经验？"}; EX -->|"否"| DW["文档编写者<br/>组装自包含正文"]; EX -->|"是"| KN["项目事实 + 可复用经验候选"]; KN --> DW; KN -->|"用户同意"| RI["维护能力插件知识库<br/>reference-iteration"]
    DP --> DG{"当前是否允许生成存档？"}; DW --> DG; DG -->|"否"| SK["跳过"]; DG -->|"是"| IN["结构化文档内容"]
    IN --> DR["生成器预演<br/>dry-run"]; DR --> WR["原子新建 + 写后复核"]; WR --> OUT["变更存档 / 系统指南<br/>文件路径 + 文件指纹 + 写入结果"]
    WF -.-> AH["当前任务记录 / 正式交接"]; OUT -.-> NEXT["使用者 / 后续智能体"]; AH -.-> NEXT
```

规划文件和项目存档可以放在不同目录。`experience.extract` 只返回事实与候选，再由当前任务整理成项目文档；维护能力插件知识库还需用户同意。生成器只安全新建单份文档，不创建目录、覆盖旧文件、更新索引或执行 Git/wiki 发布；当前任务仍以正式任务记录和交接为准。

[任务记录与交接协议](core/artifact-protocol.md)定义正式记录；[Codex 运行适配](adapters/codex/runtime-adapter.md)与[Claude Code 运行适配](adapters/claudecode/runtime-adapter.md)定义平台行为。安装、刷新、移除或重新安装必须获得用户明确授权，并用新任务验证插件能被重新发现。

[版本演进](../../docs/architecture/evolution.md)记录当前方向、发布边界与迁移结论。
