# Sacha Orchestra 开发文档规则

> 文档身份：插件开发使用；不进入发布插件。

## 身份与 Owner

- `CONTEXT.md` 是开发控制面提炼术语与规则的统一入口及开发专用术语 Owner；它保存插件内共享术语的开发侧同步视图，但不复制入口、Role、批准、迁移或协调动作。
- `integrations/**` 保存当前 Provider、Project Integration 和其他开发接入指南；指南只解释开发者如何提供、维护和核查接入，不成为安装后 Runtime 依赖。
- `release.md` 保存 Human 显式快速发版、普通发版或安装时使用的开发期操作指南；[`EVOLUTION.md`](../EVOLUTION.md) 仍拥有当前版本身份，[`scripts/release.py`](../scripts/release.py) 仍拥有机械执行。
- `plan/**` 保存具名任务的 Spec、Execution Report 和 Review Artifact；它们只服务对应任务、恢复或历史取证，不拥有当前产品流程、Runtime 路由或版本状态。

## 读取与维护

- 开发者或 Reviewer → 修改提炼术语或开发规则 → 先读 `CONTEXT.md`，再按[根 `AGENTS.md`](../AGENTS.md) 核对 [`PLUGIN_DESIGN.md`](../PLUGIN_DESIGN.md)、插件内 Runtime Owner 与直接消费者 → 不从历史任务 Artifact 恢复当前机制。
- 开发者或 Reviewer → 修改 Provider、Binding 或 Project Integration 接入 → 只读 `integrations/` 中目标指南及其具名 Owner/消费者 → 不遍历无关 Provider 或历史计划。
- 发布执行者 → Human 显式要求快速发版、普通发版或安装 → 读取 `release.md`、[`EVOLUTION.md`](../EVOLUTION.md) 和精确 staged delta → 不为恢复背景读取全部开发文档或 Runtime Owner。
- 当前任务 → 精确引用 `plan/**` 中的 Artifact → 只读该 path、其当前直接消费者和必要原始证据 → Artifact 状态、日期或“已批准”措辞不使其成为当前产品权威；普通实施不得扫描 `plan/**` 寻找规则或“最新”任务。
- 维护者 → 历史 Artifact 与当前 Owner 冲突且仍会误导当前操作 → 只增加最短的“历史/已取代、替代版本或当前 Owner”入口 → 不现代化正文、不建立第二套生命周期或集中状态索引。

## 内容与验证

- 开发文档可以链接发布插件内的 Runtime Owner；发布插件 Runtime 文档不得依赖本目录承载安装后语义。
- 当前事实、开发决定、Runtime 映射、任务 Artifact 和测试输入分别留在其唯一 Owner；移动或删除文档时同次修复直接入口和可达链接，不复制正文维持旧 path。
- `tests/runtime-scenarios/**` 的 `task.md`、fixture 与 `oracle.md` 是测试输入和裁决材料，不是产品文档；场景流程由 [`tests/runtime-scenarios/README.md`](../tests/runtime-scenarios/README.md) 拥有。
- 纯开发文档改动复核身份、Owner、直接消费者、链接和有界 diff，并按[根 `AGENTS.md`](../AGENTS.md) 选择最小验证；不得用 prose 正则或 Runtime validator 证明文档语义。
