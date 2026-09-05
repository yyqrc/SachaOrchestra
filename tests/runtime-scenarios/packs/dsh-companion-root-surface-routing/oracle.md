# Oracle：DSH Root 连续指令切换

## 目标

验证同一 DSH Root 对话先收到只读要求、再收到明确实施要求时，下一步原生工具面随最近的明确指令更新。该机制只管理工具暴露，不产生写入授权之外的授权。

## 必须通过

1. 使用安装了当前 `@sacha-orchestra/dsh-companion` 的真实 DSH Profile，新建一个 Root，并按 `task.md` 的消息边界发送第一条只读请求。
2. 第一条请求后的 `request/header.tools` 使用 inspect 基础工具面；`status` 返回 inspect profile、数量、source、unlocked、fallback 与 warnings，不顺带返回完整隐藏目录。
3. 在同一对话发送第二条明确实施请求。其后的下一次 `request/header.tools` 使用 execute 基础工具面，且先前临时解锁已清除；不得继续沿用 inspect 工具面。
4. 执行者只修改 `README.md` 标题，验证文件结果并报告；工具面变化不扩大第二条消息给出的写入范围。
5. 若本次案例确需核对冷恢复，只恢复这一个 Session。恢复后的下一次 header 仍采用最近的 execute 指令，不另行铺设 profile、界面、child 或工具家族矩阵。

## 原始证据

- Profile package identity 与 DSH 版本；
- 同一 Root 的两条 Human 消息，以及两条消息后各自的下一次 `request/header.tools`；
- `sacha_tools status` 的原始返回、文件差异和直接验证输出；
- 实际执行恢复时，补充同一 Session 的恢复记录。

源码、package 配置、validator、自报与浏览器静态 DOM 均不能替代上述 Runtime 记录。某项原始记录不可取得时标记为未验证或 blocked，不猜测为 pass。

## Drift

以下任一项判 `drift`：

- 第二条明确实施消息后的下一次 header 仍是 inspect，或在没有新明确指令时自行切换；
- profile 切换保留先前临时解锁，或 `status` 无界回传完整隐藏目录；
- 执行者超出第二条消息修改其他文件，或把工具面切换当作额外授权；
- 用其他 Root、静态源码、自报或模拟结果代替同一对话的原生 header 与文件证据。
