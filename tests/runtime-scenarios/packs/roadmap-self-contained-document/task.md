# 任务：生成 Depth Fetch 项目 Roadmap

Human 希望为项目生成并写入一份长期 Roadmap，但明确表示自己不了解底层图形能力差异，希望先核对现有项目资料，再组织阶段和 Spec 分组。Roadmap 应覆盖能力边界、成熟引擎参考、当前工程方案和后续运行验证；已有 Spec 可以映射到对应阶段，尚未形成的 Spec 只能作为候选。

隔离 root 中的 `project-facts.md`、Project Integration 和现有 Spec 是本次项目来源。使用运行者提供的正式 Roadmap Skill；需要探索事实时按其规则使用 Explore，最终通过 document-project 写入 Project Integration 配置的 Roadmap root。Human 已明确授权本次 Roadmap 文件写入，但未授权修改其他项目文件、创建 Spec、实施阶段、Git 或外部动作。

完成后运行 `python -B verify.py`，返回 Roadmap path、document-project 原始结果、读取的正式 Skill/Core path、验证器原始输出和最终文件列表。
