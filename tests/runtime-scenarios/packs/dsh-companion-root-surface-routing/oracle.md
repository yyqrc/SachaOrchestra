# Oracle：DSH companion Root tool-surface routing

## 目标

验证安装在整个 DSH Profile 的 companion 能按当前任务收窄 Root 原生工具 schema，并通过有界目录、下一 step 解锁、reset 与 Session 原生记录恢复长尾能力。该机制只管理 DSH 传输与暴露，不改变 Sacha Core、授权或完成判断。

## 必须通过

1. 使用安装了单一 `@sacha-orchestra/dsh-companion` 的真实 DSH Profile；同一 Profile 不再加载旧 `dsh-visualizer` 或 `dsh-subagents` 包。
2. 新建 fresh inspect Root 执行 `task.md`。首个 `request/header.tools` 只包含 inspect 基础工具、`sacha_tools` 与具名 Sacha 只读入口；`write`、MCP/App、Agent Teams、普通 subagent/workflow 和部署/调试长尾不得出现。
3. `status` 只返回 profile、数量、source、unlocked、fallback 与 warnings；不得顺带返回完整隐藏工具名。
4. `catalog(query="wait_agent")` 与 `help(name="wait_agent")` 有界返回真实 schema metadata。Companion 在全部 `agent/created` composition 完成后的 `agent/session-start` 安装 fail-closed policy；启动期 late global tools 经 `tools/change` 合并进同一个有界 catalog，不能因冷启动早采样而永久丢失。
5. `unlock(wait_agent)` 后，下一 step 的 `request/header.tools` 必须出现 `wait_agent`，随后真实调用成功或返回原生 `noProgress`，不得因它是 Root exact-scope 工具而报 unknown。另用受控原生调用把 `unlock` 与此前未广告的隐藏调用放在同一 assistant message；后者必须被 guard 拒绝。`task.md` 只覆盖 next-step 正例，不能替代该负例。
6. `reset` 后的下一 step header 不再出现 `wait_agent`，status 显示 unlocked 为空并恢复 inspect 基础数量。
7. state route 在 Root live 期间返回与原始 header 一致的 profile、visible/hidden/advertised 精确名单、unlocked、source 与 fallback；默认 Human 面板只显示自然中文模式和数量，不展开完整工具名。
8. 使用两个额外 fresh Root 分别提交明确实施和明确复核任务。首个 header 必须分别为 execute 与 review surface；“不要修改 Core”“交付前独立复核”等附带约束不得把明确实施任务误判为 inspect/review。
9. 重启 DSH 后恢复同一 inspect Session。恢复只消费首条 Human message、成功配对的 `sacha_tools` call/result 与最后 `request/header`；不得新增未知 Session event。恢复后的 status/header 与重启前最后已提交的 unlock/reset 一致。
10. 新建或观察一个 continuable child，child header 不得出现 `sacha_tools`，也不得继承 Root restriction；child 能力只由对应 `sacha_research|sacha_worker|sacha_review` 的 toolFilter 与直接 Runtime 证据决定。

## 原始证据

- Profile package/bundle identity 与 DSH 版本；
- fresh Root 的 `request/header`、`tool/call`、`tool/result` 与重启后 Session export；
- live state route JSON；
- 浏览器中默认面板的可见文字和截图；
- child descriptor、child `request/header.tools` 与 direct-parent/continuable 记录。

源码、package 配置、validator、自报与浏览器静态 DOM 均不能替代上述 Runtime 记录。某项原始记录不可取得时标记为未验证或 blocked，不猜测为 pass。

当前 `task.md` 不会主动制造 same-response 非法调用；未另行执行受控负例时，本 pack 只能报告部分通过。

## Drift

以下任一项判 `drift`：

- Root 首轮重新暴露完整长尾目录，或首次 durable tool call 后自动恢复完整 Standard catalog；
- `sacha_tools` 执行隐藏工具、扩大权限，或 catalog/status 无界回传全部 metadata；
- schema filter、guidance filter 与 execution guard 使用不同 effective allow；
- exact-scope 工具可见但无法查询/解锁，或解锁在尚未广告的同一 response 内直接执行；
- 用自定义 Session event、第二份 DAG/任务状态、Role/Gate/Artifact 或 Sacha 专属工具协议保存恢复状态；
- Root policy 泄漏到 child，或用 child/Agent Teams 状态反推 Sacha Scope、Outcome 或完成。
