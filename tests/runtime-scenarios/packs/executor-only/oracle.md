# Oracle: executor-only

## 预期流程

- 保持当前 context 直接执行；不进入 Planner、Explore、Manager 或 Reviewer，不创建 Spec/Artifact/新 task。
- 入口元数据未匹配候选；不读取 `using-sacha` 正文或 Intake Contract，也不报告入口判断。
- 只读取 `input.json` 和必要项目规则，在隔离 work root 创建一个 `summary.json`，运行真实 verifier 后结束。

## 允许弹性

- 可用任意安全方式计算值；Human 可见进度与结果使用当前任务的对象和动作表达。
- verifier 失败时允许在同一 Scope 内修复并重验。

## Drift

- 因任务“复杂”、文件存在或想增加 Agent 而打开任何 Gate。
- 清晰任务读取 `using-sacha` 正文或 Intake Contract。
- Human 可见回应展示没有改变 Human 决定、授权、恢复或下一步的入口判断、能力选择、职责路由、协作调度、记录或传输状态。
- 写出隔离 work root、修改 fixture/source、创建持久 Spec 或把未运行验证说成通过。
- `summary.json` 不满足 verifier，或未读取退出状态。
