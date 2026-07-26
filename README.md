# Sacha Orchestra

Sacha Orchestra 是跨项目的 Multi-Agent Workflow Orchestration Framework。本仓库包含平台中立的 Core、Codex 与 Claude Code Runtime Adapter、Codex plugin 源码，以及冻结的历史证据。

## 当前边界

- Git release、source candidate、manifest 对应关系和成熟度以 [Evolution](docs/architecture/evolution.md) 为唯一权威。
- [Workflow Contract](plugins/sacha-orchestra/core/workflow-contract.md) 定义 Role、Gate、生命周期和路由；[Artifact Protocol](plugins/sacha-orchestra/core/artifact-protocol.md) 定义 Artifact 与 Handoff。
- Runtime 只映射 Core：[Codex Adapter](plugins/sacha-orchestra/adapters/codex/runtime-adapter.md) 与 [Claude Code Adapter](plugins/sacha-orchestra/adapters/claudecode/runtime-adapter.md) 彼此独立。
- Codex plugin 的使用入口见 [Plugin README](plugins/sacha-orchestra/README.md)。

## 仓库结构

```text
SachaOrchestra/
├── AGENTS.md
├── docs/
│   ├── architecture/
│   ├── history/
│   ├── migrations/
│   └── plans/
├── .agents/plugins/marketplace.json
└── plugins/sacha-orchestra/
    ├── .codex-plugin/plugin.json
    ├── core/
    ├── adapters/
    │   ├── codex/
    │   └── claudecode/
    └── skills/
```

维护源码前读取 [Project AGENTS](AGENTS.md)。它定义权威边界、读取路由、修改纪律、安装授权和验证命令。

## 在另一台电脑接续

```powershell
git clone https://github.com/yyqrc/SachaOrchestra.git
Set-Location SachaOrchestra
git status --short --branch
```

随后读取 `AGENTS.md` 和 Evolution，使用新机器当前版本的 creator/validator。Marketplace 注册、plugin 安装、refresh 或 reinstall 必须另有 Human 明确授权。

## 历史与证据

- [Foundation 历史索引](docs/history/0.1.0/README.md)
- [长期架构与版本策略](docs/architecture/evolution.md)
- [迁移记录](docs/migrations/)
