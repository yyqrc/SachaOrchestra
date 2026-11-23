# Oracle：DSH 主会话的工具切换和写入授权

## 目标

在同一个 DSH 主会话中核对首次工具暴露、工具集切换和写入。配套包依据会话事件切换工具集。用户的第二条消息才授权修改目标标题。

## 必须通过

1. 使用已安装当前 `@sacha-orchestra/dsh-companion` 的真实 DSH Profile。从全新的主会话发送第一条只读请求。在任何切换事件之前，首个模型请求采用 `bootstrap` 工具集。
2. 核对 `sacha_tools status` 的原始返回。它给出 `phase`、`visible_count`、`hidden_count`、`source`、`unlocked`、`fallback` 与 `warnings`，不附完整隐藏目录。阶段须与调用当时已记录的会话事件一致。
3. 自动切换由首个已记录的 `tool/call` 或 `assistant/message` 触发。排除 `sacha_tools` 自己的控制调用。PTC 模式下按原生日志识别事件，计入另行记录的 `run_code` 调用。核对该事件之后的下一次模型请求已采用 `resident` 工具集。切换可以发生在第一条只读请求期间。
4. 在同一会话发送第二条消息。核对只有第二条消息给出写入授权后，执行者才修改 `README.md` 标题，并直接检查和报告结果。
5. 若本次确需检查冷恢复，只恢复这一个会话。根据会话中已记录的事件和已成功执行的阶段控制重建工具集。

## 原始证据

- Profile package identity 与 DSH 版本；
- 同一主会话的两条用户消息、首个切换事件，以及切换前后的 `request/header.tools`。PTC 模式下同时取模型实际收到的工具 SDK 段；
- `sacha_tools status` 的原始返回、文件差异和直接验证输出；
- 实际执行恢复时，补充同一 Session 的恢复记录。

源码、package 配置、validator、自报与浏览器静态 DOM 均不能替代上述 Runtime 记录。某项原始记录不可取得时标记为未验证或 blocked，不猜测为 pass。

## Drift

以下任一项判 `drift`：

- 合格事件出现前已开放 `resident` 工具集，或首个合格事件后的下一次请求仍停在 `bootstrap`。原生日志只有 `sacha_tools` 控制调用时，自动切换也属于偏差；
- `status` 返回的阶段与调用时的记录不符，或附带完整隐藏目录；
- 执行者在第一条只读请求中写入，或第二条消息后修改范围超出指定标题；
- 用其他 Root、静态源码、自报或模拟结果代替同一对话的原生 header 与文件证据。
