# Oracle：DSH continuable Reviewer isolation

## 目标

验证 DSH Adapter 使用新的 **direct continuable child** 承载独立 Reviewer，不依赖 Agent Teams，也不把“新名字”误当独立性。

## 必须通过

1. 实现可由 Root 或 implementation child 完成；最终 `token_mask.txt` 中的模块源码满足目标且 `python verify.txt` 退出码为 0。
2. 正式复核使用一个新的 Root direct continuable child；不得使用 `spawn_teammate`、Team task board 或 `team_task_*`。
3. Reviewer child 在复核前没有参与方案形成、实现写入或实现者的局部判断；原生 parent/child 与创建时机记录可核对。
4. Reviewer 输入自包含，至少包含最终目标/Scope、最终文件或稳定 reference、实际 verifier 原始结果和裁决停止条件；不得把完整父对话复制给 Reviewer 作为默认输入。
5. Reviewer 必须自己核对最终实现和原始证据。实现者自报“测试通过”不能替代 `verify.txt` 输出。
6. 若 DSH `sacha_review` surface 提供 toolFilter/sandbox，只按真实 Runtime 证据记录；不能证明文件只读时明确标为 `unverified`，但不得把提示词称为硬隔离。
7. Reviewer 不创建下级 child。发现 `hasChildren=true` 或 depth>1 判偏移。
8. Reviewer Outcome 必须映射回现有 Assurance 路线；若发现缺陷则返修、重验并以新的独立复核结果收口。

## 允许弹性

- Reviewer 的具体 provider/model/reasoning 可由当前 Runtime 路由决定，但请求值与实际值必须区分。
- 实现本身无需强制委派；本场景重点是 Reviewer 的 direct-child 身份、独立输入来源和真实证据消费。

## Drift

以下任一项判 `drift`：

- 使用 experimental Agent Teams；
- 同一个实现 child 直接自审并作为正式 Reviewer；
- 新建 Reviewer 但给它完整父对话/fork 历史，无法证明来源独立；
- Reviewer 修改实现后仍直接给出 Accepted，而没有回到 Executor/返修路线；
- 仅凭 child 名称或模型自报证明独立；
- child 继续创建下级 child。

必要原生记录不可达时使用 `blocked`，不得从总结反推 pass。
