# Sacha Orchestra

Sacha Orchestra 是跨项目、多智能体的工作流协调框架。本仓库包含平台中立的核心协议、Codex 与 Claude Code 运行适配、Codex 插件源码，以及冻结的历史证据。

## 当前边界

- Git 发布版本、源码候选、部署清单的对应关系和成熟度以[版本演进](docs/architecture/evolution.md)为唯一权威。
- [入口规则](plugins/sacha-orchestra/core/intake-contract.md)定义何时使用 Sacha，[工作流规则](plugins/sacha-orchestra/core/workflow-contract.md)定义角色和进入条件，[验收规则](plugins/sacha-orchestra/core/assurance-contract.md)定义独立复核，[协调规则](plugins/sacha-orchestra/core/coordination-contract.md)定义任务协调与结果返回，[交接协议](plugins/sacha-orchestra/core/artifact-protocol.md)定义持久记录。
- 运行适配只负责把核心协议映射到具体平台：[Codex 运行适配](plugins/sacha-orchestra/adapters/codex/runtime-adapter.md)与[Claude Code 运行适配](plugins/sacha-orchestra/adapters/claudecode/runtime-adapter.md)彼此独立。
- Codex 插件通过 `using-sacha` 判断任务；使用概览和流程图见[插件说明](plugins/sacha-orchestra/README.md)。
- 当前真实问题驱动的插件迭代方向见[当前迭代路线图](ITERATION-ROADMAP-PROPOSAL.md)。
- 能力插件如何声明能力目录并与项目接入、任务角色闭环，见开发期[能力提供方接入指南](docs/integrations/capability-provider-guide.md)；该指南不随插件部署。

## 仓库结构

```text
SachaOrchestra/
├── AGENTS.md
├── docs/
│   ├── architecture/
│   ├── history/
│   ├── integrations/
│   ├── migrations/
│   └── plans/
├── tests/
├── .agents/plugins/marketplace.json
└── plugins/sacha-orchestra/
    ├── .codex-plugin/plugin.json
    ├── core/
    ├── adapters/
    │   ├── codex/
    │   └── claudecode/
    ├── scripts/
    └── skills/
```

维护源码前读取[项目规则](AGENTS.md)。它定义权威边界、读取路线、修改纪律、安装授权和验证命令。

## 在另一台电脑接续

```powershell
git clone https://github.com/yyqrc/SachaOrchestra.git
Set-Location SachaOrchestra
git status --short --branch
```

随后读取 `AGENTS.md` 和版本演进文档，并使用新机器当前版本的创建与校验工具。Marketplace 注册、插件安装、刷新或重新安装必须另有用户明确授权。

## 历史与证据

- [基础版本历史索引](docs/history/0.1.0/README.md)
- [0.2.1 CGame 能力插件接入设计归档](docs/history/0.2.1/cgame-domain-capability-integration.md)
- [0.2.2 迭代路线图设计归档](docs/history/0.2.2/iteration-roadmap-2026-07-24.md)
- [长期架构与版本策略](docs/architecture/evolution.md)
- [迁移记录](docs/migrations/)
