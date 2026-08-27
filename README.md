# Sacha Orchestra

> 文档身份：插件开发使用；不进入发布插件。

Sacha Orchestra 是跨项目、多智能体的工作流协调框架。本仓库包含平台中立的核心协议、Codex、Claude Code、Cursor 与 DeepSeek Harness 运行适配、四个 Runtime 共用的 Agent Plugin 源码与 marketplace 清单，以及独立安装的 DSH continuable-subagent 与可视化 companion。

本文件只负责仓库导航，不定义工作流，也不复制顶层设计；完整流程骨架、Role/Skill 职责和 Core owner 的唯一权威是仓库根的[插件顶层设计](PLUGIN_DESIGN.md)。它与 `AGENTS.md` 同属开发控制面，不随插件发布。

## 当前边界

- 当前 release、当前待发布源码版本、当前 breaking boundary、成熟度与尚未实施的长期方向以[版本演进](EVOLUTION.md)为唯一权威；部署清单只声明当前源码版本。
- [插件顶层设计](PLUGIN_DESIGN.md)定义完整流程骨架、Role/Skill 职责、Core owner 和自上而下变更顺序；[术语规则](plugins/sacha-orchestra/core/terminology-contract.md)、[入口规则](plugins/sacha-orchestra/core/intake-contract.md)、[工作流规则](plugins/sacha-orchestra/core/workflow-contract.md)、[验收规则](plugins/sacha-orchestra/core/assurance-contract.md)、[协调规则](plugins/sacha-orchestra/core/coordination-contract.md)和[交接协议](plugins/sacha-orchestra/core/artifact-protocol.md)分别实现 Runtime 局部语义。
- 运行适配只负责把核心协议映射到具体平台：[Codex 运行适配](plugins/sacha-orchestra/adapters/codex/runtime-adapter.md)、[Claude Code 运行适配](plugins/sacha-orchestra/adapters/claudecode/runtime-adapter.md)、[Cursor 运行适配](plugins/sacha-orchestra/adapters/cursor/runtime-adapter.md)与 [DeepSeek Harness 运行适配](plugins/sacha-orchestra/adapters/dsh/runtime-adapter.md)彼此独立。
- Codex、Claude Code、Cursor 与 DSH deployment 共用同一 Agent Plugin 源码；Cursor 与 DSH 通过 Agent Plugins 开放标准加载根 `plugin.json` 与 `skills/`。`using-sacha` 是唯一默认入口。Runtime 不读取顶层设计，由 Workflow Contract 和各 Skill 自包含执行。
- [DSH subagent companion bundle](integrations/dsh/sacha-subagents/README.md)只把 DSH 官方 continuable-subagent 能力组合成 `sacha_research`、`sacha_worker`、`sacha_review` 三个 Adapter surface；不拥有 Gate、Manager DAG、授权或完成判断。
- [DSH 可视化 companion plugin](integrations/dsh/sacha-visualizer/README.md)独立构建和安装；它回放 Sacha phase/Gate/Manager DAG/delegation/Review/Evidence，并观察 Root 的 continuable direct children，不进入 marketplace，也不替代 Core、Adapter、Artifact 或 Runtime 证据。
- 能力插件如何声明能力目录并与项目接入、任务角色闭环，见开发期[能力提供方接入指南](docs/integrations/capability-provider-guide.md)；该指南不随插件部署。
- Role 与流程行为不靠 Markdown 文本自测；可复现任务包和独立 evaluator 流程见 [Runtime scenarios](tests/runtime-scenarios/README.md)。

## 仓库结构

```text
SachaOrchestra/
├── AGENTS.md
├── PLUGIN_DESIGN.md
├── README.md
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
├── .cursor-plugin/marketplace.json
├── docs/
│   ├── AGENTS.md
│   ├── CONTEXT.md
│   ├── integrations/
│   ├── plan/
│   └── release.md
├── tests/
│   └── runtime-scenarios/
├── integrations/dsh/
│   ├── sacha-subagents/
│   │   ├── package.json
│   │   └── cordis.patch.yml
│   └── sacha-visualizer/
│       ├── package.json
│       ├── cordis.patch.yml
│       └── src/
└── plugins/sacha-orchestra/
    ├── plugin.json
    ├── .codex-plugin/plugin.json
    ├── .claude-plugin/plugin.json
    ├── README.md
    ├── core/
    ├── adapters/
    │   ├── codex/
    │   ├── claudecode/
    │   ├── cursor/
    │   └── dsh/
    ├── scripts/
    └── skills/
```

维护源码前读取[项目规则](AGENTS.md)。它定义权威边界、读取路线、修改纪律、安装授权和验证命令。
