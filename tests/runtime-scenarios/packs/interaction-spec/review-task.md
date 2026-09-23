# 任务：复核图像检查窗口候选

使用 Sacha Reviewer，只读核对本 root 的 approved-behavior.md、candidate.py 及 candidate-checks.py。允许运行现有检查和无持久副作用的本地调用。依据真实候选和直接结果判断是否满足批准行为，不能仅采信测试总数或候选自报；不修复、不放宽行为要求，不派发代理。

返回具体问题、行为依据、证据及 Outcome。不得读取规划阶段产物、源包、oracle、其他会话或开发文档；不得写文件、操作 Git、安装或访问外部资源。
