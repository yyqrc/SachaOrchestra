# Runtime scenario workspace rules

- 当前目录是唯一任务 root；只读取和修改当前目录中的 `instructions.md`、任务输入与 verifier。除显式给出的 Sacha 入口 Skill/Core/Adapter 外，不读取父目录或 SachaOrchestra 开发文档。
- 授权只覆盖 `instructions.md` 明确要求的当前 root 内写入和本地验证；不执行 Git、安装、发布、远程资源、权限或 workspace 外动作。
- 保护输入，采用满足目标的最小改动；读取 verifier 退出状态、stdout、stderr 和失败信息，只声明直接证据覆盖的范围。
- 若需要 Human 决定，只问会改变实现或验收的最小问题；能在当前授权和事实内继续时直接继续。
