# 全局 Codex 配置备份

2026-09-05 的本机快照，供恢复个人规则、Skills 和本地工具使用。仅供开发备份，不进入 Sacha 发布插件；压缩包中的规则和技能不会被本仓库自动加载。

备份文件：`global-codex.zip`，共 111 个文件。生成后已检查 ZIP 完整性，并逐文件与来源进行字节比较，全部一致。

| 压缩包路径 | 原始来源与内容 |
| --- | --- |
| `codex/AGENTS.md` | `%USERPROFILE%/.codex/AGENTS.md`，原样备份 |
| `codex/skills/` | `%USERPROFILE%/.codex/skills/`，包含正文、元数据、脚本和资源，以及 `.system` |
| `tools/windows-x64/cprobe.exe` | `%USERPROFILE%/.local/bin/cprobe.exe`，版本 0.2.1 |
| `tools/windows-x64/change-probe.exe` | `%USERPROFILE%/.local/bin/change-probe.exe`，保留已安装的等价入口 |
| `tools/windows-x64/fastctx.exe` | `%USERPROFILE%/.fastctx/bin/fastctx.exe`，版本 0.2.5 |
| `tools/windows-x64/rg.exe` | 当前 PATH 中的 ripgrep 可执行文件 |

个人 Skills（8 个）：agent-rule-maintenance, caveman, change-probe, cli-creator, eli5, gc-minimal-zine-poster-v0-3, human-information-design, playwright。

内置 Skills（6 个）：imagegen, openai-docs, plugin-creator, review-agent, skill-creator, skill-installer。

## 恢复

1. 将压缩包解压到单独目录，先比较目标机器现有文件，保留需要的较新内容。
2. 将 `codex/AGENTS.md` 和需要的 `codex/skills/` 内容复制到目标机器的 Codex 用户目录；默认是 `%USERPROFILE%/.codex/`。内置 `.system` 来自本次快照，恢复前核对目标 Codex 的版本兼容性。
3. 按需将 `cprobe.exe`、`change-probe.exe`、`rg.exe` 放入目标机器的 PATH 目录；将 `fastctx.exe` 放入指定工具目录，并由目标机器的 MCP 配置指向它。
4. 用 `cprobe --version`、`rg --version` 和 FastCtx 的 `--version` 检查工具，再验证实际需要的技能与 MCP 连接。

工具是当前 Windows 可执行文件的备份，不包含工具源码。Python、Node.js/npm/npx、Git、SVN、Bash 等依赖仍需由目标环境提供；Playwright 的包装脚本已随技能保存，浏览器与 npm 下载缓存未包含。

未包含插件安装缓存中的 Skills、凭据、会话、记忆、全局 `config.toml`、Python 字节码缓存和 FastCtx 的旧版 `.bak`。本次没有修改全局安装，没有执行恢复或验证跨机器运行，也没有推送远程仓库。
